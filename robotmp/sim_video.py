"""Render a video from actual PyBullet camera frames and telemetry."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path

from .diagnosis import LLMConfig, make_diagnoser
from .environment import FailureMode
from .runner import default_store, run_episode
from .sim_environment import PyBulletPickPlaceEnv, SimConfig


def _font_path(explicit: str | None) -> str:
    candidates = [explicit, "C:/Windows/Fonts/msyh.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("Chinese font missing; pass --font with a .ttf/.ttc file")


def _ffmpeg_path(explicit: str | None) -> str:
    if explicit and Path(explicit).is_file():
        return explicit
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        candidates = list(Path("C:/Users/Highland/AppData/Roaming/Python").glob("Python*/site-packages/imageio_ffmpeg/binaries/ffmpeg*.exe"))
        if candidates:
            return str(candidates[0])
    raise RuntimeError("ffmpeg unavailable; install imageio-ffmpeg or pass --ffmpeg")


def render(output: Path, failure_mode: FailureMode, fps: int, font: str | None, ffmpeg: str | None, diagnoser, llm_model: str) -> dict:
    from PIL import Image, ImageDraw, ImageFont

    output.mkdir(parents=True, exist_ok=True)
    font_file = _font_path(font)
    font_title = ImageFont.truetype(font_file, 30)
    font_value = ImageFont.truetype(font_file, 25)
    font_small = ImageFont.truetype(font_file, 20)
    frames: list[tuple[object, dict]] = []
    holder: list[PyBulletPickPlaceEnv] = []

    def on_step(state):
        if holder:
            frames.append((holder[0].capture_rgb(640, 480), asdict(state)))

    envs: list[PyBulletPickPlaceEnv] = []

    def factory(mode: FailureMode):
        env = PyBulletPickPlaceEnv(mode, gui=False, config=SimConfig(gripper_model="urdf", arm_model="xarm6", frame_callback=on_step))
        holder.append(env)
        envs.append(env)
        return env

    events: list[dict] = []
    try:
        result = run_episode("feedback", failure_mode, default_store(output / "sim_video_skills.json"), diagnoser=diagnoser, observer=events.append, env_factory=factory, close_env=False)
        # Capture a final frame after the result event, then close the physics client.
        env = envs[0]
        frames.append((env.capture_rgb(640, 480), asdict(env.observe())))
    finally:
        for env in envs:
            env.close()

    if not frames:
        raise RuntimeError("PyBullet produced no camera frames")
    diagnosis_event = next((event for event in events if event["kind"] == "diagnosis"), None)
    diagnosis_source = diagnosis_event.get("source", type(diagnoser).__name__) if diagnosis_event else type(diagnoser).__name__
    diagnosis_label = "LLM / OpenAI" if "OpenAICompatible" in diagnosis_source else "规则诊断"
    diagnosis_name = diagnosis_event.get("skill", {}).get("name", "—") if diagnosis_event else "—"

    width, height = 1280, 720
    ffmpeg_exe = _ffmpeg_path(ffmpeg)
    target = output / "robotmp_simulation.mp4"
    command = [ffmpeg_exe, "-y", "-loglevel", "error", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for raw, state in frames:
            frame = Image.fromarray(raw).resize((960, 720)).convert("RGB")
            canvas = Image.new("RGB", (width, height), "#09111e")
            canvas.paste(frame, (0, 0))
            draw = ImageDraw.Draw(canvas)
            draw.rectangle((960, 0, width, height), fill="#111e30")
            draw.text((986, 32), "PyBullet 实际仿真", font=font_title, fill="#50d8ee")
            draw.text((986, 73), f"诊断器: {diagnosis_label}", font=font_small, fill="#bda8ff")
            rows = [
                ("仿真时间", f"{state['timestamp']:.2f} s", "#50d8ee"),
                ("物体高度", f"{state['object']['position_m'][2]:.3f} m", "#68e6b2"),
                ("夹爪力度", f"{state['robot']['gripper_force']:.2f}", "#ffc478"),
                ("观测置信度", f"{state['object']['confidence']:.2f}", "#bda8ff"),
                ("阶段", state["phase"], "#eaf2fb"),
                ("已抬升", "是" if state["object"]["lifted"] else "否", "#68e6b2" if state["object"]["lifted"] else "#ff8490"),
            ]
            y = 115
            for label, value, color in rows:
                draw.text((986, y), label, font=font_small, fill="#8fa4be")
                draw.text((986, y + 29), value, font=font_value, fill=color)
                y += 87
            events_text = ", ".join(state["events"]) if state["events"] else "—"
            draw.text((986, 650), "事件", font=font_small, fill="#8fa4be")
            draw.text((986, 680), events_text[:26], font=font_small, fill="#eaf2fb")
            process.stdin.write(canvas.tobytes())
        process.stdin.close()
        stderr = process.stderr.read().decode(errors="replace")
        code = process.wait()
        if code:
            raise RuntimeError(f"ffmpeg failed ({code}): {stderr}")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stderr.close()

    info = {
        "file": str(target.resolve()),
        "frames": len(frames),
        "fps": fps,
        "duration_seconds": len(frames) / fps,
        "width": width,
        "height": height,
        "backend": "PyBullet",
        "robot_urdf": "pybullet_data/xarm/xarm6_with_gripper.urdf",
        "arm_joints": 6,
        "control": "inverse kinematics + POSITION_CONTROL",
        "result": asdict(result),
        "diagnosis_source": diagnosis_source,
        "diagnosis_label": diagnosis_label,
        "diagnosis_skill_name": diagnosis_name,
        "llm_model": llm_model,
        "trace": str((output / "trace.json").resolve()),
    }
    (output / "trace.json").write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "video_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    return info


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/simulation_video"))
    parser.add_argument("--failure-mode", choices=[item.value for item in FailureMode], default="low_grip_force")
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--font")
    parser.add_argument("--ffmpeg")
    parser.add_argument("--diagnoser", choices=["auto", "rules", "llm"], default="auto")
    parser.add_argument("--llm-base-url")
    parser.add_argument("--llm-model")
    parser.add_argument("--llm-wire-api", choices=["responses", "chat"])
    parser.add_argument("--llm-timeout", type=float)
    parser.add_argument("--llm-log", help="JSONL log for model requests and responses")
    args = parser.parse_args()
    if not 1 <= args.fps <= 60:
        parser.error("--fps must be between 1 and 60")
    try:
        import PIL  # noqa: F401
        import pybullet  # noqa: F401
    except ImportError:
        parser.exit(1, "Run this command with the project's py311 simulation environment.\n")
    config = LLMConfig.from_env()
    if args.llm_base_url:
        config = LLMConfig(args.llm_base_url, config.model, config.wire_api, config.api_key, config.timeout_seconds, config.log_path)
    if args.llm_model:
        config = LLMConfig(config.base_url, args.llm_model, config.wire_api, config.api_key, config.timeout_seconds, config.log_path)
    if args.llm_wire_api:
        config = LLMConfig(config.base_url, config.model, args.llm_wire_api, config.api_key, config.timeout_seconds, config.log_path)
    if args.llm_timeout is not None:
        config = LLMConfig(config.base_url, config.model, config.wire_api, config.api_key, args.llm_timeout, config.log_path)
    if args.llm_log is not None:
        config = LLMConfig(config.base_url, config.model, config.wire_api, config.api_key, config.timeout_seconds, args.llm_log)
    diagnoser = make_diagnoser(args.diagnoser, config)
    print(json.dumps(render(args.output, FailureMode(args.failure_mode), args.fps, args.font, args.ffmpeg, diagnoser, config.model), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
