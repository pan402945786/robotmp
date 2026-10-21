"""Render the last validated long-distance catch from recorded physical states."""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

# The copied Conda environment needs its DLL directories when run without activation.
_dll_handles = []
if sys.platform == 'win32':
    _dll_paths = [Path(sys.prefix), Path(sys.prefix) / 'Library/bin', Path(sys.prefix) / 'DLLs']
    _dll_paths = [directory for directory in _dll_paths if directory.is_dir()]
    os.environ['PATH'] = os.pathsep.join(map(str, _dll_paths)) + os.pathsep + os.environ.get('PATH', '')
    _dll_handles = [os.add_dll_directory(str(directory)) for directory in _dll_paths]

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pybullet as p
import pybullet_data

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / 'docs/long_distance_throw_catch_20261021_clean_validation/range_y010_03.json'
DEFAULT_OUTPUT = ROOT / 'docs/long_distance_catch_video_20261021'
W, H, FPS = 1920, 1080, 30
BG, PANEL, TEXT, MUTED = '#0c1728', '#14243a', '#edf4fc', '#a0b4cc'
CYAN, GREEN, GOLD = '#59ddf5', '#78e8b0', '#ffc774'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RecordedCatch:
    def __init__(self, source):
        self.source = source
        self.report = load(source)
        prefix = source.with_suffix('')
        self.trace_path = Path(str(prefix) + '_control_trace.json')
        self.csv_path = Path(str(prefix) + '_physics.csv')
        self.rows = load(self.trace_path)
        self.times = [r['time_s'] for r in self.rows]
        assert all(b > a for a, b in zip(self.times, self.times[1:]))
        for row in self.rows:
            assert len(row['q']) == 6 and len(row['finger_q']) == 6
            assert len(row['cube_orientation']) == 4
        self.sources = [source, self.trace_path, self.csv_path]
        self.hashes = {str(f.relative_to(ROOT)): digest(f) for f in self.sources}
        with self.csv_path.open(encoding='utf-8-sig', newline='') as stream:
            flight = [r for r in csv.DictReader(stream) if r['phase'] == 'flight']
        assert len(flight) == len(self.rows)
        self.csv_error = max(math.dist([float(c[k]) for k in ('x', 'y', 'z')], r['cube'])
                             for c, r in zip(flight, self.rows))
        assert self.csv_error < 1e-9
        self.contact = self.report['capture_contact_time_s']
        held = [r for r in self.rows if r['time_s'] >= self.contact - 1e-8]
        self.bilateral_hold = all({9, 12}.issubset(set(r['contacts'])) for r in held)
        assert self.report['complete_success'] and self.bilateral_hold

    def at(self, t):
        i = bisect.bisect_left(self.times, t)
        i = min(i, len(self.rows) - 1)
        if i and abs(self.times[i - 1] - t) < abs(self.times[i] - t):
            i -= 1
        return i, self.rows[i]


class Renderer:
    def __init__(self, data, output):
        self.data, self.output = data, output
        self.cid = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.cid)
        p.loadURDF('plane.urdf', physicsClientId=self.cid)
        self.arm = p.loadURDF('xarm/xarm6_with_gripper.urdf', [.1, 0, .7],
                              useFixedBase=True, physicsClientId=self.cid)
        table = p.createVisualShape(p.GEOM_BOX, halfExtents=[.65, .55, .035],
                                    rgbaColor=[.62, .67, .73, 1], physicsClientId=self.cid)
        self.table = p.createMultiBody(0, -1, table, [.35, 0, .665], physicsClientId=self.cid)
        size = data.report['cube_size_m'] / 2
        visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[size] * 3,
                                     rgbaColor=[.05, .65, .83, 1], physicsClientId=self.cid)
        self.cube = p.createMultiBody(0, -1, visual, physicsClientId=self.cid)
        self.fonts = {s: ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', s)
                      for s in (18, 20, 22, 24, 28, 32, 38, 48, 64)}
        self.frames = 0
        self.log = (output / 'render.ffmpeg.log').open('w', encoding='utf-8')
        self.proc = subprocess.Popen([
            imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-v', 'error', '-f', 'rawvideo',
            '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
            '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '19',
            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output / 'latest_experiment.mp4')],
            stdin=subprocess.PIPE, stderr=self.log)

    def text(self, draw, xy, text, size=24, color=TEXT):
        draw.text(xy, text, font=self.fonts[size], fill=color)

    def camera(self, center, distance, yaw, width, height):
        view = p.computeViewMatrixFromYawPitchRoll(center, distance, yaw, -18, 0, 2)
        projection = p.computeProjectionMatrixFOV(46, width / height, .005, 10)
        _, _, rgba, _, _ = p.getCameraImage(width, height, view, projection,
            renderer=p.ER_TINY_RENDERER, physicsClientId=self.cid)
        return Image.fromarray(np.asarray(rgba, dtype=np.uint8)[:, :, :3]), (
            np.array(projection).reshape(4, 4, order='F') @ np.array(view).reshape(4, 4, order='F'))

    def project(self, position, matrix, rect):
        point = matrix @ np.r_[position, 1.]
        if point[3] <= 0:
            return None
        point = point[:3] / point[3]
        if max(abs(point[0]), abs(point[1])) > 1:
            return None
        x, y, w, h = rect
        return int(x + (point[0] + 1) * w / 2), int(y + (1 - point[1]) * h / 2)

    def scene(self, t, mode):
        index, row = self.data.at(t)
        for joint, angle in zip(range(1, 7), row['q']):
            p.resetJointState(self.arm, joint, angle, physicsClientId=self.cid)
        for joint, angle in zip(range(8, 14), row['finger_q']):
            p.resetJointState(self.arm, joint, angle, physicsClientId=self.cid)
        p.resetBasePositionAndOrientation(self.cube, row['cube'], row['cube_orientation'], physicsClientId=self.cid)
        frame = Image.new('RGB', (W, H), BG)
        main = (24, 150, 1190, 730)
        detail = (1238, 150, 658, 410)
        image, matrix = self.camera([.35, .10, 1.06], 2.05, 50, main[2], main[3])
        frame.paste(image, main[:2])
        center = ((np.array(row['cube']) + np.array(row['capture_point'])) * .5).tolist()
        image, _ = self.camera(center, .43, 65, detail[2], detail[3])
        frame.paste(image, detail[:2])
        draw = ImageDraw.Draw(frame)
        self.text(draw, (24, 16), '最新实验 · 横向抛出后物理接回', 38)
        self.text(draw, (24, 73), '2026-10-21  /  最终独立验证 03  /  50 mm 方块 · 100 g', 24, MUTED)
        self.text(draw, (1390, 30), '本轮最终验证  3 / 3 成功', 28, GREEN)
        self.text(draw, (24, 113), mode, 24, CYAN)
        self.text(draw, (1240, 113), '夹持特写 · 同一时刻的原始姿态', 24, CYAN)
        for key, color in [('cube', CYAN), ('capture_point', GOLD)]:
            pixels = [self.project(r[key], matrix, main) for r in self.data.rows[:index + 1:2]]
            for a, b in zip(pixels, pixels[1:]):
                if a and b:
                    draw.line([a, b], fill=color, width=3)
        time = row['time_s']
        held = max(0., time - self.data.contact)
        bilateral = {9, 12}.issubset(set(row['contacts']))
        phase = '双指夹持 · 保持' if held > 0 else '下降 · 接触制动' if bilateral else '上抛飞行' if row['truth_velocity'][2] > 0 else '下降 · 在线接近'
        self.text(draw, (1240, 579), phase, 28, GREEN if bilateral else GOLD)
        metrics = [
            ('释放后时间', f'{time:.3f} s'),
            ('实际受力双指接触', '是' if bilateral else '否'),
            ('接回后连续保持', f'{held:.3f} / 1.000 s'),
            ('物体 / 夹持点距离', f'{row["distance_m"] * 1000:.1f} mm'),
            ('相对速度', f'{row["relative_speed_m_s"]:.3f} m/s'),
            ('方块固定约束', '无（原实验记录）'),
        ]
        for i, (label, value) in enumerate(metrics):
            y = 635 + i * 42
            self.text(draw, (1240, y), label, 22, MUTED)
            self.text(draw, (1550, y), value, 22, GREEN if i in (1, 2, 5) else TEXT)
        # A top view makes the modest horizontal range visible without perspective distortion.
        left, top, width, height = 55, 255, 230, 235
        draw.rounded_rectangle((left - 15, top - 50, left + width + 20, top + height + 45), 12, fill=PANEL)
        self.text(draw, (left, top - 40), '水平轨迹 · 俯视', 20, TEXT)
        release = self.data.report['release_position']
        def point(pos):
            return (left + 45 + (pos[0] - release[0]) * 1200,
                    top + height - 30 - (pos[1] - release[1]) * 1200)
        draw.line([(left + 30, top + height - 30), (left + width, top + height - 30)], fill=MUTED, width=1)
        draw.line([(left + 45, top + height), (left + 45, top)], fill=MUTED, width=1)
        trail = [point(r['cube']) for r in self.data.rows[:index + 1:2]]
        if len(trail) > 1:
            draw.line(trail, fill=CYAN, width=3)
        x, y = point(row['cube'])
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=GREEN)
        self.text(draw, (left, top + height + 10), '刻度参考：100 mm', 18, MUTED)
        draw.line((left, top + height + 4, left + 120, top + height + 4), fill=TEXT, width=2)
        self.text(draw, (35, 899), '青色：方块实测轨迹    金色：夹持参考点轨迹', 22, MUTED)
        x0, x1, y0 = 35, 1885, 980
        draw.rounded_rectangle((x0, y0, x1, y0 + 8), 4, fill=PANEL)
        draw.rounded_rectangle((x0, y0, x0 + max(8, (x1 - x0) * time / self.data.times[-1]), y0 + 8), 4, fill=CYAN)
        for tt, label in [(0, '释放'), (.10, '顶点'), (self.data.contact, '确认夹持'), (self.data.times[-1], '保持通过')]:
            x = x0 + (x1 - x0) * tt / self.data.times[-1]
            draw.line((x, y0 - 8, x, y0 + 14), fill=GOLD, width=2)
            self.text(draw, (min(x1 - 100, max(x0, x - 20)), y0 + 20), label, 20, MUTED)
        self.text(draw, (35, 1038), '记录回放：机器人关节、六指角、方块位置与姿态均取自原始记录；画面未运行物理或接回控制。', 20, MUTED)
        return frame

    def card(self, title, lines):
        frame = Image.new('RGB', (W, H), BG)
        draw = ImageDraw.Draw(frame)
        draw.rounded_rectangle((100, 120, 1820, 960), 24, fill=PANEL)
        self.text(draw, (160, 185), 'ROBOTMP  /  2026-10-21', 28, CYAN)
        self.text(draw, (160, 290), title, 48)
        for i, line in enumerate(lines):
            self.text(draw, (165, 425 + 80 * i), line, 32, GREEN if i == 0 else TEXT)
        return frame

    def write(self, frame, count=1):
        raw = frame.tobytes()
        for _ in range(count):
            self.proc.stdin.write(raw)
        self.frames += count

    def close(self):
        self.proc.stdin.close()
        code = self.proc.wait()
        self.log.close()
        p.disconnect(self.cid)
        if code:
            raise RuntimeError(f'ffmpeg exited with {code}')


def render(source, output):
    output.mkdir(parents=True, exist_ok=True)
    data = RecordedCatch(source)
    renderer = Renderer(data, output)
    try:
        renderer.write(renderer.card('横向抛出接回 · 最新一次最终验证', [
            '最终验证第 3 次：成功；本轮独立验证 3 / 3 成功',
            '50 mm 方块，100 g；接回阶段没有物体固定约束',
            '水平释放到下降段最近接近点：117.4 mm',
            '原始记录回放：先原速，再以 0.125× 慢放接回']), 2 * FPS)
        for t in np.arange(0, data.times[-1], 1 / FPS):
            renderer.write(renderer.scene(float(t), '01  释放 → 飞行 → 接回 → 保持  /  1× 原速'))
        for t in np.arange(0, .42, .125 / FPS):
            renderer.write(renderer.scene(float(t), '02  释放与接回细看  /  0.125× 慢放'))
        for t in np.arange(.42, data.times[-1], 1 / FPS):
            renderer.write(renderer.scene(float(t), '03  持续双指保持  /  1× 原速'))
        final = renderer.scene(data.times[-1], '04  保持结束  /  结果定格')
        final.save(output / 'caught.png')
        renderer.write(final, 2 * FPS)
        renderer.write(renderer.card('结果：接回并稳定保持', [
            f'连续受力双指保持 {data.report["continuous_hold_duration_s"]:.4f} s',
            f'保持结束物体速度 {data.report["hold_final_speed_m_s"]:.5f} m/s',
            f'实测上抛增高 {data.report["measured_rise_m"] * 1000:.1f} mm；运动限制检查通过',
            '位置观测 79 帧；本轮在线控制使用当时已送达的观测',
            '适用范围：PyBullet xArm6 / 50 mm 方块 / 100 g']), 3 * FPS)
    finally:
        renderer.close()
    assert all(digest(ROOT / name) == value for name, value in data.hashes.items())
    video = output / 'latest_experiment.mp4'
    reader = imageio_ffmpeg.read_frames(str(video))
    metadata = next(reader)
    reader.close()
    manifest = dict(source=str(source.relative_to(ROOT)), label=data.report['label'],
        selection='Last trial in the latest documented final clean validation (2026-10-21), range_y010_03',
        source_sha256=data.hashes, source_files_unchanged=True,
        mode='Recorded state replay in isolated visual-only PyBullet client; no simulation steps or control',
        recorded_fields=['q', 'finger_q', 'cube', 'cube_orientation', 'contacts', 'truth_velocity'],
        sampling='Nearest recorded state at 240 Hz; presentation at 30 fps',
        scope='Release through flight, capture, and hold; acquisition and pre-throw preparation omitted',
        csv_trace_max_position_error_m=data.csv_error,
        every_hold_frame_bilateral=data.bilateral_hold,
        complete_success=data.report['complete_success'],
        horizontal_release_to_closest_m=data.report['long_distance_metrics']['horizontal_release_to_closest_m'],
        continuous_hold_duration_s=data.report['continuous_hold_duration_s'],
        frames=renderer.frames, fps=FPS, duration_s=renderer.frames / FPS,
        video_metadata=metadata, video_sha256=digest(video))
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>最新实验 · 横向抛出接回 · 2026-10-21</title><style>body{background:#0c1728;color:#edf4fc;font:18px/1.7 system-ui;max-width:1500px;margin:32px auto;padding:0 24px}video{width:100%;border-radius:14px}p{color:#a0b4cc}a{color:#59ddf5}</style>
<h1>最新实验 · 横向抛出接回</h1><p>2026-10-21 最终独立验证第 3 次（range_y010_03）。50 mm 方块，100 g；本轮最终验证 3 / 3 成功。</p>
<video controls preload="metadata" poster="caught.png" src="latest_experiment.mp4"></video>
<p>水平释放到下降段最近接近点 117.4 mm；连续双指保持 1.0042 s；保持结束速度 0.00152 m/s。原速展示释放至保持，再以 0.125× 慢放复看接回。</p>
<p>本视频根据原始机器人关节、六指角、方块位置和姿态记录回放，独立渲染场景未运行物理或接回控制。接触与成功指标来自原实验日志。未展示抓取和抛前准备阶段。</p>
<p><a href="manifest.json">数据来源与校验</a> · <a href="../LONG_DISTANCE_THROW_CATCH_RESULTS.md">实验结果</a> · <a href="latest_experiment.mp4" download>下载 MP4</a></p></html>'''
    (output / 'index.html').write_text(html, encoding='utf-8')
    print(json.dumps({'video': str(video), 'frames': renderer.frames, 'duration_s': renderer.frames / FPS}, ensure_ascii=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    render(args.source.resolve(), args.output.resolve())


if __name__ == '__main__':
    main()
