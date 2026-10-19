"""Independently check saved 240 Hz traces and model log completeness."""
import csv
import hashlib
import json
import math
from pathlib import Path


OUTPUT = Path(__file__).resolve().parent
ROOT = OUTPUT.parent.parent


def check_trace(label):
    report = json.loads((OUTPUT / f'{label}.json').read_text(encoding='utf-8'))
    with (OUTPUT / f'{label}_physics.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    events = [json.loads(line) for line in (OUTPUT / 'events.jsonl').read_text(encoding='utf-8').splitlines()]
    events = [event for event in events if event.get('trial') == label]
    release = next(event for event in events if event['kind'] == 'release_measured')
    catch = next(event for event in events if event['kind'] == 'descending_catch_gate_passed')
    t0, t1 = release['state']['timestamp'], catch['state']['timestamp']
    flight = [row for row in rows if t0 < float(row['t_s']) <= t1]
    rise = max(float(row['z_m']) for row in flight) - release['state']['object']['position_m'][2]
    final = rows[-480:]
    speeds = [math.sqrt(sum(float(row[key]) ** 2 for key in ('vx', 'vy', 'vz'))) for row in final]
    angular = [math.sqrt(sum(float(row[key]) ** 2 for key in ('wx', 'wy', 'wz'))) for row in final]
    positions = [[float(row[key]) for key in ('x_m', 'y_m', 'z_m')] for row in final]
    max_drift = max(math.dist(positions[0], pos) for pos in positions)
    checks = {
        'reported_complete_success': report['passed'],
        'free_flight_rise_at_least_005m': rise >= 0.05,
        'all_flight_constraints_absent': all(row['constraint'] == 'False' for row in flight),
        'all_flight_environment_contacts_absent': all(row['contact'] == 'False' for row in flight),
        'at_least_10_flight_steps': len(flight) >= 10,
        'ascent_and_descent_both_sampled': any(float(row['vz']) > 0 for row in flight) and float(flight[-1]['vz']) < -0.05,
        'catch_below_wrist_in_finger_workspace': float(flight[-1]['ee_z']) - float(flight[-1]['z_m']) >= 0.10,
        'last_two_seconds_all_released_and_contacting_ground': len(final) == 480 and all(
            row['constraint'] == 'False' and row['contact'] == 'True' for row in final),
        'last_two_seconds_all_speeds_below_001': max(speeds) <= 0.01,
        'last_two_seconds_all_angular_speeds_below_005': max(angular) <= 0.05,
        'last_two_seconds_max_drift_below_003': max_drift <= 0.003,
    }
    return {'label': label, 'checks': checks, 'passed': all(checks.values()),
            'independently_measured_rise_m': rise, 'unconstrained_flight_steps': len(flight),
            'final_two_second_max_speed_m_s': max(speeds),
            'final_two_second_max_angular_speed_rad_s': max(angular),
            'final_two_second_max_drift_m': max_drift}


def main():
    summary = json.loads((OUTPUT / 'summary.json').read_text(encoding='utf-8'))
    labels = ['attempt_01', 'validation_01', 'validation_02', 'validation_03', 'reloaded_replay']
    traces = [check_trace(label) for label in labels]
    records = [json.loads(line) for line in (OUTPUT / 'model_events.jsonl').read_text(encoding='utf-8').splitlines()]
    ids = sorted({record['request_id'] for record in records})
    calls = []
    for request_id in ids:
        call = [record for record in records if record['request_id'] == request_id]
        kinds = [record['event'] for record in call]
        response = next((record for record in call if record['event'] == 'response'), None)
        complete = kinds == ['request', 'response', 'parsed_output']
        complete = complete and json.loads(response['raw_response']) == response['output']
        calls.append({'request_id': request_id, 'events': kinds, 'complete': complete})
    source = ROOT / 'artifacts/verification_20261019/skills.json'
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    checks = {'all_saved_traces_pass_independent_audit': all(trace['passed'] for trace in traces),
              'all_model_inputs_raw_outputs_and_parsed_outputs_present': bool(calls) and all(call['complete'] for call in calls),
              'source_skill_unchanged': source_hash == summary['source_skill_sha256']
                  == hashlib.sha256((OUTPUT / 'source_skill.json').read_bytes()).hexdigest(),
              'low_grip_force_validation_reused_recovery': summary['validation_reports'][1]['recovery_used'],
              'three_independent_validations': len(summary['validation_reports']) == 3,
              'reloaded_replay_passed': summary['replay']['passed']}
    result = {'passed': all(checks.values()), 'checks': checks, 'traces': traces, 'model_calls': calls}
    (OUTPUT / 'independent_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
