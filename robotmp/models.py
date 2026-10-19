from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Phase = Literal[
    "observe",
    "approach",
    "grasp",
    "lift",
    "transport",
    "trace",
    "place",
    "finished",
    "failed",
]
ComparisonStatus = Literal["match", "uncertain", "deviation"]
SkillStatus = Literal["candidate", "testing", "verified", "disabled"]


@dataclass
class ObjectState:
    object_id: str
    position_m: list[float]
    visible: bool
    grasped: bool
    lifted: bool
    confidence: float


@dataclass
class RobotState:
    gripper_open: bool
    gripper_force: float
    end_effector_position_m: list[float]


@dataclass
class SceneState:
    timestamp: float
    phase: Phase
    object: ObjectState
    robot: RobotState
    events: list[str] = field(default_factory=list)


@dataclass
class Prediction:
    prediction_id: str
    action: str
    expected_phase: Phase
    expected_events: list[str]
    expected_object_lifted: bool
    position_tolerance_m: float
    confidence: float
    applied_skill_ids: list[str] = field(default_factory=list)
    requires_lift_evidence: bool = True


@dataclass
class ComparisonResult:
    status: ComparisonStatus
    errors: list[str] = field(default_factory=list)
    severity: Literal["none", "low", "medium", "high"] = "none"


@dataclass
class Skill:
    skill_id: str
    name: str
    status: SkillStatus
    version: int
    task: str
    object_types: list[str]
    trigger_conditions: list[str]
    facts: list[str]
    hypotheses: list[str]
    prediction_correction: list[str]
    recovery: list[str]
    validation_trials: int = 0
    false_success_rate: float | None = None
    recovery_success_rate: float | None = None
    prerequisite_skill_ids: list[str] = field(default_factory=list)
    parameters: dict[str, float | int | str] = field(default_factory=dict)
    validation_success_rate: float | None = None
    validation_metrics: dict[str, float | int | bool] = field(default_factory=dict)
