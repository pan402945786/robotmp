from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import ObjectState, RobotState, SceneState


class FailureMode(str, Enum):
    NONE = "none"
    MISALIGNED_GRASP = "misaligned_grasp"
    LOW_GRIP_FORCE = "low_grip_force"
    OCCLUDED = "occluded"


@dataclass
class EpisodeResult:
    success: bool
    false_success: bool
    recovered: bool
    failure_mode: str


class PickPlaceEnv:
    """Small deterministic environment used to exercise the MVP loop."""

    def __init__(self, failure_mode: FailureMode = FailureMode.NONE):
        self.failure_mode = FailureMode(failure_mode)
        self.reset()

    def reset(self) -> SceneState:
        self._time = 0.0
        self._phase = "observe"
        self._object_position = [0.0, 0.0, 0.75]
        self._object_visible = self.failure_mode != FailureMode.OCCLUDED
        self._grasped = False
        self._lifted = False
        self._gripper_open = True
        self._gripper_force = 0.0
        self._events: list[str] = []
        self._stopped = False
        return self.observe()

    def observe(self) -> SceneState:
        confidence = 0.35 if not self._object_visible else 0.95
        return SceneState(
            timestamp=self._time,
            phase=self._phase,
            object=ObjectState(
                object_id="cube",
                position_m=list(self._object_position),
                visible=self._object_visible,
                grasped=self._grasped,
                lifted=self._lifted,
                confidence=confidence,
            ),
            robot=RobotState(
                gripper_open=self._gripper_open,
                gripper_force=self._gripper_force,
                end_effector_position_m=[0.0, 0.0, 0.8 if self._lifted else 0.75],
            ),
            events=list(self._events),
        )

    def execute(self, action: str) -> SceneState:
        if self._stopped and action != "stop":
            raise RuntimeError("environment is stopped; reset before executing more actions")
        self._time += 0.1
        self._events = []

        if action == "approach_object":
            self._phase = "approach"
            self._events.append("object_approached")
        elif action == "close_gripper":
            self._phase = "grasp"
            self._gripper_open = False
            self._gripper_force = 0.4 if self.failure_mode == FailureMode.LOW_GRIP_FORCE else 1.0
            self._grasped = self.failure_mode not in {
                FailureMode.MISALIGNED_GRASP,
                FailureMode.LOW_GRIP_FORCE,
            }
            self._events.extend(["gripper_closed", "gripper_contact"])
        elif action == "lift_object":
            self._phase = "lift"
            if self._grasped:
                self._lifted = True
                self._phase = "transport"
                self._object_position[2] += 0.15
                self._events.append("object_lift_detected")
            else:
                self._lifted = False
        elif action == "move_to_target":
            if self._lifted:
                self._phase = "transport"
                self._object_position[0] = 0.5
                self._events.append("object_at_target")
            else:
                self._phase = "failed"
        elif action == "release_object":
            self._gripper_open = True
            self._gripper_force = 0.0
            if self._lifted:
                self._phase = "finished"
                self._events.append("object_released")
            else:
                self._phase = "failed"
        elif action == "refresh_object_pose":
            self._object_visible = True
            self._events.append("object_pose_refreshed")
        elif action == "retry_grasp":
            self.failure_mode = FailureMode.NONE
            self._phase = "grasp"
            self._grasped = False
            self._lifted = False
            self._events.append("grasp_retry_requested")
        elif action == "stop":
            self._stopped = True
            self._events.append("safety_stop")
        else:
            raise ValueError(f"unknown action: {action}")

        return self.observe()

    @property
    def stopped(self) -> bool:
        return self._stopped
