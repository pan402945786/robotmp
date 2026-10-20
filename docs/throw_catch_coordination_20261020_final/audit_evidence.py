"""Recompute detailed probe peaks and actuator limits from saved CSV files."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
audits = []
for report in summary["repeats"]:
    with (ROOT / f"{report['label']}_physics.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    swing = [row for row in rows if row["phase"] == "swing"]
    peak = max(float(row["vz"]) for row in swing)
    checks = {
        "peak_matches_report": abs(peak-report["peak_vz_m_s"]) < 1e-9,
        "all_recorded_ticks_have_grasp_constraint": all(row["constraint"] == "True" for row in rows),
        "no_recorded_ground_contact": all(row["ground_contact"] == "False" for row in rows),
        "recorded_joint_speeds_within_tolerance": all(
            abs(float(row[f"qd{i}"])) <= summary["limits"]["velocity"][i]*1.05 for row in rows for i in range(6)),
        "recorded_motor_torques_within_limits": all(
            abs(float(row[f"tau{i}"])) <= summary["limits"]["effort"][i]*1.001 for row in rows for i in range(6)),
        "recorded_joint_positions_within_limits": all(
            summary["limits"]["lower"][i]-.001 <= float(row[f"q{i}"]) <= summary["limits"]["upper"][i]+.001
            for row in rows for i in range(6)),
        "no_release_or_complete_task_claim": not report["released"] and not summary["goal_achieved"],
    }
    audits.append({"label":report["label"],"rows":len(rows),"peak_vz_m_s":peak,
                   "checks":checks,"passed":all(checks.values())})
result = {"passed":all(a["passed"] for a in audits),"traces":audits,
          "scope":"CSV audit of recorded ticks; self-penetration checks are in trial reports and not independently recomputed here"}
(ROOT / "independent_audit.json").write_text(json.dumps(result, indent=2)+"\n",encoding="utf-8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["passed"] else 1)
