"""Post-experiment audit and skill review. Never imported by the controller."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from .catch_gripper_geometry import measure_opening
from .catch_online_control import RobotModel
from .skills import SkillStore
from .throw_catch_online import ROOT,SKILL_PATH,save_json


def audit(output):
    rows=[]
    for folder in sorted({path.parent for path in (ROOT/"docs").glob("*/online_[0-9][0-9][0-9].json")}):
        for path in sorted(folder.glob("online_[0-9][0-9][0-9].json")):
            report=json.loads(path.read_text(encoding="utf-8"))
            label=report["label"]
            obs_file=folder/f"{label}_observations.json"
            decisions_file=folder/f"{label}_decisions.json"
            observations=json.loads(obs_file.read_text()) if obs_file.exists() else []
            decisions=json.loads(decisions_file.read_text()) if decisions_file.exists() else []
            contract=all(o["captured_at"]<=o["delivered_at"]+1e-8
                         and o["delivered_at"]<=o["received_at"]+1e-8 for o in observations)
            contract &= all(d["latest_observation_at"]<=d["issued_at"]+1e-8 for d in decisions)
            active=len(observations)>=4 and len(decisions)>0
            row=dict(label=label,report=str(path.relative_to(ROOT)),report_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                released=bool(report.get("released")),observations=len(observations),causal_contract=bool(contract),
                active_causal=bool(active and contract),motion_checks=report.get("motion_checks_passed"),
                captured=bool(report.get("physical_capture")),geometry_gate_blocked=bool(report.get("geometry_gate_blocked")),
                forecast_100ms_free_rmse_m=report.get("free_flight_forecast_100ms_rmse_m"),
                max_planner_wall_s=report.get("max_planner_wall_s"),planner_deadline_misses=report.get("planner_deadline_misses"),
                latency_s=report.get("scenario",{}).get("latency_s"),noise_m=report.get("scenario",{}).get("noise_m"),
                source_causality_field=report.get("causality_passed"))
            rows.append(row)
    model=RobotModel()
    try:
        geometry=measure_opening(model)
    finally:
        model.close()
    result=dict(scope="posthoc evidence audit only; no trajectory is fed back as an intercept target",
        attempts=len(rows),released_attempts=sum(r["released"] for r in rows),
        active_causal_trials=sum(r["active_causal"] for r in rows),
        motion_valid_causal_trials=sum(bool(r["active_causal"] and r["motion_checks"]) for r in rows),
        physical_capture_trials=sum(r["captured"] for r in rows),
        zero_observation_attempts=sum(r["observations"]==0 for r in rows),
        geometry=geometry,trials=rows)
    output.mkdir(parents=True,exist_ok=True)
    save_json(output/"audit.json",result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"docs/throw_catch_online_audit_20261020")
    parser.add_argument("--update-skill",action="store_true")
    args=parser.parse_args()
    result=audit(args.output)
    if args.update_skill:
        store=SkillStore(SKILL_PATH)
        skill=store.all()[0]
        skill.version+=1
        skill.task="online_throw_catch"
        skill.status="candidate"
        skill.parameters.update(require_centered_grasp_fit=True,handoff_brake_s=.35)
        if "centered_grasp_geometry_fit == true" not in skill.trigger_conditions:
            skill.trigger_conditions.append("centered_grasp_geometry_fit == true")
        for fact in ("measured_center_grasp_gap_86_9mm_is_smaller_than_the_100mm_cube",
                     "100mm_centered_box_penetrates_both_open_fingers_80mm_box_clears",
                     "geometry_fit_is_a_prerequisite_for_the_centered_parallel_grasp_policy",
                     "contact_impulses_must_not_be_learned_as_air_drag",
                     "quadratic_acceleration_and_velocity_must_use_the_same_window_time",
                     "floating_point_timestamp_audits_require_separate_tolerance_checks",
                     "zero_observation_aborts_do_not_validate_causal_interception"):
            if fact not in skill.facts:
                skill.facts.append(fact)
        old="position_history_requires_online_drag_estimation"
        if old in skill.facts:
            skill.facts.remove(old)
        if "assess_drag_using_free_flight_forecasts_before_contact" not in skill.prediction_correction:
            skill.prediction_correction.append("assess_drag_using_free_flight_forecasts_before_contact")
        skill.validation_metrics.update(causal_trials=result["active_causal_trials"],
            physical_capture_trials=result["physical_capture_trials"],
            motion_valid_causal_trials=result["motion_valid_causal_trials"],
            centered_grasp_fit=False,complete_success=False,uses_offline_flight=False)
        store.save_candidate(skill)
        save_json(args.output/"skill_review.json",asdict(skill))
    print(json.dumps({key:value for key,value in result.items() if key not in ("geometry","trials")},ensure_ascii=False))


if __name__=="__main__":
    main()
