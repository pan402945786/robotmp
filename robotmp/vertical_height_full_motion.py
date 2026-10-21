"""Capture complete state histories without changing launch or catch control."""
from __future__ import annotations
import bisect
import copy
import csv
import json
from pathlib import Path
import numpy as np
from .vertical_height_catch import ROOT, audit_trial, save, stages
from .throw_catch_online import run_trial
from .long_distance_catch_video import RecordedCatch, digest

VALIDATION = ROOT / 'docs/vertical_height_catch_20261021_final'
MOTION = ROOT / 'docs/vertical_height_catch_20261021_full_motion'


class FullMotionObserver:
    latest = {}
    def __init__(self, offset):
        self.offset = offset
        self.rows = []

    def __call__(self, env, phase, tick):
        if phase in ('flight', 'result'):
            return  # The existing flight trace already records these exact states.
        p, cid = env.p, env.client
        joints = p.getJointStates(env._gripper_id, list(range(1, 7)) + list(range(8, 14)), physicsClientId=cid)
        pos, orientation = p.getBasePositionAndOrientation(env._cube_id, physicsClientId=cid)
        velocity, angular = p.getBaseVelocity(env._cube_id, physicsClientId=cid)
        link = p.getLinkState(env._gripper_id, 6, computeForwardKinematics=True, physicsClientId=cid)
        point = p.multiplyTransforms(link[4], link[5], self.offset, [0, 0, 0, 1])[0]
        contacts = p.getContactPoints(env._cube_id, env._gripper_id, physicsClientId=cid)
        row = dict(absolute_time_s=env._time, phase=phase, q=[j[0] for j in joints[:6]],
            qd=[j[1] for j in joints[:6]], finger_q=[j[0] for j in joints[6:]],
            cube=list(pos), cube_orientation=list(orientation), truth_velocity=list(velocity),
            truth_angular_velocity=list(angular), capture_point=list(point),
            contacts=sorted({c[4] for c in contacts if c[9] > .05}),
            contact_forces=[dict(link=c[4], normal_force_n=c[9]) for c in contacts],
            object_constraint=env._constraint_id is not None,
            distance_m=float(np.linalg.norm(np.array(pos)-point)))
        if self.rows and abs(self.rows[-1]['absolute_time_s']-env._time) < 1e-10:
            self.rows[-1] = row
        else:
            self.rows.append(row)


REPLAY = ROOT / 'docs/vertical_height_catch_20261021_full_replay'


def capture_prethrow(reference_path, output):
    """Record the missing pre-release states; a new catch is not assumed."""
    reference = json.loads(reference_path.read_text(encoding='utf-8'))
    label = reference['label']+'_prethrow'
    observer = FullMotionObserver(reference['capture_offset_m'])
    report = run_trial(copy.deepcopy(reference['controller_parameters']),
        copy.deepcopy(reference['scenario']), output, label, observer=observer)
    if not report.get('released'):
        raise RuntimeError('Prethrow capture did not reach the original release.')
    for row in observer.rows:
        row['time_s'] = row['absolute_time_s']-report['release_time_s']
    save(output/f'{label}_full_motion.json', observer.rows)
    return output/f'{label}_full_motion.json'


def prepare_replays(source=VALIDATION, recordings=MOTION, output=REPLAY):
    output.mkdir(parents=True, exist_ok=True)
    recordings.mkdir(parents=True, exist_ok=True)
    validation = json.loads((source/'summary.json').read_text(encoding='utf-8'))
    entries = []
    keys = ['t_s','x','y','z','vx','vy','vz']+[f'q{i}' for i in range(6)]+[f'qd{i}' for i in range(6)]
    for stage in validation['stages']:
        label = stage['name']+'_03'
        original_path = source/f'{label}.json'
        reference = json.loads(original_path.read_text(encoding='utf-8'))
        candidates = sorted(recordings.glob(label+'*_full_motion.json'))
        if not candidates:
            candidates = [capture_prethrow(original_path,recordings)]
        for candidate in candidates:
            fresh_prefix = candidate.name.removesuffix('_full_motion.json')
            fresh_csv = recordings/f'{fresh_prefix}_physics.csv'
            fresh_flight = recordings/f'{fresh_prefix}_control_trace.json'
            with (source/f'{label}_physics.csv').open(newline='') as f:
                a = [r for r in csv.DictReader(f) if r['phase']!='flight']
            with fresh_csv.open(newline='') as f:
                b = [r for r in csv.DictReader(f) if r['phase']!='flight']
            if len(a)!=len(b):
                continue
            max_error = max(abs(float(x[k])-float(y[k])) for x,y in zip(a,b) for k in keys)
            flight = json.loads((source/f'{label}_control_trace.json').read_text(encoding='utf-8'))
            fresh = json.loads(fresh_flight.read_text(encoding='utf-8'))
            first_error = max(max(abs(x-y) for x,y in zip(flight[0][k],fresh[0][k]))
                for k in ('q','qd','cube','cube_orientation','finger_q','truth_velocity'))
            if max_error>1e-9 or first_error>1e-9:
                continue
            prethrow = json.loads(candidate.read_text(encoding='utf-8'))
            prethrow = [dict(r,source_segment='matched_prethrow_recording') for r in prethrow
                if r['absolute_time_s']<=reference['release_time_s']+1e-9]
            for row in prethrow:
                row['time_s']=row['absolute_time_s']-reference['release_time_s']
            combined = prethrow+[dict(r,phase='flight',object_constraint=False,
                absolute_time_s=r['time_s']+reference['release_time_s'],source_segment='original_validated_flight') for r in flight]
            target = output/f'{label}_full_motion.json'
            save(target,combined)
            sources = [candidate,fresh_csv,fresh_flight,original_path,source/f'{label}_control_trace.json',source/f'{label}_physics.csv']
            entries.append(dict(label=label,original_report=str(original_path.relative_to(ROOT)),
                full_motion=str(target.relative_to(ROOT)),prethrow_recording=str(candidate.relative_to(ROOT)),
                prethrow_numeric_max_error=max_error,release_first_frame_max_error=first_error,
                matching_prethrow_samples=len(a),
                source_sha256={str(f.relative_to(ROOT)):digest(f) for f in sources},
                mode='Matched pre-release recording followed by the original validated flight and hold.'))
            print(json.dumps(dict(label=label,matched_prethrow_error=max_error,
                matched_release_error=first_error,full_motion_samples=len(combined))),flush=True)
            break
        else:
            raise RuntimeError(f'No exactly matched prethrow available: {label}')
    save(output/'manifest.json',dict(records=entries,mode='State-record reconstruction; no controller changes',
        original_validation=str((source/'audit.json').relative_to(ROOT)),
        note='Fresh recording catches can differ with planner wall time; their outcomes are not substituted for validated catches.'))
    recording_audits=[]
    for report_path in sorted(recordings.glob('height*.json')):
        if any(s in report_path.stem for s in ('control_trace','decisions','geometry','observations','full_motion')):
            continue
        report=json.loads(report_path.read_text(encoding='utf-8'))
        stage=next(s for s in stages() if report['label'].startswith(s['name']))
        recording_audits.append(audit_trial(recordings,report,stage['minimum_rise_m']))
    save(recordings/'audit_index.json',dict(records=recording_audits,
        scope='All recording attempts, including failed fresh catches; video uses original validated flight.'))
    return entries


class FullRecordedCatch(RecordedCatch):
    def __init__(self, source, motion):
        super().__init__(source)
        self.flight_rows = self.rows
        self.rows = json.loads(motion.read_text(encoding='utf-8'))
        self.times = [r['time_s'] for r in self.rows]
        assert all(a<b for a,b in zip(self.times,self.times[1:]))
        assert self.times[0]<-1.
        self.swing_start=min(r['time_s'] for r in self.rows if r['phase']=='swing')
        self.apex_time=max(self.flight_rows,key=lambda r:r['cube'][2])['time_s']
        self.sources.append(motion)
        self.hashes[str(motion.relative_to(ROOT))]=digest(motion)


if __name__=='__main__':
    prepare_replays()
