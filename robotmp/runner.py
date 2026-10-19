from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from .diagnosis import LLMUnavailable, RuleBasedDiagnoser
from .environment import FailureMode, PickPlaceEnv
from .models import Skill
from .monitor import compare_prediction
from .predictor import make_prediction
from .skills import SkillStore


@dataclass
class RunResult:
    mode: str
    failure_mode: str
    status: str
    false_success: bool
    recovered: bool
    applied_skill_ids: list[str]


def run_episode(
    mode: str,
    failure_mode: FailureMode,
    skill_store: SkillStore,
    diagnoser: object | None = None,
    observer: Callable[[dict], None] | None = None,
    env_factory: Callable[[FailureMode], object] | None = None,
    close_env: bool = True,
    after_lift: Callable[[object], None] | None = None,
) -> RunResult:
    """Run the existing policy, optionally emitting detached telemetry snapshots."""
    env = (env_factory or PickPlaceEnv)(failure_mode)
    diagnoser = diagnoser or RuleBasedDiagnoser()
    state = env.reset()
    prediction = None
    comparison = None

    def emit(kind: str, **details) -> None:
        if observer is not None:
            observer({
                "kind": kind,
                "state": asdict(env.observe()),
                "prediction": asdict(prediction) if prediction else None,
                "comparison": asdict(comparison) if comparison else None,
                **details,
            })

    def execute(action: str) -> None:
        if action == "move_to_target" and after_lift is not None:
            after_lift(env)
        env.execute(action)
        emit("action", action=action)

    def finish(result: RunResult) -> RunResult:
        emit("result", result=asdict(result))
        close = getattr(env, "close", None)
        if close_env and close is not None:
            close()
        return result

    emit("reset")
    skills: list[Skill] = []
    if mode == "skills":
        skills = skill_store.retrieve("pick_and_place", state.object.object_id, state.phase)
        emit("retrieve", skills=[asdict(skill) for skill in skills])

    execute("approach_object")
    execute("close_gripper")
    prediction = make_prediction(env.observe(), skills)
    emit("prediction")
    execute("lift_object")
    observed = env.observe()

    if mode == "baseline":
        false_success = not observed.object.lifted
        if observed.object.lifted:
            execute("move_to_target")
            execute("release_object")
        return finish(RunResult(mode, failure_mode.value, "success" if not false_success else "false_success", false_success, False, []))

    comparison = compare_prediction(prediction, observed)
    emit("comparison")
    if comparison.status == "match":
        execute("move_to_target")
        execute("release_object")
        return finish(RunResult(mode, failure_mode.value, "success", False, False, prediction.applied_skill_ids))

    if comparison.status == "uncertain":
        execute("stop")
        return finish(RunResult(mode, failure_mode.value, "uncertain", False, False, prediction.applied_skill_ids))

    try:
        candidate = diagnoser.generate(prediction, observed, comparison, skills)
        emit("diagnosis", skill=asdict(candidate), source=type(diagnoser).__name__)
    except LLMUnavailable as exc:
        fallback = RuleBasedDiagnoser()
        candidate = fallback.generate(prediction, observed, comparison, skills)
        emit("diagnosis_fallback", error=str(exc), skill=asdict(candidate), source=type(fallback).__name__)
    if mode == "skills":
        skill_store.save_candidate(candidate)
        emit("candidate", skill=asdict(candidate))
    execute("refresh_object_pose")
    execute("retry_grasp")
    execute("close_gripper")
    execute("lift_object")
    recovered = env.observe().object.lifted
    if recovered:
        execute("move_to_target")
        execute("release_object")
    else:
        execute("stop")
    return finish(RunResult(
        mode,
        failure_mode.value,
        "recovered" if recovered else "failed",
        False,
        recovered,
        prediction.applied_skill_ids,
    ))


def validate_skill(
    skill_store: SkillStore,
    failure_mode: FailureMode = FailureMode.LOW_GRIP_FORCE,
    trials: int = 20,
    env_factory: Callable[[FailureMode], object] | None = None,
    diagnoser: object | None = None,
) -> Skill:
    false_successes = 0
    recoveries = 0
    for _ in range(trials):
        result = run_episode("feedback", failure_mode, skill_store, diagnoser=diagnoser, env_factory=env_factory)
        false_successes += int(result.false_success)
        recoveries += int(result.recovered)
    return skill_store.promote_verified(
        "grasp_without_lift_v1",
        trials=trials,
        false_success_rate=false_successes / trials,
        recovery_success_rate=recoveries / trials,
    )


def default_store(path: str | Path = "artifacts/skills.json") -> SkillStore:
    return SkillStore(path)


def summarize_results(results: list[RunResult]) -> dict[str, float | int]:
    total = len(results)
    if total == 0:
        return {
            "trials": 0,
            "success_rate": 0.0,
            "false_success_rate": 0.0,
            "recovery_rate": 0.0,
            "skill_application_rate": 0.0,
        }
    return {
        "trials": total,
        "success_rate": sum(result.status in {"success", "recovered"} for result in results) / total,
        "false_success_rate": sum(result.false_success for result in results) / total,
        "recovery_rate": sum(result.recovered for result in results) / total,
        "skill_application_rate": sum(bool(result.applied_skill_ids) for result in results) / total,
    }


def run_ab_experiment(
    failure_mode: FailureMode,
    trials: int,
    root: str | Path = "artifacts/experiment",
    env_factory: Callable[[FailureMode], object] | None = None,
    diagnoser: object | None = None,
) -> dict[str, dict[str, float | int]]:
    root = Path(root)
    summaries: dict[str, dict[str, float | int]] = {}

    for mode in ("baseline", "feedback"):
        store = default_store(root / f"{mode}.json")
        results = [run_episode(mode, failure_mode, store, diagnoser=diagnoser, env_factory=env_factory) for _ in range(trials)]
        summaries[mode] = summarize_results(results)

    skill_store = default_store(root / "skills.json")
    run_episode("skills", failure_mode, skill_store, diagnoser=diagnoser, env_factory=env_factory)
    validate_skill(skill_store, failure_mode=failure_mode, trials=max(5, min(trials, 20)), env_factory=env_factory, diagnoser=diagnoser)
    results = [run_episode("skills", failure_mode, skill_store, diagnoser=diagnoser, env_factory=env_factory) for _ in range(trials)]
    summaries["skills"] = summarize_results(results)
    return summaries
