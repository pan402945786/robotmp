"""PyBullet backend for the robotmp pick-and-place loop."""
from __future__ import annotations

from dataclasses import dataclass
import math
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
    xarm_steps_per_action: int = 48
    time_step_s: float = 1.0 / 240.0
    table_z: float = 0.70
    cube_half_extent: float = 0.05
    grasp_width: float = 0.115
    realtime: bool = False
    gripper_model: str = "urdf"
    arm_model: str = "none"
    arm_base_x: float = 0.10
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
            self._gripper_id = p.loadURDF("xarm/xarm6_with_gripper.urdf", [c.arm_base_x, 0, c.table_z], useFixedBase=True, physicsClientId=self.client)
            # The high-level MVP owns grasp success; disabling uncontrolled
            # robot-cube contact keeps the visual grasp stable while the
            # explicit fixed constraint models the acquired object.
            for link_index in [-1, *range(p.getNumJoints(self._gripper_id, physicsClientId=self.client))]:
                p.setCollisionFilterPair(self._gripper_id, self._cube_id, link_index, -1, 0, physicsClientId=self.client)
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
        p.setJointMotorControl2(self._gripper_id, self._finger_joint_ids[0], p.POSITION_CONTROL, targetPosition=target, force=50, maxVelocity=2, physicsClientId=self.client)

    def _step(self, count: int | None = None) -> None:
        default_steps = self.config.xarm_steps_per_action if self.config.arm_model == "xarm6" else self.config.steps_per_action
        for _ in range(count or default_steps):
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

    def _create_grasp_constraint(self) -> None:
        """Attach the cube using the measured contact pose, not a fixed offset."""
        p = self.p
        cube_position, cube_orientation = p.getBasePositionAndOrientation(self._cube_id, physicsClientId=self.client)
        if self.config.arm_model in {"arm6dof", "xarm6"}:
            link_state = p.getLinkState(self._gripper_id, self._ee_link_index, computeForwardKinematics=True, physicsClientId=self.client)
            parent_position, parent_orientation = link_state[4], link_state[5]
            inverse_position, inverse_orientation = p.invertTransform(parent_position, parent_orientation)
            parent_frame_position, parent_frame_orientation = p.multiplyTransforms(
                inverse_position,
                inverse_orientation,
                cube_position,
                cube_orientation,
            )
            self._constraint_id = p.createConstraint(
                self._gripper_id,
                self._ee_link_index,
                self._cube_id,
                -1,
                p.JOINT_FIXED,
                [0, 0, 0],
                parent_frame_position,
                [0, 0, 0],
                parent_frame_orientation,
                [0, 0, 0, 1],
                physicsClientId=self.client,
            )
            return
        self._constraint_id = p.createConstraint(
            self._wrist_id,
            -1,
            self._cube_id,
            -1,
            p.JOINT_FIXED,
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            physicsClientId=self.client,
        )

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
            if self.config.arm_model in {"arm6dof", "xarm6"}:
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
            cube_position = self._cube_position()
            ee_position = self._actual_ee_position() if self.config.arm_model in {"arm6dof", "xarm6"} else self._ee_position
            grasp_distance = sum((a - b) ** 2 for a, b in zip(cube_position, ee_position)) ** 0.5
            contact_or_aligned = contact_before_step or self._contact_detected() or (
                self.config.arm_model == "xarm6" and grasp_distance <= 0.16
            )
            if self._grasped and contact_or_aligned:
                self._create_grasp_constraint()
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

    def move_held_object(self, target: list[float], *, steps: int = 48) -> SceneState:
        """Track an object-center waypoint using the measured grasp offset and IK."""
        if self._stopped:
            raise RuntimeError("environment is stopped; reset before executing more actions")
        if self.config.arm_model != "xarm6":
            raise ValueError("held-object trajectories require the xarm6 position controller")
        if len(target) != 3 or not all(math.isfinite(value) for value in target):
            raise ValueError("target must contain three finite coordinates")
        if not isinstance(steps, int) or steps < 1:
            raise ValueError("steps must be a positive integer")
        state = self.observe()
        if not state.object.grasped or self._constraint_id is None or state.robot.gripper_open:
            raise RuntimeError("held-object motion requires a closed gripper and an active grasp")
        if not state.object.lifted or state.object.confidence < 0.7:
            raise RuntimeError("held-object motion requires visible lift evidence")
        if target[2] < self._object_start[2] + 0.07:
            raise ValueError("held-object waypoint is too close to the table")
        self._events = []
        self._phase = "trace"
        ee_target = [ee + goal - actual for ee, goal, actual in zip(
            state.robot.end_effector_position_m, target, state.object.position_m
        )]
        self._set_gripper_pose(ee_target, open_gripper=False)
        self._step(steps)
        self._events.append("held_object_waypoint_reached")
        return self.observe()

    def settle_object(self, *, steps: int = 240) -> SceneState:
        """Observe a released object for one simulated second without resetting it."""
        if self._stopped or self._grasped or self._constraint_id is not None:
            raise RuntimeError("settling requires a released object and a running environment")
        self._events = []
        self._step(steps)
        self._events.append("placement_settled")
        return self.observe()

    @property
    def stopped(self) -> bool:
        return self._stopped

    def close(self) -> None:
        if not self._closed:
            self.p.disconnect(self.client)
            self._closed = True
