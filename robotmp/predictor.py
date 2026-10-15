from __future__ import annotations

from itertools import count

from .models import Prediction, SceneState, Skill

_ids = count(1)


def make_prediction(state: SceneState, skills: list[Skill]) -> Prediction:
    applied = [skill.skill_id for skill in skills]
    guarded = any(skill.name == "grasp_without_lift" for skill in skills)
    return Prediction(
        prediction_id=f"pred-{next(_ids)}",
        action="lift_object",
        expected_phase="lift" if guarded else "transport",
        expected_events=["object_lift_detected"],
        expected_object_lifted=True,
        position_tolerance_m=0.03,
        confidence=0.75 if not guarded else 0.9,
        applied_skill_ids=applied,
        requires_lift_evidence=True,
    )
