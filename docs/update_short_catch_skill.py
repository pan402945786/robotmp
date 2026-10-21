"""Save failed-attempt lessons and the audited, explicitly scoped catch skill."""
from copy import deepcopy
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/short_vertical_catch_20261020_final"


def main():
    audit=json.loads((OUT/"audit.json").read_text())
    if audit["trials"]!=20 or audit["independent_passes"]!=20:
        raise RuntimeError("scoped skill requires all twenty independent audits")
    summary=json.loads((OUT/"summary.json").read_text())
    path=ROOT/"assets/skills/causal_throw_catch_candidate.json"
    skills=json.loads(path.read_text())
    skill=skills[0]
    skill["version"]=25
    roots=list((ROOT/"docs").glob("catch_after_grasp_fix_20261020_*"))+[
        ROOT/"docs/prethrow_grasp_fix_20261020",ROOT/"docs/short_vertical_catch_20261020",OUT]
    reports=[]
    for folder in roots:
        for file in folder.glob("*.json"):
            r=json.loads(file.read_text(encoding="utf-8"))
            if isinstance(r,dict) and "released" in r and r.get("cube_size_m")==.05:
                reports.append(r)
    skill["validation_trials"]=76+len(reports)
    skill["validation_success_rate"]=None  # Conditions and acceptance rules changed during diagnosis.
    skill["parameters"].update(summary["parameters"])
    skill["parameters"].pop("require_initial_bilateral_contact",None)
    skill["parameters"].pop("pre_release_max_finger_gap_m",None)
    skill["parameters"]["launch_profile"]=dict(release_gate=1.45,pre_spin=False,release_inward_only=False,
        vertical_toss=dict(duration_s=.28,speed_m_s=1.8,x_m=.55,start_z_m=1.12,travel_m=.23))
    facts=["short_vertical_launch_reduces_lateral_drift_and_return_speed",
        "wait_for_observed_separation_before_descent_triggered_closure",
        "6cm_center_separation_is_a_policy_gate_collision_restoration_still_uses_15mm_surface_clearance",
        "continuous_full_close_after_contact_can_rotate_fingers_and_eject_the_cube",
        "retain_measured_contact_finger_angles_with_small_preload_and_reduced_hold_torque",
        "one_second_hold_requires_uninterrupted_opposed_contact_and_final_speed_below_005m_s",
        "short_vertical_catch_passed_20_of_20_scoped_simulation_trials_after_grasp_fix",
        "short_throw_success_does_not_verify_high_throw_visual_perception_or_hardware"]
    skill["facts"].extend(f for f in facts if f not in skill["facts"])
    for correction in ("recompute_launch_from_measured_grasp_offset_and_robot_model",
                       "choose_closure_from_delivered_descent_observations_not_fixed_flight_time"):
        if correction not in skill["prediction_correction"]:
            skill["prediction_correction"].append(correction)
    metrics=skill["validation_metrics"]
    metrics.update(complete_success=True,post_grasp_fix_recorded_attempts=len(reports),
        physical_capture_trials=sum(bool(r.get("physical_capture")) for r in reports),
        causal_trials=69+sum(bool(r.get("causality_passed")) for r in reports),
        motion_valid_causal_trials=62+sum(bool(r.get("causality_passed") and r.get("motion_checks_passed")) for r in reports),
        post_grasp_fix_serialization_aborts=1,post_grasp_fix_reported_successes=sum(r.get("complete_success",False) for r in reports),
        short_vertical_final_trials=20,short_vertical_final_successes=20,
        short_vertical_min_hold_s=audit["min_hold_s"],short_vertical_max_final_speed_m_s=audit["max_final_speed_m_s"],
        last_trial="validated_20",last_observation_count=summary["reports"][-1]["position_observations"],
        complete_success_scope="50mm short vertical throw only; general/high throw remains candidate")
    path.write_text(json.dumps(skills,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"general_skill_v25.json").write_text(json.dumps(skill,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    scoped=deepcopy(skill)
    scoped.update(skill_id="short_vertical_throw_catch_50mm_v1",name="contact_checked_short_vertical_throw_catch_50mm",
        task="short_vertical_throw_catch_50mm",status="verified",version=1,validation_trials=20,
        validation_success_rate=1.,false_success_rate=0.,recovery_success_rate=None,
        trigger_conditions=["PyBullet xarm6_with_gripper model", "cube_edge_m == 0.05",
            "mass_kg in tested 0.08/0.10/0.12 cases", "initial_bilateral_contact_verified",
            "pre_release_finger_geometry_passed", "fresh timestamped position observations at 60Hz",
            "short vertical launch profile with stationary return near release point"],
        validation_metrics=dict(complete_success=True,independent_audit_passes=20,
            minimum_uninterrupted_hold_s=audit["min_hold_s"],max_final_speed_m_s=audit["max_final_speed_m_s"],
            min_rise_m=audit["min_rise_m"],max_rise_m=audit["max_rise_m"],uses_offline_flight=False,
            catch_uses_object_constraint=False,initial_acquisition_uses_contact_checked_fixed_hold=True,
            max_observation_noise_m=.002,max_latency_s=2/60,max_drop_rate=.1,
            evidence="docs/short_vertical_catch_20261020_final/audit.json",
            scope="twenty discrete simulation cases; no claim about all parameter combinations, high throws or hardware"))
    scoped["hypotheses"]=["larger vertical launches require separate validation"]
    (ROOT/"assets/skills/short_vertical_throw_catch_50mm.json").write_text(
        json.dumps([scoped],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"verified_skill.json").write_text(json.dumps(scoped,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(general_version=25,general_status=skill["status"],scoped_status=scoped["status"],
                         final_successes=20,recorded_postfix_attempts=len(reports))))


if __name__=="__main__":
    main()
