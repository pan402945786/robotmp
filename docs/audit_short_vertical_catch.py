"""Independently recompute final catch evidence from saved forces and physical CSV."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from robotmp.catch_online_control import RobotModel

OUT=ROOT/"docs/short_vertical_catch_20261020_final"


def audit(output=OUT):
    model=RobotModel()
    try:
        infos=[model.p.getJointInfo(model.arm,j,physicsClientId=model.client) for j in model.joints]
        lower=np.array([i[8] for i in infos]);upper=np.array([i[9] for i in infos])
        vmax=np.array([i[11] for i in infos]);effort=np.array([i[10] for i in infos])
    finally:
        model.close()
    rows=[]
    for path in sorted(output.glob("validated_[0-9][0-9].json")):
        r=json.loads(path.read_text())
        label=r["label"]
        sources=[path]+[output/f"{label}_{suffix}" for suffix in
            ("control_trace.json","observations.json","decisions.json","physics.csv")]
        trace=json.loads(sources[1].read_text());obs=json.loads(sources[2].read_text());decisions=json.loads(sources[3].read_text())
        with sources[4].open() as stream:
            physics=list(csv.DictReader(stream))
        flight=[row for row in physics if row["phase"]=="flight"]
        assert len(flight)==len(trace)
        csv_error=max(np.linalg.norm(np.array([float(p[k]) for k in ("x","y","z")])-t["cube"])
                      for p,t in zip(flight,trace))
        captured=r.get("capture_contact_time_s")
        held=[t for t in trace if captured is not None and t["time_s"]>=captured-1e-8]
        def bilateral(t):
            links={f["link"] for f in t["contact_forces"] if f["normal_force_n"]>.05}
            return {9,12}.issubset(links) and t["collision_enabled"]
        all_held=bool(held and all(bilateral(t) for t in held))
        duration=held[-1]["time_s"]-held[0]["time_s"] if held else 0.
        no_constraint=all(p["constraint"]=="False" for p in flight)
        speed=float(np.linalg.norm(trace[-1]["truth_velocity"]))
        q=np.array([[float(p[f"q{i}"]) for i in range(6)] for p in physics])
        qd=np.array([[float(p[f"qd{i}"]) for i in range(6)] for p in physics])
        tau=np.array([[float(p[f"tau{i}"]) for i in range(6)] for p in physics])
        motion=bool(np.all(q>=lower-.001) and np.all(q<=upper+.001)
                    and np.max(np.abs(qd)/vmax)<=1.05 and np.max(np.abs(tau)/effort)<=1.001
                    and not r["self_penetration_detected"])
        causal=bool(len(obs)>=4 and decisions and
            all(o["captured_at"]<=o["delivered_at"]+1e-8 and o["delivered_at"]<=o["received_at"]+1e-8 for o in obs) and
            all(d["latest_observation_at"]<=d["issued_at"]+1e-8 for d in decisions))
        separation=bool(r["collision_clearance_at_enable_m"]>=.015 and
            r["collision_reenabled_at_s"]+1/240<r["first_robot_contact_time_s"])
        initial=bool(r["initial_grasp_evidence"]["verified"] and
            r["initial_grasp_evidence"]["consecutive_contact_ticks"]>=12 and
            r["pre_release_grasp_checks"]["passed"] and r["pre_release_grasp_checks"]["max_positive_gap_m"]<=.002)
        passed=bool(initial and causal and motion and separation and no_constraint and all_held and duration>=1.
                    and speed<.05 and csv_error<1e-9 and not r["ground_contact"] and trace[-1]["cube"][2]>.2)
        rows.append(dict(label=label,passed=passed,source_success=r["complete_success"],
            physical_hold_duration_s=duration,all_hold_frames_have_opposed_contact_forces=all_held,
            final_speed_m_s=speed,no_object_constraint_after_release=no_constraint,
            initial_grasp_verified=initial,causal=causal,motion=motion,separation=separation,
            measured_rise_m=r["apex_height_m"]-r["release_position"][2],
            prethrow_max_gap_m=r["pre_release_grasp_checks"]["max_positive_gap_m"],
            prethrow_max_penetration_m=r["pre_release_grasp_checks"]["max_penetration_m"],
            max_joint_speed_ratio=float(np.max(np.abs(qd)/vmax)),csv_trace_position_error_m=float(csv_error),
            scenario=r["scenario"],source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}))
    source_paths=[ROOT/"robotmp"/n for n in ("sim_environment.py","throw_catch_coordination.py","vertical_toss.py",
                                           "catch_online_control.py","throw_catch_online.py")]
    result=dict(trials=len(rows),independent_passes=sum(r["passed"] for r in rows),
        min_hold_s=min(r["physical_hold_duration_s"] for r in rows),
        max_final_speed_m_s=max(r["final_speed_m_s"] for r in rows),
        min_rise_m=min(r["measured_rise_m"] for r in rows),max_rise_m=max(r["measured_rise_m"] for r in rows),
        max_prethrow_gap_m=max(r["prethrow_max_gap_m"] for r in rows),
        max_prethrow_penetration_m=max(r["prethrow_max_penetration_m"] for r in rows),
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        scope="Saved-evidence audit. Opposed forces, uninterrupted hold, physical CSV consistency, arm limits, "
              "timestamps and absence of object constraints are recomputed. Self-contact diagnosis uses the saved model check.",
        records=rows)
    (output/"audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("records","source_sha256")}))
    if not rows or result["independent_passes"]!=len(rows):
        raise RuntimeError("a final catch did not pass independent audit")
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=OUT)
    audit(parser.parse_args().output)
