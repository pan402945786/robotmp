"""Causal catch experiments: observe, predict, execute, reflect, update project skill."""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict
import json
import math
from pathlib import Path
import random
import subprocess

import numpy as np

from .catch_observation import PositionObservation
from .catch_online_control import OnlineCatchController, RobotModel
from .models import Skill
from .skills import SkillStore
from .throw_catch_coordination import command, trial
from .throw_catch_spin import POSES, DELAYS


ROOT=Path(__file__).resolve().parents[1]
SKILL_PATH=ROOT/"assets/skills/causal_throw_catch_candidate.json"
DEFAULT_OUTPUT=ROOT/"docs/throw_catch_online_20261020"


def initial_skill():
    return Skill(skill_id="causal_observation_catch_v1",name="causal_observation_catch",status="candidate",version=1,
        task="online_throw_catch",object_types=["cube"],
        trigger_conditions=["measured_lift", "fresh_timestamped_object_observations", "joint_encoder_observations"],
        facts=["offline_complete_flight_intercepts_are_not_realtime_catch_evidence",
               "current_sensor_is_simulated_position_observation_not_camera_perception",
               "intercept_uses_only_already_delivered_observations_and_robot_model",
               "finger_geometry_and_contact_are_required_for_capture_claims"],
        hypotheses=["receding_horizon_prediction_can_adapt_to_changed_flights"],
        prediction_correction=["estimate_velocity_from_timestamped_position_history",
            "extrapolate_from_capture_time_to_account_for_latency", "model_planning_wall_time_as_command_delay",
            "do_not_read_previous_flight_csv_or_intercept_endpoints"],
        recovery=["stop_tracking_if_observations_are_stale", "record_failed_attempt_before_retry",
                  "retain_candidate_status_until_contact_and_hold_validation"],
        prerequisite_skill_ids=["grasp_without_lift_v1"],
        parameters=dict(window_frames=10,estimate_drag=False,stale_s=.075,replan_s=.10,
                        ik_seeds=3,horizon_step_s=.06,tilt_weight=0.,time_hysteresis=0.,coast_s=.04,close_lead_s=.22),
        validation_metrics={"complete_success":False,"uses_offline_flight":False})


def save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def checkpoint(output,reason):
    paths=[Path("robotmp/catch_observation.py"),Path("robotmp/catch_online_control.py"),Path("robotmp/catch_gripper_geometry.py"),
           Path("robotmp/catch_online_audit.py"),
           Path("robotmp/throw_catch_493_video.py"),
           Path("robotmp/throw_catch_online.py"),Path("tests/test_catch_observation.py"),
           Path("tests/test_catch_online_control.py"),Path("assets/skills/causal_throw_catch_candidate.json"),
           Path("docs/THROW_CATCH_ONLINE_LEARNING.md"),Path("pyproject.toml"),output.relative_to(ROOT)]
    paths=[str(path) for path in paths if (ROOT/path).exists()]
    subprocess.run(["git","add","--",*paths],cwd=ROOT,check=True,capture_output=True)
    changed=subprocess.run(["git","diff","--cached","--quiet","--",*paths],cwd=ROOT)
    if changed.returncode==1:
        result=subprocess.run(["git","commit","--only","-m",reason,"--",*paths],cwd=ROOT,
                              check=True,capture_output=True,text=True,encoding="utf-8")
        print(result.stdout.strip(),flush=True)
    elif changed.returncode:
        raise RuntimeError("git diff failed")


def run_trial(parameters,scenario,output,label,*,observer=None):
    rng=random.Random(scenario["seed"])
    model=RobotModel()
    if "capture_offset_z_m" in parameters:
        model.capture_offset[2]=float(parameters["capture_offset_z_m"])
    from .catch_gripper_geometry import measure_opening
    cube_size=float(scenario.get("cube_size_m",.05))
    if not math.isfinite(cube_size) or cube_size<=0:
        model.close()
        raise ValueError("cube_size_m must be finite and positive")
    geometry=measure_opening(model,cube_size)
    geometry_fit=next(row for row in geometry["centered_box_clearance"] if row["box_width_m"]==cube_size)["centered_fit"]
    save_json(output/f"{label}_gripper_geometry.json",geometry)
    if parameters.get("require_centered_grasp_fit",False) and not geometry_fit:
        report=dict(label=label,released=False,caught=False,physical_capture=False,complete_success=False,
                    geometry_gate_blocked=True,failure_reason="centered_grasp_geometry_incompatible",
                    uses_offline_flight=False,position_observations=0,planner_calls=0,scenario=scenario,
                    controller_parameters=parameters,gripper_geometry=geometry,cube_size_m=cube_size)
        save_json(output/f"{label}.json",report)
        model.close()
        return report
    controller=OnlineCatchController(model,parameters)
    observations=[]
    trace=[]
    predictions=[]
    forecast_errors=[]
    free_flight_errors=[]
    release_gate=scenario.get("release_gate",4.90)
    launch={"q":list(POSES["best_coordination"]["q"]),"velocity":list(POSES["best_coordination"]["velocity"])}
    launch["velocity"]=[v*scenario.get("swing_scale",1.) for v in launch["velocity"]]

    def handler(env,report,sample,offset):
        p=env.p
        start=env._time
        dt=env.config.time_step_s
        period=1./scenario.get("sensor_hz",60)
        next_capture=0.
        inbox=deque()
        enabled=False
        enabled_at=None
        enabled_clearance=None
        contact_ticks=0
        capture_at=None
        hold_contacts=0
        hold_finger_targets=None
        stale_ticks=0
        best_distance=math.inf
        best_relative=math.inf
        best_row=None
        best_free_flight_row=None
        capture_gate=None
        first_violation=None
        first_robot_contact=None
        apex=env._cube_position()[2]
        report["launch_checks_at_release"]={key:report[key] for key in
            ("max_joint_velocity_ratios","max_motor_torque_ratios","joint_position_violation","self_penetration_detected","ground_contact")}
        report["launch_checks_at_release"]=json.loads(json.dumps(report["launch_checks_at_release"]))
        # Scenario conditions are hidden from the controller and fixed before flight evolves.
        if "drag" in scenario:
            p.changeDynamics(env._cube_id,-1,linearDamping=scenario["drag"],physicsClientId=env.client)
        if observer is not None:
            observer.latest=report
        for tick in range(480):
            now=env._time-start
            true_pos,orientation=p.getBasePositionAndOrientation(env._cube_id,physicsClientId=env.client)
            current_contacts=p.getContactPoints(env._cube_id,env._gripper_id,physicsClientId=env.client)
            if current_contacts and first_robot_contact is None:
                first_robot_contact=now
                controller.estimator.drag_updates_enabled=False
            if now+1e-9>=next_capture:
                if rng.random()>=scenario.get("drop_rate",0.):
                    measured=tuple(float(v+rng.gauss(0,scenario.get("noise_m",0.))) for v in true_pos)
                    inbox.append(PositionObservation(now,now+scenario.get("latency_s",0.),measured))
                next_capture+=period
            while inbox and inbox[0].delivered_at<=now+1e-9:
                frame=inbox.popleft()
                accepted=controller.observe(frame,now)
                observations.append(dict(**asdict(frame),received_at=now,accepted=accepted))
                if accepted and controller.estimator.ready(now):
                    at=round((now+.1)/dt)*dt
                    prediction,_=controller.estimator.predict(at)
                    predictions.append((at,prediction))
            for at,prediction in list(predictions):
                if now+1e-9>=at:
                    forecast_errors.append(float(np.linalg.norm(np.array(true_pos)-prediction)))
                    if first_robot_contact is None:
                        free_flight_errors.append(forecast_errors[-1])
                    predictions.remove((at,prediction))
            states=[p.getJointState(env._gripper_id,j,physicsClientId=env.client) for j in env._arm_joint_ids]
            q=np.array([s[0] for s in states])
            qd=np.array([s[1] for s in states])
            controller.observe_contacts(now,q,qd,{c[4] for c in current_contacts if c[9]>.05})
            target,speed,closing=controller.control(now,q,qd,dt)
            stale_ticks+=int(now>.12 and not controller.estimator.ready(now))
            command(env,target,speed)
            if capture_at is not None and hold_finger_targets is None and parameters.get("latch_contact_fingers",True):
                squeeze=float(parameters.get("grip_hold_angle_step_rad",.015))
                hold_finger_targets=[float(np.clip(p.getJointState(env._gripper_id,j,physicsClientId=env.client)[0]+squeeze,0.,.85))
                                     for j in range(8,14)]
            # The URDF mimic joints need explicit actuation in this simulator.
            for joint in range(8,14):
                finger_target=(hold_finger_targets[joint-8] if hold_finger_targets is not None else
                               (.85 if closing else float(parameters.get("open_finger_angle_rad",0.))))
                finger_force=float(parameters.get("grip_hold_force_nm",1.)) if hold_finger_targets is not None else 50.
                p.setJointMotorControl2(env._gripper_id,joint,p.POSITION_CONTROL,
                    targetPosition=finger_target,force=finger_force,maxVelocity=2,physicsClientId=env.client)
            capture_point,jac,_,rotation=model.state(q)
            clear=not p.getClosestPoints(env._cube_id,env._gripper_id,.015,physicsClientId=env.client)
            # A moving catch can follow the released object closely enough that
            # the geometric 15 mm query stays occupied even after the object
            # has causally separated.  Permit an observation-backed handoff
            # when the caller explicitly requests it; the short vertical skill
            # keeps the stricter geometric-only gate.
            observed_clear = False
            if (not enabled and parameters.get("enable_collision_after_observed_separation", False)
                    and controller.estimator.ready(now)):
                observed_cube, observed_velocity = controller.estimator.predict(now)
                point_now, _, _, _ = model.state(q)
                observed_clear = bool(np.linalg.norm(observed_cube - point_now)
                                      >= float(parameters.get("observed_separation_m", .06)))
            descent_clear = False
            if (not enabled and parameters.get("enable_collision_on_predicted_descent", False)
                    and controller.estimator.ready(now)
                    and now >= float(parameters.get("collision_enable_min_flight_s", 0.0))):
                descent_cube, descent_velocity = controller.estimator.predict(now)
                descent_point, _, _, _ = model.state(q)
                descent_clear = bool(descent_velocity[2] < -.05 and
                                     np.linalg.norm(descent_cube - descent_point)
                                     <= float(parameters.get("enable_collision_descent_distance_m", .12)))
            geometric_allowed = clear and not parameters.get("disable_geometric_collision_enable", False)
            if not enabled and (geometric_allowed or observed_clear or descent_clear):
                for link in range(-1,p.getNumJoints(env._gripper_id,physicsClientId=env.client)):
                    p.setCollisionFilterPair(env._gripper_id,env._cube_id,link,-1,1,physicsClientId=env.client)
                enabled=True
                enabled_at=now
                points=p.getClosestPoints(env._cube_id,env._gripper_id,.25,physicsClientId=env.client)
                enabled_clearance=min((point[8] for point in points),default=.25)
                report["collision_enable_observed_clear"] = observed_clear
                report["collision_enable_predicted_descent"] = descent_clear
            env._phase="online_catch"
            env._step(1)
            pos,vel,ground=sample("flight",tick)
            apex=max(apex,pos[2])
            report["measured_rise_m"]=apex-report["release_position"][2]
            states=[p.getJointState(env._gripper_id,j,physicsClientId=env.client) for j in env._arm_joint_ids]
            point,jac,_,rotation=model.state(np.array([s[0] for s in states]))
            point_v=jac@np.array([s[1] for s in states])
            distance=math.dist(pos,point)
            relative=math.dist(vel,point_v)
            contacts=p.getContactPoints(env._cube_id,env._gripper_id,physicsClientId=env.client)
            links={c[4] for c in contacts if c[9]>.05}
            _,cube_orientation=p.getBasePositionAndOrientation(env._cube_id,physicsClientId=env.client)
            _,angular_velocity=p.getBaseVelocity(env._cube_id,physicsClientId=env.client)
            bilateral={9,12}.issubset(links)
            row=dict(time_s=now+dt,cube=list(pos),truth_velocity=list(vel),capture_point=point.tolist(),
                capture_velocity=point_v.tolist(),distance_m=distance,relative_speed_m_s=relative,
                contacts=sorted(links),closing=closing,collision_enabled=enabled,
                observation_at=controller.estimator.history[-1].captured_at if controller.estimator.history else None,
                commanded_q=target.tolist(),commanded_qd=speed.tolist(),q=[s[0] for s in states],qd=[s[1] for s in states])
            row.update(cube_orientation=list(cube_orientation),truth_angular_velocity=list(angular_velocity),
                finger_q=[p.getJointState(env._gripper_id,j,physicsClientId=env.client)[0] for j in range(8,14)],
                contact_forces=[dict(link=c[4],normal_force_n=c[9]) for c in contacts])
            trace.append(row)
            violation=(max(report["max_joint_velocity_ratios"])>1.05 or report["joint_position_violation"]
                       or report["self_penetration_detected"])
            if violation and first_violation is None:
                first_violation=dict(time_s=now+dt,speed_ratios=list(report["max_joint_velocity_ratios"]),
                    joint_position_violation=report["joint_position_violation"],self_penetration=report["self_penetration_detected"])
            if vel[2]<-.05 and distance<best_distance:
                best_distance,best_row=distance,row
            if (vel[2]<-.05 and first_robot_contact is None and not contacts
                    and (best_free_flight_row is None or distance<best_free_flight_row["distance_m"])):
                best_free_flight_row=row
            if vel[2]<-.05 and distance<.04:
                best_relative=min(best_relative,relative)
            if controller.estimator.ready(now+dt):
                seen,seen_v=controller.estimator.predict(now+dt)
                if (seen_v[2]<-.05 and np.linalg.norm(seen-point)<=.025
                        and np.linalg.norm(seen_v-point_v)<=1. and capture_gate is None):
                    capture_gate=dict(time_s=now+dt,distance_m=float(np.linalg.norm(seen-point)),
                                      relative_speed_m_s=float(np.linalg.norm(seen_v-point_v)))
            if bilateral and controller.estimator.ready(now+dt) and controller.estimator.predict(now+dt)[1][2]<0:
                contact_ticks+=1
            else:
                contact_ticks=0
            if contact_ticks>=12 and capture_at is None:
                capture_at=now+dt
            if capture_at is not None:
                hold_contacts+=int(bilateral)
                if now+dt-capture_at>=float(parameters.get("hold_duration_s",.5)):
                    break
            if ground:
                break
            if violation and parameters.get("abort_on_motion_violation",False):
                command(env,[s[0] for s in states])
                break
        hold_duration=float(parameters.get("hold_duration_s",.5))
        hold_rows=[row for row in trace if capture_at is not None and row["time_s"]>=capture_at-1e-8]
        separation=bool(enabled and (first_robot_contact is None or
                                     enabled_at+dt <= first_robot_contact + 1e-9))
        final_speed=float(np.linalg.norm(trace[-1]["truth_velocity"])) if trace else math.inf
        longest_run=run=0
        for row in hold_rows:
            run=run+1 if {9,12}.issubset(row["contacts"]) and row["collision_enabled"] else 0
            longest_run=max(longest_run,run)
        continuous_hold=max(0,longest_run-1)*dt
        hold=bool(capture_at is not None and env._time-start-capture_at>=hold_duration
                  and hold_rows and all({9,12}.issubset(row["contacts"]) for row in hold_rows)
                  and env._cube_position()[2]>.2 and not report["ground_contact"] and final_speed<.05
                  and separation and env._constraint_id is None)
        checks=bool(not report["joint_position_violation"] and not report["self_penetration_detected"]
            and max(report["max_joint_velocity_ratios"])<=1.05 and max(report["max_motor_torque_ratios"])<=1.001)
        causal=all(o["captured_at"]<=o["delivered_at"]+1e-8
                   and o["delivered_at"]<=o["received_at"]+1e-8 for o in observations)
        causal &= all(e["latest_observation_at"]<=e["issued_at"]+1e-8 for e in controller.events)
        report.update(caught=hold,catch_hold_passed=hold,complete_success=bool(hold and checks and causal),physical_capture=hold and checks,
            capture_contact_time_s=capture_at,observed_capture_gate=capture_gate,collision_enabled=enabled,
            tactile_capture_time_s=controller.tactile_capture_at,
            descent_servo_started_at_s=controller.servo_started_at,
            collision_reenabled_at_s=enabled_at,
            collision_clearance_at_enable_m=enabled_clearance,free_flight_separation_verified=separation,
            required_hold_duration_s=hold_duration,continuous_hold_duration_s=continuous_hold,
            hold_observation_duration_s=hold_rows[-1]["time_s"]-hold_rows[0]["time_s"] if hold_rows else 0.,
            hold_contact_ticks=hold_contacts,hold_final_speed_m_s=final_speed,
            catch_hold_finger_targets=hold_finger_targets,
            no_catch_constraint=env._constraint_id is None,causality_contract_passed=bool(causal),
            causality_passed=bool(causal and len(observations)>=4 and (controller.plan_count>0 or controller.events)),uses_offline_flight=False,
            position_observations=len(observations),position_sensor_source="simulated noisy delayed position measurements",
            truth_velocity_used_by_controller=False,stale_control_ticks=stale_ticks,planner_calls=controller.plan_count,
            planner_deadline_misses=controller.deadline_misses,max_planner_wall_s=controller.max_plan_wall_s,
            late_plan_rejections=controller.late_plan_rejections,first_motion_violation=first_violation,
            estimated_drag=controller.estimator.drag,forecast_100ms_rmse_m=float(np.sqrt(np.mean(np.square(forecast_errors)))) if forecast_errors else None,
            free_flight_forecast_100ms_rmse_m=float(np.sqrt(np.mean(np.square(free_flight_errors)))) if free_flight_errors else None,
            first_robot_contact_time_s=first_robot_contact,
            closest_descending=best_row,best_relative_within_4cm_m_s=best_relative if math.isfinite(best_relative) else None,
            closest_free_flight_descending=best_free_flight_row,centered_grasp_fit=geometry_fit,
            apex_height_m=apex,measured_rise_m=apex-report["release_position"][2],
            free_flight=separation,flight_contact=report["ground_contact"],motion_checks_passed=checks,
            capture_offset_m=model.capture_offset.tolist(),controller_parameters=parameters,scenario=scenario)
        if not hold:
            report["failure_reason"]="no_bilateral_finger_capture_and_hold"
        save_json(output/f"{label}_observations.json",observations)
        save_json(output/f"{label}_decisions.json",controller.events)
        save_json(output/f"{label}_control_trace.json",trace)
        if observer is not None:
            observer(env,"result",tick)
    try:
        report=trial(launch,scenario.get("mass_kg",.1),.35,DELAYS["best_coordination"],
            spin={"turns":1.5,"joints":[0],"directions":[1]} if scenario.get("pre_spin",True) else None,
            release_threshold=release_gate,release_inward_only=scenario.get("release_inward_only",False),
            release_radial_speed_max=scenario.get("release_radial_speed_max_m_s"),
            vertical_toss=scenario.get("vertical_toss"),
            release_handler=handler,output=output,label=label,observer=observer,cube_size_m=cube_size)
    finally:
        model.close()
    if not report.get("released"):
        report.update(caught=False,physical_capture=False,complete_success=False,position_observations=0,
                      planner_calls=0,failure_reason=report.get("error","measured_release_gate_not_reached"))
        save_json(output/f"{label}.json",report)
    return report


def reflect(skill,report,label):
    skill.version+=1
    skill.validation_trials+=1
    skill.status="candidate"
    lessons=[]
    forecast_error=report.get("free_flight_forecast_100ms_rmse_m",report.get("forecast_100ms_rmse_m"))
    if forecast_error and forecast_error>.025:
        skill.parameters["estimate_drag"]=True
        lessons.append("position_history_requires_online_drag_estimation")
    if report.get("planner_deadline_misses",0):
        skill.parameters["ik_seeds"]=max(0,int(skill.parameters["ik_seeds"])-2)
        skill.parameters["horizon_step_s"]=.10
        lessons.append("slow_kinematic_search_must_not_be_treated_as_instantaneous")
    if not report.get("caught"):
        lessons.append("position_velocity_approach_is_not_bilateral_contact_capture")
        skill.parameters["time_hysteresis"]=2.
    if report.get("first_robot_contact_time_s") is not None and not report.get("caught"):
        lessons.append("one_sided_finger_impact_does_not_establish_capture")
        lessons.append("ballistic_prediction_error_after_contact_is_not_free_flight_model_error")
    if not report.get("motion_checks_passed",True):
        skill.parameters.update(strict_trajectory=True,abort_on_motion_violation=True,ik_iterations=35)
        lessons.append("reject_infeasible_complete_paths_and_recheck_after_planning_delay")
        lessons.append("reserve_joint_travel_for_followthrough_and_braking")
        first=report.get("first_motion_violation")
        if first and first["time_s"]<.02:
            lessons.append("release_handoff_must_preserve_joint_velocity_before_braking")
            skill.parameters["handoff_brake_s"]=.35
    for lesson in lessons:
        if lesson not in skill.facts:
            skill.facts.append(lesson)
    skill.validation_metrics.update(complete_success=bool(report.get("complete_success")),uses_offline_flight=False,
        causal_trials=int(skill.validation_metrics.get("causal_trials",0))+int(report.get("causality_passed",False)),
        physical_capture_trials=int(skill.validation_metrics.get("physical_capture_trials",0))+int(report.get("physical_capture",False)),
        last_trial=label,last_observation_count=report.get("position_observations",0))
    skill.validation_success_rate=skill.validation_metrics["physical_capture_trials"]/skill.validation_trials
    skill.false_success_rate=None
    skill.recovery_success_rate=None
    return lessons


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument("--trials",type=int,default=3)
    parser.add_argument("--git",action="store_true",help="commit each completed experiment and skill update")
    parser.add_argument("--video",action="store_true",help="record the first fresh causal experiment")
    parser.add_argument("--close-lead",type=float,help="test an alternative finger closing lead, in seconds")
    parser.add_argument("--cube-size-mm",type=float,default=50.,help="cube edge length in mm (default: 50)")
    parser.add_argument("--diagnostic",action="store_true",help="explicitly test a flight despite incompatible centered-grasp geometry")
    args=parser.parse_args()
    if not math.isfinite(args.cube_size_mm) or args.cube_size_mm<=0:
        parser.error("cube size must be finite and positive")
    if not 1<=args.trials<=12:
        parser.error("trials must be between 1 and 12")
    if args.close_lead is not None and not 0<=args.close_lead<=.5:
        parser.error("close lead must be between 0 and 0.5 seconds")
    output=args.output.resolve()
    output.relative_to(ROOT)
    if (output/"summary.json").exists():
        parser.error("choose a new experiment output directory")
    output.mkdir(parents=True,exist_ok=True)
    store=SkillStore(SKILL_PATH)
    skills=store.all()
    skill=skills[0] if skills else initial_skill()
    store.save_candidate(skill)
    reports=[]
    scenarios=[dict(seed=101,release_gate=4.90,sensor_hz=60,noise_m=0.,latency_s=0.,drop_rate=0.),
        dict(seed=202,release_gate=4.87,sensor_hz=60,noise_m=.001,latency_s=1/60,drop_rate=.05,drag=.06),
        dict(seed=303,release_gate=4.84,sensor_hz=60,noise_m=.002,latency_s=2/60,drop_rate=.10,drag=.025),
        dict(seed=404,release_gate=4.90,sensor_hz=60,noise_m=.001,latency_s=1/60,drop_rate=.05,mass_kg=.12)]
    journal=ROOT/"docs/THROW_CATCH_ONLINE_LEARNING.md"
    if not journal.exists():
        journal.write_text("# 基于在线观测的接回实验\n\n旧的完整飞行离线选点只保留为历史诊断，不能作为本轮控制输入或成功证据。\n\n传感输入为仿真器采样的位置观测，可带噪声、延迟和漏帧；不是摄像头检测。控制器没有动态世界句柄，只接收已送达的位置观测和关节编码器状态。独立运动学模型允许求解未来动作，不读取未来物体状态。\n",encoding="utf-8")
    for index in range(args.trials):
        scenario=scenarios[index%len(scenarios)].copy()
        scenario.update(skill.parameters.get("launch_profile",{}))
        scenario["cube_size_m"]=args.cube_size_mm/1000
        scenario["seed"]+=1000*(index//len(scenarios))
        label=f"online_{skill.validation_trials+1:03d}"
        version_used=skill.version
        snapshot=json.loads(json.dumps(asdict(skill)))
        parameters=dict(skill.parameters)
        if args.close_lead is not None:
            parameters["close_lead_s"]=args.close_lead
        if args.diagnostic:
            parameters["require_centered_grasp_fit"]=False
            parameters["geometry_diagnostic"]=True
        snapshot["parameters"]=parameters
        save_json(output/f"{label}_skill_before.json",snapshot)
        recorder=None
        observer=None
        if args.video and index==0:
            from .throw_catch_493_video import Recorder
            flow="离手观测 → 下降闭合 → 接触保持" if parameters.get("stationary_catch") else "位置观测 → 在线预测 → 重规划"
            recorder=Recorder(output/f"{label}.mp4",fps=30,title="xArm6 在线观测接回实验",
                subtitle=f"{flow} | {args.cube_size_mm:g} mm | {scenario.get('mass_kg',.1)*1000:g} g",
                release_gate=scenario["release_gate"],grasp_detail=args.cube_size_mm<=80)
            class VideoObserver:
                latest={}
                def __call__(self,env,phase,tick):
                    recorder.capture(env,self.latest,phase)
            observer=VideoObserver()
        try:
            report=run_trial(parameters,scenario,output,label,observer=observer)
        finally:
            if recorder is not None:
                recorder.close()
        if recorder is not None:
            report.update(video=str(output/f"{label}.mp4"),video_frames=recorder.frames)
            save_json(output/f"{label}.json",report)
        reports.append(report)
        lessons=reflect(skill,report,label)
        store.save_candidate(skill)
        save_json(output/f"{label}_reflection.json",dict(skill_version_used=version_used,updated_skill_version=skill.version,
            lessons=lessons,skill_after=asdict(skill)))
        compact={key:report.get(key) for key in ("label","released","caught","physical_capture","causality_passed",
            "position_observations","planner_calls","planner_deadline_misses","max_planner_wall_s","forecast_100ms_rmse_m",
            "estimated_drag","motion_checks_passed","error")}
        compact["closest_distance_m"]=report.get("closest_descending",{}).get("distance_m") if report.get("closest_descending") else None
        with journal.open("a",encoding="utf-8") as stream:
            stream.write(f"\n## {label}：skill v{version_used} → v{skill.version}\n\n")
            stream.write("```json\n"+json.dumps(compact,ensure_ascii=False,indent=2)+"\n```\n\n")
            stream.write("本次反思："+"；".join(lessons)+"。完整接稳未通过时保持 candidate，不记成功。\n")
        save_json(output/"summary.json",dict(scope="causal position-observation catch experiments",reports=reports,skill=asdict(skill)))
        print(json.dumps(compact,ensure_ascii=False),flush=True)
        if args.git:
            checkpoint(output,f"experiment: {label} causal catch evidence and skill v{skill.version}")


if __name__=="__main__":
    main()
