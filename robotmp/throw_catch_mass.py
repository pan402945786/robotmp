"""Reproducible mass-only comparison and bounded two-metre capability search.

No model calls or automatic commits. A passed release gate alone is not a
completed throw/catch/placement skill.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import tempfile

from .throw_catch_2m import REQUIRED_VZ, TARGET_RISE_M, run_gate_trial

MASSES_KG = (0.10, 0.05, 0.02, 0.01, 0.005, 0.001, 0.0001)
BASE_PARAMETERS = {"target_x_m": 0.35, "target_z_m": 1.10, "release_after_steps": 72}


class ProbeAudit:
    def __init__(self, output):
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)

    def event(self, event):
        # run_gate_trial saves the complete events and its compact physics CSV.
        pass


def compact(report):
    keys = ("trial", "cube_mass_kg", "parameters", "max_measured_vz_m_s",
            "final_measured_vz_m_s", "max_joint_velocity_ratios", "lifted",
            "release_permitted", "released", "release_vz_m_s", "constraint_retained",
            "safety_stop", "error")
    result = {key: report[key] for key in keys if key in report}
    speed = report.get("max_measured_vz_m_s", 0.0)
    result["ideal_vacuum_rise_from_peak_speed_m"] = max(0.0, speed) ** 2 / (2 * 9.81)
    result["joint_speed_limits_passed"] = max(report.get("max_joint_velocity_ratios", [math.inf])) <= 1.05
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/throw_catch_mass_20261020"))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--skip-search", action="store_true")
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    if (output / "summary.json").exists():
        parser.error("output already contains a summary; choose a fresh directory")
    comparison = []
    for mass in MASSES_KG:
        audit = ProbeAudit(output / f"mass_{mass:g}kg")
        trials = [compact(run_gate_trial(i, BASE_PARAMETERS, audit, cube_mass_kg=mass))
                  for i in range(1, args.repeats + 1)]
        comparison.extend(trials)
        print(json.dumps({"mass_g": mass * 1000,
                          "peak_vz_m_s": [r.get("max_measured_vz_m_s") for r in trials],
                          "released": any(r.get("released") for r in trials)}, ensure_ascii=False), flush=True)
    search = []
    if not args.skip_search:
        # Preserve the existing bounded single-target IK primitive and URDF limits.
        # Save the exhaustive compact table, then detailed repeats of the best case.
        with tempfile.TemporaryDirectory(prefix="robotmp_mass_search_") as temporary:
            audit = ProbeAudit(temporary)
            for mass in MASSES_KG:
                for x in (0.20, 0.30, 0.35, 0.45, 0.60):
                    for z in (1.05, 1.10, 1.35, 1.60, 1.90):
                        parameters = {"target_x_m": x, "target_z_m": z, "release_after_steps": 120}
                        search.append(compact(run_gate_trial(1, parameters, audit, cube_mass_kg=mass)))
                best = max((r for r in search if r["cube_mass_kg"] == mass),
                           key=lambda r: r.get("max_measured_vz_m_s", -math.inf))
                print(json.dumps({"search_mass_g": mass * 1000, "best": best}, ensure_ascii=False), flush=True)
    candidates = [r for r in comparison + search if "error" not in r]
    best = max(candidates, key=lambda r: r.get("max_measured_vz_m_s", -math.inf))
    best_trials = [compact(run_gate_trial(i, best["parameters"], ProbeAudit(output / "best_repeated"),
                                        cube_mass_kg=best["cube_mass_kg"]))
                   for i in range(1, args.repeats + 1)]
    summary = {
        "local_time": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "target_rise_m": TARGET_RISE_M, "required_vz_m_s": REQUIRED_VZ,
        "baseline_mass_kg": 0.10, "mass_comparison_parameters": BASE_PARAMETERS,
        "mass_comparison": comparison, "bounded_search": search,
        "best": best, "best_repeated": best_trials,
        "release_gate_reached": any(r.get("released", False) for r in comparison + search),
        "goal_achieved": False,
        "scope": "Single-target xArm6 POSITION_CONTROL, fixed grasp, robot-cube collision disabled; "
                 "same cube dimensions, gravity, URDF limits, controller and damping across masses. "
                 "The ideal rise column is a peak-speed estimate, not measured free flight. "
                 "No full task or verified skill is claimed by a capability probe.",
    }
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        fields = ["phase", "cube_mass_kg", "trial", "target_x_m", "target_z_m", "release_after_steps",
                  "max_measured_vz_m_s", "ideal_vacuum_rise_from_peak_speed_m", "released", "joint_speed_limits_passed"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for phase, reports in (("mass_only", comparison), ("bounded_search", search), ("best_repeated", best_trials)):
            for report in reports:
                row = {key: report.get(key, "") for key in fields}
                row.update(report["parameters"])
                row["phase"] = phase
                writer.writerow(row)
    print(json.dumps({"best": best, "release_gate_reached": summary["release_gate_reached"],
                      "summary": str(output / "summary.json")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
