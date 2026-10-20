"""Repair only the encoded title overlay; preserve the original recording."""
from pathlib import Path
import hashlib
import json
import subprocess

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "throw_catch_50mm_20261020_final"
source = OUT / "validation_01.mp4"
target = OUT / "validation_01_labeled.mp4"
reader = imageio_ffmpeg.read_frames(str(source))
metadata = next(reader)
fonts = [ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", size) for size in (26, 19)]
process = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-v", "error",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1280x720", "-r", "30", "-i", "-",
    "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", str(target)], stdin=subprocess.PIPE)
frames = 0
try:
    for index, raw in enumerate(reader):
        frame = Image.frombytes("RGB", metadata["size"], raw)
        draw = ImageDraw.Draw(frame)
        draw.rectangle((0, 0, 959, 71), fill="#0b1524")
        draw.text((18, 10), "50 mm 方块：抛出后在线接回", font=fonts[0], fill="#68e6ff")
        draw.text((18, 45), "50 mm | 100 g | 真实仿真录像 | 结果：未接稳", font=fonts[1], fill="white")
        process.stdin.write(frame.tobytes())
        if index == 205:
            frame.save(OUT / "contact.png")
        frames += 1
finally:
    reader.close()
    process.stdin.close()
    code = process.wait()
if code:
    raise RuntimeError(f"ffmpeg exited with {code}")
result = dict(source=source.name, source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    output=target.name, output_sha256=hashlib.sha256(target.read_bytes()).hexdigest(), frames=frames,
    fps=30, edit="Only top-left title rectangle [0,0,960,72] repaired for text encoding; "
    "scene content and frame order retained; output re-encoded with H.264.")
(OUT / "title_repair.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
