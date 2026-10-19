"""Decode the complete demonstration and save key frames for visual review."""
import json
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


OUTPUT = Path(__file__).resolve().parent
reader = imageio_ffmpeg.read_frames(str(OUTPUT / 'demo.mp4'), pix_fmt='rgb24')
metadata = next(reader)
width, height = metadata['size']
fps = metadata['fps']
duration = metadata['duration']
times = [0.6, 1.8, 2.20, 2.55, 4.5, max(0, duration - 0.5)]
indices = [round(t * fps) for t in times]
frames = {}
count = 0
for index, raw in enumerate(reader):
    if index in indices:
        frame = Image.frombytes('RGB', (width, height), raw)
        frames[index] = frame
        frame.save(OUTPUT / f'video_frame_{index:04d}.png')
    count += 1
reader.close()
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 18)
sheet = Image.new('RGB', (1280, 1152), '#101d30')
draw = ImageDraw.Draw(sheet)
for i, (time, index) in enumerate(zip(times, indices)):
    x, y = (i % 2) * 640, (i // 2) * 384
    sheet.paste(frames[index].resize((640, 360)), (x, y))
    draw.text((x + 12, y + 360), f'视频时间 {time:.2f}s', font=font, fill='white')
sheet.save(OUTPUT / 'video_contact_sheet.png')
report = json.loads((OUTPUT / 'reloaded_replay.json').read_text(encoding='utf-8'))
info = {'size': [width, height], 'fps': fps, 'duration_s': duration,
        'decoded_frames': count, 'expected_frames': report['video_frames'],
        'all_frames_decode': count == report['video_frames'],
        'flight_slow_motion_factor': 4, 'audio': False,
        'scope': 'actual PyBullet camera frames, idealized fixed-constraint grasp and catch'}
(OUTPUT / 'video_info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(info, ensure_ascii=False, indent=2))
if not info['all_frames_decode']:
    raise SystemExit('video frame count mismatch')
