"""Audited 5 cm free-flight toss, descending catch and gentle ground placement."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, replace
import hashlib
import json
import math
from pathlib import Path
import subprocess

from .diagnosis import LLMConfig, OpenAICompatibleDiagnoser
from .environment import FailureMode
from .figure_eight import Journal, PREREQUISITE
from .models import Skill
from .monitor import compare_prediction
from .predictor import make_prediction
from .runner import default_store
from .sim_environment import SimConfig
from .throw_catch import ThrowEnv as BaseThrowEnv

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = Path('docs/throw_catch_005m_20261019')
SKILL_PATH = Path('assets/skills/throw_005m_catch_ground.json')
TARGET_RISE_M = 0.05
REQUIRED_VZ = math.sqrt(2 * 9.81 * TARGET_RISE_M)


class Audit(Journal):
    def checkpoint(self, reason):
        paths = [self.document, self.model_document, self.output, SKILL_PATH,
                 Path('robotmp/throw_catch_005m.py'), Path('tests/test_throw_catch_005m.py')]
        subprocess.run(['git', 'add', '--', *[str(p) for p in paths if p.exists()]],
                       cwd=ROOT, check=True, capture_output=True)
        diff = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=ROOT)
        if diff.returncode == 1:
            result = subprocess.run(['git', 'commit', '-m', f'experiment: {reason}'],
                                    cwd=ROOT, check=True, capture_output=True,
                                    text=True, encoding='utf-8')
            print(result.stdout.strip(), flush=True)
        elif diff.returncode:
            raise RuntimeError('git diff failed')

    def model_event(self, record):
        super().model_event(record)
        self.checkpoint(f"5cm model {record['event']} {record.get('request_id', '')[:8]}")


def validate_parameters(raw):
    bounds = {'target_x_m': (0.25, 0.55), 'target_z_m': (0.40, 0.85),
              'release_min_vz_m_s': (1.04, 1.40), 'max_sweep_steps': (20, 180),
              'catch_lead_s': (0.0, 0.12)}
    if not isinstance(raw, dict) or set(raw) != set(bounds):
        raise ValueError(f'parameters must contain exactly {list(bounds)}')
    for key, (low, high) in bounds.items():
        value = raw[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f'{key} must be finite numeric')
        if not low <= value <= high:
            raise ValueError(f'{key} outside [{low}, {high}]')
    if not isinstance(raw['max_sweep_steps'], int):
        raise ValueError('max_sweep_steps must be integer')
    return dict(raw)


def catch_gate(position, velocity, ee, ee_velocity, *, had_apex, rise, ticks, contact):
    return bool(had_apex and rise >= TARGET_RISE_M and ticks >= 10 and not contact
                and velocity[2] < -0.05 and math.dist(position, ee) <= 0.13
                and math.dist(velocity, ee_velocity) <= 1.0)


def acceptance(report):
    return bool(report.get('lift_confirmed') and report.get('release_vz_m_s', 0) >= REQUIRED_VZ
                and report.get('free_flight') and report.get('rise_from_release_m', 0) >= TARGET_RISE_M
                and report.get('had_apex') and not report.get('flight_contact_before_catch', True)
                and report.get('caught') and report.get('catch_hold_passed')
                and report.get('placement', {}).get('passed')
                and max(report.get('max_joint_velocity_ratios', [math.inf])) <= 1.05
                and 'error' not in report)


class ThrowEnv(BaseThrowEnv):
    def _set_xarm_pose(self, position, *, open_gripper):
        if not hasattr(self, 'placement_orientation'):
            return super()._set_xarm_pose(position, open_gripper=open_gripper)
        p = self.p
        self._ee_position = list(position)
        solution = p.calculateInverseKinematics(
            self._gripper_id, self._ee_link_index, position,
            targetOrientation=self.placement_orientation,
            lowerLimits=self._arm_lower, upperLimits=self._arm_upper,
            jointRanges=[b - a for a, b in zip(self._arm_lower, self._arm_upper)],
            restPoses=[0.] * 6, maxNumIterations=200, residualThreshold=1e-5,
            physicsClientId=self.client)
        for i, (joint, target) in enumerate(zip(self._arm_joint_ids, solution[:6])):
            p.setJointMotorControl2(self._gripper_id, joint, p.POSITION_CONTROL,
                targetPosition=min(self._arm_upper[i], max(self._arm_lower[i], target)),
                force=self._arm_effort[i], maxVelocity=self._arm_velocity[i], physicsClientId=self.client)
        self._gripper_open = open_gripper
        p.setJointMotorControl2(self._gripper_id, self._finger_joint_ids[0], p.POSITION_CONTROL,
            targetPosition=0. if open_gripper else 0.85, force=50, maxVelocity=2, physicsClientId=self.client)

    def reset(self):
        super().reset()
        # Ground scene is created before any task action, without moving the cube.
        self.p.removeBody(self._table_id, physicsClientId=self.client)
        self.ground = self.p.loadURDF('plane.urdf', physicsClientId=self.client)
        self._step(24)
        return self.observe()

    def support_height(self):
        _, orientation = self.p.getBasePositionAndOrientation(self._cube_id, physicsClientId=self.client)
        matrix = self.p.getMatrixFromQuaternion(orientation)
        return self.config.cube_half_extent * sum(abs(v) for v in matrix[6:9])


class CameraVideo:
    def __init__(self, path):
        import imageio_ffmpeg
        self.frames = 0
        self.path = path
        self.error_stream = path.with_suffix('.ffmpeg.log').open('w', encoding='utf-8')
        self.process = subprocess.Popen([
            imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', '-f', 'rawvideo',
            '-pix_fmt', 'rgb24', '-s', '1280x720', '-r', '30', '-i', '-', '-an',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart', str(path)], stdin=subprocess.PIPE, stderr=self.error_stream)

    def capture(self, env, report):
        from PIL import Image, ImageDraw, ImageFont
        p = env.p
        view = p.computeViewMatrixFromYawPitchRoll([0.30, 0, 0.30], 1.25, 50, -22, 0, 2)
        projection = p.computeProjectionMatrixFOV(48, 960 / 720, 0.02, 4)
        _, _, rgba, _, _ = p.getCameraImage(960, 720, view, projection,
                                           renderer=p.ER_TINY_RENDERER, physicsClientId=env.client)
        frame = Image.new('RGB', (1280, 720), '#101d30')
        frame.paste(Image.fromarray(rgba[:, :, :3]), (0, 0))
        draw = ImageDraw.Draw(frame)
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 19)
        title = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 25)
        draw.rectangle((0, 0, 960, 74), fill='#101d30')
        draw.text((20, 10), '抓取 → 自由抛起至少 5 cm → 接住 → 平稳放地', font=title, fill='#70e4ff')
        draw.text((20, 46), f'PyBullet xArm6 | 仿真 {env._time:.2f}s | 固定约束模拟抓持', font=font, fill='white')
        z = env._cube_position()[2]
        velocity, _ = p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        lines = ['实测状态', f'阶段：{env._phase}', f'物体中心：{z:.4f} m',
                 f'向上速度：{velocity[2]:.3f} m/s',
                 f'抓持约束：{"有" if env._constraint_id is not None else "无"}',
                 f'释放高度：{report.get("release_height_m", 0):.4f} m',
                 f'飞行升高：{report.get("rise_from_release_m", 0):.4f} m',
                 '目标升高：≥ 0.0500 m', f'下降接住：{"是" if report.get("caught") else "等待"}',
                 f'地面静置：{"通过" if report.get("placement", {}).get("passed") else "等待"}',
                 '重力：9.81 m/s²', '30 fps / 飞行片段慢放 4×']
        for i, line in enumerate(lines):
            draw.text((978, 30 + i * 43), line, font=font, fill='#70e4ff' if i == 0 else 'white')
        if env._phase == 'transport' and not env._grasped:
            draw.text((20, 680), '物体无抓持约束：真实自由飞行（慢放 4×）', font=font, fill='#ffb858')
        self.process.stdin.write(frame.tobytes())
        self.frames += 1

    def close(self):
        self.process.stdin.close()
        code = self.process.wait()
        self.error_stream.close()
        if code:
            raise RuntimeError(f'ffmpeg exited {code}')


def execute_trial(parameters, old, audit, label, failure=FailureMode.NONE, video_path=None):
    parameters = validate_parameters(parameters)
    report = {'label': label, 'parameters': parameters, 'failure_mode': failure.value,
              'applied_skill_ids': [old.skill_id], 'lift_confirmed': False, 'caught': False,
              'free_flight': False, 'placement': {'passed': False}, 'recovery_used': False}
    env = None
    samples = 0
    max_ratios = [0.] * 6
    video = CameraVideo(video_path) if video_path else None
    stream = (audit.output / f'{label}_physics.csv').open('w', newline='', encoding='utf-8')
    writer = csv.writer(stream)
    writer.writerow(['t_s', 'phase', 'x_m', 'y_m', 'z_m', 'vx', 'vy', 'vz', 'wx', 'wy', 'wz',
                     'ee_x', 'ee_y', 'ee_z', 'constraint', 'contact',
                     *[f'joint_{i}_velocity' for i in range(1, 7)]])

    def sample(state):
        nonlocal samples
        if env is None:
            return
        linear, angular = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        joints = [env.p.getJointState(env._gripper_id, j, physicsClientId=env.client)[1]
                  for j in env._arm_joint_ids]
        for i, value in enumerate(joints):
            max_ratios[i] = max(max_ratios[i], abs(value) / env._arm_velocity[i])
        writer.writerow([state.timestamp, state.phase, *state.object.position_m, *linear, *angular,
                         *state.robot.end_effector_position_m, env._constraint_id is not None,
                         bool(env.p.getContactPoints(env._cube_id, physicsClientId=env.client)), *joints])
        stream.flush()
        samples += 1
        # 30 fps normally, 120 simulation samples/s in free flight for 4x slow motion.
        if video and samples % (2 if env._phase == 'transport' and not env._grasped else 8) == 0:
            video.capture(env, report)

    def emit(kind, **detail):
        audit.event({'trial': label, 'kind': kind, 'state': asdict(env.observe()), **detail})

    def action(name):
        env.execute(name)
        emit('action', action=name)

    def move_object(target, steps):
        state = env.observe()
        ee_target = [ee + goal - actual for ee, goal, actual in zip(
            state.robot.end_effector_position_m, target, state.object.position_m)]
        env._set_gripper_pose(ee_target, open_gripper=False)
        env._step(steps)

    audit.note(f'开始 {label}：参数 {json.dumps(parameters)}；故障 {failure.value}。')
    audit.checkpoint(f'begin 5cm trial {label}')
    try:
        env = ThrowEnv(failure, config=SimConfig(arm_model='xarm6', table_z=0, frame_callback=sample))
        emit('ground_scene_ready', ground_z_m=0, ideal_grasp_model='fixed_constraint')
        emit('prerequisite_retrieved', skill=asdict(old))
        action('approach_object')
        action('close_gripper')
        prediction = make_prediction(env.observe(), [old])
        action('lift_object')
        comparison = compare_prediction(prediction, env.observe())
        emit('lift_comparison', prediction=asdict(prediction), comparison=asdict(comparison))
        if comparison.status != 'match':
            report['recovery_used'] = True
            emit('existing_skill_recovery', recovery=old.recovery)
            for name in ['refresh_object_pose', 'retry_grasp', 'close_gripper', 'lift_object']:
                action(name)
        if not env._grasped or not env.observe().object.lifted:
            raise RuntimeError('no measured lift; release blocked')
        report['lift_confirmed'] = True
        emit('lift_gate_passed')
        audit.checkpoint(f'5cm {label} grasp and lift measured')
        # Settle the held object before a dedicated launch sweep.
        env._phase = 'trace'
        move_object([0.40, 0, 0.22], 240)
        emit('launch_start_settled')
        before = env.observe()
        offset = [a - b for a, b in zip(before.robot.end_effector_position_m, before.object.position_m)]
        target = [parameters['target_x_m'], 0, parameters['target_z_m']]
        ee_target = [a + b for a, b in zip(target, offset)]
        env._set_gripper_pose(ee_target, open_gripper=False)
        emit('upward_sweep_commanded', target=target)
        launch_v = [0, 0, 0]
        max_vz = -math.inf
        for tick in range(parameters['max_sweep_steps']):
            env._step(1)
            launch_v, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            max_vz = max(max_vz, launch_v[2])
            emit('sweep_step', tick=tick, velocity=list(launch_v))
            if launch_v[2] >= parameters['release_min_vz_m_s']:
                break
        report['max_sweep_vz_m_s'] = max_vz
        if launch_v[2] < parameters['release_min_vz_m_s']:
            raise RuntimeError('current measured release speed gate blocked')
        release = env.release_in_motion()
        pos0 = release.object.position_m
        launch_v, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        report.update(release_height_m=pos0[2], release_vz_m_s=launch_v[2],
                      release_velocity_m_s=list(launch_v), release_time_s=env._time)
        emit('release_measured', velocity=list(launch_v), required_vz_m_s=REQUIRED_VZ,
             constraint_active=env._constraint_id is not None)
        audit.checkpoint(f'5cm {label} release measured')
        apex = pos0[2]
        had_apex = False
        flight_contact = False
        ee_previous = env._actual_ee_position()
        for tick in range(480):
            pos = env._cube_position()
            vel, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            # Track the moving cube horizontally while keeping the wrist near launch height.
            lead = parameters['catch_lead_s']
            intercept = [pos[0] + vel[0] * lead + offset[0],
                         pos[1] + vel[1] * lead + offset[1], pos0[2] + offset[2]]
            env._set_gripper_pose(intercept, open_gripper=True)
            env._step(1)
            pos = env._cube_position()
            vel, _ = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            ee = env._actual_ee_position()
            ee_vel = [(a - b) / env.config.time_step_s for a, b in zip(ee, ee_previous)]
            ee_previous = ee
            contacts = env.p.getContactPoints(env._cube_id, physicsClientId=env.client)
            flight_contact |= bool(contacts)
            apex = max(apex, pos[2])
            report['rise_from_release_m'] = apex - pos0[2]
            if vel[2] <= 0 and not had_apex:
                had_apex = True
                emit('apex_observed', apex_height_m=apex, rise_m=apex - pos0[2])
            emit('flight_step', velocity=list(vel), ee_velocity=ee_vel,
                 catch_distance_m=math.dist(pos, ee), relative_speed_m_s=math.dist(vel, ee_vel),
                 constraint_active=env._constraint_id is not None, contact=bool(contacts))
            if catch_gate(pos, vel, ee, ee_vel, had_apex=had_apex, rise=apex - pos0[2],
                          ticks=tick + 1, contact=flight_contact):
                report.update(caught=True, catch_time_s=env._time, catch_vz_m_s=vel[2],
                              catch_distance_m=math.dist(pos, ee), catch_relative_speed_m_s=math.dist(vel, ee_vel))
                env.catch()
                emit('descending_catch_gate_passed', distance_m=report['catch_distance_m'],
                     relative_speed_m_s=report['catch_relative_speed_m_s'])
                break
            if contacts:
                emit('flight_failed_environment_contact', bodies=[c[2] for c in contacts])
                break
        report.update(apex_height_m=apex, rise_from_release_m=apex - pos0[2],
                      had_apex=had_apex, free_flight=tick + 1 >= 10, flight_ticks=tick + 1,
                      flight_contact_before_catch=flight_contact)
        if not report['caught']:
            raise RuntimeError('descending catch gate not reached')
        env._phase = 'trace'
        env._step(120)
        report['catch_hold_passed'] = bool(env._constraint_id is not None and env._grasped
                                         and env._cube_position()[2] > 0.10)
        emit('catch_hold_evaluation', passed=report['catch_hold_passed'])
        audit.checkpoint(f'5cm {label} flight and catch measured')
        env._phase = 'place'
        # Rotate the held cube upright using wrist IK, never by resetting the cube.
        p = env.p
        cube_pos, cube_orn = p.getBasePositionAndOrientation(env._cube_id, physicsClientId=env.client)
        ee_orn = p.getLinkState(env._gripper_id, env._ee_link_index,
                              computeForwardKinematics=True, physicsClientId=env.client)[5]
        _, inv_ee = p.invertTransform([0, 0, 0], ee_orn)
        _, relative = p.multiplyTransforms([0, 0, 0], inv_ee, [0, 0, 0], cube_orn)
        _, upright_ee = p.invertTransform([0, 0, 0], relative)
        if sum(a * b for a, b in zip(ee_orn, upright_ee)) < 0:
            upright_ee = [-v for v in upright_ee]
        for index in range(1, 61):
            alpha = index / 60
            q = [(1 - alpha) * a + alpha * b for a, b in zip(ee_orn, upright_ee)]
            norm = math.sqrt(sum(v * v for v in q))
            env.placement_orientation = [v / norm for v in q]
            move_object(list(cube_pos), 4)
            emit('held_cube_uprighting', index=index)
        move_object(list(cube_pos), 120)
        emit('held_cube_upright_settled', support_height_m=env.support_height())
        # Feedback lowering uses actual pose and the rotated cube's support extent.
        for step in range(700):
            pos = env._cube_position()
            support = env.support_height()
            linear, angular = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            contacts = env.p.getContactPoints(env._cube_id, env.ground, physicsClientId=env.client)
            if contacts and math.dist(linear, [0, 0, 0]) < 0.015:
                emit('ground_supported_before_release', support_height_m=support, velocity=list(linear))
                break
            drop = min(0.002, max(0.0001, pos[2] - support + 0.0001))
            move_object([pos[0], pos[1], max(support - 0.0002, pos[2] - drop)], 12)
            emit('ground_lowering_step', index=step, support_height_m=support)
        else:
            raise RuntimeError('ground lowering did not reach low-speed support')
        linear, angular = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        initial = env._cube_position()
        report['placement_release_speed_m_s'] = math.dist(linear, [0, 0, 0])
        report['placement_release_height_m'] = initial[2]
        # Record before removal; execute(release_object) itself advances 48 steps.
        emit('gentle_release_before', position=initial, velocity=list(linear))
        action('release_object')
        for window in range(8):
            env.settle_object(steps=60)
            emit('ground_settle_observation', window=window)
        final = env._cube_position()
        linear, angular = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
        placement = {'drift_m': math.dist(initial, final), 'speed_m_s': math.dist(linear, [0, 0, 0]),
                     'angular_speed_rad_s': math.dist(angular, [0, 0, 0]),
                     'ground_contact': bool(env.p.getContactPoints(env._cube_id, env.ground, physicsClientId=env.client)),
                     'height_error_m': abs(final[2] - env.support_height()),
                     'released': not env._grasped and env._constraint_id is None}
        placement['passed'] = bool(placement['ground_contact'] and placement['released']
                                   and placement['drift_m'] <= 0.003 and placement['speed_m_s'] <= 0.01
                                   and placement['angular_speed_rad_s'] <= 0.05 and placement['height_error_m'] <= 0.003
                                   and report['placement_release_speed_m_s'] <= 0.015)
        report['placement'] = placement
        emit('placement_evaluation', metrics=placement)
        if video:
            for _ in range(30):
                video.capture(env, report)
    except Exception as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
        if env is not None:
            emit('trial_error', error=report['error'])
        else:
            audit.event({'trial': label, 'kind': 'trial_error', 'error': report['error']})
    finally:
        if env is not None:
            env.close()
        stream.close()
        if video:
            video.close()
            report['video_frames'] = video.frames
    report['physics_samples'] = samples
    report['max_joint_velocity_ratios'] = max_ratios
    report['passed'] = acceptance(report)
    (audit.output / f'{label}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    audit.note(f'{label} 结束：{json.dumps(report, ensure_ascii=False)}')
    audit.checkpoint(f'5cm measured trial {label}')
    return report


def propose(client, old, reports, previous=None):
    return client.request_json(
        'Design a high-level skill experiment in local PyBullet xArm6. JSON only, Chinese prose. '
        'Goal: grasp, toss upward with measured free-flight rise >=0.05m from release, catch on descent, '
        'place gently on ground z=0. Reuse grasp_without_lift_v1. Ground scene, arm base z=0. '
        'No object position/velocity injection, launch force, gravity change, joint-limit change. '
        'Idealized fixed-constraint grasp/catch; robot-cube collision disabled, so results are simulation scoped. '
        'Predefined local primitive settles held cube near [0.40,0,0.22], sweeps toward target, releases at FIRST '
        'step when CURRENT vz >= release_min_vz_m_s, then follows horizontal flight with catch_lead_s. '
        'Catch requires real apex, rise>=0.05m, descending vz<-0.05m/s, wrist distance<=0.13m, relative '
        'speed<=1m/s, >=10 unconstrained ticks, no flight contact. Then hold 0.5s, lower slowly to actual '
        'ground support, release at speed<=0.015m/s, observe 2s, drift<=0.003m, speed<=0.01m/s. '
        'Choose parameters exactly: target_x_m [0.25,0.55], target_z_m [0.40,0.85], '
        'release_min_vz_m_s [1.04,1.40], max_sweep_steps integer [20,180], catch_lead_s [0,0.12]. '
        'Return decision try/stop/accept, prerequisite_skill_ids ["grasp_without_lift_v1"], parameters, '
        'observed_facts array, hypotheses array, rationale string. First response must try. '
        'After a success propose the SAME parameters for independent validation. Accept only after '
        'three complete consecutive validation trials. Preserve the exact 0.05m target throughout. '
        'No code or low-level joint commands. Use actual measured reports to refine parameters.',
        {'goal': '抓起→自由飞行相对升高至少0.05米→下降接住→平稳放到z=0地面',
         'existing_verified_skill': asdict(old), 'target_rise_m': TARGET_RISE_M,
         'required_vz_m_s': REQUIRED_VZ, 'reports': reports, 'previous': previous})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--seed-store', type=Path, default=Path('artifacts/verification_20261019/skills.json'))
    parser.add_argument('--max-attempts', type=int, default=6)
    parser.add_argument('--probe', type=Path, help='Run a logged local calibration from a JSON parameter file')
    parser.add_argument('--replay-only', action='store_true')
    args = parser.parse_args()
    if args.max_attempts < 1:
        parser.error('--max-attempts must be positive')
    audit = Audit(args.output, Path('docs/THROW_CATCH_005M_LEARNING.md'), Path('docs/THROW_CATCH_005M_LLM_CALLS.md'))
    old = next(s for s in default_store(args.seed_store).all() if s.skill_id == PREREQUISITE and s.status == 'verified')
    if 'require_lift_evidence_before_transport' not in old.prediction_correction:
        raise ValueError('prerequisite lacks lift evidence invariant')
    source_hash = hashlib.sha256(args.seed_store.read_bytes()).hexdigest()
    (args.output / 'source_skill.json').write_bytes(args.seed_store.read_bytes())
    audit.event({'kind': 'source_verified', 'source_path': str(args.seed_store), 'sha256': source_hash,
                 'target_rise_m': TARGET_RISE_M, 'ground_z_m': 0})
    if args.probe:
        report = execute_trial(json.loads(args.probe.read_text(encoding='utf-8-sig')), old, audit, 'calibration')
        return 0 if report['passed'] else 2
    if args.replay_only:
        skill = next(s for s in default_store(SKILL_PATH).all() if s.status == 'verified')
        report = execute_trial(skill.parameters, old, audit, 'reloaded_replay', video_path=args.output / 'demo.mp4')
        return 0 if report['passed'] else 2
    if (args.output / 'summary.json').exists():
        raise ValueError('completed output exists; use a fresh --output')
    config = replace(LLMConfig.from_env(), log_path=str(args.output / 'llm_full.jsonl'), timeout_seconds=180)
    client = OpenAICompatibleDiagnoser(config, log_observer=audit.model_event)
    reports, proposals, validations = [], [], []
    failure = None
    try:
        for attempt in range(1, args.max_attempts + 1):
            proposal = propose(client, old, reports, proposals[-1] if proposals else None)
            proposals.append(proposal)
            if proposal.get('prerequisite_skill_ids') != [PREREQUISITE]:
                raise ValueError('model did not explicitly reuse source skill')
            params = validate_parameters(proposal.get('parameters'))
            if proposal.get('decision') == 'stop':
                audit.note('模型建议停止当前原语搜索；保存测量结果。')
                break
            if proposal.get('decision') != 'try':
                raise ValueError('learning proposal must choose try or stop')
            audit.event({'kind': 'model_proposal_validated', 'proposal': proposal})
            report = execute_trial(params, old, audit, f'attempt_{attempt:02d}')
            reports.append(report)
            if report['passed']:
                # Return measured success to model before freezing parameters for validation.
                review = propose(client, old, reports, proposal)
                proposals.append(review)
                reviewed = validate_parameters(review.get('parameters'))
                if review.get('decision') != 'try' or reviewed != params:
                    audit.note('模型修改成功参数；继续学习后再正式验证。')
                    continue
                audit.note('冻结成功参数，开始三次独立完整验证：正常、低夹持力恢复、正常。')
                for i, mode in enumerate([FailureMode.NONE, FailureMode.LOW_GRIP_FORCE, FailureMode.NONE], 1):
                    validations.append(execute_trial(params, old, audit, f'validation_{i:02d}', mode))
                reports.extend(validations)
                final_review = propose(client, old, reports, review)
                proposals.append(final_review)
                if all(r['passed'] for r in validations):
                    break
                validations = []
        if reports and not validations:
            proposals.append(propose(client, old, reports, proposals[-1]))
    except Exception as exc:
        failure = f'{type(exc).__name__}: {exc}'
        audit.note(f'学习流程事件：{failure}')
    complete = len(validations) == 3 and all(r['passed'] for r in validations)
    selected = validations[-1] if complete else next((r for r in reversed(reports) if r['passed']), reports[-1] if reports else None)
    skill = Skill(skill_id='throw_005m_catch_ground_v1', name='throw_005m_catch_ground',
        status='verified' if complete else 'candidate', version=1, task='throw_catch_ground', object_types=['cube'],
        trigger_conditions=['object_visible == true', 'ground_reachable == true'],
        facts=['0.05m_measured_free_flight_rise_required', 'fixed_constraint_simulation_only',
               'descending_catch_and_low_speed_ground_placement_are_separate_gates'],
        hypotheses=[], prediction_correction=['require_lift_evidence_before_release',
            'gate_release_on_current_measured_velocity', 'require_unconstrained_apex_before_catch',
            'require_ground_support_before_gentle_release'],
        recovery=old.recovery + ['block_release_without_current_velocity', 'retain_failed_trial_evidence'],
        prerequisite_skill_ids=[PREREQUISITE], parameters=selected['parameters'] if selected else {},
        validation_trials=len(validations), validation_success_rate=sum(r['passed'] for r in validations) / len(validations) if validations else 0,
        validation_metrics={'complete_three_trial_validation': complete, 'target_rise_m': TARGET_RISE_M,
            'min_validation_rise_m': min((r.get('rise_from_release_m', 0) for r in validations), default=0),
            'max_validation_placement_drift_m': max((r.get('placement', {}).get('drift_m', 0) for r in validations), default=0)})
    default_store(SKILL_PATH).save_candidate(skill)
    replay = None
    if complete:
        reloaded = next(s for s in default_store(SKILL_PATH).all() if s.skill_id == skill.skill_id and s.status == 'verified')
        replay = execute_trial(reloaded.parameters, old, audit, 'reloaded_replay', video_path=args.output / 'demo.mp4')
    summary = {'goal_achieved': complete, 'new_skill_status': skill.status, 'error': failure,
               'source_skill_sha256': source_hash,
               'source_unchanged': source_hash == hashlib.sha256(args.seed_store.read_bytes()).hexdigest(),
               'reports': reports, 'proposals': proposals, 'validation_reports': validations, 'replay': replay,
               'scope': 'PyBullet xArm6, ground scene, idealized fixed-constraint grasp/catch; parameter search and skill composition'}
    (args.output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    audit.note(f'实验结束：goal_achieved={complete}；技能 {skill.status}；原技能未变；汇总 {args.output / "summary.json"}')
    audit.checkpoint('preserve 5cm learning verification and replay outcome')
    return 0 if complete and replay and replay['passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
