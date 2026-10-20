"""Object-free IK and velocity feasibility search for the measured descending flight."""
from pathlib import Path
import json
import math
import numpy as np
import pybullet as p
import pybullet_data

out = Path(__file__).resolve().parent / "throw_catch_493_recovery_20261020"
flight = json.loads((out/"baseline_diagnosis.json").read_text())["flight"]
p.connect(p.DIRECT)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
arm = p.loadURDF("xarm/xarm6_with_gripper.urdf", [.1,0,.7], useFixedBase=True)
joints = [i for i in range(p.getNumJoints(arm)) if p.getJointInfo(arm,i)[3] >= 0]
lower = np.array([p.getJointInfo(arm,i)[8] for i in range(1,7)])
upper = np.array([p.getJointInfo(arm,i)[9] for i in range(1,7)])
vmax = np.array([p.getJointInfo(arm,i)[11] for i in range(1,7)])
rng = np.random.default_rng(493)

def speed_fit(jac, velocity):
    v = np.zeros(6)
    # Coordinate descent solves the bounded convex least-squares velocity fit.
    for _ in range(100):
        for i in range(6):
            axis=jac[:,i]
            v[i]=np.clip(v[i]+axis@(velocity-jac@v)/(axis@axis+1e-12),-vmax[i],vmax[i])
    return float(np.linalg.norm(jac@v-velocity)),v

results=[]
for row in flight[::3]:
    t=row["after_release_s"]
    if not .86 <= t <= 1.09:
        continue
    pos=np.array(row["cube"])
    target=pos+np.array([0,0,.108])
    for fixed_orientation in (True,False):
        best=None
        for attempt in range(30):
            seed=rng.uniform(lower+.05,upper-.05)
            for j,q in zip(range(1,7),seed):
                p.resetJointState(arm,j,q)
            kwargs={"targetOrientation":p.getQuaternionFromEuler([math.pi,0,0])} if fixed_orientation else {}
            sol=p.calculateInverseKinematics(arm,6,target.tolist(),maxNumIterations=200,
                residualThreshold=1e-5,**kwargs)
            q=np.array(sol[:6])
            for i in (0,3,5):
                q[i]=(q[i]+math.pi)%(2*math.pi)-math.pi
            if np.any(q<lower+.01) or np.any(q>upper-.01):
                continue
            for j,value in zip(range(1,7),q):
                p.resetJointState(arm,j,value)
            ee=np.array(p.getLinkState(arm,6,computeForwardKinematics=True)[4])
            if np.linalg.norm(ee-target)>.005:
                continue
            allq=[p.getJointState(arm,j)[0] for j in joints]
            jac=np.array(p.calculateJacobian(arm,6,[0,0,0],allq,[0.]*len(allq),[0.]*len(allq))[0])[:,:6]
            error,qd=speed_fit(jac,np.array(row["velocity"]))
            record=dict(t_s=t,ee=ee.tolist(),cube=row["cube"],velocity=row["velocity"],
                        q=q.tolist(),qd=qd.tolist(),ee_velocity=(jac@qd).tolist(),
                        relative_speed_bound_m_s=error,fixed_orientation=fixed_orientation)
            if best is None or error<best["relative_speed_bound_m_s"]:
                best=record
        if best:
            results.append(best)
    print(json.dumps(results[-2:]),flush=True)
(out/"reachability.json").write_text(json.dumps(dict(scope="instantaneous kinematics only; no path, collision, torque or acceleration guarantee",results=results),indent=2)+"\n")
print("BEST",json.dumps(sorted(results,key=lambda r:r["relative_speed_bound_m_s"])[:5]))
