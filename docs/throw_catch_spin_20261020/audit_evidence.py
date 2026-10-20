"""Independently audit recorded velocities, limits, angle continuity and loops."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
loops = json.loads((ROOT / "loop_summary.json").read_text(encoding="utf-8"))
coordinated = json.loads((ROOT / "coordinated_loop_summary.json").read_text(encoding="utf-8"))
limits = json.loads((ROOT.parent / "throw_catch_coordination_20261020_final/summary.json").read_text(encoding="utf-8"))["limits"]
audits = []
reports = summary["matched_baselines"] + summary["repeats"] + [summary["long_spin"]] + loops["traces"] + coordinated["traces"]
for report in reports:
    with (ROOT / f"{report['label']}_physics.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    moving = [r for r in rows if r["phase"] in ("spin", "swing")]
    peak_row = max(moving, key=lambda r: float(r["vz"]))
    peak = float(peak_row["vz"])
    max_delta_error = max(abs((float(b[f"q{i}"])-float(a[f"q{i}"])) /
        (float(b["t_s"])-float(a["t_s"])) - float(b[f"qd{i}"]))
        for a, b in zip(rows, rows[1:]) for i in range(6))
    checks = {
        "peak_matches_report": abs(peak-report["peak_vz_m_s"]) < 1e-9,
        "constraint_held": all(r["constraint"] == "True" for r in rows),
        "no_ground_contact": all(r["ground_contact"] == "False" for r in rows),
        "joint_speeds_within_tolerance": all(abs(float(r[f"qd{i}"])) <= limits["velocity"][i]*1.05
                                             for r in rows for i in range(6)),
        "motor_torques_within_limits": all(abs(float(r[f"tau{i}"])) <= limits["effort"][i]*1.001
                                           for r in rows for i in range(6)),
        "joint_positions_within_limits": all(limits["lower"][i]-.001 <= float(r[f"q{i}"]) <= limits["upper"][i]+.001
                                              for r in rows for i in range(6)),
        "joint_increments_match_measured_velocity_no_wraps": max_delta_error < 1e-7,
        "peak_attachment_velocity_error_below_0_1": math.dist(
            [float(peak_row[k]) for k in ("vx", "vy", "vz")],
            [float(peak_row[k]) for k in ("point_vx", "point_vy", "point_vz")]) < .1,
        "no_release_or_full_task_claim": not report["released"] and not summary["goal_achieved"] and not loops["goal_achieved"],
    }
    extra = {}
    if "spin_plan" in report:
        for index, spec in report["spin_plan"]["joints"].items():
            i = int(index)
            trace = [r for r in rows if r["phase"] == "spin"]
            measured_turns = spec["direction"] * (float(trace[-1][f"q{i}"]) - report["prepared_q"][i]) / (2*math.pi)
            speeds = [m["joint_speed_rad_s"] for m in report["spin_milestones"] if m["joint"] == i+1]
            checks[f"J{i+1}_completed_turns"] = abs(measured_turns-report["spin_plan"]["turns"]) < .01
            checks[f"J{i+1}_accelerates_at_milestones"] = all(a < b for a, b in zip(speeds, speeds[1:]))
            extra[f"J{i+1}_measured_turns"] = measured_turns
    if "loop" in report:
        loop = report["loop"]
        trace = [r for r in rows if r["phase"] == "swing"]
        a1, a2 = loop["sine"][1:3]
        b1, b2 = loop["cosine"][1:3]
        determinant = a1*b2 - a2*b1
        angles = []
        for r in trace:
            y1, y2 = float(r["q1"])-loop["center"][1], float(r["q2"])-loop["center"][2]
            angles.append(math.atan2((y1*b2-y2*b1)/determinant, (a1*y2-a2*y1)/determinant))
        angle = sum(math.atan2(math.sin(b-a), math.cos(b-a)) for a,b in zip(angles,angles[1:]))
        measured_turns = angle / (2*math.pi)
        checks["actual_joint_cycles_match_requested"] = abs(measured_turns-loop["turns"]) < .02
        checks["all_cycle_milestones_recorded"] = len(report["cycle_milestones"]) == loop["turns"]
        if report["label"].startswith("vertical_"):
            checks["trajectory_in_vertical_plane"] = max(float(r["y"]) for r in trace)-min(float(r["y"]) for r in trace) < .005
        extra.update(measured_cycles=measured_turns,
                     vertical_span_m=max(float(r["z"]) for r in trace)-min(float(r["z"]) for r in trace),
                     horizontal_span_m=max(float(r["x"]) for r in trace)-min(float(r["x"]) for r in trace),
                     closure_error_m=math.dist([float(trace[0][k]) for k in ("x","y","z")],
                                               [float(trace[-1][k]) for k in ("x","y","z")]))
    audits.append(dict(label=report["label"], rows=len(rows), peak_vz_m_s=peak,
                       checks=checks, passed=all(checks.values()), **extra))
result = {"passed": all(a["passed"] for a in audits), "traces": audits,
          "scope": "Recorded-tick audit; self-penetration results come from online diagnostics, "
                   "not recomputed here. Original 5% speed and 0.1% effort tolerances retained."}
(ROOT / "independent_audit.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["passed"] else 1)
