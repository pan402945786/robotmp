"""Render an existing causal experiment for review, never for robot control.

Arm joint angles and object centers come from recorded physics. Object rotation
and finger joint angles were not recorded, so their appearance is illustrative.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg

from .sim_environment import _require_pybullet,_pybullet_data

ROOT=Path(__file__).resolve().parents[1]
WIDTH,HEIGHT,FPS=1920,1080,30
COLORS=dict(bg="#0b1524",panel="#132238",text="#edf4ff",muted="#a6b7cd",
            cube="#5bd6e6",observation="#72a4ff",prediction="#ffd177",tcp="#7de3af",danger="#ff8e96")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def select_best(audit):
    ranking=[]
    for item in audit["trials"]:
        if not item["active_causal"] or not item["motion_checks"]:
            continue
        path=ROOT/item["report"]
        report=load(path)
        trace=load(path.with_name(report["label"]+"_control_trace.json"))
        contact=report.get("first_robot_contact_time_s")
        before=[row for row in trace if row["truth_velocity"][2]<-.05 and not row["contacts"]
            and row["cube"][2]>.2 and (contact is None or row["time_s"]<contact-1e-8)]
        if not before:
            continue
        row=min(before,key=lambda row:row["distance_m"])
        ranking.append(dict(label=report["label"],report=item["report"],time_s=row["time_s"],
                            distance_m=row["distance_m"],relative_speed_m_s=row["relative_speed_m_s"]))
    if not ranking:
        raise RuntimeError("no motion-valid causal experiment with a pre-contact descending sample")
    return sorted(ranking,key=lambda item:(item["distance_m"],item["relative_speed_m_s"]))


class RecordedExperiment:
    def __init__(self,selection):
        self.selection=selection
        self.path=ROOT/selection["report"]
        self.report=load(self.path)
        stem=self.path.with_suffix("")
        self.sources=[self.path]+[Path(str(stem)+suffix) for suffix in
            ("_physics.csv","_control_trace.json","_observations.json","_decisions.json")]
        self.hashes={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in self.sources}
        self.trace=load(self.sources[2])
        self.observations=load(self.sources[3])
        self.decisions=load(self.sources[4])
        self.release=self.report["release_time_s"]
        self.flight_times=[row["time_s"] for row in self.trace]
        self.observation_times=[row["received_at"] for row in self.observations]
        self.available=[row for row in self.decisions if row.get("plan")]
        self.available.sort(key=lambda row:row["issued_at"]+row["wall_s"])
        self.available_times=[row["issued_at"]+row["wall_s"] for row in self.available]
        with self.sources[1].open(encoding="utf-8") as stream:
            rows=list(csv.DictReader(stream))
        self.times=np.array([float(row["t_s"])-self.release for row in rows])
        self.positions=np.array([[float(row[key]) for key in ("x","y","z")] for row in rows])
        self.q=np.array([[float(row[f"q{i}"]) for i in range(6)] for row in rows])
        self.phases=[row["phase"] for row in rows]
        self.tcp=np.array([row["capture_point"] for row in self.trace])
        # Illustrative opening follows only the recorded closing command and its speed limit.
        angle=.85
        previous=0.
        self.finger_angles=[]
        for row in self.trace:
            target=.85 if row["closing"] else 0.
            distance=2*(row["time_s"]-previous)
            angle+=float(np.clip(target-angle,-distance,distance))
            self.finger_angles.append(angle)
            previous=row["time_s"]
        self.apex_time=max(self.trace,key=lambda row:row["cube"][2])["time_s"]
        self.physics_trace_max_error=0.
        for row in self.trace:
            at=np.searchsorted(self.times,row["time_s"])
            at=min(at,len(self.times)-1)
            if at and abs(self.times[at-1]-row["time_s"])<abs(self.times[at]-row["time_s"]):
                at-=1
            self.physics_trace_max_error=max(self.physics_trace_max_error,float(np.max(np.abs(self.positions[at]-row["cube"]))))
        if self.physics_trace_max_error>1e-6:
            raise RuntimeError("CSV and control trace positions do not match")

    def state(self,t):
        q=np.array([np.interp(t,self.times,self.q[:,i]) for i in range(6)])
        position=np.array([np.interp(t,self.times,self.positions[:,i]) for i in range(3)])
        index=max(0,min(len(self.trace)-1,bisect.bisect_right(self.flight_times,t)-1))
        row=self.trace[index] if t>=0 else None
        phase=self.phases[max(0,min(len(self.phases)-1,np.searchsorted(self.times,t,side="right")-1))]
        angle=float(np.interp(t,self.flight_times,self.finger_angles)) if t>=0 else .85
        obs_count=bisect.bisect_right(self.observation_times,t+1e-9) if t>=0 else 0
        plan_index=bisect.bisect_right(self.available_times,t+1e-9)-1
        plan=self.available[plan_index] if plan_index>=0 and t>=0 else None
        return dict(q=q,position=position,row=row,phase=phase,angle=angle,obs_count=obs_count,plan=plan)


class Renderer:
    def __init__(self,data,output):
        self.data=data
        self.p=_require_pybullet()
        p=self.p
        self.client=p.connect(p.DIRECT)
        p.setAdditionalSearchPath(_pybullet_data.getDataPath(),physicsClientId=self.client)
        p.loadURDF("plane.urdf",physicsClientId=self.client)
        self.arm=p.loadURDF("xarm/xarm6_with_gripper.urdf",[.1,0,.7],useFixedBase=True,physicsClientId=self.client)
        # This client is a renderer: no dynamics steps and no controller execution.
        visual=p.createVisualShape(p.GEOM_BOX,halfExtents=[.05]*3,rgbaColor=[.15,.72,.80,.75],physicsClientId=self.client)
        self.cube=p.createMultiBody(0,-1,visual,physicsClientId=self.client)
        self.fonts={size:ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",size) for size in (18,20,22,24,26,30,34,44,58)}
        self.output=output
        self.frames=0
        self.keyframes={}
        self.last_frame=None
        self.log=(output/"render.ffmpeg.log").open("w",encoding="utf-8")
        self.process=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),"-y","-v","error","-f","rawvideo",
            "-pix_fmt","rgb24","-s",f"{WIDTH}x{HEIGHT}","-r",str(FPS),"-i","-","-an","-c:v","libx264",
            "-preset","fast","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(output/"best_online_catch.mp4")],
            stdin=subprocess.PIPE,stderr=self.log)

    def text(self,draw,xy,value,size=24,fill=None):
        draw.text(xy,value,font=self.fonts[size],fill=fill or COLORS["text"])

    def camera(self,center,distance,width,height):
        p=self.p
        view=p.computeViewMatrixFromYawPitchRoll(center,distance,48,-15,0,2)
        projection=p.computeProjectionMatrixFOV(48,width/height,.015,10)
        _,_,rgba,_,_=p.getCameraImage(width,height,view,projection,renderer=p.ER_TINY_RENDERER,physicsClientId=self.client)
        matrix=np.array(projection).reshape((4,4),order="F")@np.array(view).reshape((4,4),order="F")
        return Image.fromarray(rgba[:,:,:3]),matrix

    def project(self,point,matrix,rect):
        clip=matrix@np.r_[point,1.]
        if clip[3]<=0:
            return None
        ndc=clip[:3]/clip[3]
        if abs(ndc[0])>1 or abs(ndc[1])>1 or not -1<=ndc[2]<=1:
            return None
        x,y,w,h=rect
        return (int(x+(ndc[0]+1)*w/2),int(y+(1-ndc[1])*h/2))

    def marker(self,draw,point,matrix,rect,color,label=None,cross=False):
        pixel=self.project(point,matrix,rect)
        if pixel is None:return
        x,y=pixel
        if cross:
            draw.line((x-10,y,x+10,y),fill=color,width=3)
            draw.line((x,y-10,x,y+10),fill=color,width=3)
        else:
            draw.ellipse((x-6,y-6,x+6,y+6),outline=color,width=3)
        if label:
            self.text(draw,(x+12,y-22),label,20,color)

    def scene(self,t,mode):
        data=self.data
        state=data.state(t)
        p=self.p
        for j,q in zip(range(1,7),state["q"]):
            p.resetJointState(self.arm,j,float(q),physicsClientId=self.client)
        for j in range(8,14):
            p.resetJointState(self.arm,j,state["angle"],physicsClientId=self.client)
        p.resetBasePositionAndOrientation(self.cube,state["position"],[0,0,0,1],physicsClientId=self.client)
        frame=Image.new("RGB",(WIDTH,HEIGHT),COLORS["bg"])
        main=(0,84,1280,800)
        detail=(1300,84,600,450)
        overview,overview_matrix=self.camera([.05,.12,1.25],3.4,1280,800)
        frame.paste(overview,main[:2])
        point=np.array(state["row"]["capture_point"]) if state["row"] else state["position"]
        center=(point+state["position"])*.5
        distance=max(.58,min(1.6,math.dist(point,state["position"])*1.8+.4))
        inset,inset_matrix=self.camera(center.tolist(),distance,600,450)
        frame.paste(inset,detail[:2])
        draw=ImageDraw.Draw(frame)
        self.text(draw,(24,12),f"在线观测接回 · 当前最佳接近记录  {data.report['label']}",34)
        self.text(draw,(1120,22),"运动检查通过  /  结果：未接稳",26,COLORS["danger"])
        self.text(draw,(24,94),mode,26,"#253b52")
        draw.rectangle((1300,84,1900,124),fill=COLORS["panel"])
        self.text(draw,(1320,90),"夹爪与物体局部视角",24)
        if t>=0:
            end=bisect.bisect_right(data.flight_times,t)
            past=data.trace[:end]
            for rows,color,key in ((past,COLORS["cube"],"cube"),(past,COLORS["tcp"],"capture_point")):
                pixels=[self.project(row[key],overview_matrix,main) for row in rows[::4]]
                for a,b in zip(pixels,pixels[1:]):
                    if a is not None and b is not None:draw.line((*a,*b),fill=color,width=3)
            for matrix,rect in ((overview_matrix,main),(inset_matrix,detail)):
                self.marker(draw,state["position"],matrix,rect,COLORS["cube"],"物体中心")
                self.marker(draw,point,matrix,rect,COLORS["tcp"],"夹持参考点")
                if state["obs_count"]:
                    observation=data.observations[state["obs_count"]-1]
                    self.marker(draw,observation["position"],matrix,rect,COLORS["observation"],cross=False)
                if state["plan"]:
                    prediction=state["plan"]["plan"]
                    self.marker(draw,prediction["cube"],matrix,rect,COLORS["prediction"],"当时的候选预测",cross=True)
            self.timeline(draw,t,state)
        else:
            self.text(draw,(30,925),"准备与预转：按原始关节记录展示",26)
            self.text(draw,(30,973),"释放以后，接回控制只使用本轮当时已送达的观测。",24,COLORS["muted"])
        row=state["row"]
        self.text(draw,(1320,552),"本次试验记录",30)
        metrics=[("相对释放时间",f"{t:+.3f} s"),
                 ("阶段",state["phase"] if t<0 else ("上升" if row["truth_velocity"][2]>0 else "下降 / 接近")),
                 ("已送达观测",str(state["obs_count"])),
                 ("物体高度",f"{state['position'][2]:.3f} m"),
                 ("参考点距离",f"{row['distance_m']*100:.2f} cm" if row else "—"),
                 ("相对速度",f"{row['relative_speed_m_s']:.2f} m/s" if row else "—")]
        for i,(label,value) in enumerate(metrics):
            self.text(draw,(1320,605+i*48),label,24,COLORS["muted"])
            self.text(draw,(1625,605+i*48),value,24)
        contact=data.report.get("first_robot_contact_time_s")
        touched=contact is not None and t>=contact-1e-8
        self.text(draw,(1320,905),"已发生接触，未形成稳定双指夹持" if touched else "接触前：位置和速度仍需同时对齐",22,COLORS["danger"] if touched else COLORS["muted"])
        self.text(draw,(1320,953),"指面开口 86.9 mm < 方块 100 mm",22,COLORS["prediction"])
        self.text(draw,(24,1030),"记录可视化，不参与控制。六轴角度、物体中心来自原始记录；物体姿态与手指开合为示意。",20,COLORS["muted"])
        self.text(draw,(24,1057),"青：物体轨迹  ·  绿：夹持参考点  ·  蓝：已送达位置观测  ·  黄：当时算出的候选相遇点（不代表已执行）",18,COLORS["muted"])
        return frame

    def timeline(self,draw,t,state):
        rect=(50,927,1230,1004)
        x0,y0,x1,y1=rect
        draw.line((x0,y1,x1,y1),fill=COLORS["muted"],width=1)
        draw.line((x0,y0,x0,y1),fill=COLORS["muted"],width=1)
        end=self.data.trace[-1]["time_s"]
        def xy(at,z):return (x0+(x1-x0)*at/end,y1-(y1-y0)*z/2.6)
        past=[xy(row["time_s"],row["cube"][2]) for row in self.data.trace if row["time_s"]<=t]
        if len(past)>1:draw.line(past,fill=COLORS["cube"],width=3)
        x,_=xy(t,0)
        draw.line((x,y0,x,y1),fill=COLORS["prediction"],width=2)
        self.text(draw,(50,891),"本次高度记录（只展开至当前画面）",22)
        self.text(draw,(940,891),f"飞行时长 {t:.3f} s",22,COLORS["muted"])

    def write(self,frame,count=1):
        raw=frame.tobytes()
        for _ in range(count):
            self.process.stdin.write(raw)
            self.frames+=1
        self.last_frame=frame

    def card(self,title,lines):
        frame=Image.new("RGB",(WIDTH,HEIGHT),COLORS["bg"])
        draw=ImageDraw.Draw(frame)
        self.text(draw,(120,150),title,58)
        for i,(line,color) in enumerate(lines):
            self.text(draw,(125,300+i*100),line,34,color)
        return frame

    def close(self):
        self.process.stdin.close()
        code=self.process.wait()
        self.log.close()
        self.p.disconnect(self.client)
        if code:raise RuntimeError(f"ffmpeg failed: {code}")


def render(output):
    output.mkdir(parents=True,exist_ok=True)
    if (output/"manifest.json").exists():
        raise ValueError("choose a new output folder")
    audit_path=ROOT/"docs/throw_catch_online_audit_20261020/audit.json"
    ranking=select_best(load(audit_path))
    data=RecordedExperiment(ranking[0])
    renderer=Renderer(data,output)
    selected=data.selection
    try:
        intro=renderer.card("当前最佳接近记录 · 在线观测接回",[
            (f"{data.report['label']}：因果观测有效，运动检查通过",COLORS["text"]),
            (f"首次接触前最近距离 {selected['distance_m']*100:.2f} cm；相对速度 {selected['relative_speed_m_s']:.2f} m/s",COLORS["cube"]),
            ("结果仍是未接稳，不能把单侧碰撞算成成功。",COLORS["danger"]),
            ("以下为这次原始记录的可视化；记录不会回送给控制器。",COLORS["muted"])])
        renderer.write(intro,2*FPS)
        start=float(data.times[0])
        for t in np.arange(start,0,4/FPS):
            renderer.write(renderer.scene(float(t),"准备与预转 · 4×"))
        freeze_at=selected["time_s"]
        frozen=False
        apex_saved=False
        for t in np.arange(0,data.trace[-1]["time_s"]+1e-8,.25/FPS):
            if not frozen and t>=freeze_at:
                frame=renderer.scene(freeze_at,"接触前最近点 · 定格")
                frame.save(output/"closest_precontact.png")
                renderer.write(frame,2*FPS)
                frozen=True
            frame=renderer.scene(float(t),"完整飞行 · 0.25× 慢放")
            if not apex_saved and t>=data.apex_time:
                frame.save(output/"apex.png")
                apex_saved=True
            renderer.write(frame)
        for t in np.arange(max(0,freeze_at-.15),min(data.trace[-1]["time_s"],freeze_at+.18),.125/FPS):
            renderer.write(renderer.scene(float(t),"局部接近复看 · 0.125× 慢放"))
        outro=renderer.card("经验更新：接近不等于接稳",[
            ("每次用新观测预测；位置、速度和夹持姿态一起检查。",COLORS["text"]),
            ("计算和观测延迟都要计入；接触后不能继续按自由飞行学习。",COLORS["text"]),
            ("当前指面开口约 86.9 mm，100 mm 方块不适合中心夹持。",COLORS["prediction"]),
            ("本次未接稳；经验 skill 仍为 candidate。",COLORS["danger"])])
        renderer.write(outro,3*FPS)
    finally:
        renderer.close()
    hashes_after={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in data.sources}
    if hashes_after!=data.hashes:raise RuntimeError("source data changed during rendering")
    video=output/"best_online_catch.mp4"
    reader=imageio_ffmpeg.read_frames(str(video))
    metadata=next(reader)
    reader.close()
    manifest=dict(selected=selected,selection_rule="smallest pre-contact descending distance among active causal motion-valid records",
        ranking=ranking,source_hashes=data.hashes,source_files_unchanged=True,
        physics_csv_trace_max_position_error_m=data.physics_trace_max_error,
        mode="posthoc record visualization in an isolated render-only scene; no control or new experiment",
        limitations=["object orientation was not recorded; box orientation is illustrative",
                     "finger joint angles were not recorded; opening illustrates the logged command",
                     "yellow marks are computed candidate points available by that time, not proof of activated plans"],
        frames=renderer.frames,fps=FPS,duration_s=renderer.frames/FPS,video_metadata=metadata,
        video_sha256=hashlib.sha256(video.read_bytes()).hexdigest(),physical_capture=False)
    (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    html=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>当前最佳在线接近记录</title>
<style>body{{background:#0b1524;color:#edf4ff;font:18px/1.65 system-ui;max-width:1300px;margin:36px auto;padding:0 24px}}video{{width:100%;border-radius:12px}}a{{color:#72cfff}}p{{color:#bac8d9}}</style>
<h1>当前最佳在线接近记录 · {data.report['label']}</h1><p>运动检查通过；首次接触前最近距离 {selected['distance_m']*100:.2f} cm，相对速度 {selected['relative_speed_m_s']:.2f} m/s。结果：未接稳。</p>
<video controls preload="metadata" poster="closest_precontact.png" src="best_online_catch.mp4"></video>
<p>原始在线试验记录可视化，不参与控制。物体中心与六轴角度来自记录；物体姿态和手指开合为示意。黄色标记为当时已算出的候选相遇点。</p>
<p><a href="../CAUSAL_THROW_CATCH_SKILL.md">经验 skill 语言版</a> · <a href="manifest.json">数据来源与筛选依据</a></p></html>'''
    (output/"index.html").write_text(html,encoding="utf-8")
    print(json.dumps(dict(video=str(video),selected=selected,frames=renderer.frames,duration_s=renderer.frames/FPS),ensure_ascii=False))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"docs/best_online_catch_video_20261020")
    args=parser.parse_args()
    render(args.output.resolve())


if __name__=="__main__":
    main()
