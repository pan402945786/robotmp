"""Evidence-first xArm6 throw/catch learning for a 0.5 m toss; no state injection."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, replace
import hashlib
import json
import math
from pathlib import Path
import subprocess

from .diagnosis import LLMConfig, OpenAICompatibleDiagnoser
from .environment import FailureMode
from .figure_eight import Journal, PREREQUISITE
from .models import Skill
from .monitor import compare_prediction
from .predictor import make_prediction
from .runner import default_store
from .sim_environment import PyBulletPickPlaceEnv, SimConfig

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = Path("docs/throw_catch_05m_20261019")
SKILL_PATH = Path("assets/skills/throw_05m_catch_ground_candidate.json")
TARGET_RISE_M = 0.5
REQUIRED_VZ = math.sqrt(2 * 9.81 * TARGET_RISE_M)


class Audit(Journal):
    def checkpoint(self, reason):
        paths = [self.document, self.model_document, self.output, SKILL_PATH,
                 Path("robotmp/throw_catch_05m.py"), Path("tests/test_throw_catch.py")]
        paths = [str(p) for p in paths if p.exists()]
        subprocess.run(["git", "add", "--", *paths], cwd=ROOT, check=True, capture_output=True)
        changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        if changed.returncode == 1:
            result = subprocess.run(["git", "commit", "-m", f"experiment: {reason}"],
                                    cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
            print(result.stdout.strip(), flush=True)
        elif changed.returncode:
            raise RuntimeError("git staged diff failed")

    def model_event(self, record):
        super().model_event(record)
        self.checkpoint(f"save throw catch model {record['event']} {record.get('request_id', '')[:8]}")


def validate_parameters(raw):
    bounds = {"target_x_m": (0.25, 0.55), "target_z_m": (1.05, 1.60),
              "release_after_steps": (4, 120)}
    if not isinstance(raw, dict) or set(raw) != set(bounds):
        raise ValueError(f"parameters must have exactly {list(bounds)}")
    for key, (low, high) in bounds.items():
        value = raw[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{key} must be finite numeric")
        if not low <= value <= high:
            raise ValueError(f"{key} outside bounds")
    if not isinstance(raw["release_after_steps"], int):
        raise ValueError("release_after_steps must be integer")
    return dict(raw)


def catch_gate(position, velocity, ee, ee_velocity, *, had_apex, flight_contact, flight_ticks=0):
    return (had_apex and flight_ticks >= 10 and not flight_contact and velocity[2] < -0.05
            and math.dist(position, ee) <= 0.13
            and math.dist(velocity, ee_velocity) <= 1.0)


def acceptance(report):
    return bool(report.get("lift_confirmed") and report.get("release_vz_m_s", 0) >= REQUIRED_VZ
                and report.get("free_flight") and report.get("apex_height_m", 0) >= 0.5
                and report.get("rise_from_release_m", 0) >= TARGET_RISE_M
                and report.get("caught") and report.get("placement", {}).get("passed"))


class ThrowEnv(PyBulletPickPlaceEnv):
    def release_in_motion(self):
        if not self.observe().object.lifted or not self._grasped or self._constraint_id is None:
            raise RuntimeError("throw requires acquired grasp and measured lift")
        self.p.removeConstraint(self._constraint_id, physicsClientId=self.client)
        self._constraint_id = None
        self._grasped = False
        self._gripper_open = True
        self._gripper_force = 0.0
        self._set_gripper_pose(self._actual_ee_position(), open_gripper=True)
        self._phase = "transport"
        self._events = ["object_released_in_motion"]
        # Deliberately no physics step here: caller records the exact release state.
        return self.observe()
    def catch(self):
        if self._constraint_id is not None:
            raise RuntimeError("catch requires a released object")
        self._gripper_open = False
        self._gripper_force = 1.0
        self._set_gripper_pose(self._actual_ee_position(), open_gripper=False)
        self._create_grasp_constraint()
        self._grasped = True
        self._events = ["descending_object_caught_with_gated_fixed_constraint"]
        return self.observe()


class ReleaseGateBlocked(RuntimeError):
    """Safety stop after measured launch speed failed the 0.5 m gate."""


def execute_trial(parameters, old, audit, label, failure=FailureMode.NONE):
    parameters = validate_parameters(parameters)
    report = {"label": label, "failure_mode": failure.value, "parameters": parameters,
              "applied_skill_ids": [], "lift_confirmed": False, "caught": False,
              "free_flight": False, "placement": {"passed": False, "status": "not_reached"}}
    stream = (audit.output / f"{label}_physics.csv").open("w", encoding="utf-8", newline="")
    writer = csv.writer(stream)
    writer.writerow(["t_s", "phase", "x_m", "y_m", "z_m", "vx", "vy", "vz",
                     "wx", "wy", "wz", "ee_x", "ee_y", "ee_z", "constraint", "contact",
                     *[f"joint_{i}_velocity" for i in range(1, 7)]])
    samples = 0
    max_joint_ratios = [0.0] * 6
    env = None

    def sample(state):
        nonlocal samples
        if env is None:
            return
        linear, angular = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        joint_vel = [env.p.getJointState(env._gripper_id, j, physicsClientId=env.client)[1]
                     for j in env._arm_joint_ids]
        for i, v in enumerate(joint_vel):
            max_joint_ratios[i] = max(max_joint_ratios[i], abs(v) / env._arm_velocity[i])
        writer.writerow([state.timestamp, state.phase, *state.object.position_m, *linear, *angular,
                         *state.robot.end_effector_position_m, env._constraint_id is not None,
                         bool(env.p.getContactPoints(env._cube_id, physicsClientId=env.client)), *joint_vel])
        stream.flush()
        samples += 1

    def emit(kind, **detail):
        audit.event({"trial": label, "kind": kind, "state": asdict(env.observe()), **detail})

    def action(name):
        env.execute(name)
        emit("action", action=name)

    audit.note(f"开始 {label}；参数 {json.dumps(parameters)}；故障 {failure.value}。")
    try:
        env = ThrowEnv(failure, config=SimConfig(arm_model="xarm6", frame_callback=sample))
        ground = env.p.loadURDF("plane.urdf", physicsClientId=env.client)
        emit("scene_ready", ground_body_id=ground, physics_trace=f"{label}_physics.csv",
             model="xarm6", ground_z_m=0, table_z_m=0.70,
             cube_dynamics=env.p.getDynamicsInfo(env._cube_id, -1, physicsClientId=env.client))
        skills = [old]
        report["applied_skill_ids"] = [s.skill_id for s in skills]
        emit("prerequisite_retrieved", skill=asdict(old))
        action("approach_object")
        action("close_gripper")
        prediction = make_prediction(env.observe(), skills)
        action("lift_object")
        comparison = compare_prediction(prediction, env.observe())
        emit("lift_comparison", prediction=asdict(prediction), comparison=asdict(comparison))
        if comparison.status != "match":
            emit("grasp_recovery_from_existing_skill", recovery=old.recovery)
            for name in ["refresh_object_pose", "retry_grasp", "close_gripper", "lift_object"]:
                action(name)
        if not env.observe().object.grasped or not env.observe().object.lifted:
            raise RuntimeError("lift evidence missing; launch blocked")
        report["lift_confirmed"] = True
        emit("lift_gate_passed")
        before = env.observe()
        target = [parameters["target_x_m"], before.object.position_m[1], parameters["target_z_m"]]
        ee_target = [ee + goal - actual for ee, goal, actual in zip(
            before.robot.end_effector_position_m, target, before.object.position_m)]
        env._phase = "trace"
        env._set_gripper_pose(ee_target, open_gripper=False)
        emit("upward_sweep_commanded", object_target=target, steps=parameters["release_after_steps"])
        max_vz = float("-inf")
        for i in range(parameters["release_after_steps"]):
            env._step(1)
            emit("sweep_step", index=i + 1)
            release_velocity, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            max_vz = max(max_vz, float(release_velocity[2]))
        report["max_measured_vz_m_s"] = max_vz
        if max_vz < REQUIRED_VZ:
            env.execute("stop")
            report.update(release_vz_m_s=max_vz, free_flight=False, flight_contact_before_catch=False)
            emit("release_gate_blocked", measured_max_vz_m_s=max_vz,
                 required_vz_m_s=REQUIRED_VZ, target_rise_m=TARGET_RISE_M,
                 reason="measured upward speed cannot support 0.5m rise")
            env._step(120)
            emit("post_gate_safety_observation")
            report["gate_blocked"] = True
            raise ReleaseGateBlocked("release gate blocked")
        release_state = env.release_in_motion()
        release_pos = list(release_state.object.position_m)
        release_v, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        report.update(release_height_m=release_pos[2], release_velocity_m_s=list(release_v),
                      release_vz_m_s=release_v[2],
                      ideal_vacuum_rise_m=max(0, release_v[2]) ** 2 / (2 * 9.81),
                      required_vz_for_target_rise_m_s=REQUIRED_VZ)
        emit("release_measured", **{k: v for k, v in report.items() if k.startswith("release") or k.startswith("ideal") or k.startswith("required")})
        apex = release_pos[2]
        had_apex = False
        ascent_seen = release_v[2] > 0.05
        flight_contact = False
        ee_previous = env._actual_ee_position()
        flight_ticks = 0
        for tick in range(240 * 8):
            pos = env._cube_position()
            vel, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            # Track a near-workspace descending intercept, with actual observations each tick.
            if vel[2] < 0:
                fall = max(0.0, pos[2] - 0.94)
                intercept_t = (vel[2] + math.sqrt(vel[2] ** 2 + 2 * 9.81 * fall)) / 9.81
                intercept = [pos[0] + vel[0] * intercept_t, pos[1] + vel[1] * intercept_t, 1.06]
                if 0.20 <= intercept[0] <= 0.65 and abs(intercept[1]) <= 0.30:
                    env._set_gripper_pose(intercept, open_gripper=True)
            env._step(1)
            flight_ticks += 1
            pos = env._cube_position()
            vel, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            ee = env._actual_ee_position()
            ee_vel = [(a - b) / env.config.time_step_s for a, b in zip(ee, ee_previous)]
            ee_previous = ee
            contacts = env.p.getContactPoints(env._cube_id, physicsClientId=env.client)
            flight_contact |= bool(contacts)
            apex = max(apex, pos[2])
            if vel[2] > 0.05:
                ascent_seen = True
            if ascent_seen and vel[2] <= 0 and not had_apex:
                had_apex = True
                emit("apex_or_initial_descent", measured_height_m=apex, vz_m_s=vel[2])
            if tick % 12 == 0:
                emit("flight_observation", velocity_m_s=list(vel), ee_velocity_m_s=ee_vel,
                     catch_distance_m=math.dist(pos, ee), relative_speed_m_s=math.dist(vel, ee_vel),
                     constraint_active=env._constraint_id is not None, contact=bool(contacts))
            if catch_gate(pos, vel, ee, ee_vel, had_apex=had_apex, flight_contact=flight_contact,
                          flight_ticks=flight_ticks):
                env.catch()
                report["caught"] = True
                emit("catch_gate_passed", distance_m=math.dist(pos, ee), relative_speed_m_s=math.dist(vel, ee_vel))
                break
            if contacts:
                emit("missed_catch_object_contacted_environment", contact_body_ids=[c[2] for c in contacts])
                break
        report.update(apex_height_m=apex, rise_from_release_m=apex - release_pos[2],
                      free_flight=flight_ticks > 0, flight_ticks=flight_ticks,
                      flight_contact_before_catch=flight_contact)
        if report["caught"]:
            # Ground placement: carry beyond the tabletop, then descend with measured feedback.
            pos = env._cube_position()
            env.move_held_object([0.95, pos[1], max(1.0, pos[2])], steps=240)
            emit("carry_outside_table")
            if env._cube_position()[0] < 0.88:
                raise RuntimeError("ground placement unreachable outside table; retain grasp")
            for i in range(400):
                pos = env._cube_position()
                ee = env._actual_ee_position()
                env._set_gripper_pose([ee[0], ee[1], ee[2] - min(0.002, max(0, pos[2] - 0.05))], open_gripper=False)
                env._step(2)
                emit("ground_lowering_step", index=i)
                if pos[2] <= 0.055:
                    break
            if env._cube_position()[2] > 0.055:
                raise RuntimeError("ground height unreachable; no ground placement claim")
            action("release_object")
            initial = env._cube_position()
            env.settle_object(steps=480)
            final = env._cube_position()
            linear, angular = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            ground_contact = bool(env.p.getContactPoints(env._cube_id, ground, physicsClientId=env.client))
            report["placement"] = {"drift_m": math.dist(initial, final), "speed_m_s": math.dist(linear, [0, 0, 0]),
                                   "angular_speed_rad_s": math.dist(angular, [0, 0, 0]), "ground_contact": ground_contact,
                                   "height_error_m": abs(final[2] - 0.05), "released": not env._grasped}
            p = report["placement"]
            p["passed"] = p["ground_contact"] and p["released"] and p["drift_m"] <= 0.003 and p["speed_m_s"] <= 0.01 and p["height_error_m"] <= 0.003 and p["angular_speed_rad_s"] <= 0.05
            emit("placement_evaluation", metrics=p)
        else:
            emit("placement_not_reached", reason="未通过接球门槛，不能声明已接住后平稳放地")
            env._step(480)
            emit("post_failure_settled_observation")
    except ReleaseGateBlocked:
        pass
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
        if env is not None:
            emit("trial_error", error=report["error"])
        else:
            audit.event({"trial": label, "kind": "trial_error", "error": report["error"]})
    finally:
        if env is not None:
            env.close()
        stream.close()
    report["physics_samples"] = samples
    report["max_joint_velocity_ratios"] = max_joint_ratios
    # Even apparent success cannot validate motion that exceeded the URDF velocities.
    report["passed"] = acceptance(report) and max(max_joint_ratios) <= 1.05 and "error" not in report
    (audit.output / f"{label}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    audit.note(f"{label} 结束：{json.dumps(report, ensure_ascii=False)}")
    audit.checkpoint(f"save measured throw catch trial {label}")
    return report


def propose(client, old, reports, capability, previous=None):
    return client.request_json(
        "You design a high-level Skill experiment in LOCAL PyBullet xArm6 simulation. JSON only, Chinese prose. "
        "Goal: pick up cube, release it upward, achieve BOTH world z>=0.5m AND rise>=0.5m from release, catch, place on ground. "
        "Reuse grasp_without_lift_v1. Object velocity/position injection, launch forces and changing gravity are forbidden. "
        "Local predefined primitive moves the measured held-object pose toward one Cartesian IK target under URDF limits, "
        "releases constraint after N physics steps and observes real flight. Fixed-constraint catch requires descent, "
        "distance<=0.13m and relative speed<=1m/s. Ground is z=0, tabletop z=0.70. "
        f"Release is permitted only when measured upward speed is at least {REQUIRED_VZ:.6f} m/s. "
        "Choose ONLY parameters target_x_m [0.25,0.55], target_z_m [1.05,1.60], release_after_steps integer [4,120]. "
        "Return decision ('try','stop','accept'), prerequisite_skill_ids, parameters, observed_facts array, hypotheses array, "
        "rationale string, next_requirements array. First response must try. After failures revise parameters or stop "
        "with an evidence-based capability assessment. Never accept unless at least 3 independent complete successful "
        "trials have passed all stages. A small measured height is failure, even if primitive finished. "
        "Do not claim a sampled failure mathematically proves all controllers infeasible. No executable code or joint commands.",
        {"goal": "抓起→抛高至少10米→接住→平稳放地", "existing_verified_skill": asdict(old),
         "capability": capability, "actual_reports": reports, "previous": previous})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=EVIDENCE)
    parser.add_argument("--seed-store", type=Path, default=Path("artifacts/verification_20261019/skills.json"))
    parser.add_argument("--max-attempts", type=int, default=4)
    args = parser.parse_args()
    if args.max_attempts < 1:
        parser.error("--max-attempts must be positive")
    audit = Audit(args.output, Path("docs/THROW_CATCH_LEARNING.md"), Path("docs/THROW_CATCH_LLM_CALLS.md"))
    if (args.output / "summary.json").exists():
        raise ValueError("output already has a completed run; specify a fresh --output")
    old = next(s for s in default_store(args.seed_store).all() if s.skill_id == PREREQUISITE and s.status == "verified")
    if "require_lift_evidence_before_transport" not in old.prediction_correction:
        raise ValueError("source Skill lacks lift evidence invariant")
    source_hash = hashlib.sha256(args.seed_store.read_bytes()).hexdigest()
    (args.output / "source_skill.json").write_bytes(args.seed_store.read_bytes())
    env = ThrowEnv(config=SimConfig(arm_model="xarm6"))
    try:
        capability = {"time_step_s": env.config.time_step_s, "gravity_m_s2": 9.81,
                      "joint_velocity_limits_rad_s": env._arm_velocity,
                      "joint_effort_limits_Nm": env._arm_effort,
                      "joint_lower_rad": env._arm_lower, "joint_upper_rad": env._arm_upper,
                      "cube_mass_kg": 0.10, "target_rise_m": TARGET_RISE_M,
                      "required_vz_for_target_rise_m_s": REQUIRED_VZ,
                      "grasp_model": "fixed constraint; robot-cube collision disabled; idealized acquisition",
                      "ground_z_m": 0, "table_z_m": 0.70}
    finally:
        env.close()
    audit.event({"kind": "capability_inspection", "source_sha256": source_hash, **capability})
    config = replace(LLMConfig.from_env(), log_path=str(args.output / "llm_full.jsonl"), timeout_seconds=180)
    client = OpenAICompatibleDiagnoser(config, log_observer=audit.model_event)
    reports, proposals = [], []
    failure = None
    try:
        for attempt in range(1, args.max_attempts + 1):
            proposal = propose(client, old, reports, capability, proposals[-1] if proposals else None)
            if proposal.get("prerequisite_skill_ids") != [PREREQUISITE]:
                raise ValueError("model did not explicitly reuse prerequisite")
            decision = proposal.get("decision")
            if decision not in {"try", "stop", "accept"} or (not reports and decision != "try"):
                raise ValueError("invalid model decision")
            params = validate_parameters(proposal.get("parameters"))
            proposals.append(proposal)
            audit.event({"kind": "model_proposal_validated", "proposal": proposal})
            if decision == "stop":
                audit.note("模型根据已测量失败证据建议停止当前原语搜索。保留候选，不升级为已验证技能。")
                break
            if decision == "accept":
                if len(reports) < 3 or not all(r["passed"] for r in reports[-3:]):
                    raise ValueError("model attempted acceptance without three complete successes")
                break
            report = execute_trial(params, old, audit, f"attempt_{attempt:02d}",
                                   FailureMode.LOW_GRIP_FORCE if attempt == 2 else FailureMode.NONE)
            reports.append(report)
        # Always return measured results to the model, including the final allowed trial.
        if reports and proposals[-1].get("decision") == "try":
            review = propose(client, old, reports, capability, proposals[-1])
            proposals.append(review)
            audit.event({"kind": "final_model_review", "proposal": review})
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        audit.note(f"学习流程事件：{failure}。所有已产生的请求、响应及实验保留。")
    complete = len(reports) >= 3 and all(r["passed"] for r in reports[-3:])
    candidate = Skill(skill_id="throw_05m_catch_ground_v1", name="throw_05m_catch_ground",
        status="candidate", version=1, task="throw_catch_ground", object_types=["cube"],
        trigger_conditions=["object_grasped == true", "measured_lift == true"],
        facts=["require_measured_release_velocity_and_free_flight", "0.5m_rise_is_required", "catch_and_ground_placement_are_independent_gates"],
        hypotheses=["current_sweep_primitive_may_lack_0.5m_release_energy"],
        prediction_correction=["require_measured_vz_before_release", "require_0.5m_free_flight_before_success", "require_gated_catch_and_stable_ground_contact"],
        recovery=["retain_failure_evidence", "do_not_promote_incomplete_skill"],
        prerequisite_skill_ids=[PREREQUISITE], parameters=reports[-1]["parameters"] if reports else {},
        validation_trials=len(reports), validation_success_rate=sum(r["passed"] for r in reports) / len(reports) if reports else 0,
        validation_metrics={"complete_three_trial_validation": complete,
                            "target_rise_m": TARGET_RISE_M,
                            "required_vz_m_s": REQUIRED_VZ,
                            "max_observed_apex_m": max((r.get("apex_height_m", 0) for r in reports), default=0),
                            "max_observed_rise_m": max((r.get("rise_from_release_m", 0) for r in reports), default=0)})
    # Promotion and reloadable successful skill require a separate explicit complete validation path.
    default_store(SKILL_PATH).save_candidate(candidate)
    summary = {"goal_achieved": complete, "new_skill_status": "candidate", "error": failure,
               "source_skill_sha256": source_hash, "source_unchanged": source_hash == hashlib.sha256(args.seed_store.read_bytes()).hexdigest(),
               "capability": capability, "reports": reports, "proposals": proposals,
               "scope": "PyBullet xArm6 fixed-constraint simulation; bounded primitive search, not neural training or hardware"}
    (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    audit.note(f"实验结束：goal_achieved={complete}，试验数={len(reports)}，新技能状态 candidate；原技能保持不变。汇总：{args.output / 'summary.json'}")
    audit.checkpoint("preserve throw catch learning outcome and candidate")
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
