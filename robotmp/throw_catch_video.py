"""Render a compact audit video from a throw/catch physics CSV."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


def load_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def render(csv_path: Path, report_path: Path, output: Path, fps: int = 30):
    rows = load_rows(csv_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen([
        ffmpeg, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "1280x720", "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264",
        "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(output)], stdin=subprocess.PIPE)
    font_path = "C:/Windows/Fonts/msyh.ttc"
    font = ImageFont.truetype(font_path, 24)
    small = ImageFont.truetype(font_path, 18)
    # Keep every measured state visible while limiting a long trace to 30 fps.
    step = max(1, len(rows) // (30 * 24))
    trail = []
    phase_colors = {"approach": "#84a9d8", "grasp": "#ffd166", "lift": "#40c9a2",
                    "trace": "#5ee7ff", "transport": "#ff9f43", "finished": "#76e06f"}
    try:
        for index in range(0, len(rows), step):
            row = rows[index]
            x, y, z = float(row["x_m"]), float(row["y_m"]), float(row["z_m"])
            ex, ey, ez = float(row["ee_x"]), float(row["ee_y"]), float(row["ee_z"])
            trail.append((x, z))
            frame = Image.new("RGB", (1280, 720), "#0b1220")
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0, 0, 1280, 72), fill="#16243a")
            draw.text((24, 12), "robotmp 抓取 → 抛掷 → 接球审计回放", font=font, fill="#62e8ff")
            draw.text((24, 44), f"仿真 {float(row['t_s']):.3f}s   阶段 {row['phase']}   约束 {'是' if row['constraint']=='True' else '否'}   接触 {'是' if row['contact']=='True' else '否'}", font=small, fill="white")

            # World x-z view. The 10 m requirement is deliberately visible.
            lx, ly, lw, lh = 35, 105, 770, 570
            draw.rectangle((lx, ly, lx + lw, ly + lh), outline="#40556f", width=2)
            def px(v): return int(lx + (v + 0.2) / 1.4 * lw)
            def pz(v): return int(ly + lh - min(v, 12.0) / 12.0 * lh)
            draw.line((px(-0.2), pz(0), px(1.2), pz(0)), fill="#d3a85c", width=5)
            draw.line((px(-0.2), pz(0.70), px(1.2), pz(0.70)), fill="#677b96", width=2)
            draw.line((px(-0.2), pz(10), px(1.2), pz(10)), fill="#ff5c7a", width=2)
            draw.text((lx + 12, pz(10) - 28), "目标世界高度 10 m", font=small, fill="#ff8da1")
            draw.text((lx + 12, pz(0.70) - 24), "桌面 z=0.70 m", font=small, fill="#a7b8cf")
            if len(trail) > 1:
                draw.line([(px(a), pz(b)) for a, b in trail], fill="#5ee7ff", width=4)
            draw.ellipse((px(x) - 10, pz(z) - 10, px(x) + 10, pz(z) + 10), fill=phase_colors.get(row["phase"], "#ffffff"), outline="white", width=2)
            draw.ellipse((px(ex) - 7, pz(ez) - 7, px(ex) + 7, pz(ez) + 7), fill="#ffffff")
            draw.line((px(x), pz(z), px(ex), pz(ez)), fill="#9aa9bd", width=2)
            draw.text((lx + 12, ly + 12), "实测 x-z 轨迹（比例尺：z 0–12 m）", font=small, fill="#d7e4f5")

            # Evidence panel.
            rx, ry = 840, 105
            draw.text((rx, ry), "实测证据", font=font, fill="#62e8ff")
            lines = [
                f"释放竖直速度：{report.get('release_vz_m_s', 0):.3f} m/s",
                f"最高世界高度：{report.get('apex_height_m', 0):.3f} m",
                f"相对释放上升：{report.get('rise_from_release_m', 0):.3f} m",
                f"接球门槛：{'通过' if report.get('caught') else '未通过'}",
                f"放地：{'通过' if report.get('placement', {}).get('passed') else '未完成'}",
                f"整体：{'通过' if report.get('passed') else '未通过'}",
            ]
            for n, line in enumerate(lines):
                color = "#76e06f" if ("通过" in line and "未" not in line) else "#ffb0b0" if "未" in line else "white"
                draw.text((rx, ry + 48 + n * 34), line, font=small, fill=color)
            draw.text((rx, 430), "判定规则", font=font, fill="#62e8ff")
            rules = ["真实抬升后才允许释放", "世界高度 ≥10 m", "相对释放点上升 ≥10 m", "下降中满足距离/速度门槛", "接住后地面静置稳定"]
            for n, line in enumerate(rules):
                draw.text((rx, 474 + n * 30), "• " + line, font=small, fill="#d7e4f5")
            proc.stdin.write(frame.tobytes())
    finally:
        proc.stdin.close()
        code = proc.wait()
        if code:
            raise RuntimeError(f"ffmpeg failed: {code}")
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(render(args.csv, args.report, args.output))


if __name__ == "__main__":
    main()
