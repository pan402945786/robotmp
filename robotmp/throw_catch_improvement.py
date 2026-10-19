"""Analyze throw/catch evidence and validate a release-safety improvement."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
import json
import math
from pathlib import Path

from .sim_environment import SimConfig
from .throw_catch import ThrowEnv

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path("docs/throw_catch_evidence_v2")
OUTPUT = Path("docs/throw_catch_improvement_20261019")
SKILL_PATH = Path("assets/skills/throw_catch_candidate.json")
REQUIRED_VZ = math.sqrt(2 * 9.81 * 10.0)


def release_gate(max_upward_velocity: float, required_vz: float = REQUIRED_VZ) -> bool:
    """Permit a release only if measured upward speed can meet the height target."""
    return math.isfinite(max_upward_velocity) and max_upward_velocity >= required_vz


def read_reports():
    return [json.loads((SOURCE / f"attempt_{i:02d}.json").read_text(encoding="utf-8")) for i in range(1, 5)]


def summarize(reports):
    return {
        "trials": len(reports),
        "max_release_vz_m_s": max(r.get("release_vz_m_s", 0.0) for r in reports),
        "max_apex_height_m": max(r.get("apex_height_m", 0.0) for r in reports),
        "max_rise_from_release_m": max(r.get("rise_from_release_m", 0.0) for r in reports),
        "caught_trials": sum(bool(r.get("caught")) for r in reports),
        "complete_successes": sum(bool(r.get("passed")) for r in reports),
        "joint_velocity_ratio_max": max(max(r.get("max_joint_velocity_ratios", [0.0])) for r in reports),
        "required_vz_m_s": REQUIRED_VZ,
    }


def run_gate_trial(index: int, target_x: float, release_steps: int):
    out = OUTPUT / f"gate_{index:02d}.json"
    csv_path = OUTPUT / f"gate_{index:02d}_physics.csv"
    OUTPUT.mkdir(parents=True, exist_ok=True)
    env = ThrowEnv(config=SimConfig(arm_model="xarm6"))
    rows = []
    events = []

    def record(kind, **extra):
        state = env.observe()
        linear, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        rows.append({"t_s": state.timestamp, "phase": state.phase, "x_m": state.object.position_m[0],
                     "y_m": state.object.position_m[1], "z_m": state.object.position_m[2],
                     "vz_m_s": linear[2], "constraint": env._constraint_id is not None,
                     "grasped": state.object.grasped, "lifted": state.object.lifted})
        events.append({"kind": kind, "state": asdict(state), **extra})

    try:
        record("reset")
        for action in ("approach_object", "close_gripper", "lift_object"):
            env.execute(action)
            record("action", action=action)
        if not env.observe().object.lifted:
            raise RuntimeError("lift evidence missing")
        start = env.observe()
        target = [target_x, start.object.position_m[1], 1.35]
        ee_target = [ee + goal - actual for ee, goal, actual in zip(
            start.robot.end_effector_position_m, target, start.object.position_m)]
        env._phase = "trace"
        env._set_gripper_pose(ee_target, open_gripper=False)
        max_vz = float("-inf")
        for step in range(release_steps):
            env._step(1)
            linear, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            max_vz = max(max_vz, linear[2])
            record("measured_trace_step", index=step + 1, vz_m_s=linear[2])
        permitted = release_gate(max_vz)
        if permitted:
            release = env.release_in_motion()
            record("release_gate_passed", measured_max_vz_m_s=max_vz)
            released = True
        else:
            env.execute("stop")
            record("release_gate_blocked", measured_max_vz_m_s=max_vz,
                   required_vz_m_s=REQUIRED_VZ, reason="10m height is physically unsupported by measured motion")
            release = env.observe()
            released = False
        result = {"trial": index, "target_x_m": target_x, "release_steps": release_steps,
                  "max_measured_vz_m_s": max_vz, "required_vz_m_s": REQUIRED_VZ,
                  "release_permitted": permitted, "released": released,
                  "safety_stop": env.stopped, "constraint_retained": env._constraint_id is not None,
                  "lifted": release.object.lifted, "events": events}
    except Exception as exc:
        result = {"trial": index, "target_x_m": target_x, "release_steps": release_steps,
                  "error": f"{type(exc).__name__}: {exc}", "events": events}
    finally:
        env.close()
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["t_s", "phase", "x_m", "y_m", "z_m", "vz_m_s", "constraint", "grasped", "lifted"])
        writer.writeheader()
        writer.writerows(rows)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def update_skill(summary, gate_results):
    skill = json.loads(SKILL_PATH.read_text(encoding="utf-8"))
    item = skill[0]
    item["version"] = 2
    item["status"] = "candidate"
    item["facts"] = [
        "require_measured_release_velocity_and_free_flight",
        "10m_height_is_not_evidence_of_catch_or_ground_placement",
        f"four_prior_trials_max_release_vz_{summary['max_release_vz_m_s']:.6f}_m_s_vs_required_{REQUIRED_VZ:.6f}_m_s",
        f"four_prior_trials_max_apex_{summary['max_apex_height_m']:.6f}_m_and_max_rise_{summary['max_rise_from_release_m']:.6f}_m",
        "xarm6_table_scene_cannot_reach_ground_placement_target_with_current_workspace",
    ]
    item["hypotheses"] = [
        "current_single_target_ik_primitive_cannot supply the measured launch energy",
        "release timing must be gated by measured upward velocity instead of fixed steps",
        "10m throwing requires a dedicated high speed trajectory or launch mechanism and a reachable ground placement scene",
    ]
    item["prediction_correction"] = [
        "require_lift_evidence_before_release",
        "require_measured_vz_at_least_14.007142_m_s_before_release",
        "block_release_and_safety_stop_when_height_capability_is_not_observed",
        "require_reachable_ground_placement_workspace_before_acceptance",
        "require_gated_catch_and_stable_ground_contact",
    ]
    item["recovery"] = [
        "retain_failure_evidence",
        "do_not_release_when_velocity_gate_is_blocked",
        "upgrade_throw_trajectory_or_hardware_before_retrying_10m_goal",
        "do_not_promote_incomplete_skill",
    ]
    item["validation_trials"] = len(gate_results)
    item["validation_success_rate"] = 0.0
    item["validation_metrics"] = {
        "complete_three_trial_validation": False,
        "prior_throw_trials": summary["trials"],
        "prior_max_release_vz_m_s": summary["max_release_vz_m_s"],
        "prior_max_apex_height_m": summary["max_apex_height_m"],
        "prior_max_rise_from_release_m": summary["max_rise_from_release_m"],
        "improvement_gate_trials": len(gate_results),
        "improvement_gate_blocked_trials": sum(not r.get("release_permitted", False) for r in gate_results),
        "improvement_gate_safety_stops": sum(r.get("safety_stop", False) for r in gate_results),
    }
    SKILL_PATH.write_text(json.dumps(skill, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return skill


def main():
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    OUTPUT = args.output
    reports = read_reports()
    prior = summarize(reports)
    gate_results = [run_gate_trial(i, x, 48) for i, x in enumerate((0.25, 0.40, 0.55), 1)]
    skill = update_skill(prior, gate_results)
    analysis = {
        "date": "2026-10-19",
        "prior_evidence": prior,
        "failure_analysis": [
            "释放能量不足：达到相对上升10米需要约14.007 m/s竖直释放速度；历史最大实测仅1.095 m/s，约为要求的7.8%。",
            "释放时机不可靠：固定4、24、48步分别得到负、正、负或低速释放；目标位置不等于释放速度。",
            "关节余量不足：历史最大关节速度比约1.005，多个关节已贴近URDF速度上限；不能靠原参数范围补足约13倍速度差。",
            "接球只在第4次通过下降距离和相对速度门槛；前三次先接触环境。接球本身不是完整任务成功。",
            "放地失败：当前桌面和xArm6工作空间无法把物体送到z=0地面目标，必须改场景或增加可达放置动作。",
        ],
        "improvement_plan": [
            "释放前先确认真实抬升，再持续测量物体竖直速度；只有达到14.007142 m/s才允许解除抓持约束。",
            "门控失败时安全停止并记录证据，禁止把固定步数完成或短暂接球当作成功。",
            "下一版运动控制需要专用高速抛掷轨迹、扩大速度/加速度能力或独立抛射机构；仅调整当前三个参数没有证据能达到10米。",
            "将地面放置改成可达场景：扩大地面区域并提供低位末端工作空间，或使用移动基座/专用放置机构。",
            "重新验证时至少3次独立完整通过抬升、两项10米高度、下降接球和地面静置，才可升级为verified。",
        ],
        "gate_validation": gate_results,
        "updated_skill": skill,
        "status": "candidate_only",
    }
    (OUTPUT / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"prior": prior, "gate_results": gate_results, "skill_status": skill[0]["status"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
