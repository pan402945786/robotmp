"""PyBullet backend for the robotmp pick-and-place loop."""
from __future__ import annotations

from dataclasses import dataclass
import time
from pathlib import Path
from typing import Any, Callable

from .environment import FailureMode
from .models import ObjectState, RobotState, SceneState

try:
    import pybullet as _p
    import pybullet_data as _pybullet_data
except ImportError:  # Keep the rule backend importable in Python 3.14.
    _p = None
    _pybullet_data = None


def _require_pybullet():
    if _p is None:
        raise RuntimeError(
            "PyBullet is not installed in this Python environment. "
            "Use the project's Conda py311 environment and install pybullet==3.2.7."
        )
    return _p


@dataclass
class SimConfig:
    steps_per_action: int = 24
    time_step_s: float = 1.0 / 240.0
    table_z: float = 0.70
    cube_half_extent: float = 0.05
    grasp_width: float = 0.115
    realtime: bool = False
    gripper_model: str = "urdf"
    arm_model: str = "none"
    frame_callback: Callable[[SceneState], None] | None = None


class PyBulletPickPlaceEnv:
    """A minimal PyBullet scene with a dynamic cube and two gripper fingers."""

    def __init__(self, failure_mode: FailureMode = FailureMode.NONE, *, gui: bool = False, config: SimConfig | None = None):
        self.p = _require_pybullet()
        self.config = config or SimConfig()
        self.failure_mode = FailureMode(failure_mode)
        self.client = self.p.connect(self.p.GUI if gui else self.p.DIRECT)
        if self.client < 0:
            raise RuntimeError("PyBullet could not create a physics client")
        self._closed = False
        self.reset()

    def reset(self) -> SceneState:
        p, c = self.p, self.config
        p.resetSimulation(physicsClientId=self.client)
        p.setGravity(0, 0, -9.81, physicsClientId=self.client)
        p.setTimeStep(c.time_step_s, physicsClientId=self.client)
        p.setPhysicsEngineParameter(numSolverIterations=80, physicsClientId=self.client)
        p.setAdditionalSearchPath(_pybullet_data.getDataPath())
        self._time = 0.0
        self._phase = "observe"
        self._events: list[str] = []
        self._anomalies: list[str] = []
        self._stopped = False
        self._object_visible = self.failure_mode != FailureMode.OCCLUDED
        # Keep the target outside the xArm6 home envelope.  The arm is moved
        # to this target by IK during approach; spawning at x=0.45 prevents
        # the default URDF pose from touching the cube before the task starts.
        self._object_start = [0.45 if c.arm_model in {"arm6dof", "xarm6"} else 0.0, 0.0, c.table_z + c.cube_half_extent]
        self._ee_position = [0.0, 0.0, c.table_z + 0.17]
        self._gripper_open = True
        self._gripper_force = 0.0
        self._grasped = False
        self._lifted = False
        self._constraint_id: int | None = None
        self._arm_joint_ids: list[int] = []
        self._ee_link_index = -1
        self._arm_lower: list[float] = []
        self._arm_upper: list[float] = []
        self._arm_effort: list[float] = []
        self._arm_velocity: list[float] = []

        table_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.8, 0.8, 0.02], physicsClientId=self.client)
        table_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.8, 0.8, 0.02], rgbaColor=[0.24, 0.34, 0.44, 1], physicsClientId=self.client)
        self._table_id = p.createMultiBody(0, table_shape, table_visual, [0, 0, c.table_z - 0.02], physicsClientId=self.client)

        cube_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[c.cube_half_extent] * 3, physicsClientId=self.client)
        cube_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[c.cube_half_extent] * 3, rgbaColor=[0.15, 0.75, 0.86, 1], physicsClientId=self.client)
        self._cube_id = p.createMultiBody(0.10, cube_shape, cube_visual, self._object_start, physicsClientId=self.client)

        if c.arm_model == "arm6dof":
            arm_urdf = Path(__file__).resolve().parent.parent / "assets" / "arm6dof_gripper.urdf"
            self._gripper_id = p.loadURDF(str(arm_urdf), [0, 0, c.table_z], useFixedBase=True, physicsClientId=self.client)
            self._wrist_id = self._gripper_id
            self._arm_joint_ids = list(range(6))
            self._finger_joint_ids = [6, 7]
            self._finger_ids = [self._gripper_id]
            self._ee_link_index = 5
            self._ee_position = self._actual_ee_position()
            self._set_gripper_pose(self._ee_position, open_gripper=True)
            self._step(10)
            return self.observe()

        if c.arm_model == "xarm6":
            self._gripper_id = p.loadURDF("xarm/xarm6_with_gripper.urdf", [0, 0, c.table_z], useFixedBase=True, physicsClientId=self.client)
            self._wrist_id = self._gripper_id
            self._arm_joint_ids = list(range(1, 7))
            self._finger_joint_ids = [8]
            self._finger_ids = [self._gripper_id]
            self._ee_link_index = 6
            for joint_id in self._arm_joint_ids:
                info = p.getJointInfo(self._gripper_id, joint_id, physicsClientId=self.client)
                self._arm_lower.append(float(info[8]))
                self._arm_upper.append(float(info[9]))
                self._arm_effort.append(float(info[10]))
                self._arm_velocity.append(float(info[11]))
            self._ee_position = self._actual_ee_position()
            self._set_gripper_pose(self._ee_position, open_gripper=True)
            self._step(10)
            return self.observe()

        wrist_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.065, 0.06, 0.025], physicsClientId=self.client)
        wrist_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.065, 0.06, 0.025], rgbaColor=[0.60, 0.68, 0.77, 1], physicsClientId=self.client)
        self._wrist_id = p.createMultiBody(0, wrist_shape, wrist_visual, self._ee_position, physicsClientId=self.client)
        self._finger_joint_ids: list[int] = []
        self._finger_ids: list[int] = []
        if c.gripper_model == "urdf":
            urdf = Path(__file__).resolve().parent.parent / "assets" / "gripper.urdf"
            self._gripper_id = p.loadURDF(str(urdf), self._ee_position, useFixedBase=True, physicsClientId=self.client)
            self._finger_joint_ids = [0, 1]
            self._finger_ids = [self._gripper_id]
        elif c.gripper_model == "procedural":
            finger_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.012, 0.05, 0.07], physicsClientId=self.client)
            finger_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.012, 0.05, 0.07], rgbaColor=[0.74, 0.81, 0.89, 1], physicsClientId=self.client)
            self._finger_ids = [
                p.createMultiBody(0, finger_shape, finger_visual, [-0.08, 0, self._ee_position[2] - 0.07], physicsClientId=self.client),
                p.createMultiBody(0, finger_shape, finger_visual, [0.08, 0, self._ee_position[2] - 0.07], physicsClientId=self.client),
            ]
            self._gripper_id = self._wrist_id
        else:
            raise ValueError(f"unknown gripper model: {c.gripper_model}")
        self._set_gripper_pose(self._ee_position, open_gripper=True)
        self._step(10)
        return self.observe()

    def _set_gripper_pose(self, position: list[float], *, open_gripper: bool) -> None:
        p = self.p
        if self.config.arm_model == "arm6dof":
            self._set_arm_pose(position, open_gripper=open_gripper)
            return
        if self.config.arm_model == "xarm6":
            self._set_xarm_pose(position, open_gripper=open_gripper)
            return
        self._ee_position = list(position)
        p.resetBasePositionAndOrientation(self._wrist_id, position, [0, 0, 0, 1], physicsClientId=self.client)
        offset = 0.08 if open_gripper else self.config.grasp_width / 2
        if self.config.gripper_model == "urdf":
            target = 0.0 if open_gripper else 0.022
            for joint_id, axis in zip(self._finger_joint_ids, [1.0, 1.0]):
                # Position control supplies the actuator model; resetting the
                # joint state makes the first MVP deterministic even with a
                # fixed base and a short action horizon.
                p.resetJointState(self._gripper_id, joint_id, target, physicsClientId=self.client)
                p.setJointMotorControl2(
                    self._gripper_id,
                    joint_id,
                    p.POSITION_CONTROL,
                    targetPosition=target,
                    force=max(20.0, self._gripper_force * 50.0),
                    maxVelocity=5.0,
                    physicsClientId=self.client,
                )
        else:
            for sign, finger_id in zip([-1, 1], self._finger_ids):
                p.resetBasePositionAndOrientation(finger_id, [position[0] + sign * offset, position[1], position[2] - 0.07], [0, 0, 0, 1], physicsClientId=self.client)

    def _actual_ee_position(self) -> list[float]:
        if self.config.arm_model in {"arm6dof", "xarm6"}:
            state = self.p.getLinkState(self._gripper_id, self._ee_link_index, computeForwardKinematics=True, physicsClientId=self.client)
            return [float(value) for value in state[4]]
        return list(self._ee_position)

    def _set_arm_pose(self, position: list[float], *, open_gripper: bool) -> None:
        p = self.p
        self._ee_position = list(position)
        solution = p.calculateInverseKinematics(
            self._gripper_id,
            self._ee_link_index,
            position,
            targetOrientation=p.getQuaternionFromEuler([0, 0, 0]),
            lowerLimits=[-3.14, -2.2, -2.5, -3.14, -2.5, -3.14],
            upperLimits=[3.14, 2.2, 2.5, 3.14, 2.5, 3.14],
            jointRanges=[6.28, 4.4, 5.0, 6.28, 5.0, 6.28],
            restPoses=[0.0, 0.3, -0.8, 0.0, 0.5, 0.0],
            maxNumIterations=100,
            residualThreshold=1e-4,
            physicsClientId=self.client,
        )
        for joint_id, target in zip(self._arm_joint_ids, solution[:6]):
            # Seed the commanded pose so the short action horizon is
            # deterministic; the position controller then holds the joints.
            p.resetJointState(self._gripper_id, joint_id, target, physicsClientId=self.client)
            p.setJointMotorControl2(self._gripper_id, joint_id, p.POSITION_CONTROL, targetPosition=target, force=80, maxVelocity=3, physicsClientId=self.client)
        finger_target = 0.0 if open_gripper else 0.022
        self._gripper_open = open_gripper
        for joint_id in self._finger_joint_ids:
            p.resetJointState(self._gripper_id, joint_id, finger_target, physicsClientId=self.client)
            p.setJointMotorControl2(self._gripper_id, joint_id, p.POSITION_CONTROL, targetPosition=finger_target, force=20, maxVelocity=5, physicsClientId=self.client)

    def _set_xarm_pose(self, position: list[float], *, open_gripper: bool) -> None:
        p = self.p
        self._ee_position = list(position)
        solution = p.calculateInverseKinematics(
            self._gripper_id,
            self._ee_link_index,
            position,
            targetOrientation=p.getQuaternionFromEuler([3.14159265, 0, 0]),
            lowerLimits=self._arm_lower,
            upperLimits=self._arm_upper,
            jointRanges=[upper - lower for lower, upper in zip(self._arm_lower, self._arm_upper)],
            restPoses=[0.0] * len(self._arm_joint_ids),
            maxNumIterations=200,
            residualThreshold=1e-5,
            physicsClientId=self.client,
        )
        for index, (joint_id, target) in enumerate(zip(self._arm_joint_ids, solution[:len(self._arm_joint_ids)])):
            target = min(self._arm_upper[index], max(self._arm_lower[index], target))
            p.resetJointState(self._gripper_id, joint_id, target, physicsClientId=self.client)
            p.setJointMotorControl2(
                self._gripper_id,
                joint_id,
                p.POSITION_CONTROL,
                targetPosition=target,
                force=self._arm_effort[index],
                maxVelocity=self._arm_velocity[index],
                physicsClientId=self.client,
            )
        target = 0.0 if open_gripper else 0.85
        self._gripper_open = open_gripper
        p.resetJointState(self._gripper_id, self._finger_joint_ids[0], target, physicsClientId=self.client)
        p.setJointMotorControl2(self._gripper_id, self._finger_joint_ids[0], p.POSITION_CONTROL, targetPosition=target, force=50, maxVelocity=2, physicsClientId=self.client)

    def _step(self, count: int | None = None) -> None:
        for _ in range(count or self.config.steps_per_action):
            self.p.stepSimulation(physicsClientId=self.client)
            self._time += self.config.time_step_s
            if self.config.frame_callback is not None:
                self.config.frame_callback(self.observe())
            if self.config.realtime:
                time.sleep(self.config.time_step_s)

    def _cube_position(self) -> list[float]:
        position, _ = self.p.getBasePositionAndOrientation(self._cube_id, physicsClientId=self.client)
        return [float(value) for value in position]

    def _contact_detected(self) -> bool:
        return bool(self.p.getClosestPoints(self._cube_id, self._gripper_id, distance=0.01, physicsClientId=self.client))

    def observe(self) -> SceneState:
        position = self._cube_position()
        if self.config.arm_model in {"arm6dof", "xarm6"}:
            self._ee_position = self._actual_ee_position()
        confidence = 0.35 if not self._object_visible else 0.95
        lifted = position[2] > self._object_start[2] + 0.06
        self._lifted = lifted
        return SceneState(
            timestamp=self._time,
            phase=self._phase,
            object=ObjectState("cube", position, self._object_visible, self._grasped, lifted, confidence),
            robot=RobotState(self._gripper_open, self._gripper_force, list(self._ee_position)),
            events=list(dict.fromkeys(self._events + self._anomalies)),
        )

    def execute(self, action: str) -> SceneState:
        if self._stopped and action != "stop":
            raise RuntimeError("environment is stopped; reset before executing more actions")
        self._events = []
        if action == "approach_object":
            self._phase = "approach"
            self._set_gripper_pose([self._object_start[0], self._object_start[1], self.config.table_z + 0.17], open_gripper=True)
            if self.config.arm_model == "arm6dof":
                self._step()
            self._events.append("object_approached")
        elif action == "close_gripper":
            self._phase = "grasp"
            self._gripper_open = False
            self._gripper_force = 0.4 if self.failure_mode == FailureMode.LOW_GRIP_FORCE else 1.0
            self._set_gripper_pose(self._ee_position, open_gripper=False)
            position_before = self._cube_position()
            contact_before_step = self._contact_detected()
            self._step()
            position_after = self._cube_position()
            displacement = sum((a - b) ** 2 for a, b in zip(position_after, position_before)) ** 0.5
            if displacement > 0.01:
                if "object_displaced_before_grasp" not in self._anomalies:
                    self._anomalies.append("object_displaced_before_grasp")
                self._events.append("object_displaced_before_grasp")
            self._grasped = self.failure_mode not in {FailureMode.MISALIGNED_GRASP, FailureMode.LOW_GRIP_FORCE}
            if self._grasped and (contact_before_step or self._contact_detected()):
                parent_link = self._ee_link_index if self.config.arm_model in {"arm6dof", "xarm6"} else -1
                self._constraint_id = self.p.createConstraint(self._wrist_id, parent_link, self._cube_id, -1, self.p.JOINT_FIXED, [0, 0, 0], [0, 0, -0.12], [0, 0, 0], physicsClientId=self.client)
                self._events.extend(["gripper_closed", "gripper_contact", "grasp_constraint_created"])
            else:
                self._grasped = False
                self._events.extend(["gripper_closed", "gripper_contact"])
        elif action == "lift_object":
            self._phase = "lift"
            if self._grasped:
                self._set_gripper_pose([self._ee_position[0], self._ee_position[1], self._ee_position[2] + 0.15], open_gripper=False)
                if self._constraint_id is not None and self.config.arm_model not in {"arm6dof", "xarm6"}:
                    self.p.resetBasePositionAndOrientation(
                        self._cube_id,
                        [self._ee_position[0], self._ee_position[1], self._ee_position[2] - 0.12],
                        [0, 0, 0, 1],
                        physicsClientId=self.client,
                    )
                self._step()
                self._phase = "transport"
                if self.observe().object.lifted:
                    self._events.append("object_lift_detected")
            else:
                self._step()
        elif action == "move_to_target":
            if self._lifted and self._grasped:
                self._phase = "transport"
                place_z = self.config.table_z + 0.17 if self.config.arm_model in {"arm6dof", "xarm6"} else self._ee_position[2]
                self._set_gripper_pose([0.5, self._ee_position[1], place_z], open_gripper=False)
                if self._constraint_id is not None and self.config.arm_model not in {"arm6dof", "xarm6"}:
                    self.p.resetBasePositionAndOrientation(
                        self._cube_id,
                        [self._ee_position[0], self._ee_position[1], self._ee_position[2] - 0.12],
                        [0, 0, 0, 1],
                        physicsClientId=self.client,
                    )
                self._step()
                self._events.append("object_at_target")
            else:
                self._phase = "failed"
        elif action == "release_object":
            self._gripper_open = True
            self._gripper_force = 0.0
            if self._constraint_id is not None:
                self.p.removeConstraint(self._constraint_id, physicsClientId=self.client)
                self._constraint_id = None
            self._grasped = False
            self._set_gripper_pose(self._ee_position, open_gripper=True)
            self._step(self.config.steps_per_action * 2)
            self._phase = "finished" if self._cube_position()[2] <= self._object_start[2] + 0.06 else "failed"
            self._events.append("object_released")
        elif action == "refresh_object_pose":
            self._object_visible = True
            self._events.append("object_pose_refreshed")
        elif action == "retry_grasp":
            self.failure_mode = FailureMode.NONE
            self._phase = "grasp"
            self._grasped = False
            self._lifted = False
            current = self._cube_position()
            self._object_start = [current[0], current[1], self._object_start[2]]
            self._set_gripper_pose([current[0], current[1], self.config.table_z + 0.17], open_gripper=True)
            if self.config.arm_model in {"arm6dof", "xarm6"}:
                self._step()
            self._events.append("grasp_retry_requested")
        elif action == "stop":
            self._stopped = True
            self._events.append("safety_stop")
        else:
            raise ValueError(f"unknown action: {action}")
        return self.observe()

    def capture_rgb(self, width: int = 640, height: int = 480) -> Any:
        p = self.p
        view = p.computeViewMatrixFromYawPitchRoll([0.2, 0, 0.78], 1.3, 45, -30, 0, 2)
        projection = p.computeProjectionMatrixFOV(55, width / height, 0.02, 5)
        _, _, rgba, _, _ = p.getCameraImage(width, height, view, projection, renderer=p.ER_TINY_RENDERER, physicsClientId=self.client)
        return rgba[:, :, :3]

    @property
    def stopped(self) -> bool:
        return self._stopped

    def close(self) -> None:
        if not self._closed:
            self.p.disconnect(self.client)
            self._closed = True
