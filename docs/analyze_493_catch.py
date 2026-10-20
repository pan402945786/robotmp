"""Offline diagnosis of the original 493 recording (never changes its data)."""
from pathlib import Path
import csv
import json
import math
import sys

import numpy as np
import pybullet as p
import pybullet_data
from PIL import Image, ImageDraw
import imageio_ffmpeg
import subprocess

root = Path(__file__).resolve().parents[1]
source = root / "docs/throw_catch_493_video_20261020"
out = root / "docs/throw_catch_493_recovery_20261020"
out.mkdir(exist_ok=True)
summary = json.loads((source / "full_493_summary.json").read_text())
rows = list(csv.DictReader((source / "full_493_physics.csv").open()))
client = p.connect(p.DIRECT)
p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=client)
arm = p.loadURDF("xarm/xarm6_with_gripper.urdf", [.1, 0, .7], useFixedBase=True, physicsClientId=client)
stats = []
prev_ee = None
prev_time = None
for row in rows:
    for joint in range(1, 7):
        p.resetJointState(arm, joint, float(row[f"q{joint-1}"]), physicsClientId=client)
    ee = np.array(p.getLinkState(arm, 6, computeForwardKinematics=True, physicsClientId=client)[4])
    t = float(row["t_s"])
    vel = np.array([float(row[k]) for k in ("vx", "vy", "vz")])
    pos = np.array([float(row[k]) for k in ("x", "y", "z")])
    if row["phase"] == "flight":
        ee_v = (ee - prev_ee) / (t - prev_time)
        stats.append(dict(t_s=t, after_release_s=t-summary["release_time_s"],
                          cube=pos.tolist(), velocity=vel.tolist(), ee=ee.tolist(),
                          ee_velocity=ee_v.tolist(), distance_m=float(np.linalg.norm(pos-ee)),
                          relative_speed_m_s=float(np.linalg.norm(vel-ee_v)),
                          clearance_m=float(ee[2]-pos[2]),
                          ground_contact=row["ground_contact"] == "True"))
    prev_ee, prev_time = ee, t
p.disconnect(client)
descending = [r for r in stats if r["velocity"][2] < -.05 and not r["ground_contact"]]
nearest = min(descending, key=lambda r:r["distance_m"])
within = [r for r in descending if r["distance_m"] <= .13]
result = dict(source=str(source), nearest_descending=nearest,
              samples_within_13cm=len(within),
              best_relative_speed_within_13cm=min((r["relative_speed_m_s"] for r in within), default=None),
              snapshots=[min(stats, key=lambda r:abs(r["after_release_s"]-t)) for t in (.0,.25,.5,.75,.9,1.,1.1,1.2)],
              flight=stats)
(out / "baseline_diagnosis.json").write_text(json.dumps(result, indent=2)+"\n")
print(json.dumps({k:v for k,v in result.items() if k != "flight"}, indent=2))
# Extract selected real video frames into one reviewable contact sheet.
canvas = Image.new("RGB", (1280, 3*384), "white")
draw = ImageDraw.Draw(canvas)
for i, sec in enumerate((14.4,14.6,14.9,15.1,15.3,15.5)):
    target = out / f"original_{sec:.1f}.png"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-ss", str(sec),
                    "-i", str(source/"xarm6_throw_493.mp4"), "-frames:v", "1", str(target)], check=True)
    im = Image.open(target).convert("RGB").resize((640,360))
    x,y=(i%2)*640,(i//2)*384
    canvas.paste(im,(x,y))
    draw.text((x+8,y+363), f"Original video {sec:.1f}s", fill="black")
canvas.save(out/"original_contact_sheet.png")
