"""Continue throw/catch learning with a two-metre release-height target."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, replace
import hashlib
import json
import math
from pathlib import Path

from .diagnosis import LLMConfig, LLMUnavailable, OpenAICompatibleDiagnoser
from .figure_eight import Journal, PREREQUISITE
from .models import Skill
from .runner import default_store
from .sim_environment import SimConfig
from .throw_catch import ThrowEnv

TARGET_RISE_M = 2.0
REQUIRED_VZ = math.sqrt(2 * 9.81 * TARGET_RISE_M)
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = Path("docs/throw_catch_2m_20261019")
OLD_SKILL = Path("assets/skills/throw_catch_candidate.json")
NEW_SKILL = Path("assets/skills/throw_2m_catch_ground_candidate.json")


class Audit2(Journal):
    def model_event(self, record):
        super().model_event(record)


def validate_parameters(raw):
    required = {"target_x_m": (0.20, 0.60), "target_z_m": (1.05, 1.90), "release_after_steps": (12, 120)}
    if not isinstance(raw, dict) or set(raw) != set(required):
        raise ValueError(f"parameters must have exactly {list(required)}")
    for key, (low, high) in required.items():
        value = raw[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"invalid {key}")
    if not isinstance(raw["release_after_steps"], int):
        raise ValueError("release_after_steps must be an integer")
    return dict(raw)


def run_gate_trial(index, parameters, audit):
    csv_path = audit.output / f"gate_{index:02d}_physics.csv"
    report_path = audit.output / f"gate_{index:02d}.json"
    env = ThrowEnv(config=SimConfig(arm_model="xarm6"))
    rows, events = [], []

    def emit(kind, **extra):
        state = env.observe()
        linear, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        rows.append({"t_s": state.timestamp, "phase": state.phase, "x_m": state.object.position_m[0],
                     "y_m": state.object.position_m[1], "z_m": state.object.position_m[2],
                     "vz_m_s": linear[2], "constraint": env._constraint_id is not None,
                     "grasped": state.object.grasped, "lifted": state.object.lifted})
        event = {"trial": index, "kind": kind, "state": asdict(state), **extra}
        events.append(event)
        audit.event(event)

    result = {"trial": index, "target_rise_m": TARGET_RISE_M, "required_vz_m_s": REQUIRED_VZ,
              "parameters": parameters, "release_permitted": False, "released": False}
    try:
        emit("reset")
        for action in ("approach_object", "close_gripper", "lift_object"):
            env.execute(action)
            emit("action", action=action)
        start = env.observe()
        if not start.object.lifted:
            raise RuntimeError("lift evidence missing")
        target = [parameters["target_x_m"], start.object.position_m[1], parameters["target_z_m"]]
        ee_target = [ee + goal - actual for ee, goal, actual in zip(start.robot.end_effector_position_m, target, start.object.position_m)]
        env._phase = "trace"
        env._set_gripper_pose(ee_target, open_gripper=False)
        max_vz = float("-inf")
        for step in range(parameters["release_after_steps"]):
            env._step(1)
            linear, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            max_vz = max(max_vz, linear[2])
            emit("trace_step", index=step + 1, vz_m_s=linear[2])
        gate = max_vz >= REQUIRED_VZ
        if gate:
            env.release_in_motion()
            emit("release_gate_passed", measured_max_vz_m_s=max_vz)
            result["release_permitted"] = True
            result["released"] = True
        else:
            env.execute("stop")
            emit("release_gate_blocked", measured_max_vz_m_s=max_vz,
                 reason="measured velocity cannot support a 2m rise")
        result.update({"max_measured_vz_m_s": max_vz, "safety_stop": env.stopped,
                       "constraint_retained": env._constraint_id is not None,
                       "lifted": env.observe().object.lifted, "events": events})
    except Exception as exc:
        result.update({"error": f"{type(exc).__name__}: {exc}", "events": events})
    finally:
        env.close()
    audit.append(csv_path, "") if False else None
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["t_s", "phase", "x_m", "y_m", "z_m", "vz_m_s", "constraint", "grasped", "lifted"])
        writer.writeheader()
        # Events carry states, so write the compact trace extracted from them.
        for event in events:
            state = event.get("state", {})
            obj = state.get("object", {})
            writer.writerow({"t_s": state.get("timestamp", 0), "phase": state.get("phase", ""),
                             "x_m": obj.get("position_m", [0, 0, 0])[0], "y_m": obj.get("position_m", [0, 0, 0])[1],
                             "z_m": obj.get("position_m", [0, 0, 0])[2], "vz_m_s": event.get("vz_m_s", ""),
                             "constraint": event.get("state", {}).get("object", {}).get("grasped", False),
                             "grasped": obj.get("grasped", False), "lifted": obj.get("lifted", False)})
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def propose(client, old_skill, previous, probe):
    instructions = (
        "You propose a high-level Skill experiment in local PyBullet xArm6 simulation. Return JSON only in Chinese. "
        "The target is changed from 10m to a TWO-METRE rise above the measured release point. This requires "
        f"vertical release speed >= {REQUIRED_VZ:.6f} m/s under gravity 9.81. Reuse grasp_without_lift_v1. "
        "Do not output code, joint commands, force injection, velocity injection, position reset, or gravity changes. "
        "Choose only target_x_m [0.20,0.60], target_z_m [1.05,1.90], release_after_steps integer [12,120]. "
        "A proposal may be tried only when measured lift evidence exists. Release must be blocked when measured "
        f"upward speed is below {REQUIRED_VZ:.6f} m/s. Return decision ('try' or 'stop'), prerequisite_skill_ids, "
        "parameters, observed_facts, hypotheses, rationale, next_requirements. Do not claim success without measured "
        "world height >=2m, rise >=2m, gated catch, and stable ground placement."
    )
    return client.request_json(instructions, {"goal": "抓起→抛高至少2米→接住→平稳放地",
        "target_rise_m": TARGET_RISE_M, "required_vz_m_s": REQUIRED_VZ,
        "existing_skill": asdict(old_skill), "previous_proposal": previous, "probe_results": probe})


def main():
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    OUTPUT = args.output
    OUTPUT.mkdir(parents=True, exist_ok=True)
    old = json.loads(OLD_SKILL.read_text(encoding="utf-8"))[0]
    source_hash = hashlib.sha256(OLD_SKILL.read_bytes()).hexdigest()
    journal = Audit2(OUTPUT, Path("docs/THROW_CATCH_LEARNING.md"), Path("docs/THROW_CATCH_LLM_CALLS.md"))
    journal.note(f"目标改为释放后相对上升 {TARGET_RISE_M} m；要求竖直释放速度 {REQUIRED_VZ:.6f} m/s。")
    probe = [{"target_x_m": 0.35, "target_z_m": 1.10, "release_after_steps": 72, "observed_max_vz_m_s": 2.027},
             {"target_x_m": 0.25, "target_z_m": 1.10, "release_after_steps": 72, "observed_max_vz_m_s": 1.554},
             {"target_x_m": 0.20, "target_z_m": 1.35, "release_after_steps": 72, "observed_max_vz_m_s": 1.490}]
    config = replace(LLMConfig.from_env(), log_path=str(OUTPUT / "llm_full.jsonl"), timeout_seconds=180)
    client = OpenAICompatibleDiagnoser(config, log_observer=journal.model_event)
    previous = None
    try:
        proposal = propose(client, Skill(**old), previous, probe)
        model_decision = proposal.get("decision")
        raw_parameters = proposal.get("parameters", {})
        # The model may include explanatory metadata alongside the three allowed controls.
        params = validate_parameters({key: raw_parameters[key] for key in ("target_x_m", "target_z_m", "release_after_steps")})
        journal.event({"kind": "model_proposal_validated", "proposal": proposal,
                       "decision": model_decision, "parameters_used": params})
        if model_decision == "stop":
            journal.note("模型建议停止释放；按用户将目标改为 2 m 的指令，继续执行只释放门控验证，不解除抓持约束。")
    except Exception as exc:
        proposal = {"decision": "fallback_try", "error": f"{type(exc).__name__}: {exc}",
                    "parameters": {key: probe[0][key] for key in ("target_x_m", "target_z_m", "release_after_steps")},
                    "prerequisite_skill_ids": [PREREQUISITE]}
        params = proposal["parameters"]
        journal.note(f"模型提案不可用，使用已测最佳参数作为保守回退：{proposal['error']}")
    reports = [run_gate_trial(i, params, journal) for i in range(1, 4)]
    blocked = all(not r.get("release_permitted", False) for r in reports)
    skill = {
        "skill_id": "throw_2m_catch_ground_v1", "name": "throw_2m_catch_ground", "status": "candidate", "version": 1,
        "task": "throw_catch_ground", "object_types": ["cube"],
        "trigger_conditions": ["object_grasped == true", "measured_lift == true"],
        "facts": ["target_rise_is_2m", f"required_release_vz_{REQUIRED_VZ:.6f}_m_s",
                  "prior_10m_search_max_release_vz_1.094805_m_s", "new_2m_probe_max_release_vz_2.027000_m_s",
                  "ground_placement_workspace_remains_unverified"],
        "hypotheses": ["current_position_ik_primitive_still_lacks_2m_throw_energy",
                       "measured_velocity_gate_prevents_false_success",
                       "dedicated_throw_trajectory_or_launcher_is_required"],
        "prediction_correction": ["require_lift_evidence_before_release", f"require_measured_vz_at_least_{REQUIRED_VZ:.6f}_m_s_before_release",
                                   "block_release_and_safety_stop_when_gate_fails", "require_2m_world_and_relative_height",
                                   "require_gated_catch_and_stable_ground_contact"],
        "recovery": ["retain_failure_evidence", "do_not_release_when_velocity_gate_is_blocked",
                     "upgrade_throw_trajectory_before_retry", "do_not_promote_incomplete_skill"],
        "validation_trials": len(reports), "false_success_rate": None, "recovery_success_rate": None,
        "prerequisite_skill_ids": [PREREQUISITE], "parameters": params, "validation_success_rate": 0.0,
        "validation_metrics": {"target_rise_m": TARGET_RISE_M, "required_vz_m_s": REQUIRED_VZ,
                                "gate_trials": len(reports), "gate_blocked_trials": sum(not r.get("release_permitted", False) for r in reports),
                                "safety_stop_trials": sum(r.get("safety_stop", False) for r in reports), "complete_success": False}}
    NEW_SKILL.write_text(json.dumps([skill], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"target_rise_m": TARGET_RISE_M, "required_vz_m_s": REQUIRED_VZ, "source_skill_sha256": source_hash,
        "model_proposal": proposal, "reports": reports, "release_gate_validated": blocked,
               "goal_achieved": False, "new_skill": skill}
    (OUTPUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    journal.note(f"2米目标实验结束：门控验证={blocked}；完整目标完成=False；Skill 保持 candidate。")


if __name__ == "__main__":
    main()
