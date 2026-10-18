from __future__ import annotations

from .models import ComparisonResult, Prediction, SceneState


def compare_prediction(prediction: Prediction, observed: SceneState) -> ComparisonResult:
    errors: list[str] = []

    if prediction.expected_object_lifted and not observed.object.lifted:
        errors.append("expected_lift_but_not_detected")

    for event in prediction.expected_events:
        if event not in observed.events:
            errors.append(f"missing_event:{event}")

    if "object_displaced_before_grasp" in observed.events and not observed.object.lifted:
        errors.append("object_displaced_before_grasp")

    if observed.object.confidence < 0.5:
        return ComparisonResult(status="uncertain", errors=errors, severity="low")
    if errors:
        return ComparisonResult(status="deviation", errors=errors, severity="medium")
    return ComparisonResult(status="match", errors=[], severity="none")
