"""Joint-space throwing probes under the existing URDF speed/effort limits.

Pose resets are confined to an independent, object-free kinematics client.
Dynamic trials start from a physical grasp and never reset joint/object states.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import random

from .sim_environment import SimConfig, _require_pybullet, _pybullet_data
from .throw_catch import ThrowEnv
from .throw_catch_2m import REQUIRED_VZ
from .spin_trajectory import accelerate, coast_and_brake, periodic_state, plan_spin


def acquire(mass, *, observer=None):
    env = ThrowEnv(config=SimConfig(arm_model="xarm6", cube_mass_kg=mass))
    # Broad swings need floor clearance; preserve the original base elevation.
    env.p.removeBody(env._table_id, physicsClientId=env.client)
    env.ground = env.p.loadURDF("plane.urdf", physicsClientId=env.client)
    # Original cube must retain its tabletop start support until acquired.
    shape = env.p.createCollisionShape(env.p.GEOM_BOX, halfExtents=[0.08, 0.08, 0.02], physicsClientId=env.client)
    stand = env.p.createMultiBody(0, shape, -1, [0.45, 0, 0.68], physicsClientId=env.client)
    if observer is not None:
        observer(env, "scene", 0)
        env.config.frame_callback = lambda state: observer(env, state.phase, round(state.timestamp/env.config.time_step_s))
    for action in ("approach_object", "close_gripper", "lift_object"):
        env.execute(action)
    if not env.observe().object.lifted or env._constraint_id is None:
        env.close()
        raise RuntimeError("physical lift evidence missing")
    env.p.removeBody(stand, physicsClientId=env.client)
    state = env.p.getLinkState(env._gripper_id, env._ee_link_index, computeForwardKinematics=True, physicsClientId=env.client)
    cube = env.p.getBasePositionAndOrientation(env._cube_id, physicsClientId=env.client)
    inv = env.p.invertTransform(state[4], state[5])
    offset = env.p.multiplyTransforms(*inv, *cube)[0]
    env.config.frame_callback = None
    return env, offset


def kinematic_candidates(env, offset, count, seed):
    """Sample point Jacobians in a separate object-free client (not a trajectory)."""
    p = env.p
    client = p.connect(p.DIRECT)
    try:
        p.setAdditionalSearchPath(_pybullet_data.getDataPath(), physicsClientId=client)
        arm = p.loadURDF("xarm/xarm6_with_gripper.urdf", [0.10, 0, 0.70], useFixedBase=True, physicsClientId=client)
        movable = [j for j in range(p.getNumJoints(arm, physicsClientId=client))
                   if p.getJointInfo(arm, j, physicsClientId=client)[3] >= 0]
        # localPosition is in the URDF link frame; verified by finite differences.
        rng = random.Random(seed)
        candidates = []
        for _ in range(count):
            q = [0.0] + [rng.uniform(lo + 0.1, hi - 0.1)
                         for lo, hi in zip(env._arm_lower[1:], env._arm_upper[1:])]
            for index in (3, 5):
                q[index] = (q[index] + math.pi) % (2 * math.pi) - math.pi
            for joint, value in zip(env._arm_joint_ids, q):
                p.resetJointState(arm, joint, value, physicsClientId=client)
            all_q = [p.getJointState(arm, j, physicsClientId=client)[0] for j in movable]
            linear, _ = p.calculateJacobian(arm, 6, offset, all_q, [0.] * len(all_q), [0.] * len(all_q), physicsClientId=client)
            jz = linear[2][:6]
            bound = sum(abs(j) * v for j, v in zip(jz, env._arm_velocity))
            link = p.getLinkState(arm, 6, computeForwardKinematics=True, physicsClientId=client)
            point = p.multiplyTransforms(link[4], link[5], offset, [0, 0, 0, 1])[0]
            if point[2] < 0.25:
                continue
            velocity = [math.copysign(v * 0.95, j) if abs(j) > 1e-5 else 0.
                        for j, v in zip(jz, env._arm_velocity)]
            candidates.append({"q": q, "velocity": velocity, "sampled_vz_bound_m_s": bound,
                               "jacobian_z": list(jz), "cube_position": list(point)})
        candidates.sort(key=lambda c: c["sampled_vz_bound_m_s"], reverse=True)
        return candidates
    finally:
        p.disconnect(client)


def command(env, q, qd=None, speed_scale=1.0):
    p = env.p
    for i, joint in enumerate(env._arm_joint_ids):
        p.setJointMotorControl2(env._gripper_id, joint, p.POSITION_CONTROL,
            targetPosition=max(env._arm_lower[i] + 0.01, min(env._arm_upper[i] - 0.01, q[i])),
            targetVelocity=0. if qd is None else qd[i], force=env._arm_effort[i],
            maxVelocity=env._arm_velocity[i] * speed_scale, physicsClientId=env.client)


def self_penetrations(env):
    """Non-neighbor arm pairs, plus gripper versus the upper arm/base.

    Exclude adjacent joints and the attached gripper's internal mechanism.
    This diagnoses geometry; the existing model does not resolve self contact.
    """
    p = env.p
    pairs = [(i, j) for i in range(7) for j in range(i+2, 7)]
    pairs += [(i, j) for i in range(5) for j in range(7, 14)]
    return [(i, j, point[8]) for i, j in pairs
            for point in p.getClosestPoints(env._gripper_id, env._gripper_id, 0.,
                linkIndexA=i, linkIndexB=j, physicsClientId=env.client) if point[8] < -0.001]


def baseline(mass):
    """Old one-target IK sweep after the identical support/scene preparation."""
    env, _ = acquire(mass)
    try:
        state = env.observe()
        target = [0.35, state.object.position_m[1], 1.10]
        ee_target = [ee+goal-actual for ee, goal, actual in zip(
            state.robot.end_effector_position_m, target, state.object.position_m)]
        env._set_gripper_pose(ee_target, open_gripper=False)
        peak = 0.
        for _ in range(120):
            env._step(1)
            peak = max(peak, env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)[0][2])
        return {"cube_mass_kg": mass, "peak_vz_m_s": peak, "released": False}
    finally:
        env.close()


def trial(candidate, mass, lead, delays, *, output=None, label="probe", spin=None, loop=None,
          observer=None, swing_steps=None, continuation=None, release_threshold=None,
          release_handler=None):
    """Run a launch probe; optional hooks record and continue a calibrated launch.

    A continuation is responsible for its own explicit release policy. The
    default probe retains the original two-metre release gate.
    """
    if swing_steps is not None and (not isinstance(swing_steps, int) or swing_steps < 1):
        raise ValueError("swing_steps must be a positive integer")
    env, offset = acquire(mass, observer=observer)
    p = env.p
    report = {"label": label, "cube_mass_kg": mass, "lead_s": lead, "delays_s": delays,
              "candidate": candidate, "released": False, "peak_vz_m_s": 0.,
              "max_joint_velocity_ratios": [0.] * 6, "max_motor_torque_ratios": [0.] * 6,
              "ground_contact": False, "joint_position_violation": False,
              "self_penetration_detected": False, "self_check_stride_steps": 1 if output is not None else 8,
              "phase_peaks": {}, "spin_milestones": []}
    rows = []
    dt = env.config.time_step_s

    def sample(phase, tick):
        states = [p.getJointState(env._gripper_id, j, physicsClientId=env.client) for j in env._arm_joint_ids]
        pos, _ = p.getBasePositionAndOrientation(env._cube_id, physicsClientId=env.client)
        vel, _ = p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        link = p.getLinkState(env._gripper_id, 6, computeLinkVelocity=True, physicsClientId=env.client)
        # Constraint-consistent velocity at the cube, evaluated from wrist twist.
        delta = [a - b for a, b in zip(pos, link[0])]
        cross = [link[7][1]*delta[2]-link[7][2]*delta[1],
                 link[7][2]*delta[0]-link[7][0]*delta[2],
                 link[7][0]*delta[1]-link[7][1]*delta[0]]
        point_v = [a + b for a, b in zip(link[6], cross)]
        report["current_point_velocity"] = point_v
        for i, state in enumerate(states):
            report["max_joint_velocity_ratios"][i] = max(report["max_joint_velocity_ratios"][i], abs(state[1])/env._arm_velocity[i])
            report["max_motor_torque_ratios"][i] = max(report["max_motor_torque_ratios"][i], abs(state[3])/env._arm_effort[i])
            if not env._arm_lower[i]-0.001 <= state[0] <= env._arm_upper[i]+0.001:
                report["joint_position_violation"] = True
        cube_contact = bool(p.getContactPoints(env._cube_id, env.ground, physicsClientId=env.client))
        robot_contact = bool(p.getContactPoints(env._gripper_id, env.ground, physicsClientId=env.client))
        contact = cube_contact or robot_contact
        # Intentional supported placement is permitted only in continuation phases.
        report["ground_contact"] |= robot_contact or (cube_contact and phase not in ("place", "placement_settle", "result"))
        if tick % report["self_check_stride_steps"] == 0:
            penetrations = self_penetrations(env)
            if penetrations:
                report.update(self_penetration_detected=True, self_penetration_example=penetrations[:3])
        row = [env._time, phase, tick, *pos, *vel, *point_v,
               *[s[0] for s in states], *[s[1] for s in states], *[s[3] for s in states],
               env._constraint_id is not None, contact]
        if output is not None:
            rows.append(row)
        phase_peak = report["phase_peaks"].setdefault(phase, {"vz_m_s": 0., "speed_m_s": 0.})
        phase_peak["vz_m_s"] = max(phase_peak["vz_m_s"], vel[2])
        phase_peak["speed_m_s"] = max(phase_peak["speed_m_s"], math.sqrt(sum(v*v for v in vel)))
        if phase in ("spin", "swing") and vel[2] > report["peak_vz_m_s"]:
            contributions = []
            for state, joint in zip(states, env._arm_joint_ids):
                joint_link = p.getLinkState(env._gripper_id, joint, computeForwardKinematics=True, physicsClientId=env.client)
                matrix = p.getMatrixFromQuaternion(joint_link[5])
                axis = [matrix[2], matrix[5], matrix[8]]
                r = [a-b for a,b in zip(pos, joint_link[4])]
                contributions.append((axis[0]*r[1]-axis[1]*r[0])*state[1])
            report.update(peak_vz_m_s=vel[2], peak_phase=phase, peak_time_s=env._time, peak_position=list(pos),
                          peak_velocity=list(vel), peak_q=[s[0] for s in states],
                          peak_qd=[s[1] for s in states], peak_point_velocity=list(point_v),
                          peak_joint_vz_contributions=contributions,
                          peak_cube_point_velocity_error_m_s=math.dist(vel, point_v))
        if observer is not None:
            observer(env, phase, tick)
        return pos, vel, contact

    try:
        if spin is not None and loop is not None:
            raise ValueError("choose a pre-rotation or a periodic loop")
        if loop is not None:
            report["loop"] = loop
            report["cycle_milestones"] = []
            if loop["turns"] <= 0 or loop["rate"] <= 0:
                raise ValueError("positive loop turns and terminal phase rate required")
            for i, (c, a, b) in enumerate(zip(loop["center"], loop["sine"], loop["cosine"])):
                amplitude = math.hypot(a, b)
                if not env._arm_lower[i]+.02 <= c-amplitude <= c+amplitude <= env._arm_upper[i]-.02:
                    raise ValueError(f"J{i+1}: periodic loop exceeds position limit")
                if amplitude*loop["rate"] > .95*env._arm_velocity[i]+1e-8:
                    raise ValueError(f"J{i+1}: periodic loop exceeds target speed limit")
        start = [max(lo + 0.05, min(hi - 0.05, q - v * lead))
                 for lo, hi, q, v in zip(env._arm_lower, env._arm_upper, candidate["q"], candidate["velocity"])]
        if loop is not None:
            start = periodic_state(0., **loop)[0]
        spin_plan = None
        if spin is not None:
            spin_plan = plan_spin(start, env._arm_lower, env._arm_upper, env._arm_velocity, **spin)
            report["spin_plan"] = spin_plan
            start = spin_plan["start_q"]
        command(env, start, speed_scale=0.25)
        for tick in range(2400):
            env._step(1)
            _, _, contact = sample("prepare", tick)
            q = [p.getJointState(env._gripper_id, j, physicsClientId=env.client)[0] for j in env._arm_joint_ids]
            if contact:
                raise RuntimeError("preparation contacted ground")
            if tick > 120 and max(abs(a-b) for a,b in zip(q,start)) < 0.015:
                break
        else:
            raise RuntimeError("preparation failed to track")
        for tick in range(120):
            env._step(1)
            sample("settle", tick)
        actual_start = [p.getJointState(env._gripper_id, j, physicsClientId=env.client)[0] for j in env._arm_joint_ids]
        report["prepared_q"] = actual_start
        if spin_plan is not None:
            milestones = {index: .5 for index in spin_plan["joints"]}
            for tick in range(math.ceil(spin_plan["duration_s"] / dt)):
                elapsed = min((tick + 1) * dt, spin_plan["duration_s"])
                target, qd = list(actual_start), [0.] * 6
                for index, spec in spin_plan["joints"].items():
                    distance, speed = accelerate(elapsed, spec["distance_rad"], spec["speed_rad_s"])
                    target[index] += spec["direction"] * distance
                    qd[index] = spec["direction"] * speed
                command(env, target, qd)
                env._step(1)
                pos, vel, contact = sample("spin", tick)
                if contact:
                    raise RuntimeError("pre-rotation contacted ground")
                for index, spec in spin_plan["joints"].items():
                    state = p.getJointState(env._gripper_id, env._arm_joint_ids[index], physicsClientId=env.client)
                    turns = spec["direction"] * (state[0] - actual_start[index]) / (2 * math.pi)
                    if turns >= milestones[index]:
                        report["spin_milestones"].append({"joint": index+1, "turns": milestones[index],
                            "measured_turns": turns, "t_s": env._time,
                            "joint_speed_rad_s": abs(state[1]), "vz_m_s": vel[2],
                            "cube_speed_m_s": math.sqrt(sum(v*v for v in vel))})
                        milestones[index] += .5
            report["spin_end"] = {"q": [p.getJointState(env._gripper_id, j, physicsClientId=env.client)[0]
                                             for j in env._arm_joint_ids],
                                  "qd": [p.getJointState(env._gripper_id, j, physicsClientId=env.client)[1]
                                              for j in env._arm_joint_ids]}
            report["spin_end"]["measured_turns"] = {
                index: spec["direction"] * (report["spin_end"]["q"][index] - actual_start[index]) / (2 * math.pi)
                for index, spec in spin_plan["joints"].items()}
            # Use the last commanded position as launch anchor: position and
            # velocity targets are continuous across the spin/swing boundary.
            actual_start = target
        # Acceleration ramp and staggered launches; no state resets or impulses.
        ramp = 0.12
        duration = 2 * lead + max(delays) + .25 if loop is None else 4 * math.pi * loop["turns"] / loop["rate"]
        next_cycle = 1
        cycle_peak, cycle_speed = 0., 0.
        ticks = math.ceil(duration / dt)
        if swing_steps is not None:
            ticks = min(ticks, swing_steps)
        for tick in range(ticks):
            elapsed = tick * dt if loop is None else min((tick + 1) * dt, duration)
            target, qd = [], []
            for q, v, delay in zip(actual_start, candidate["velocity"], delays):
                t = max(0., elapsed - delay)
                integral = t*t/(2*ramp) if t < ramp else t-ramp/2
                target.append(q + v*integral)
                qd.append(v*min(1., t/ramp))
            if spin_plan is not None:
                for index, spec in spin_plan["joints"].items():
                    distance, speed = coast_and_brake(elapsed, spec["speed_rad_s"],
                        spin_plan["brake_start_s"], spin_plan["brake_duration_s"])
                    target[index] = actual_start[index] + spec["direction"] * distance
                    qd[index] = spec["direction"] * speed
            if loop is not None:
                target, qd, phase = periodic_state(elapsed, **loop)
            command(env, target, qd)
            env._step(1)
            pos, vel, contact = sample("swing", tick)
            if loop is not None:
                cycle_peak = max(cycle_peak, vel[2])
                cycle_speed = max(cycle_speed, math.sqrt(sum(v*v for v in vel)))
                if phase >= next_cycle * 2 * math.pi - 1e-9:
                    report["cycle_milestones"].append({"cycle": next_cycle, "t_s": env._time,
                        "peak_vz_m_s": cycle_peak, "peak_speed_m_s": cycle_speed,
                        "commanded_phase_rad": phase,
                        "commanded_phase_rate_rad_s": math.sqrt(phase / (2*math.pi*loop["turns"])) * loop["rate"]})
                    next_cycle += 1
                    cycle_peak, cycle_speed = 0., 0.
            if contact:
                raise RuntimeError("swing contacted ground")
            threshold = REQUIRED_VZ if release_threshold is None else release_threshold
            if vel[2] >= threshold:
                # Verify joint limits and attachment fidelity before any release.
                if (max(report["max_joint_velocity_ratios"]) <= 1.05
                        and not report["joint_position_violation"]
                        and not report["self_penetration_detected"]
                        and max(report["max_motor_torque_ratios"]) <= 1.001
                        and math.dist(vel, report["current_point_velocity"]) < 0.1):
                    env.release_in_motion()
                    report.update(released=True, release_velocity=list(vel), release_position=list(pos),
                                  release_threshold_m_s=threshold, release_time_s=env._time)
                    if release_handler is not None:
                        release_handler(env, report, sample, offset)
                        break
                    apex = pos[2]
                    for flight_tick in range(480):
                        env._step(1)
                        flight_pos, flight_vel, contact = sample("flight", flight_tick)
                        apex = max(apex, flight_pos[2])
                        if flight_vel[2] <= 0 or contact:
                            break
                    report.update(measured_rise_m=apex-pos[2], apex_height_m=apex)
                    break
        def valid():
            return bool(not report["ground_contact"] and not report["joint_position_violation"]
                               and not report["self_penetration_detected"]
                               and max(report["max_joint_velocity_ratios"]) <= 1.05
                               and max(report["max_motor_torque_ratios"]) <= 1.001
                               and report.get("peak_cube_point_velocity_error_m_s", math.inf) < 0.1)
        report["launch_valid"] = valid()
        if continuation is not None:
            continuation(env, report, sample)
        report["valid"] = valid()
    except Exception as exc:
        report.update(error=f"{type(exc).__name__}: {exc}", valid=False)
    finally:
        env.close()
    report["ideal_vacuum_rise_m"] = max(0., report["peak_vz_m_s"])**2/(2*9.81)
    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
        (output/f"{label}.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        with (output/f"{label}_physics.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["t_s","phase","tick","x","y","z","vx","vy","vz","point_vx","point_vy","point_vz",
                             *[f"q{i}" for i in range(6)], *[f"qd{i}" for i in range(6)],
                             *[f"tau{i}" for i in range(6)],"constraint","ground_contact"])
            writer.writerows(rows)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/throw_catch_coordination_20261020"))
    parser.add_argument("--poses", type=int, default=12000)
    parser.add_argument("--candidates", type=int, default=10)
    args = parser.parse_args()
    if args.poses < 1 or args.candidates < 1:
        parser.error("--poses and --candidates must be positive")
    if (args.output/"summary.json").exists():
        parser.error("choose a new output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    env, offset = acquire(0.10)
    try:
        candidates = kinematic_candidates(env, offset, args.poses, 20261020)
        limits = {"lower": env._arm_lower, "upper": env._arm_upper,
                  "velocity": env._arm_velocity, "effort": env._arm_effort}
    finally:
        env.close()
    (args.output/"kinematics.json").write_text(json.dumps({"poses": args.poses, "offset": offset,
        "limits": limits, "best_candidates": candidates[:100],
        "scope": "sampled instantaneous kinematic bound; no dynamics, collision or reachability guarantee"}, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"sampled_bound": candidates[0]}, ensure_ascii=False), flush=True)
    reports = []
    baselines = [baseline(mass) for mass in (0.10, 0.001) for _ in range(3)]
    schedules = {"synchronous": [0.]*6,
                 "proximal_distal_40ms": [0.,0.,0.04,0.06,0.08,0.10],
                 "proximal_distal_80ms": [0.,0.,0.08,0.12,0.16,0.20]}
    # Spread initial poses rather than probing near-duplicates from random search.
    selected = []
    for candidate in candidates:
        if all(math.dist(candidate["q"], c["q"]) > 0.8 for c in selected):
            selected.append(candidate)
        if len(selected) >= args.candidates:
            break
    for index, candidate in enumerate(selected):
        for lead in (0.20, 0.35):
            for name, delays in schedules.items():
                report = trial(candidate, 0.10, lead, delays, label=f"pose_{index}_{lead}_{name}")
                reports.append(report)
        print(json.dumps({"candidate":index,"best":max(reports[-6:], key=lambda r:r["peak_vz_m_s"])}), flush=True)
    valid = [r for r in reports if r.get("valid")]
    best = max(valid, key=lambda r:r["peak_vz_m_s"]) if valid else None
    repeats = []
    if best:
        for mass in (0.10,0.001):
            for i in range(3):
                repeats.append(trial(best["candidate"],mass,best["lead_s"],best["delays_s"],
                                     output=args.output,label=f"best_{mass}kg_{i+1}"))
    summary = {"required_vz_m_s":REQUIRED_VZ,"pose_samples":args.poses,"limits":limits,
               "matched_baselines": baselines,
               "sampled_kinematic_best":candidates[0],"reports":reports,"best":best,"repeats":repeats,
               "goal_achieved":False,
               "scope":"speed/launch probe only; fixed grasp, robot-cube collision disabled; "
                       "self penetration diagnosed at intervals (every tick for detailed repeats), no self-contact response; "
                       "no full catch or placement task, no global impossibility proof"}
    (args.output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"best":best,"summary":str(args.output/"summary.json")}),flush=True)


if __name__ == "__main__":
    main()
