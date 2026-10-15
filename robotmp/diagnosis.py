from __future__ import annotations

from .models import ComparisonResult, Prediction, SceneState, Skill


class RuleBasedDiagnoser:
    """Deterministic local substitute for an LLM during MVP development."""

    def generate(
        self,
        prediction: Prediction,
        observation: SceneState,
        comparison: ComparisonResult,
        skill_context: list[Skill],
    ) -> Skill:
        if "expected_lift_but_not_detected" not in comparison.errors:
            raise ValueError("no grasp-without-lift diagnosis applies")
        return Skill(
            skill_id="grasp_without_lift_v1",
            name="grasp_without_lift",
            status="candidate",
            version=1,
            task="pick_and_place",
            object_types=[observation.object.object_id],
            trigger_conditions=[
                "gripper_closed == true",
                "lift_window_elapsed == true",
                "object_lifted == false",
            ],
            facts=[
                "gripper_closed_does_not_imply_grasp_success",
                "object_lift_was_not_detected",
            ],
            hypotheses=[
                "grasp_point_may_be_misaligned",
                "insufficient_grip_force",
            ],
            prediction_correction=[
                "do_not_enter_transport_phase",
                "require_lift_evidence_before_transport",
            ],
            recovery=[
                "stop_transport_motion",
                "refresh_object_pose",
                "retry_grasp_if_safe",
            ],
        )
