from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .diagnosis import RuleBasedDiagnoser
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
    diagnoser: RuleBasedDiagnoser | None = None,
) -> RunResult:
    env = PickPlaceEnv(failure_mode)
    diagnoser = diagnoser or RuleBasedDiagnoser()
    state = env.reset()
    skills: list[Skill] = []
    if mode == "skills":
        skills = skill_store.retrieve("pick_and_place", state.object.object_id, state.phase)

    env.execute("approach_object")
    env.execute("close_gripper")
    prediction = make_prediction(env.observe(), skills)
    env.execute("lift_object")
    observed = env.observe()

    if mode == "baseline":
        false_success = not observed.object.lifted
        if observed.object.lifted:
            env.execute("move_to_target")
            env.execute("release_object")
        return RunResult(mode, failure_mode.value, "success" if not false_success else "false_success", false_success, False, [])

    comparison = compare_prediction(prediction, observed)
    if comparison.status == "match":
        env.execute("move_to_target")
        env.execute("release_object")
        return RunResult(mode, failure_mode.value, "success", False, False, prediction.applied_skill_ids)

    if comparison.status == "uncertain":
        env.execute("stop")
        return RunResult(mode, failure_mode.value, "uncertain", False, False, prediction.applied_skill_ids)

    candidate = diagnoser.generate(prediction, observed, comparison, skills)
    if mode == "skills":
        skill_store.save_candidate(candidate)
    env.execute("refresh_object_pose")
    env.execute("retry_grasp")
    env.execute("close_gripper")
    env.execute("lift_object")
    recovered = env.observe().object.lifted
    if recovered:
        env.execute("move_to_target")
        env.execute("release_object")
    else:
        env.execute("stop")
    return RunResult(
        mode,
        failure_mode.value,
        "recovered" if recovered else "failed",
        False,
        recovered,
        prediction.applied_skill_ids,
    )


def validate_skill(
    skill_store: SkillStore,
    failure_mode: FailureMode = FailureMode.LOW_GRIP_FORCE,
    trials: int = 20,
) -> Skill:
    false_successes = 0
    recoveries = 0
    for _ in range(trials):
        result = run_episode("feedback", failure_mode, skill_store)
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
) -> dict[str, dict[str, float | int]]:
    root = Path(root)
    summaries: dict[str, dict[str, float | int]] = {}

    for mode in ("baseline", "feedback"):
        store = default_store(root / f"{mode}.json")
        results = [run_episode(mode, failure_mode, store) for _ in range(trials)]
        summaries[mode] = summarize_results(results)

    skill_store = default_store(root / "skills.json")
    run_episode("skills", failure_mode, skill_store)
    validate_skill(skill_store, failure_mode=failure_mode, trials=max(5, min(trials, 20)))
    results = [run_episode("skills", failure_mode, skill_store) for _ in range(trials)]
    summaries["skills"] = summarize_results(results)
    return summaries

