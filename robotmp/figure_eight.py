"""Learn and verify a held-object vertical figure eight through a logged local LLM."""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import uuid

from .diagnosis import LLMConfig, OpenAICompatibleDiagnoser
from .environment import FailureMode
from .models import Skill
from .runner import default_store, run_episode
from .sim_environment import PyBulletPickPlaceEnv, SimConfig


PREREQUISITE = "grasp_without_lift_v1"
NEW_SKILL = "held_vertical_figure_eight_v1"
LOCAL_TZ = timezone(timedelta(hours=8))


class Journal:
    """Flush every action and every model request/response to disk immediately."""

    def __init__(self, output: Path, document: Path, model_document: Path):
        self.output = output
        output.mkdir(parents=True, exist_ok=True)
        self.document = document
        self.model_document = model_document
        document.parent.mkdir(parents=True, exist_ok=True)
        model_document.parent.mkdir(parents=True, exist_ok=True)
        self.session = uuid.uuid4().hex[:12]
        self.step = 0
        self.note(f"开始运行 {self.session}；输出目录 {output}。")

    @staticmethod
    def append(path: Path, text: str):
        with path.open("a", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()

    def note(self, text: str):
        stamp = datetime.now(LOCAL_TZ).isoformat(timespec="seconds")
        self.append(self.document, f"\n\n[{stamp}] {text}\n")
        print(text, flush=True)

    def event(self, event: dict):
        self.step += 1
        record = {"session": self.session, "step": self.step,
                  "local_time": datetime.now(LOCAL_TZ).isoformat(), **event}
        self.append(self.output / "events.jsonl", json.dumps(record, ensure_ascii=False) + "\n")
        state = event.get("state", {})
        position = state.get("object", {}).get("position_m")
        position_text = ", ".join(f"{v:.5f}" for v in position) if position else "—"
        sim_time = state.get("timestamp", 0.0)
        detail = {key: value for key, value in event.items() if key != "state"}
        if state:
            detail.update({"物体抓持": state["object"]["grasped"],
                           "实际抬升": state["object"]["lifted"],
                           "事件": state["events"]})
        line = (f"\n{self.step}. 仿真 {sim_time:.3f}s；物体中心 ({position_text}) m；"
                f"{json.dumps(detail, ensure_ascii=False)}\n")
        self.append(self.document, line)

    def model_event(self, record: dict):
        record = {"session": self.session, **record}
        self.append(self.output / "model_events.jsonl", json.dumps(record, ensure_ascii=False) + "\n")
        stamp = datetime.now(LOCAL_TZ).isoformat(timespec="seconds")
        self.append(self.model_document,
                    f"\n\n## {stamp} | {record['event']} | {record.get('request_id', '—')}\n\n"
                    f"```json\n{json.dumps(record, ensure_ascii=False, indent=2)}\n```\n")
        self.note(f"大模型 {record['event']}；request_id={record.get('request_id')}；"
                  f"完整内容已写入 {self.model_document}。")


def validate_parameters(raw: dict) -> dict:
    bounds = {"half_width_m": (0.03, 0.08), "half_height_m": (0.06, 0.11),
              "center_raise_m": (0.08, 0.14), "samples": (48, 96), "steps_per_waypoint": (24, 120)}
    if not isinstance(raw, dict) or set(raw) != set(bounds):
        raise ValueError(f"parameters must have exactly {list(bounds)}")
    result = {}
    for key, (low, high) in bounds.items():
        value = raw[key]
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError(f"{key} must be finite and numeric")
        if not low <= value <= high:
            raise ValueError(f"{key} outside [{low}, {high}]")
        if key in {"samples", "steps_per_waypoint"} and (not isinstance(value, int) or value % 2):
            raise ValueError(f"{key} must be an even integer")
        result[key] = value
    if result["half_height_m"] < 1.3 * result["half_width_m"]:
        raise ValueError("vertical figure eight must be taller than it is wide")
    if result["center_raise_m"] < result["half_height_m"]:
        raise ValueError("the lower loop must not descend below the initial lifted height")
    return result


def waypoints(center: list[float], parameters: dict) -> list[list[float]]:
    p = validate_parameters(parameters)
    return [[center[0], center[1] + p["half_width_m"] * math.sin(2 * angle),
             center[2] + p["half_height_m"] * math.sin(angle)]
            for angle in [2 * math.pi * index / p["samples"] for index in range(p["samples"] + 1)]]


def polygon_area(points: list[list[float]]) -> float:
    return sum(a[1] * b[2] - b[1] * a[2] for a, b in zip(points, points[1:] + points[:1])) / 2


def trajectory_metrics(actual: list[list[float]], targets: list[list[float]], parameters: dict) -> dict:
    if len(actual) != len(targets) or len(actual) != parameters["samples"] + 1:
        return {"passed": False, "error": "incomplete_trajectory", "waypoints": len(actual)}
    center = targets[0]
    half = parameters["samples"] // 2
    errors = [math.dist(a, b) for a, b in zip(actual, targets)]
    upper_area = polygon_area(actual[:half + 1])
    lower_area = polygon_area(actual[half:])
    expected_area = 4 * parameters["half_width_m"] * parameters["half_height_m"] / 3
    metrics = {
        "waypoints": len(actual), "max_tracking_error_m": max(errors),
        "rms_tracking_error_m": math.sqrt(sum(e * e for e in errors) / len(errors)),
        "closure_error_m": math.dist(actual[-1], actual[0]),
        "midpoint_crossing_error_m": math.dist(actual[half], center),
        "plane_error_m": max(abs(p[0] - center[0]) for p in actual),
        "upper_loop_area_m2": upper_area, "lower_loop_area_m2": lower_area,
        "vertical_span_m": max(p[2] for p in actual) - min(p[2] for p in actual),
        "horizontal_span_m": max(p[1] for p in actual) - min(p[1] for p in actual),
    }
    metrics["passed"] = (
        metrics["max_tracking_error_m"] <= 0.02 and metrics["closure_error_m"] <= 0.015
        and metrics["midpoint_crossing_error_m"] <= 0.015 and metrics["plane_error_m"] <= 0.015
        and upper_area * lower_area < 0
        and min(abs(upper_area), abs(lower_area)) >= expected_area * 0.6
        and metrics["vertical_span_m"] >= parameters["half_height_m"] * 1.7
        and metrics["horizontal_span_m"] >= parameters["half_width_m"] * 1.7
    )
    return metrics


class ReplayVideo:
    """Stream simulated camera frames; constant memory and real simulation pacing."""

    def __init__(self, output: Path):
        import imageio_ffmpeg
        import subprocess
        self.output = output
        self.error_stream = (output.parent / "ffmpeg.log").open("w", encoding="utf-8")
        self.process = subprocess.Popen([
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo",
            "-pix_fmt", "rgb24", "-s", "960x720", "-r", "24", "-i", "-", "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", str(output)], stdin=subprocess.PIPE,
            stderr=self.error_stream)
        self.tick = 0
        self.frames = 0

    def capture(self, env, state):
        self.tick += 1
        if self.tick % 10:
            return
        from PIL import Image, ImageDraw, ImageFont
        frame = Image.fromarray(env.capture_rgb(960, 720)).convert("RGB")
        draw = ImageDraw.Draw(frame)
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
        draw.rectangle((0, 0, 960, 75), fill="#111e30")
        draw.text((15, 5), "已验证抓取 Skill → 持物竖直画 8 → 放回桌面", font=font, fill="#50d8ee")
        draw.text((15, 39), f"仿真 {state.timestamp:.2f}s  阶段 {state.phase}  物体高度 {state.object.position_m[2]:.3f}m", font=font, fill="white")
        self.process.stdin.write(frame.tobytes())
        self.frames += 1
        if self.frames == 1:
            frame.save(self.output.parent / "preview.png")

    def close(self):
        self.process.stdin.close()
        code = self.process.wait()
        self.error_stream.close()
        if code:
            raise RuntimeError(f"video encoder failed: {code}")


def execute_trial(parameters: dict, store, journal: Journal, label: str, failure: FailureMode,
                  diagnoser, *, video: bool = False, gui: bool = False) -> dict:
    parameters = validate_parameters(parameters)
    journal.note(f"开始 {label}，故障={failure.value}，参数={json.dumps(parameters)}")
    envs = []
    events = []
    samples = []
    metrics = {"passed": False, "error": "trajectory_not_started"}
    continuous = {"samples": 0, "min_clearance_m": float("inf"), "grasp_retained": True}
    tracing = False
    recorder = ReplayVideo(journal.output / "replay.mp4") if video else None

    def on_step(state):
        if tracing:
            continuous["samples"] += 1
            continuous["min_clearance_m"] = min(continuous["min_clearance_m"], state.object.position_m[2] - 0.75)
            continuous["grasp_retained"] &= (
                state.object.grasped and not state.robot.gripper_open
                and math.dist(state.object.position_m, state.robot.end_effector_position_m) < 0.20)
        if recorder and envs:
            recorder.capture(envs[-1], state)

    def factory(mode):
        env = PyBulletPickPlaceEnv(mode, gui=gui, config=SimConfig(
            arm_model="xarm6", realtime=gui, frame_callback=on_step))
        envs.append(env)
        return env

    def emit(event):
        events.append(event)
        journal.event({"trial": label, **event})

    def draw(env):
        nonlocal tracing, metrics
        state = env.observe()
        if not state.object.lifted or not state.object.grasped:
            raise RuntimeError("cannot start figure eight without actual lift and grasp evidence")
        emit({"kind": "lift_gate_passed", "state": asdict(state), "prerequisite_skill_id": PREREQUISITE})
        tracing = True
        center = list(state.object.position_m)
        center[2] += parameters["center_raise_m"]
        state = env.move_held_object(center, steps=120)
        emit({"kind": "move_to_crossing", "state": asdict(state), "target": center})
        targets = waypoints(center, parameters)
        previous = None
        for index, target in enumerate(targets):
            state = env.move_held_object(target, steps=parameters["steps_per_waypoint"])
            actual = state.object.position_m
            samples.append({"index": index, "target": target, "actual": actual,
                            "time": state.timestamp, "grasped": state.object.grasped})
            emit({"kind": "figure_eight_waypoint", "index": index, "state": asdict(state),
                  "target": target, "tracking_error_m": math.dist(actual, target)})
            if gui and previous is not None:
                env.p.addUserDebugLine(previous, actual, [0, 0.9, 0.8], 3, physicsClientId=env.client)
            previous = actual
            if math.dist(actual, target) > 0.04 or not continuous["grasp_retained"] or continuous["min_clearance_m"] < 0.035:
                raise RuntimeError(f"trajectory execution gate failed at waypoint {index}")
        metrics = trajectory_metrics([s["actual"] for s in samples], targets, parameters)
        metrics.update(continuous)
        metrics["passed"] &= continuous["grasp_retained"] and continuous["min_clearance_m"] >= 0.035
        emit({"kind": "figure_eight_evaluation", "state": asdict(state), "metrics": metrics})
        tracing = False
        # Return to the known lifted height even for a completed but rejected candidate,
        # so the existing place action starts from its validated operating region.
        return_target = [center[0], center[1], center[2] - parameters["center_raise_m"]]
        state = env.move_held_object(return_target, steps=120)
        emit({"kind": "return_to_lift_height", "state": asdict(state), "target": return_target})

    result = None
    error = None
    placement = {"passed": False}
    try:
        result = run_episode("skills", failure, store, diagnoser=diagnoser, observer=emit,
                             env_factory=factory, close_env=False, after_lift=draw)
        env = envs[-1]
        released = env.observe()
        settled = env.settle_object()
        speed = math.sqrt(sum(v * v for v in env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)[0]))
        position = settled.object.position_m
        placement = {"drift_m": math.dist(released.object.position_m, position), "speed_m_s": speed,
                     "target_error_m": math.dist(position, [0.5, 0.0, 0.75]),
                     "released": not settled.object.grasped and settled.robot.gripper_open,
                     "height_error_m": abs(position[2] - 0.75)}
        placement["passed"] = (placement["released"] and placement["target_error_m"] <= 0.025
                               and placement["height_error_m"] <= 0.008
                               and placement["drift_m"] <= 0.003 and speed <= 0.02)
        emit({"kind": "placement_evaluation", "state": asdict(settled), "metrics": placement})
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        if envs:
            state = envs[-1].execute("stop")
            emit({"kind": "trial_stopped", "state": asdict(state), "error": error})
    finally:
        for env in envs:
            env.close()
        if recorder:
            recorder.close()
    applied = result.applied_skill_ids if result else []
    fallback = any(e["kind"] == "diagnosis_fallback" for e in events)
    report = {"label": label, "failure_mode": failure.value, "parameters": parameters,
              "trajectory": metrics, "placement": placement, "error": error,
              "applied_skill_ids": applied, "diagnosis_fallback": fallback,
              "result": asdict(result) if result else None,
              "passed": bool(metrics["passed"] and placement["passed"] and PREREQUISITE in applied and not fallback and not error)}
    (journal.output / f"{label}.json").write_text(json.dumps({"report": report, "waypoints": samples, "events": events}, ensure_ascii=False, indent=2), encoding="utf-8")
    journal.note(f"{label} 结束：{json.dumps(report, ensure_ascii=False)}")
    return report


def propose(client, old_skill: Skill, reports: list[dict], previous: dict | None = None) -> dict:
    instructions = (
        "You propose a reusable high-level robot Skill for a LOCAL PYBULLET SIMULATION. Return JSON only. "
        "Compose the supplied verified grasp skill with a predefined vertical figure-eight primitive and placement. "
        "Never output code, joint commands, torque, or arbitrary waypoints. The local primitive generates "
        "object-center targets x=cx, y=cy+a*sin(2t), z=cz+b*sin(t), 0<=t<=2pi. "
        "Choose ONLY these parameters: half_width_m [0.03,0.08], half_height_m [0.06,0.11], "
        "center_raise_m [0.08,0.14], samples even integer [48,96], steps_per_waypoint even integer [24,120]. "
        "Require half_height_m >= 1.3*half_width_m and center_raise_m >= half_height_m. "
        "The initial lifted object center is about [0.4526,0,0.9052]m, table surface 0.70m, cube half extent 0.05m. "
        "Track error <=0.02m, crossing/closure/plane error <=0.015m; two opposite signed lobe areas; "
        "continuous bottom clearance >=0.035m, grasp retained, placement error <=0.025m and drift <=0.003m. "
        "Return keys decision ('try' or 'accept'), name, description, prerequisite_skill_ids, parameters, "
        "observed_facts (array), hypotheses (array), rationale (string), recovery (array). Use Chinese prose. "
        "Accept only if supplied actual trial passed. Initial request MUST use decision try. "
        "On a failed trial, use its measured errors to revise parameters. Do not claim autonomy over controller learning."
    )
    return client.request_json(instructions, {"goal": "抓起方块，在空中竖直画一个8字，然后放下",
        "existing_verified_skill": asdict(old_skill), "previous_proposal": previous, "actual_trial_reports": reports})


def validate_proposal(proposal: dict, *, can_accept: bool):
    if proposal.get("decision") not in ({"try", "accept"} if can_accept else {"try"}):
        raise ValueError("invalid proposal decision")
    if proposal.get("prerequisite_skill_ids") != [PREREQUISITE]:
        raise ValueError("proposal must explicitly reuse the verified grasp Skill")
    for key in ["name", "description", "rationale"]:
        if not isinstance(proposal.get(key), str) or not proposal[key].strip():
            raise ValueError(f"missing text: {key}")
    for key in ["observed_facts", "hypotheses", "recovery"]:
        if not isinstance(proposal.get(key), list) or not all(isinstance(s, str) for s in proposal[key]):
            raise ValueError(f"invalid text array: {key}")
    validate_parameters(proposal["parameters"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/figure_eight_20261019"))
    parser.add_argument("--journal", type=Path, default=Path("docs/FIGURE_EIGHT_LEARNING.md"))
    parser.add_argument("--model-document", type=Path, default=Path("docs/FIGURE_EIGHT_LLM_CALLS.md"))
    parser.add_argument("--seed-store", type=Path, default=Path("artifacts/verification_20261019/skills.json"))
    parser.add_argument("--trials", type=int, default=6)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--llm-model")
    parser.add_argument("--llm-base-url", default="http://127.0.0.1:15723/v1")
    parser.add_argument("--gui", action="store_true", help="show the final independently reloaded replay")
    args = parser.parse_args()
    if args.trials < 3 or args.max_attempts < 1:
        parser.error("--trials must be >=3 and --max-attempts >=1")
    journal = Journal(args.output, args.journal, args.model_document)
    try:
        store = default_store(args.output / "skills.json")
        source = default_store(args.seed_store)
        old = next(s for s in source.all() if s.skill_id == PREREQUISITE and s.status == "verified")
        if "require_lift_evidence_before_transport" not in old.prediction_correction:
            raise ValueError("existing grasp skill lacks the lift-evidence invariant")
        store.save_candidate(old)
        journal.note(f"载入已验证前置 Skill {PREREQUISITE}，来源 {args.seed_store}，验证次数 {old.validation_trials}。")
        config = replace(LLMConfig.from_env(), base_url=args.llm_base_url.rstrip("/"),
                         log_path=str(args.output / "llm_full.jsonl"), timeout_seconds=180)
        if args.llm_model:
            config = replace(config, model=args.llm_model)
        client = OpenAICompatibleDiagnoser(config, log_observer=journal.model_event)
        reports = []
        proposal = None
        accepted = None
        for attempt in range(1, args.max_attempts + 1):
            proposal = propose(client, old, reports, proposal)
            validate_proposal(proposal, can_accept=False)
            journal.event({"kind": "model_proposal_validated", "attempt": attempt, "proposal": proposal})
            report = execute_trial(proposal["parameters"], store, journal, f"learning_{attempt}", FailureMode.LOW_GRIP_FORCE, client)
            reports.append(report)
            review = propose(client, old, reports, proposal)
            validate_proposal(review, can_accept=report["passed"])
            journal.event({"kind": "model_feedback_review", "proposal": review})
            if report["passed"] and review["decision"] == "accept" and review["parameters"] == proposal["parameters"]:
                accepted = review
                break
            proposal = review
        if accepted is None:
            raise RuntimeError("no model-proposed candidate accepted after measured trials")
        skill = Skill(skill_id=NEW_SKILL, name=accepted["name"], status="candidate", version=1,
                      task="held_vertical_figure_eight", object_types=["cube"],
                      trigger_conditions=["object_grasped == true", "object_lifted == true", "lift_evidence_confirmed == true"],
                      facts=accepted["observed_facts"], hypotheses=accepted["hypotheses"],
                      prediction_correction=["require_lift_evidence_before_transport", "require_both_vertical_lobes_and_closed_path", "verify_release_and_stability"],
                      recovery=accepted["recovery"], prerequisite_skill_ids=[PREREQUISITE], parameters=accepted["parameters"])
        store.save_candidate(skill)
        journal.note(f"新 Skill {NEW_SKILL} 保存为 candidate，开始独立重复验证。")
        validations = []
        modes = [FailureMode.NONE, FailureMode.LOW_GRIP_FORCE, FailureMode.MISALIGNED_GRASP]
        for index in range(args.trials):
            report = execute_trial(skill.parameters, store, journal, f"validation_{index + 1}", modes[index % 3], client)
            validations.append(report)
            if not report["passed"]:
                raise RuntimeError(f"independent validation {index + 1} failed; skill remains candidate")
        skill.status = "verified"
        skill.validation_trials = len(validations)
        skill.validation_success_rate = sum(r["passed"] for r in validations) / len(validations)
        skill.validation_metrics = {"max_tracking_error_m": max(r["trajectory"]["max_tracking_error_m"] for r in validations),
                                    "max_placement_error_m": max(r["placement"]["target_error_m"] for r in validations),
                                    "all_grasps_retained": all(r["trajectory"]["grasp_retained"] for r in validations)}
        store.save_candidate(skill)
        journal.note(f"新 Skill 已 verified：{json.dumps(asdict(skill), ensure_ascii=False)}")
        # Reload from disk through the same task-aware retrieval path used by later tasks.
        reloaded = default_store(store.path).retrieve("held_vertical_figure_eight", "cube", "observe")
        learned = next(s for s in reloaded if s.skill_id == NEW_SKILL and s.prerequisite_skill_ids == [PREREQUISITE])
        journal.event({"kind": "new_skill_retrieved_from_disk", "skill": asdict(learned)})
        replay = execute_trial(learned.parameters, default_store(store.path), journal, "replay", FailureMode.LOW_GRIP_FORCE, client, video=True, gui=args.gui)
        if not replay["passed"]:
            raise RuntimeError("verified Skill replay failed")
        summary = {"session": journal.session, "model": config.model, "endpoint": config.endpoint,
                   "learning_trials": reports, "independent_validations": validations,
                   "replay": replay, "learned_skill": asdict(learned),
                   "scope": "fixed-constraint PyBullet xArm6; predefined primitive with model-selected parameters; not hardware or neural training"}
        (args.output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        journal.note("学习、独立验证、重新载入复用、放下及稳定性检查全部完成。汇总：" + str(args.output / "summary.json"))
    except Exception as exc:
        journal.note(f"运行未完成：{type(exc).__name__}: {exc}。保留全部已写入的步骤和模型调用，禁止宣称验证成功。")
        raise


if __name__ == "__main__":
    main()
