"""Search measured flight intercepts after nearby, physically executed release gates."""
from pathlib import Path
import json
import math
import sys
import numpy as np
import pybullet as p
import pybullet_data
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from robotmp.throw_catch_coordination import trial,command
from robotmp.throw_catch_493_video import MASS_KG,LEAD_S,DELAYS_493,SPIN_493
from robotmp.throw_catch_spin import POSES

out=Path(__file__).resolve().parent/"throw_catch_493_recovery_20261020"
client=p.connect(p.DIRECT)
p.setAdditionalSearchPath(pybullet_data.getDataPath(),physicsClientId=client)
arm=p.loadURDF("xarm/xarm6_with_gripper.urdf",[.1,0,.7],useFixedBase=True,physicsClientId=client)
movable=[i for i in range(p.getNumJoints(arm,physicsClientId=client)) if p.getJointInfo(arm,i,physicsClientId=client)[3]>=0]
lower=np.array([p.getJointInfo(arm,i,physicsClientId=client)[8] for i in range(1,7)])
upper=np.array([p.getJointInfo(arm,i,physicsClientId=client)[9] for i in range(1,7)])
vmax=np.array([p.getJointInfo(arm,i,physicsClientId=client)[11] for i in range(1,7)])
rng=np.random.default_rng(493)

def solve(pos,vel,fixed,attempts=16):
    target=np.array(pos)+[0,0,.108]
    best=None
    for _ in range(attempts):
        for j,q in zip(range(1,7),rng.uniform(lower+.05,upper-.05)):
            p.resetJointState(arm,j,q,physicsClientId=client)
        kwargs={"targetOrientation":p.getQuaternionFromEuler([math.pi,0,0])} if fixed else {}
        q=np.array(p.calculateInverseKinematics(arm,6,target.tolist(),maxNumIterations=250,
            residualThreshold=1e-5,physicsClientId=client,**kwargs)[:6])
        for i in (0,3,5):
            q[i]=(q[i]+math.pi)%(2*math.pi)-math.pi
        if np.any(q<lower+.01) or np.any(q>upper-.01):
            continue
        for j,value in zip(range(1,7),q):
            p.resetJointState(arm,j,value,physicsClientId=client)
        state=p.getLinkState(arm,6,computeForwardKinematics=True,physicsClientId=client)
        if math.dist(state[4],target)>.003:
            continue
        if fixed:
            quat=p.getDifferenceQuaternion(state[5],p.getQuaternionFromEuler([math.pi,0,0]))
            if p.getAxisAngleFromQuaternion(quat)[1]>.02:
                continue
        allq=[p.getJointState(arm,j,physicsClientId=client)[0] for j in movable]
        jac=np.array(p.calculateJacobian(arm,6,[0,0,0],allq,[0.]*len(allq),[0.]*len(allq),physicsClientId=client)[0])[:,:6]
        qd=np.zeros(6)
        for iteration in range(70):
            for i in range(6):
                axis=jac[:,i]
                qd[i]=np.clip(qd[i]+axis@(vel-jac@qd)/(axis@axis+1e-12),-vmax[i],vmax[i])
        error=float(np.linalg.norm(vel-jac@qd))
        record=dict(relative_speed_m_s=error,q=q.tolist(),qd=qd.tolist(),ee=list(state[4]),
                    ee_velocity=(jac@qd).tolist(),fixed_orientation=fixed)
        if best is None or error<best["relative_speed_m_s"]:
            best=record
    return best

if __name__ == "__main__":
    results=[]
    for gate in (4.7,4.75,4.8,4.85,4.9):
        flight=[]
        def handler(env,report,sample,offset):
            q=[env.p.getJointState(env._gripper_id,j,physicsClientId=env.client)[0] for j in env._arm_joint_ids]
            command(env,q)
            for tick in range(330):
                env._step(1)
                pos,vel,contact=sample("flight",tick)
                if tick%4==0 and vel[2]<-.05 and .5<pos[2]<1.5:
                    flight.append(dict(time_s=(tick+1)*env.config.time_step_s,cube=list(pos),velocity=list(vel)))
                if contact:
                    break
        launch=trial(POSES["best_coordination"],MASS_KG,LEAD_S,DELAYS_493,spin=SPIN_493,
                     release_threshold=gate,release_handler=handler)
        candidates=[]
        for row in flight:
            for fixed in (True,False):
                best=solve(row["cube"],np.array(row["velocity"]),fixed)
                if best:
                    candidates.append(dict(**row,**best))
        candidates.sort(key=lambda r:r["relative_speed_m_s"])
        record=dict(gate_m_s=gate,release_position=launch.get("release_position"),release_velocity=launch.get("release_velocity"),
                    candidates=candidates,flight=flight)
        results.append(record)
        print(json.dumps(dict(gate_m_s=gate,best=candidates[:2])),flush=True)
    (out/"alternative_intercepts.json").write_text(json.dumps(results,indent=2)+"\n")
    p.disconnect(client)
