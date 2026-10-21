"""Show the actual pre-release upstroke before the validated catch replay."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from .vertical_height_full_motion import REPLAY, VALIDATION, FullRecordedCatch, prepare_replays
from .vertical_height_catch_video import HeightRenderer
from .long_distance_catch_video import ROOT, W, H, FPS, BG, TEXT, MUTED, CYAN, GREEN, GOLD, digest

OUTPUT=ROOT/'docs/vertical_height_catch_video_full_20261021'


def add_chapter_buttons(html,chapters):
    controls = '<div style="display:flex;gap:10px;flex-wrap:wrap;margin:20px 0">'
    for chapter in chapters:
        seconds=chapter['start_s']
        label=f"{int(seconds)//60:02d}:{int(seconds)%60:02d} {chapter['name']}"
        controls += (f'<button style="background:#183a3a;color:#edf4fc;border:1px solid #59ddf5;'
            f'border-radius:8px;padding:10px 14px;font:inherit;cursor:pointer" '
            f'onclick="const v=document.querySelector(\'video\');v.currentTime={seconds:.3f};v.play()">{label}</button>')
    return html.replace('</video>','</video>'+controls+'</div>',1)


class CompleteRenderer(HeightRenderer):
    def __init__(self,records,output):
        super().__init__(records,output)
        import pybullet as p
        p.removeBody(self.table,physicsClientId=self.cid)
        pedestal=p.createVisualShape(p.GEOM_BOX,halfExtents=[.14,.14,.35],rgbaColor=[.45,.50,.57,1],physicsClientId=self.cid)
        p.createMultiBody(0,-1,pedestal,[.1,0,.35],physicsClientId=self.cid)
        visual=p.createVisualShape(p.GEOM_BOX,halfExtents=[.02,.02,.02],rgbaColor=[.55,.57,.6,1],physicsClientId=self.cid)
        self.support=p.createMultiBody(0,-1,visual,[.45,0,.68],physicsClientId=self.cid)

    def apply(self,data,t):
        import pybullet as p
        index,row=super().apply(data,t)
        initial=row['phase'] in ('scene','approach','grasp','lift')
        p.changeVisualShape(self.support,-1,rgbaColor=[.55,.57,.6,1 if initial else 0],physicsClientId=self.cid)
        return index,row

    def phase(self,data,row):
        if row['time_s']<0:
            names={'scene':'夹持准备','approach':'夹持准备','grasp':'夹紧','lift':'抬升',
                   'prepare':'摆臂准备','settle':'发射前保持','swing':'向上挥臂'}
            return 0.,{9,12}.issubset(row['contacts']),names[row['phase']]
        return super().phase(data,row)

    def tile(self,n,t):
        index,_=self.records[n].at(t)
        for key in list(self.tile_cache):
            if key[0]==n and key[1]!=index:
                del self.tile_cache[key]
        tile=super().tile(n,t).copy()
        draw=ImageDraw.Draw(tile)
        draw.rectangle((580,80,795,112),fill='#14243a')
        self.text(draw,(590,88),'相对释放时间',20,MUTED)
        return tile

    def side_camera(self):
        import pybullet as p
        width,height=928,568
        view=p.computeViewMatrixFromYawPitchRoll([-.20,.01,1.04],2.65,0,-9,0,2)
        projection=p.computeProjectionMatrixFOV(46,width/height,.005,10)
        _,_,rgba,_,_=p.getCameraImage(width,height,view,projection,renderer=p.ER_TINY_RENDERER,physicsClientId=self.cid)
        matrix=np.array(projection).reshape(4,4,order='F')@np.array(view).reshape(4,4,order='F')
        return Image.fromarray(np.asarray(rgba,dtype=np.uint8)[:,:,:3]),matrix

    def complete(self,t,mode):
        data=self.records[-1]
        index,row=self.apply(data,t)
        frame=Image.new('RGB',(W,H),BG)
        rect=(24,165,1160,710)
        image,matrix=self.side_camera()
        frame.paste(image.resize(rect[2:]),rect[:2])
        center=((np.array(row['cube'])+np.array(row['capture_point']))*.5).tolist()
        distance=max(.47,float(np.linalg.norm(np.array(row['cube'])-row['capture_point']))*1.8+.28)
        image,_=self.camera(center,distance,235,600,390)
        frame.paste(image.resize((688,450)),(1208,165))
        draw=ImageDraw.Draw(frame)
        self.text(draw,(24,18),'50.2 cm 完整过程：夹持 → 挥臂上抛 → 接回',38)
        self.text(draw,(24,76),mode,24,CYAN)
        self.text(draw,(1208,126),'同一时刻的夹爪与方块特写',22,MUTED)
        held,bilateral,phase=self.phase(data,row)
        if 0<=row['time_s']<data.contact and row['truth_velocity'][2]>0:
            phase='释放后向上飞行'
        if abs(t)<1e-8:
            phase='释放瞬间 · 离手'
        self.text(draw,(1230,642),phase,32,GREEN if held else GOLD)
        for key,color in [('swing',GOLD),('flight',CYAN)]:
            points=[self.project(r['cube'],matrix,rect) for r in data.rows[:index+1:2]
                if (key=='swing' and r['phase']=='swing') or (key=='flight' and r['time_s']>=0)]
            for a,b in zip(points,points[1:]):
                if a and b:draw.line([a,b],fill=color,width=4)
        if t>=0:
            xy=self.project(data.report['release_position'],matrix,rect)
            if xy:
                x,y=xy;draw.ellipse((x-7,y-7,x+7,y+7),outline=GOLD,width=3)
                self.text(draw,(x+12,y+8),'释放点',20,GOLD)
        values=[('相对释放时间',f'{row["time_s"]:+.3f} s'),
                ('物体竖直速度',f'{row["truth_velocity"][2]:+.3f} m/s'),
                ('连续接回保持',f'{held:.3f} s'),
                ('方块固定约束','有 · 释放前' if t<0 and row['object_constraint'] else '无'),
                ('接回双指受力','是' if bilateral else '否')]
        for i,(label,value) in enumerate(values):
            self.text(draw,(1230,702+i*48),label,22,MUTED)
            self.text(draw,(1515,702+i*48),value,24,GREEN if i>=2 else TEXT)
        self.text(draw,(28,898),'金色：释放前向上挥臂轨迹    青色：离手后的实际飞行轨迹',24,GOLD)
        names=['夹持准备','摆臂','向上挥臂','释放','上升','下降接回','保持']
        active=0 if t<data.swing_start-.5 else 1 if t<data.swing_start else 2 if t<0 else 3 if t<.03 else 4 if t<data.apex_time else 5 if t<data.contact else 6
        for n,name in enumerate(names):
            x=30+n*265
            color=GREEN if n==active else MUTED
            draw.rounded_rectangle((x,949,x+240,997),8,fill='#183a3a' if n==active else '#14243a')
            self.text(draw,(x+15,956),name,24,color)
        self.text(draw,(28,1034),'上抛段补录并与原轨迹逐项核对；释放后使用原通过审计的飞行与接回记录。',22,MUTED)
        return frame


def render(output,preview=False):
    output.mkdir(parents=True,exist_ok=True)
    if not (REPLAY/'manifest.json').exists():prepare_replays()
    provenance=json.loads((REPLAY/'manifest.json').read_text(encoding='utf-8'))
    records=[FullRecordedCatch(ROOT/e['original_report'],ROOT/e['full_motion']) for e in provenance['records']]
    renderer=CompleteRenderer(records,output)
    high=records[-1]
    try:
        if preview:
            for name,t in [('ready',high.swing_start-.2),('swing',high.swing_start+.12),('release',0.),('rise',.15)]:
                renderer.complete(t,'完整上抛过程 · 预览').save(output/f'preview_{name}.png')
            renderer.grid(-.15).save(output/'preview_grid.png')
            renderer.write(renderer.complete(high.swing_start+.12,'预览'))
            return
        renderer.write(renderer.card('补全释放前的上抛动作',[
            '先看完整的 50.2 cm 档：夹持、摆臂、挥臂、离手、接回',
            '挥臂与上升均慢放；再看四档从释放前开始的同步对比',
            '上抛补录与原记录逐项一致，释放后沿用原验证记录',
            '50 mm 方块，100 g；四档原验证各 3 / 3 成功']),FPS)
        chapters=[]
        def mark(name):chapters.append(dict(name=name,start_s=renderer.frames/FPS))
        mark('夹持和摆臂准备')
        for t in np.arange(high.times[0],high.swing_start,1/FPS):
            renderer.write(renderer.complete(float(t),'01  夹持与摆臂准备  /  1× 原速'))
        renderer.write(renderer.complete(high.swing_start,'02  即将向上挥臂  /  动作起点'),15)
        mark('向上挥臂加速')
        for t in np.arange(high.swing_start,0,.125/FPS):
            renderer.write(renderer.complete(float(t),'02  向上挥臂，加速方块  /  0.125× 慢放'))
        release=renderer.complete(0.,'03  释放瞬间  /  方块离手后自由飞行')
        release.save(output/'release.png');renderer.write(release,24)
        mark('离手上升和下降接回')
        for t in np.arange(0,.85,.25/FPS):
            renderer.write(renderer.complete(float(t),'04  离手上升 → 顶点 → 下降接回  /  0.25× 慢放'))
        for t in np.arange(.85,high.times[-1],1/FPS):
            renderer.write(renderer.complete(float(t),'05  连续双指保持  /  1× 原速'))
        last=renderer.complete(high.times[-1],'05  稳定保持通过  /  结果定格')
        last.save(output/'caught_50cm.png');renderer.write(last,FPS)
        mark('四档从释放前开始同步对比')
        end=max(d.times[-1] for d in records)
        for t in np.arange(-.65,end,.25/FPS):
            renderer.write(renderer.grid(float(t)))
        last=renderer.grid(end);last.save(output/'comparison.png');renderer.write(last,30)
        renderer.write(renderer.card('完整上抛过程已补齐',[
            '10.5 → 14.0 → 20.7 → 50.2 cm，原四档验证共 12 / 12',
            '上抛段：夹持、摆臂、向上加速与释放瞬间均可见',
            '接回段：保留原通过审计的连续双指保持记录',
            '补录的释放前轨迹与离手首帧逐项误差均为零']),2*FPS)
    finally:
        renderer.close()
    for data in records:
        assert all(digest(ROOT/name)==value for name,value in data.hashes.items())
    video=output/'latest_experiment.mp4'
    manifest=dict(video=video.name,frames=renderer.frames,fps=FPS,duration_s=renderer.frames/FPS,
        chapters=chapters,source_files_unchanged=True,video_sha256=digest(video),
        replay_manifest=str((REPLAY/'manifest.json').relative_to(ROOT)),
        mode=provenance['mode'],segment_provenance=provenance['records'],
        note='Prethrow is a numerically matched recording; flight and hold are the original validated record. No fresh catch success is claimed.')
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>补全上抛过程 · 垂直抛接</title><style>body{background:#0c1728;color:#edf4fc;font:18px/1.7 system-ui;max-width:1500px;margin:32px auto;padding:0 24px}video{width:100%;border-radius:14px}p{color:#a0b4cc}a{color:#59ddf5}</style>
<h1>完整上抛接回：夹持 → 摆臂 → 向上挥臂 → 释放 → 接回</h1><p>补充完整上抛过程，先展示 50.2 cm 档，再对比 10.5 / 14.0 / 20.7 / 50.2 cm 四档。</p>
<video controls preload="metadata" poster="release.png" src="latest_experiment.mp4"></video>
<p>挥臂阶段为 0.125× 慢放，离手上升与接回为 0.25× 慢放，并标出释放瞬间。四档对比从释放前 0.65 秒开始。</p>
<p>上抛段为相同参数的补录，释放前轨迹和离手首帧与原记录逐项完全一致；释放后沿用原通过审计的飞行与接回记录。新增补录中的接回结果没有替代原验证结论。</p>
<p><a href="manifest.json">分段数据来源与章节</a> · <a href="../vertical_height_catch_20261021_full_replay/manifest.json">逐项一致性校验</a> · <a href="../VERTICAL_HEIGHT_CATCH_RESULTS.md">实验结果</a> · <a href="latest_experiment.mp4" download>下载 MP4</a></p></html>'''
    html=add_chapter_buttons(html,chapters)
    (output/'index.html').write_text(html,encoding='utf-8')
    print(json.dumps(dict(video=str(video),frames=renderer.frames,duration_s=renderer.frames/FPS,chapters=chapters)),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUTPUT)
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args();render(args.output.resolve(),args.preview)


if __name__=='__main__':main()
