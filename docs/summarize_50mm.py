"""Audit the 50 mm experiments without feeding recorded flights to control."""
from itertools import groupby
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/throw_catch_50mm_20261020_final"


def audit():
    rows = []
    for folder in sorted((ROOT / "docs").glob("throw_catch_50mm_20261020_*")):
        if folder.name.endswith("launch_probe"):
            continue  # Retained-grasp swing measurement, not a catch attempt.
        for path in sorted(folder.glob("*.json")):
            report = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(report, dict) or "label" not in report or "released" not in report:
                continue
            label = report["label"]
            def load(suffix):
                file = folder / f"{label}_{suffix}.json"
                return json.loads(file.read_text(encoding="utf-8")) if file.exists() else []
            trace, observations, decisions = load("control_trace"), load("observations"), load("decisions")
            bilateral = [bool({9, 12}.issubset(row["contacts"]) and row["collision_enabled"]) for row in trace]
            consecutive = max((sum(1 for _ in group) for hit, group in groupby(bilateral) if hit), default=0)
            causal = bool(len(observations) >= 4 and decisions and
                all(o["captured_at"] <= o["delivered_at"] + 1e-8 and
                    o["delivered_at"] <= o["received_at"] + 1e-8 for o in observations) and
                all(d["latest_observation_at"] <= d["issued_at"] + 1e-8 for d in decisions))
            first_contact = report.get("first_robot_contact_time_s")
            free = [row for row in trace if row["truth_velocity"][2] < -.05 and
                    row["collision_enabled"] and not row["contacts"] and
                    (first_contact is None or row["time_s"] < first_contact - 1e-8)]
            nearest = min(free, key=lambda row: row["distance_m"], default=None)
            rows.append(dict(label=label, report=path.relative_to(ROOT).as_posix(),
                report_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                cube_size_m=report["cube_size_m"], mass_kg=report["cube_mass_kg"],
                released=report["released"], causal=causal,
                motion_checks_passed=bool(report.get("motion_checks_passed")),
                complete_success=bool(report.get("complete_success")),
                bilateral_contact_ticks=sum(bilateral), longest_bilateral_contact_s=consecutive/240,
                closest_collision_enabled_precontact_m=nearest["distance_m"] if nearest else None,
                contact_brake_triggered=report.get("tactile_capture_time_s") is not None,
                error=report.get("error"), physical_capture=bool(report.get("physical_capture"))))
    source_paths = [ROOT / "robotmp" / name for name in
        ("throw_catch_online.py", "catch_online_control.py", "catch_gripper_geometry.py",
         "throw_catch_coordination.py", "sim_environment.py")]
    result = dict(attempts=len(rows), released=sum(r["released"] for r in rows),
        causal_trials=sum(r["causal"] for r in rows),
        motion_valid_causal_trials=sum(r["causal"] and r["motion_checks_passed"] for r in rows),
        trials_with_bilateral_contact=sum(r["bilateral_contact_ticks"] > 0 for r in rows),
        physical_capture_trials=sum(r["physical_capture"] for r in rows),
        complete_success_trials=sum(r["complete_success"] for r in rows),
        max_continuous_bilateral_contact_s=max(r["longest_bilateral_contact_s"] for r in rows),
        source_sha256={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
        scope="Posthoc audit. Tuning attempts are not independent success-rate validation. "
              "Early trials used earlier controller revisions; raw evidence is retained. "
              "Distances while collision was disabled are excluded from proximity ranking.",
        trials=rows)
    (OUT / "audit.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("trials", "source_sha256")},ensure_ascii=False))
    return result


if __name__ == "__main__":
    audit()
