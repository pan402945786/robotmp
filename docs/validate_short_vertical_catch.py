"""Fresh physical validation of the contact-checked short vertical throw/catch."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from robotmp.throw_catch_online import run_trial,save_json
from robotmp.throw_catch_493_video import Recorder


def parameters():
    p=json.loads((ROOT/"assets/skills/causal_throw_catch_candidate.json").read_text())[0]["parameters"]
    p.update(stationary_catch=True,descent_servo=False,require_observed_separation=True,
        observed_separation_m=.06,handoff_brake_s=.04,open_finger_angle_rad=.1,hold_duration_s=1.,
        latch_contact_fingers=True,grip_hold_force_nm=1.,grip_hold_angle_step_rad=.015)
    return p


def scenario(index):
    levels=[(0.,0.,0.),(.001,1/60,.05),(.002,2/60,.10),(.001,2/60,.05)]
    noise,latency,drop=levels[index%4]
    return dict(seed=3001+index,cube_size_m=.05,pre_spin=False,release_inward_only=False,
        release_gate=[1.45,1.42,1.50][index%3],mass_kg=[.10,.08,.12][(index//3)%3],
        noise_m=noise,latency_s=latency,drop_rate=drop,drag=[.025,.04,.06][(index//4)%3],
        vertical_toss=dict(duration_s=.28,speed_m_s=1.8,x_m=.55,start_z_m=1.12,travel_m=.23))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"docs/short_vertical_catch_20261020")
    parser.add_argument("--trials",type=int,default=20)
    parser.add_argument("--video",action="store_true")
    args=parser.parse_args()
    if (args.output/"summary.json").exists():
        parser.error("choose a new output directory")
    args.output.mkdir(parents=True,exist_ok=True)
    params=parameters()
    reports=[]
    for index in range(args.trials):
        label=f"validated_{index+1:02d}"
        scene=scenario(index)
        recorder=Recorder(args.output/f"{label}.mp4",title="50 mm 方块 · 接触确认后短距离抛接",
            subtitle="实际物理仿真 | 先确认离手，再根据下降观测闭合 | 连续保持 1 秒",
            release_gate=scene["release_gate"],grasp_detail=True) if args.video and index==0 else None
        class Observer:
            latest={}
            def __call__(self,env,phase,tick):
                recorder.capture(env,self.latest,phase,force=phase=="result")
                if phase=="result":
                    recorder.last_frame.save(args.output/"caught.png")
                    recorder.freeze_last(1.)
        try:
            report=run_trial(params,scene,args.output,label,observer=Observer() if recorder else None)
        finally:
            if recorder:
                recorder.close()
        if recorder:
            report.update(video_frames=recorder.frames,video_fps=recorder.fps,video_result_freeze_s=1.)
            save_json(args.output/f"{label}.json",report)
        reports.append(report)
        save_json(args.output/"summary.json",dict(parameters=params,reports=reports,
            complete_successes=sum(bool(r.get("complete_success")) for r in reports)))
        print(json.dumps({k:report.get(k) for k in ("label","released","complete_success","motion_checks_passed",
            "continuous_hold_duration_s","hold_final_speed_m_s","error")}),flush=True)


if __name__=="__main__":
    main()
