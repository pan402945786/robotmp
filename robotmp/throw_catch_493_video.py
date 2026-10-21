"""Run the 4.93 m/s launch end-to-end and record the real PyBullet scene."""
from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from pathlib import Path

from .throw_catch_coordination import trial
from .throw_catch_spin import POSES, DELAYS
from .sim_environment import _require_pybullet


RELEASE_GATE = 4.90
MASS_KG = 0.10
LEAD_S = 0.35
DELAYS_493 = DELAYS["best_coordination"]
SPIN_493 = {"turns": 1.5, "joints": [0], "directions": [1]}


def camera_matrices(p):
    """Keep the arm and the complete measured flight inside the scene panel."""
    view = p.computeViewMatrixFromYawPitchRoll([0.05, 0.12, 1.25], 3.5, 48, -15, 0, 2)
    projection = p.computeProjectionMatrixFOV(48, 960 / 720, 0.02, 10)
    return view, projection


class Recorder:
    def __init__(self, output: Path, fps: int = 30, *, title="xArm6 4.93 m/s 完整抛接实验",
                 subtitle=None, release_gate=RELEASE_GATE,grasp_detail=False):
        self.output = output
        self.fps = fps
        self.next_frame_time = -1e-9
        self.frames = 0
        self.process = None
        self.error = None
        self.title = title
        self.subtitle = subtitle
        self.release_gate = release_gate
        self.grasp_detail=grasp_detail
        self._start_video()

    def _start_video(self):
        import imageio_ffmpeg
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.log = self.output.with_suffix(".ffmpeg.log").open("w", encoding="utf-8")
        self.process = subprocess.Popen([
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo",
            "-pix_fmt", "rgb24", "-s", "1280x720", "-r", str(self.fps), "-i", "-",
            "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "19", "-pix_fmt",
            "yuv420p", "-movflags", "+faststart", str(self.output)],
            stdin=subprocess.PIPE, stderr=self.log)

    def capture(self, env, report, phase,*,force=False):
        if self.process is None or (not force and env._time + 1e-8 < self.next_frame_time):
            return
        from PIL import Image, ImageDraw, ImageFont
        p = env.p
        # Frame the entire measured 0--2.33 m flight, with room above the apex.
        # The previous close-up clipped the cube immediately after release.
        view, projection = camera_matrices(p)
        _, _, rgba, _, _ = p.getCameraImage(960, 720, view, projection,
            renderer=p.ER_TINY_RENDERER, physicsClientId=env.client)
        frame = Image.new("RGB", (1280, 720), "#0b1524")
        frame.paste(Image.fromarray(rgba[:, :, :3]), (0, 0))
        draw = ImageDraw.Draw(frame)
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 19)
        title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
        if self.grasp_detail:
            center=env._cube_position()
            detail_view=p.computeViewMatrixFromYawPitchRoll(center,.42,65,-18,0,2)
            detail_projection=p.computeProjectionMatrixFOV(48,420/280,.005,5)
            _,_,detail,_,_=p.getCameraImage(420,280,detail_view,detail_projection,
                renderer=p.ER_TINY_RENDERER,physicsClientId=env.client)
            frame.paste(Image.fromarray(detail[:,:,:3]),(20,420))
            draw.rectangle((20,420,440,450),fill="#0b1524")
            draw.text((30,423),"实时夹持局部 · 实际物理场景",font=font,fill="#68e6ff")
        draw.rectangle((0, 0, 960, 72), fill="#0b1524")
        draw.text((18, 10), self.title, font=title, fill="#68e6ff")
        draw.text((18, 45), self.subtitle or f"PyBullet | t={env._time:.2f}s | 100 g | 1.5圈底座预转 + 肩肘腕上挥", font=font, fill="white")
        pos, _ = p.getBasePositionAndOrientation(env._cube_id, physicsClientId=env.client)
        vel, _ = p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        rows = [
            ("阶段", phase, "#eaf2fb"),
            ("物体高度", f"{pos[2]:.3f} m", "#68e6b2"),
            ("竖直速度", f"{vel[2]:+.3f} m/s", "#ffc478"),
            ("总速度", f"{math.dist(vel, [0,0,0]):.3f} m/s", "#ffc478"),
            ("抓持约束", "有" if env._constraint_id is not None else "无", "#68e6b2" if env._constraint_id is not None else "#ff8490"),
            ("释放门槛", f"{self.release_gate:.2f} m/s", "#bda8ff"),
            ("峰值记录", f"{report.get('peak_vz_m_s', 0):.3f} m/s", "#68e6b2"),
            ("飞行升高", f"{report.get('measured_rise_m', 0):.3f} m", "#68e6b2"),
            ("已接回", "是" if report.get("caught") else "等待", "#68e6b2" if report.get("caught") else "#ffc478"),
            ("放置", "通过" if report.get("placement", {}).get("passed") else "等待", "#68e6b2" if report.get("placement", {}).get("passed") else "#ffc478"),
        ]
        draw.rectangle((960, 0, 1280, 720), fill="#111e30")
        y = 22
        for label, value, color in rows:
            draw.text((980, y), label, font=font, fill="#8fa4be")
            draw.text((980, y + 23), value, font=font, fill=color)
            y += 66
        self.last_frame=frame
        self.last_raw=frame.tobytes()
        self.process.stdin.write(self.last_raw)
        self.frames += 1
        self.next_frame_time = env._time + 1.0 / self.fps

    def freeze_last(self,seconds=1.):
        for _ in range(round(seconds*self.fps)):
            self.process.stdin.write(self.last_raw)
            self.frames+=1

    def close(self):
        if self.process is None:
            return
        try:
            self.process.stdin.close()
            code = self.process.wait()
            if code:
                raise RuntimeError(f"ffmpeg exited with {code}")
        finally:
            self.log.close()
            self.process = None


def continue_after_release(env, report, sample, offset, recorder):
    """Track the released cube, catch on descent, lower, release and settle."""
    p = env.p
    pos0 = list(report["release_position"])
    apex = pos0[2]
    had_apex = False
    contact = False
    previous_ee = env._actual_ee_position()
    ee0 = list(previous_ee)
    v0 = list(report["release_velocity"])
    # Choose a descending intercept near the release height.  The target is
    # planned once, then approached smoothly; per-tick ballistic chasing made
    # IK targets jump and produced artificial joint-speed spikes.
    catch_time = 1.03
    catch_cube = [pos0[i] + v0[i] * catch_time for i in range(3)]
    catch_cube[2] = pos0[2] + v0[2] * catch_time - 0.5 * 9.81 * catch_time * catch_time
    ee_delta = [ee0[i] - pos0[i] for i in range(3)]
    catch_ee = [catch_cube[i] + ee_delta[i] for i in range(3)]
    catch_ee[2] += 0.05
    caught = False
    for tick in range(600):
        pos, _ = p.getBasePositionAndOrientation(env._cube_id, physicsClientId=env.client)
        vel, _ = p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        apex = max(apex, pos[2])
        if vel[2] <= 0:
            had_apex = True
        ee = env._actual_ee_position()
        ee_velocity = [(a-b) / env.config.time_step_s for a, b in zip(ee, previous_ee)]
        previous_ee = ee
        # Track the horizontal ballistic intercept while holding the wrist at
        # the release height.  Chasing z would drive the wrist toward the
        # falling cube and prevents the required finger clearance.
        alpha = min(1., (tick + 1) / 180.)
        target = [ee0[i] + alpha * (catch_ee[i] - ee0[i]) for i in range(3)]
        env._set_gripper_pose(target, open_gripper=True)
        env._step(1)
        contacts = p.getContactPoints(env._cube_id, env.ground, physicsClientId=env.client)
        contact |= bool(contacts)
        pos, vel, _ = sample("flight", tick)
        distance = math.dist(pos, env._actual_ee_position())
        relative_speed = math.dist(vel, ee_velocity)
        if (had_apex and tick >= 10 and not contact and vel[2] < -0.05
                and distance <= 0.13 and relative_speed <= 1.0
                and env._actual_ee_position()[2] - pos[2] >= 0.10):
            env._gripper_open = False
            env._gripper_force = 1.0
            env._set_gripper_pose(env._actual_ee_position(), open_gripper=False)
            env._create_grasp_constraint()
            env._grasped = True
            env._phase = "catch"
            report.update(caught=True, catch_time_s=env._time,
                          catch_distance_m=distance, catch_relative_speed_m_s=relative_speed)
            caught = True
            break
        if contact:
            break
    report.update(apex_height_m=apex, measured_rise_m=apex-pos0[2],
                  had_apex=had_apex, free_flight=True, flight_contact=contact)
    if not caught:
        report["continuation_error"] = "descending catch gate not reached"
        return

    # Hold the caught object briefly, then lower it using measured object/EE offset.
    env._phase = "hold"
    env._step(120)
    current = list(env._cube_position())
    support_z = 0.05
    for i in range(240):
        pos = env._cube_position()
        ee = env._actual_ee_position()
        target_z = max(support_z + 0.004, pos[2] - 0.004)
        target = [ee[0] + pos[0] - ee[0], ee[1] + pos[1] - ee[1], ee[2] + target_z - pos[2]]
        env._phase = "place"
        env._set_gripper_pose(target, open_gripper=False)
        env._step(2)
        if p.getContactPoints(env._cube_id, env.ground, physicsClientId=env.client):
            break
    env._phase = "placement_settle"
    linear, angular = p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
    before = env._cube_position()
    env.release_in_motion()
    env._step(480)
    after = env._cube_position()
    linear, angular = p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
    placement = {"released": env._constraint_id is None and not env._grasped,
                 "ground_contact": bool(p.getContactPoints(env._cube_id, env.ground, physicsClientId=env.client)),
                 "drift_m": math.dist(before, after), "speed_m_s": math.dist(linear, [0,0,0]),
                 "angular_speed_rad_s": math.dist(angular, [0,0,0]),
                 "height_error_m": abs(after[2] - 0.05)}
    placement["passed"] = bool(placement["released"] and placement["ground_contact"]
                                and placement["drift_m"] <= .01 and placement["speed_m_s"] <= .03
                                and placement["angular_speed_rad_s"] <= .1 and placement["height_error_m"] <= .01)
    report["placement"] = placement
    env._phase = "result"


def run(output: Path, fps: int):
    output.mkdir(parents=True, exist_ok=True)
    recorder = Recorder(output / "xarm6_throw_493.mp4", fps)
    latest = {"report": {}}

    def observer(env, phase, tick):
        recorder.capture(env, latest["report"], phase)

    def release_handler(env, report, sample, offset):
        latest["report"] = report
        continue_after_release(env, report, sample, offset, recorder)

    try:
        report = trial(POSES["best_coordination"], MASS_KG, LEAD_S, DELAYS_493,
            output=output, label="full_493", spin=SPIN_493, observer=observer,
            release_threshold=RELEASE_GATE, release_handler=release_handler)
        latest["report"] = report
        recorder.capture(env=None, report=report, phase="result") if False else None
    finally:
        recorder.close()
    report["video"] = str((output / "xarm6_throw_493.mp4").resolve())
    report["video_frames"] = recorder.frames
    report["strategy"] = {"release_gate_m_s": RELEASE_GATE, "mass_kg": MASS_KG,
                           "spin": SPIN_493, "lead_s": LEAD_S, "delays_s": DELAYS_493}
    (output / "full_493_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/throw_catch_493_video_20261020"))
    parser.add_argument("--fps", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.fps <= 60:
        parser.error("--fps must be between 1 and 60")
    _require_pybullet()
    print(json.dumps(run(args.output, args.fps), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
