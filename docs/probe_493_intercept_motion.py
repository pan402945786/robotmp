"""Dynamically test sampled intercepts; never attach unless all original gates pass."""
from pathlib import Path
import json
import math
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from robotmp.throw_catch_coordination import trial,command
from robotmp.throw_catch_493_video import MASS_KG,LEAD_S,DELAYS_493,SPIN_493
from robotmp.throw_catch_spin import POSES

out=Path(__file__).resolve().parent/"throw_catch_493_recovery_20261020"
alternatives=json.loads((out/"alternative_intercepts.json").read_text())

def run(candidate,gate,label,coast_s=0.):
    def handler(env,report,sample,offset):
        p=env.p
        states=[p.getJointState(env._gripper_id,j,physicsClientId=env.client) for j in env._arm_joint_ids]
        q0=np.array([s[0] for s in states])
        v0=np.array([s[1] for s in states])
        q1=np.array(candidate["q"])
        v1=np.array(candidate["qd"])
        for i in (0,3,5):
            q1[i]=q0[i]+(q1[i]-q0[i]+math.pi)%(2*math.pi)-math.pi
        # Joint 6 rotates around the EE origin and has no positional leverage.
        q1[5]=q0[5]+v0[5]*.10
        v1[5]=0
        T=candidate["time_s"]
        a=(3*(q1-q0)-(2*v0+v1)*T)/T**2
        b=(2*(q0-q1)+(v0+v1)*T)/T**3
        report["intercept_candidate"]=candidate
        report["planned_max_speed_ratios"]=[0.]*6
        previous=np.array(env._actual_ee_position())
        measurements=[]
        apex=report["release_position"][2]
        for tick in range(math.ceil((T+.16)/env.config.time_step_s)):
            t=(tick+1)*env.config.time_step_s
            if t<=T:
                target=q0+v0*t+a*t*t+b*t**3
                qd=v0+2*a*t+3*b*t*t
            else:
                s=max(0.,t-T-coast_s)
                # Follow through while braking, instead of stopping at contact.
                duration=.20
                s=min(s,duration)
                target=q1+v1*(min(t-T,coast_s)+s-s*s/(2*duration))
                qd=v1*(1-s/duration)
            for i in range(6):
                report["planned_max_speed_ratios"][i]=max(report["planned_max_speed_ratios"][i],abs(qd[i])/env._arm_velocity[i])
            command(env,target,qd)
            env._step(1)
            pos,vel,contact=sample("flight",tick)
            ee=np.array(env._actual_ee_position())
            ev=(ee-previous)/env.config.time_step_s
            previous=ee
            apex=max(apex,pos[2])
            row=dict(time_s=t,cube=list(pos),velocity=list(vel),ee=ee.tolist(),ee_velocity=ev.tolist(),
                     distance_m=math.dist(pos,ee),relative_speed_m_s=math.dist(vel,ev),clearance_m=float(ee[2]-pos[2]))
            measurements.append(row)
            if (vel[2]<-.05 and not contact and row["distance_m"]<=.13
                    and row["clearance_m"]>=.10 and row["relative_speed_m_s"]<=1.
                    and max(report["max_joint_velocity_ratios"])<=1.05
                    and not report["self_penetration_detected"]):
                report["catch_gate_passed"]=row
                # This experiment validates interception only, not finger capture.
                break
            if contact:
                break
        descending=[r for r in measurements if r["velocity"][2]<-.05]
        near=[r for r in descending if r["distance_m"]<=.13 and r["clearance_m"]>=.1]
        report["closest_descending"]=min(descending,key=lambda r:r["distance_m"]) if descending else None
        report["best_within_catch_geometry"]=min(near,key=lambda r:r["relative_speed_m_s"]) if near else None
        report["apex_height_m"]=apex
        report["caught"]=False
        (out/f"{label}_intercept_trace.json").write_text(json.dumps(measurements,indent=2)+"\n")
    report=trial(POSES["best_coordination"],MASS_KG,LEAD_S,DELAYS_493,spin=SPIN_493,
                 release_threshold=gate,release_handler=handler,output=out,label=label)
    return report

if __name__=="__main__":
    results=[]
    for gate in (4.85,4.9):
        candidates=next(r for r in alternatives if r["gate_m_s"]==gate)["candidates"][:4]
        for i,candidate in enumerate(candidates):
            label=f"intercept_{gate}_{i}"
            r=run(candidate,gate,label)
            results.append(r)
            print(json.dumps({k:r.get(k) for k in ("label","valid","catch_gate_passed","closest_descending","best_within_catch_geometry","planned_max_speed_ratios","max_joint_velocity_ratios","self_penetration_detected","error")}),flush=True)
    (out/"dynamic_intercepts.json").write_text(json.dumps(results,indent=2)+"\n")
