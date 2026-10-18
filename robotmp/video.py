"""Render an MP4 from the real MVP runner's telemetry (no physics simulator)."""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .environment import FailureMode
from .runner import default_store, run_ab_experiment, run_episode, validate_skill

W, H = 1600, 900
BG = "#09111e"
PANEL = "#111e30"
EDGE = "#24354c"
TEXT = "#eaf2fb"
MUTED = "#8fa4be"
CYAN = "#50d8ee"
GREEN = "#68e6b2"
RED = "#ff8490"
AMBER = "#ffc478"
PURPLE = "#bda8ff"

ACTIONS = {
    "approach_object": "接近物体", "close_gripper": "闭合夹爪",
    "lift_object": "尝试抬升", "move_to_target": "移动至目标",
    "release_object": "释放物体", "refresh_object_pose": "刷新物体位置",
    "retry_grasp": "重试抓取 / 清除故障注入", "stop": "安全停止",
}
PHASES = {"observe": "观察", "approach": "接近", "grasp": "抓取", "lift": "抬升",
          "transport": "搬运", "finished": "完成", "failed": "失败"}
STATUS = {"success": "成功", "false_success": "误判成功", "recovered": "恢复成功",
          "failed": "失败", "uncertain": "观测不确定"}


def collect(output: Path, trials: int) -> dict:
    """Use fresh isolated stores so each render is reproducible."""
    with tempfile.TemporaryDirectory(prefix="robotmp-video-") as tmp:
        root = Path(tmp)
        traces = {}
        for key, mode, failure in [
            ("baseline", "baseline", FailureMode.LOW_GRIP_FORCE),
            ("feedback", "feedback", FailureMode.LOW_GRIP_FORCE),
            ("learning", "skills", FailureMode.LOW_GRIP_FORCE),
            ("occluded", "feedback", FailureMode.OCCLUDED),
        ]:
            events = []
            run_episode(mode, failure, default_store(root / f"{key}.json"), observer=events.append)
            traces[key] = events
        store = default_store(root / "learning.json")
        verified = validate_skill(store, trials=trials)
        traces["skills"] = []
        run_episode("skills", FailureMode.LOW_GRIP_FORCE, store, observer=traces["skills"].append)
        summary = run_ab_experiment(FailureMode.LOW_GRIP_FORCE, trials, root / "experiment")
        payload = {
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "source": "robotmp.runner.run_episode / deterministic PickPlaceEnv",
            "notes": [
                "Schematic state replay, not hardware footage or physics simulation.",
                "Video time is expanded; simulation time advances 0.1 seconds per action.",
                "Gripper force is a model scalar with no calibrated physical unit.",
                "Drawing interpolates positions only; numeric panels show exact snapshots.",
                "Recovery clears the injected fault using the existing retry_grasp action.",
                "The model leaves the object elevated and lifted=true after release.",
                "The skills policy still encounters failure; it does not preemptively change force.",
                "Charts use actual object heights; the predictor provides a lifted boolean, not a height trajectory.",
                "Comparison panel retains the first lift comparison; the runner does not re-compare after recovery.",
            ],
            "traces": traces, "verified_skill": asdict(verified), "summary": summary,
        }
    output.mkdir(parents=True, exist_ok=True)
    (output / "run_data.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def caption(event: dict) -> str:
    kind = event["kind"]
    if kind == "reset":
        return "任务开始：观察物体，等待抓取。每个动作推进 0.1 秒模型时间。"
    if kind == "retrieve":
        return "检索到已验证 Skill，预测置信度将从 0.75 调整为 0.90。" if event["skills"] else "经验库为空：本次任务将从失败中生成候选 Skill。"
    if kind == "prediction":
        return "预测：下一动作应产生物体抬升事件；是否成功需要真实反馈确认。"
    if kind == "comparison":
        return "观测置信度只有 0.35，低于 0.50 阈值，进入不确定分支。" if event["comparison"]["status"] == "uncertain" else "偏差已确认：预测应抬升，但实际未抬升，且缺少抬升事件。"
    if kind == "diagnosis":
        return "规则诊断器提出候选原因：抓取点偏移或夹爪力度不足。"
    if kind == "candidate":
        return "保存候选 Skill：夹爪闭合不等于抓取成功，搬运前必须确认抬升。"
    if kind == "result":
        status = event["result"]["status"]
        if status == "false_success":
            return "基线未检查反馈：物体仍在原处，执行结果被误判为成功。"
        if status == "uncertain":
            return "系统已安全停止：当前物体虽已抬升，但观测证据不够可靠。"
        return "实际抬升与搬运已完成。当前环境在释放后仍保留抬升状态，未模拟落台。"
    action = event.get("action")
    if action == "close_gripper":
        return "夹爪力度仅为 0.40（模型值），夹爪已闭合，但未真正抓住物体。" if event["state"]["robot"]["gripper_force"] < 0.5 else "夹爪力度为 1.00（模型值），物体已被抓住。"
    if action == "retry_grasp":
        return "现有重试逻辑清除故障注入；这是规则环境中的恢复机制。"
    if action == "lift_object":
        return "实际高度由 0.75 m 升至 0.90 m，产生 object_lift_detected 事件。" if event["state"]["object"]["lifted"] else "执行了抬升动作，但物体高度仍是 0.75 m，未产生抬升事件。"
    return {
        "approach_object": "机械臂接近物体，准备闭合夹爪。",
        "refresh_object_pose": "刷新物体位置，准备再次抓取。",
        "move_to_target": "物体沿 x 方向移动至目标位置 0.50 m。",
        "release_object": "夹爪张开，完成当前模型中的释放动作。",
        "stop": "执行 stop，环境停止接受后续运动动作。",
    }.get(action, "")


def event_label(event: dict) -> str:
    if event["kind"] == "action":
        return ACTIONS[event["action"]]
    if event["kind"] == "result":
        return STATUS[event["result"]["status"]]
    return {"reset": "初始化", "retrieve": "检索 Skill", "prediction": "生成预测",
            "comparison": "比较预测与反馈", "diagnosis": "生成失败诊断", "candidate": "保存候选 Skill"}[event["kind"]]


class Renderer:
    def __init__(self, font_path: str | None = None):
        from PIL import Image, ImageDraw, ImageFont
        self.Image, self.ImageDraw = Image, ImageDraw
        candidates = [font_path, "C:/Windows/Fonts/msyh.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
        self.font_path = next((str(p) for p in candidates if p and Path(p).is_file()), None)
        if not self.font_path:
            raise RuntimeError("Chinese font missing; supply --font with a CJK .ttf/.ttc file")
        self.fonts = {size: ImageFont.truetype(self.font_path, size) for size in [16, 18, 20, 22, 24, 26, 28, 32, 38, 44, 50, 58, 72]}

    def text(self, draw, xy, value, size=22, fill=TEXT):
        draw.text(xy, str(value), font=self.fonts[size], fill=fill)

    def box(self, draw, xy, fill=PANEL, outline=EDGE, radius=18):
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=1)

    def base(self, index, title, subtitle):
        im = self.Image.new("RGB", (W, H), BG)
        d = self.ImageDraw.Draw(im)
        self.text(d, (40, 25), "robotmp", 32, CYAN)
        self.text(d, (209, 35), "PREDICT / OBSERVE / LEARN", 16, MUTED)
        self.text(d, (1120, 31), "实际运行数据  /  状态示意回放", 20, MUTED)
        self.text(d, (40, 85), title, 44)
        self.text(d, (42, 151), subtitle, 22, MUTED)
        self.text(d, (40, 858), "轻量规则环境 · 非物理仿真   |   数值为实际快照，运动插值仅用于播放", 16, MUTED)
        self.text(d, (1375, 858), f"CHAPTER  {index:02d} / 07", 16, MUTED)
        return im

    def cube(self, d, x, y, color=CYAN):
        d.polygon([(x-26,y-14),(x,y-28),(x+26,y-14),(x,y)], fill=color)
        d.polygon([(x-26,y-14),(x,y),(x,y+36),(x-26,y+22)], fill="#26798b")
        d.polygon([(x,y),(x+26,y-14),(x+26,y+22),(x,y+36)], fill="#36a7bc")

    def scene(self, im, state, position=None):
        d = self.ImageDraw.Draw(im)
        self.box(d, (40, 210, 984, 604))
        self.text(d, (64, 229), "抓取场景", 24)
        self.text(d, (644, 233), "模型坐标 / m  ·  几何示意", 18, MUTED)
        x0, z0 = 300, 508
        def project(p):
            return x0 + p[0] * 800, z0 - (p[2] - 0.75) * 650
        for n in range(6):
            xx = x0 + n * 80
            d.line((xx, 300, xx, 542), fill="#192b40", width=1)
        for z in [0.75, 0.85, 0.95]:
            yy = project([0, 0, z])[1]
            d.line((190, yy, 920, yy), fill="#22344a", width=1)
            self.text(d, (80, yy-13), f"z {z:.2f}", 16, MUTED)
        d.polygon([(180, 532),(826,532),(919,563),(247,563)], fill="#1e3549", outline="#365570")
        d.line((700, 295, 700, 543), fill="#536346", width=2)
        d.ellipse((665, 521, 735, 542), outline=AMBER, width=2)
        self.text(d, (629, 566), "目标 x = 0.50", 18, AMBER)
        self.text(d, (252, 566), "起点 x = 0.00", 18, MUTED)
        p = position or state["object"]["position_m"]
        cx, cy = project(p)
        d.ellipse((cx-28, 518, cx+28, 528), fill="#07101a")
        # Use the model's end-effector coordinates as-is, even when simplified
        # model geometry does not match a real physical grasp.
        ex, ey = project(state["robot"]["end_effector_position_m"])
        d.line((ex, 307, ex, ey-42), fill="#46617c", width=12)
        d.line((217, 307, 832, 307), fill="#4d6885", width=16)
        d.rounded_rectangle((ex-38, ey-45, ex+38, ey-14), radius=7, fill="#92a7bd")
        gap = 42 if state["robot"]["gripper_open"] else 31
        for sign in [-1, 1]:
            gx = ex + sign * gap
            d.line((gx, ey-22, gx, ey+20), fill="#c1d0df", width=9)
            d.line((gx, ey+20, gx-sign*11, ey+20), fill="#c1d0df", width=7)
        self.cube(d, cx, cy, CYAN if state["object"]["visible"] else MUTED)
        self.text(d, (cx+40, cy-14), "cube", 18, CYAN)
        self.text(d, (cx+40, cy+12), f"z = {state['object']['position_m'][2]:.2f} m", 18, MUTED)
        self.text(d, (210, 339), "夹爪示意", 16, MUTED)
        self.text(d, (64, 272), "物体与末端位置分别读取模型", 16, MUTED)

    def metric(self, d, x, y, label, value, color, ratio=None):
        self.box(d, (x,y,x+242,y+100), fill="#15253a", outline="#15253a", radius=11)
        self.text(d, (x+15,y+11), label, 18, MUTED)
        self.text(d, (x+15,y+36), value, 32, color)
        if ratio is not None:
            d.rounded_rectangle((x+16,y+85,x+225,y+89), radius=2, fill=EDGE)
            d.rounded_rectangle((x+16,y+85,x+16+max(1,209*ratio),y+89), radius=2, fill=color)

    def dashboard(self, index, title, subtitle, events, event_index):
        e = events[event_index]
        s, p, c = e["state"], e["prediction"], e["comparison"]
        im = self.base(index, title, subtitle)
        self.scene(im, s)
        d = self.ImageDraw.Draw(im)
        self.box(d, (1006,210,1560,604))
        self.text(d, (1030,229), "关键参数 / 原始状态", 24)
        self.text(d, (1342,235), f"t = {s['timestamp']:.1f} s", 20, CYAN)
        force = s["robot"]["gripper_force"]
        self.metric(d,1030,279,"夹爪力度 · 模型值",f"{force:.2f}",AMBER,force)
        self.metric(d,1290,279,"物体高度 · m",f"{s['object']['position_m'][2]:.2f}",CYAN)
        self.metric(d,1030,391,"预测置信度",f"{p['confidence']:.2f}" if p else "—",PURPLE,p["confidence"] if p else None)
        self.metric(d,1290,391,"观测置信度",f"{s['object']['confidence']:.2f}",GREEN if s["object"]["confidence"]>=0.5 else RED,s["object"]["confidence"])
        self.text(d,(1030,510),f"实际抬升  {'是' if s['object']['lifted'] else '否'}    |    预测抬升  {'是' if p else '—'}",20)
        cmp = {"deviation":"偏差", "uncertain":"不确定", "match":"匹配"}.get(c["status"] if c else "", "尚未比较")
        self.text(d,(1030,546),f"首次比较：{cmp}",20,RED if c else MUTED)
        self.text(d,(1300,546),f"阶段：{PHASES[s['phase']]}",20,MUTED)
        self.box(d,(40,623,984,805))
        self.text(d,(64,637),"物体高度 / m",20)
        self.text(d,(430,639),"动作采样值 · 阶梯曲线（非连续动力学）",16,MUTED)
        points = []
        for event in events:
            st = event["state"]
            item=(st["timestamp"],st["object"]["position_m"][2])
            if not points or item != points[-1]:
                points.append(item)
        max_t=max(0.5,events[-1]["state"]["timestamp"])
        def chart(t,z): return 146+t/max_t*790,756-(z-.75)/.15*62
        for z in [.75,.90]:
            yy=chart(0,z)[1]
            d.line((146,yy,936,yy),fill=EDGE,width=1)
            self.text(d,(74,yy-12),f"{z:.2f}",16,MUTED)
        visible=[v for v in points if v[0] <= s["timestamp"]+1e-8]
        for a,b in zip(visible,visible[1:]):
            xa,ya=chart(*a); xb,yb=chart(*b)
            d.line((xa,ya,xb,ya,xb,yb),fill=CYAN,width=3)
        xx,yy=chart(s["timestamp"],s["object"]["position_m"][2])
        d.ellipse((xx-5,yy-5,xx+5,yy+5),fill=CYAN)
        self.text(d,(146,776),"0.0 s",16,MUTED)
        self.text(d,(873,776),f"{max_t:.1f} s",16,MUTED)
        self.box(d,(1006,623,1560,805))
        self.text(d,(1030,637),"执行记录",20)
        for row,j in enumerate(range(max(0,event_index-2),event_index+1)):
            active=j==event_index
            self.text(d,(1030,674+row*36),f"{events[j]['state']['timestamp']:.1f}s   {event_label(events[j])}",20,CYAN if active else MUTED)
        self.text(d,(42,816),caption(e),22,TEXT)
        return im

    def intro(self, payload):
        im=self.base(1,"让失败进入下一次预测","robotmp 当前项目运行可视化  /  真实执行快照与确定性实验")
        d=self.ImageDraw.Draw(im)
        steps=[("01","预测",CYAN),("02","执行",PURPLE),("03","比较",AMBER),("04","诊断",RED),("05","验证 Skill",GREEN)]
        for n,(number,label,color) in enumerate(steps):
            x=40+n*307
            self.box(d,(x,250,x+286,438))
            self.text(d,(x+24,275),number,24,color)
            self.text(d,(x+24,341),label,38)
            if n<4: self.text(d,(x+289,325),"›",24,MUTED)
        self.box(d,(40,476,1560,790))
        self.text(d,(72,501),"本次运行会展示什么",28)
        lines=["A  基线：夹爪闭合却未抬升，系统误判成功",
               "B  反馈：发现预测偏差，重试后恢复抓取",
               "C  Skill：失败经验经过验证，下一次预测检索复用",
               "D  遮挡：低置信度观测触发安全停止"]
        for n,line in enumerate(lines): self.text(d,(74,558+n*47),line,26,[RED,CYAN,GREEN,AMBER][n])
        self.text(d,(42,815),"固定故障场景；统计结果用于检查闭环逻辑，不代表真实机器人性能。",22,MUTED)
        return im

    def skill_card(self,payload):
        im=self.base(4,"把一次失败，变成可检索的经验","候选生成 → 独立重复验证 → verified → 下一任务检索")
        d=self.ImageDraw.Draw(im)
        skill=payload["verified_skill"]
        self.box(d,(40,225,956,792))
        self.text(d,(72,253),"grasp_without_lift_v1",32,CYAN)
        self.text(d,(72,310),"触发：夹爪已闭合，但未观察到物体抬升",26)
        self.text(d,(72,364),"经验：夹爪闭合不等于抓取成功",26)
        self.text(d,(72,418),"策略：搬运前要求抬升证据；失败则刷新位置并重试",24)
        self.text(d,(72,494),"本次实际变化",24,GREEN)
        self.text(d,(72,541),"预测置信度  0.75 → 0.90",32,PURPLE)
        self.text(d,(72,598),"预期阶段  transport → lift",28,CYAN)
        self.text(d,(72,666),"当前 Skill 仍会遇到首次抓取失败，再通过相同重试流程恢复。",22,MUTED)
        self.text(d,(72,707),"候选原因来自本地规则诊断器。",22,MUTED)
        self.box(d,(980,225,1560,792))
        self.text(d,(1016,255),"验证结果",28)
        self.text(d,(1016,315),"VERIFIED",44,GREEN)
        rows=[("验证次数",str(skill["validation_trials"])),("恢复成功率",f"{skill['recovery_success_rate']:.0%}"),("误判成功率",f"{skill['false_success_rate']:.0%}")]
        for n,(key,val) in enumerate(rows):
            self.text(d,(1016,416+n*105),key,24,MUTED)
            self.text(d,(1340,411+n*105),val,38,GREEN)
        self.text(d,(1016,747),"同一确定性低力度故障场景",20,MUTED)
        self.text(d,(42,815),"验证流程使用 feedback 模式重复测试，再将候选 Skill 标记为 verified。",22,MUTED)
        return im

    def summary(self,payload):
        im=self.base(7,"当前闭环已经跑通，能力边界同样可见","A / B / C 对比实验  ·  每组相同次数  ·  固定 low_grip_force 故障")
        d=self.ImageDraw.Draw(im)
        labels=[("baseline","A / 基线",RED),("feedback","B / 反馈",CYAN),("skills","C / Skill",GREEN)]
        for n,(key,title,color) in enumerate(labels):
            x=40+n*513
            self.box(d,(x,224,x+494,651))
            stat=payload["summary"][key]
            self.text(d,(x+26,248),title,32,color)
            self.text(d,(x+26,299),f"{stat['trials']} 次实际运行",20,MUTED)
            self.text(d,(x+26,339),f"{stat['success_rate']:.0%}",72,color)
            self.text(d,(x+26,430),"最终成功率",22,MUTED)
            rows=[("误判成功",stat["false_success_rate"]),("恢复发生",stat["recovery_rate"]),("Skill 应用",stat["skill_application_rate"])]
            for j,(label,value) in enumerate(rows):
                yy=486+j*49
                self.text(d,(x+26,yy),label,22,MUTED)
                self.text(d,(x+354,yy),f"{value:.0%}",24,color)
        self.box(d,(40,675,1560,797))
        self.text(d,(68,693),"已验证：预测偏差检测、失败恢复、经验保存 / 验证 / 检索、遮挡停止。",24)
        self.text(d,(68,740),"边界：确定性规则环境；Skill 尚未减少本场景重试次数；未接入物理仿真或真实硬件。",22,MUTED)
        self.text(d,(42,815),"原始数据：run_data.json   |   视频时间经过展开；参数沿用模型定义。",22,MUTED)
        return im


def schedule(payload):
    clips=[("intro",4.0,None,None)]
    for key,duration in [("baseline",9.0),("feedback",16.0),("learning_card",7.0),("skills",14.0),("occluded",9.0)]:
        if key=="learning_card":
            clips.append((key,duration,None,None))
            continue
        events=payload["traces"][key]
        weights=[2.4 if e["kind"] in {"result","comparison","prediction"} else 1.0 for e in events]
        for i,weight in enumerate(weights):
            clips.append((key,duration*weight/sum(weights),events,i))
    clips.append(("summary",8.0,None,None))
    return clips


def render(output: Path, payload: dict, fps: int, font: str | None):
    import imageio_ffmpeg
    renderer=Renderer(font)
    filename=output/"robotmp_run.mp4"
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    command=[ffmpeg,"-y","-loglevel","error","-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24",
             "-s",f"{W}x{H}","-r",str(fps),"-i","-","-an","-c:v","libx264","-preset","fast",
             "-crf","20","-pix_fmt","yuv420p","-movflags","+faststart",str(filename)]
    chapters={
        "baseline":(2,"A / 基线：动作执行，不代表任务成功","故障注入 low_grip_force  /  未检查预测与观测是否一致"),
        "feedback":(3,"B / 反馈：先发现偏差，再恢复抓取","同一低力度故障  /  监控器检测缺失的抬升证据"),
        "skills":(5,"C / Skill：下一次预测，带上失败经验","检索 grasp_without_lift_v1  /  预测置信度 0.90  /  仍通过重试恢复"),
        "occluded":(6,"D / 遮挡：证据不足，停止执行","故障注入 occluded  /  观测置信度 0.35 < 阈值 0.50"),
    }
    preview_names={"intro":"01_overview","baseline":"02_baseline","feedback":"03_feedback","learning_card":"04_skill","skills":"05_skills","occluded":"06_safety","summary":"07_summary"}
    saved=set()
    frame_count=0
    elapsed=0.0
    chapter_marks=[]
    previous_key=None
    proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for key,duration,events,i in schedule(payload):
            if key!=previous_key:
                chapter_marks.append({"chapter":key,"video_seconds":round(frame_count/fps,3)})
                print(f"Rendering {key} at {frame_count/fps:.1f}s",flush=True)
                previous_key=key
            if key=="intro": im=renderer.intro(payload)
            elif key=="learning_card": im=renderer.skill_card(payload)
            elif key=="summary": im=renderer.summary(payload)
            else: im=renderer.dashboard(*chapters[key],events,i)
            preview = key not in saved and (events is None or events[i]["kind"] in {"comparison","result"})
            if preview:
                im.save(output/f"{preview_names[key]}.png")
                saved.add(key)
            elapsed+=duration
            count=round(elapsed*fps)-frame_count
            state=events[i]["state"] if events else None
            previous=events[max(0,i-1)]["state"] if events else None
            moving=state is not None and previous["object"]["position_m"]!=state["object"]["position_m"]
            for n in range(count):
                frame=im.copy()
                if moving:
                    blend=min(1.0,(n+1)/max(1,count*.75))
                    blend=blend*blend*(3-2*blend)
                    position=[a+(b-a)*blend for a,b in zip(previous["object"]["position_m"],state["object"]["position_m"])]
                    renderer.scene(frame,state,position)
                d=renderer.ImageDraw.Draw(frame)
                d.rectangle((0,H-4,round(W*frame_count/(67*fps)),H),fill=CYAN)
                proc.stdin.write(frame.tobytes())
                frame_count+=1
        proc.stdin.close()
        errors=proc.stderr.read().decode(errors="replace")
        code=proc.wait()
        if code:
            raise RuntimeError(f"ffmpeg failed ({code}): {errors}")
    except BaseException:
        proc.kill()
        proc.wait()
        raise
    finally:
        proc.stderr.close()
    report={"file":str(filename.resolve()),"width":W,"height":H,"fps":fps,"frames":frame_count,
            "duration_seconds":frame_count/fps,"chapters":chapter_marks,"bytes":filename.stat().st_size,
            "codec":"h264","pixel_format":"yuv420p","audio":False}
    (output/"video_info.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    # A portable HTML player keeps navigation and the measured results beside the video.
    rows="".join(f"<tr><td>{name}</td><td>{s['trials']}</td><td>{s['success_rate']:.0%}</td><td>{s['false_success_rate']:.0%}</td><td>{s['recovery_rate']:.0%}</td><td>{s['skill_application_rate']:.0%}</td></tr>" for name,s in payload["summary"].items())
    links="".join(f"<button onclick=\"document.querySelector('video').currentTime={mark['video_seconds']};document.querySelector('video').play()\">{mark['chapter']}</button>" for mark in chapter_marks)
    (output/"index.html").write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>robotmp 运行可视化</title>
<style>body{{background:#09111e;color:#eaf2fb;font:16px 'Microsoft YaHei',sans-serif;max-width:1200px;margin:40px auto;padding:0 24px}}h1{{color:#50d8ee}}video{{width:100%;border-radius:16px}}p{{color:#8fa4be;line-height:1.8}}table{{border-collapse:collapse;width:100%;margin:24px 0}}td,th{{text-align:left;padding:14px;border-bottom:1px solid #24354c}}button{{background:#15253a;color:#eaf2fb;border:1px solid #24354c;border-radius:8px;padding:10px;margin:12px 10px 0 0;cursor:pointer}}a{{color:#50d8ee}}</style>
<h1>robotmp · 当前项目运行可视化</h1><p>实际执行状态与事件回放 · 1600 × 900 · {frame_count/fps:.1f} 秒 · 中文参数面板</p>
<video controls preload="metadata" poster="01_overview.png" src="robotmp_run.mp4"></video><div>{links}</div>
<table><tr><th>模式</th><th>运行次数</th><th>成功率</th><th>误判成功率</th><th>恢复发生率</th><th>Skill 应用率</th></tr>{rows}</table>
<p>场景为固定低力度故障下的确定性规则环境。动作间插值用于播放，不是物理仿真。夹爪力度为模型值，没有标定物理单位。Skill 复用改变预测置信度与预期阶段，当前仍需相同的重试流程。释放后模型保留抬升状态。视频无音轨。</p>
<p><a href="run_data.json">原始执行数据</a> · <a href="video_info.json">视频参数</a></p></html>''',encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=Path("artifacts/visualization"))
    parser.add_argument("--trials",type=int,default=20)
    parser.add_argument("--fps",type=int,default=24)
    parser.add_argument("--font",help="CJK font file (.ttf/.ttc)")
    args=parser.parse_args()
    if args.trials<1 or not 1<=args.fps<=60:
        parser.error("--trials must be positive; --fps must be between 1 and 60")
    try:
        import PIL
        import imageio_ffmpeg
    except ImportError:
        parser.exit(1,'Install video dependencies first: python -m pip install -e ".[video]"\n')
    payload=collect(args.output,args.trials)
    render(args.output,payload,args.fps,args.font)


if __name__=="__main__":
    main()
