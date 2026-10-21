"""Validate progressively higher vertical throws using fresh causal catch trials."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import sys

# Enable the local Conda runtime when invoked without activating its environment.
_dll_handles = []
if sys.platform == 'win32':
    _dirs = [Path(sys.prefix), Path(sys.prefix) / 'Library/bin', Path(sys.prefix) / 'DLLs']
    _dirs = [d for d in _dirs if d.is_dir()]
    os.environ['PATH'] = os.pathsep.join(map(str, _dirs)) + os.pathsep + os.environ.get('PATH', '')
    _dll_handles = [os.add_dll_directory(str(d)) for d in _dirs]

import numpy as np
from .catch_online_control import RobotModel
from .models import Skill
from dataclasses import asdict
from .throw_catch_online import run_trial

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'docs/vertical_height_catch_20261021_final'


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def stages():
    source = json.loads((ROOT / 'assets/skills/short_vertical_throw_catch_50mm.json').read_text(encoding='utf-8'))[0]
    base = source['parameters']
    result = []
    for name, minimum, gate, spec in [
        ('height_10cm', .10, 1.45, dict(duration_s=.28, speed_m_s=1.8, x_m=.55, start_z_m=1.12, travel_m=.23)),
        ('height_14cm', .13, 1.65, dict(duration_s=.28, speed_m_s=2.2, x_m=.55, start_z_m=1.12, goal_z_m=1.35)),
        ('height_20cm', .20, 2.0, dict(duration_s=.32, speed_m_s=2.6, speed_x_m_s=.1, x_m=.65, start_z_m=1., goal_z_m=1.23, max_horizontal_m_s=.15)),
        ('height_50cm', .49, 3.0, None),
    ]:
        parameters = copy.deepcopy(base)
        scenario = dict(cube_size_m=.05, mass_kg=.1, pre_spin=False, release_gate=gate,
                        release_inward_only=False, noise_m=0., latency_s=0., drop_rate=0., drag=.025, sensor_hz=60)
        if spec is not None:
            scenario['vertical_toss'] = spec
        if name != 'height_10cm':
            parameters.update(stationary_catch=False, descent_servo=True, servo_start_distance_m=.35,
                              servo_close_distance_m=.085, servo_position_gain=12.,
                              servo_acceleration_rad_s2=40., servo_angular_weight=.3)
        if name == 'height_50cm':
            scenario.update(swing_scale=.6, release_inward_only=True, release_radial_speed_max_m_s=0.)
            parameters.update(ik_seeds=1, ik_iterations=35, servo_start_distance_m=.4,
                              contact_brake_confirmation_ticks=12)
        parameters['launch_profile'] = {k: copy.deepcopy(v) for k, v in scenario.items()
                                        if k in ('release_gate', 'pre_spin', 'release_inward_only',
                                                 'release_radial_speed_max_m_s', 'swing_scale', 'vertical_toss')}
        result.append(dict(name=name, minimum_rise_m=minimum, parameters=parameters, scenario=scenario))
    return result


def audit_trial(output, report, minimum_rise):
    label = report['label']
    files = [output / f'{label}{suffix}' for suffix in
             ('.json', '_control_trace.json', '_physics.csv', '_observations.json', '_decisions.json')]
    if not report.get('released') or not all(f.exists() for f in files):
        return dict(label=label, passed=False, reason=report.get('error', 'release_or_evidence_missing'))
    trace = json.loads(files[1].read_text(encoding='utf-8'))
    with files[2].open(newline='', encoding='utf-8') as stream:
        physics = list(csv.DictReader(stream))
    flight = [r for r in physics if r['phase'] == 'flight']
    observations = json.loads(files[3].read_text(encoding='utf-8'))
    decisions = json.loads(files[4].read_text(encoding='utf-8'))
    consistency = len(flight) == len(trace)
    error = max((math.dist([float(c[k]) for k in ('x', 'y', 'z')], r['cube'])
                 for c, r in zip(flight, trace)), default=math.inf)
    captured = report.get('capture_contact_time_s')
    held = [r for r in trace if captured is not None and r['time_s'] >= captured - 1e-8]
    def bilateral(row):
        links = {f['link'] for f in row['contact_forces'] if f['normal_force_n'] > .05}
        return {9, 12}.issubset(links) and row['collision_enabled']
    every_hold_frame = bool(held and all(bilateral(r) for r in held))
    hold_s = held[-1]['time_s'] - held[0]['time_s'] if held else 0.
    speed = float(np.linalg.norm(trace[-1]['truth_velocity']))
    no_constraint = all(r['constraint'] == 'False' for r in flight)
    model = RobotModel()
    try:
        infos = [model.p.getJointInfo(model.arm, j, physicsClientId=model.client) for j in model.joints]
        lower, upper, effort = (np.array([i[k] for i in infos]) for k in (8, 9, 10))
        q = np.array([[float(r[f'q{i}']) for i in range(6)] for r in physics])
        qd = np.array([[float(r[f'qd{i}']) for i in range(6)] for r in physics])
        tau = np.array([[float(r[f'tau{i}']) for i in range(6)] for r in physics])
        max_speed_ratio = float(np.max(np.abs(qd) / model.vmax))
        max_torque_ratio = float(np.max(np.abs(tau) / effort))
        motion = bool(np.all(q >= lower - .001) and np.all(q <= upper + .001)
                      and max_speed_ratio <= 1.05 and max_torque_ratio <= 1.001
                      and not report['self_penetration_detected'])
    finally:
        model.close()
    causal = bool(len(observations) >= 4 and decisions and
        all(o['captured_at'] <= o['delivered_at'] + 1e-8 and o['delivered_at'] <= o['received_at'] + 1e-8 for o in observations)
        and all(d['latest_observation_at'] <= d['issued_at'] + 1e-8 for d in decisions))
    first_contact = report.get('first_robot_contact_time_s')
    enabled = report.get('collision_reenabled_at_s')
    separation = bool(report.get('free_flight_separation_verified') and enabled is not None
        and first_contact is not None and enabled + 1 / 240 <= first_contact + 1e-8
        and report['collision_clearance_at_enable_m'] >= .015)
    free = [r for r in trace if first_contact is None or r['time_s'] < first_contact - 1e-8]
    rise = max(r['cube'][2] for r in free) - report['release_position'][2]
    initial = bool(report['initial_grasp_evidence']['verified']
                   and report['initial_grasp_evidence']['consecutive_contact_ticks'] >= 12
                   and report['pre_release_grasp_checks']['passed']
                   and report['pre_release_grasp_checks']['max_positive_gap_m'] <= .002)
    ratio = math.hypot(*report['release_velocity'][:2]) / report['release_velocity'][2]
    passed = bool(initial and causal and motion and separation and no_constraint and every_hold_frame
                  and hold_s >= 1. - 1e-8 and speed < .05 and consistency and error < 1e-9
                  and rise >= minimum_rise and ratio <= .12 and not report['ground_contact'])
    return dict(label=label, passed=passed, measured_free_flight_rise_m=rise,
                source_report_success=report['complete_success'], hold_duration_s=hold_s,
                every_hold_frame_has_opposed_forces=every_hold_frame, final_speed_m_s=speed,
                no_object_constraint_after_release=no_constraint, initial_grasp_verified=initial,
                causal=causal, motion=motion, separation=separation,
                max_joint_speed_ratio=max_speed_ratio, max_torque_ratio=max_torque_ratio,
                csv_trace_position_error_m=error, release_horizontal_to_vertical_speed_ratio=ratio,
                source_sha256={f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files})


def make_skill(summary, output):
    return Skill(
        skill_id='progressive_vertical_throw_catch_50mm_v1',
        name='contact_checked_progressive_vertical_throw_catch_50mm',
        status='verified', version=1, task='progressive_vertical_throw_catch_50mm',
        object_types=['cube'],
        trigger_conditions=['PyBullet xArm6', '50 mm cube, 100 g',
            'Initial opposed contact and pre-release grasp geometry verified',
            'Clean 60 Hz position observations, drag 0.025',
            'Use only one of the four independently validated configurations'],
        prerequisite_skill_ids=['short_vertical_throw_catch_50mm_v1'],
        validation_trials=len(summary['reports']), validation_success_rate=1., false_success_rate=0.,
        facts=['The historical reference supplied the coordinated upward swing method, not a saved flight intercept.',
               'Wait for observed separation and use delivered positions plus current encoders for descent following.',
               'Confirm sustained bilateral tactile contact before contact braking at the 50 cm stage.',
               'One second of continuous opposed forces and no object constraint are required.',
               'Success at discrete stages does not prove success at all intervening or higher heights.'],
        hypotheses=['Higher stages require separate release and catch validation'],
        prediction_correction=['Estimate descent from delivered timestamped position observations',
            'Use current encoders for bounded descent following', 'Do not read historical flight endpoints'],
        recovery=['Reset contact confirmation after single-finger contact, stale observations, or rising motion',
            'Record failed higher configurations without promoting them', 'Preserve motion and contact-hold gates'],
        parameters=dict(stage_configs=summary['stages']),
        validation_metrics=dict(discrete_stage_count=4, independent_passes=len(summary['reports']),
            max_verified_rise_m=max(s['measured_rise_m'] for s in summary['stages']),
            scope='Discrete configurations only; PyBullet xArm6, 50 mm cube, 100 g, clean observations',
            height_definition='Free-flight apex minus measured release height, before robot contact',
            evidence=str(output.relative_to(ROOT) / 'audit.json')))


def run(output, trials):
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'summary.json').exists():
        raise ValueError('Choose a new output directory; existing experiments are preserved.')
    summary = dict(objective='Increasing vertical rise above release followed by a physical one-second catch',
                   reference_video='docs/best_online_catch_video_20261020', reports=[], stages=[], goal_achieved=False)
    audit_records = []
    for stage in stages():
        records = []
        for index in range(trials):
            scene = dict(stage['scenario'], seed=23100 + len(summary['reports']))
            report = run_trial(stage['parameters'], scene, output, f'{stage["name"]}_{index + 1:02d}')
            summary['reports'].append(report)
            evidence = audit_trial(output, report, stage['minimum_rise_m'])
            audit_records.append(evidence)
            records.append(evidence)
            print(json.dumps(evidence, ensure_ascii=False), flush=True)
        passed = all(r['passed'] for r in records)
        summary['stages'].append(dict(name=stage['name'], passes=sum(r['passed'] for r in records),
            trials=trials, passed=passed,
            measured_rise_m=min((r.get('measured_free_flight_rise_m', 0.) for r in records), default=0.),
            parameters=stage['parameters'], scenario=stage['scenario']))
        save(output / 'summary.json', summary)
        save(output / 'audit.json', dict(records=audit_records, independent_passes=sum(r['passed'] for r in audit_records)))
        if not passed:
            break
    summary['goal_achieved'] = bool(len(summary['stages']) == 4 and all(s['passed'] for s in summary['stages']))
    save(output / 'summary.json', summary)
    if summary['goal_achieved'] and trials >= 3:
        save(ROOT / 'assets/skills/progressive_vertical_throw_catch_50mm.json',
             [asdict(make_skill(summary, output))])
    print(json.dumps(dict(goal_achieved=summary['goal_achieved'], stages=[
        {k: s[k] for k in ('name', 'passes', 'trials', 'measured_rise_m')} for s in summary['stages']]), indent=2), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--trials-per-stage', type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.trials_per_stage <= 6:
        parser.error('--trials-per-stage must be 1 to 6')
    result = run(args.output.resolve(), args.trials_per_stage)
    if not result['goal_achieved']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
