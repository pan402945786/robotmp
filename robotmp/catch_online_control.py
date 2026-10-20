"""Observation-driven intercept planning against an independent robot model.

The controller has no access to the dynamic world, result files or future frames.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import time

import numpy as np

from .catch_observation import FlightEstimator
from .sim_environment import _require_pybullet, _pybullet_data


@dataclass
class InterceptPlan:
    issued_at: float
    intercept_at: float
    observation_at: float
    cube_position: list[float]
    cube_velocity: list[float]
    q0: np.ndarray
    v0: np.ndarray
    q1: np.ndarray
    v1: np.ndarray
    relative_speed: float
    peak_speed_ratio: float
    score: float

    def evaluate(self, now, coast=.03):
        duration=self.intercept_at-self.issued_at
        elapsed=max(0.,now-self.issued_at)
        a=(3*(self.q1-self.q0)-(2*self.v0+self.v1)*duration)/duration**2
        b=(2*(self.q0-self.q1)+(self.v0+self.v1)*duration)/duration**3
        if elapsed<=duration:
            return (self.q0+self.v0*elapsed+a*elapsed**2+b*elapsed**3,
                    self.v0+2*a*elapsed+3*b*elapsed**2)
        after=elapsed-duration
        brake=min(.25,max(0.,after-coast))
        return (self.q1+self.v1*(min(after,coast)+brake-brake**2/.5),
                self.v1*(1-brake/.25))


class RobotModel:
    """All resets below affect only this object-free kinematics client."""

    def __init__(self, *, base=(.1,0,.7)):
        self.p=_require_pybullet()
        p=self.p
        self.client=p.connect(p.DIRECT)
        p.setAdditionalSearchPath(_pybullet_data.getDataPath(),physicsClientId=self.client)
        self.arm=p.loadURDF("xarm/xarm6_with_gripper.urdf",base,useFixedBase=True,physicsClientId=self.client)
        self.joints=list(range(1,7))
        self.movable=[i for i in range(p.getNumJoints(self.arm,physicsClientId=self.client))
                      if p.getJointInfo(self.arm,i,physicsClientId=self.client)[3]>=0]
        infos=[p.getJointInfo(self.arm,j,physicsClientId=self.client) for j in self.joints]
        self.lower=np.array([i[8] for i in infos])+.015
        self.upper=np.array([i[9] for i in infos])-.015
        self.vmax=np.array([i[11] for i in infos])
        self.base=np.array(base)
        # Finger pad centroids from the loaded link geometry, not a flight replay.
        self.set(np.zeros(6))
        pads=[]
        for link,offset in ((9,[0,-.016,.029]),(12,[0,.016,.029])):
            state=p.getLinkState(self.arm,link,computeForwardKinematics=True,physicsClientId=self.client)
            pads.append(p.multiplyTransforms(state[4],state[5],offset,[0,0,0,1])[0])
        ee=p.getLinkState(self.arm,6,computeForwardKinematics=True,physicsClientId=self.client)
        inv=p.invertTransform(ee[4],ee[5])
        self.capture_offset=np.array(p.multiplyTransforms(*inv,np.mean(pads,axis=0),[0,0,0,1])[0])

    def set(self,q):
        for j,value in zip(self.joints,q):
            self.p.resetJointState(self.arm,j,float(value),physicsClientId=self.client)

    def state(self,q):
        p=self.p
        self.set(q)
        link=p.getLinkState(self.arm,6,computeForwardKinematics=True,physicsClientId=self.client)
        point=np.array(p.multiplyTransforms(link[4],link[5],self.capture_offset,[0,0,0,1])[0])
        values=[p.getJointState(self.arm,j,physicsClientId=self.client)[0] for j in self.movable]
        linear,angular=p.calculateJacobian(self.arm,6,self.capture_offset,values,[0.]*len(values),[0.]*len(values),physicsClientId=self.client)
        rotation=np.array(p.getMatrixFromQuaternion(link[5])).reshape(3,3)
        return point,np.array(linear)[:,:6],np.array(angular)[:,:6],rotation

    def fit_position(self,target,seed,*,tilt_weight=0.,iterations=65):
        q=np.clip(seed,self.lower,self.upper)
        target=np.array(target)
        for _ in range(iterations):
            point,jac,angular,rotation=self.state(q)
            error=target-point
            if np.linalg.norm(error)<.002:
                break
            if tilt_weight:
                axis=rotation[:,2]
                orient=np.cross(axis,[0,0,-1])
                matrix=np.vstack((jac,tilt_weight*angular))
                residual=np.r_[error,tilt_weight*orient]
            else:
                matrix,residual=jac,error
            delta=matrix.T@np.linalg.solve(matrix@matrix.T+np.eye(len(residual))*.0004,residual)
            q=np.clip(q+np.clip(delta,-.18,.18),self.lower,self.upper)
        point,jac,angular,rotation=self.state(q)
        return q,point,jac,rotation

    def fit_velocity(self,jac,velocity,q=None):
        qd=np.zeros(6)
        limit=self.vmax*.98
        lower=-limit
        upper=limit
        if q is not None:
            # Reserve joint travel for 40 ms of following and 250 ms of braking.
            lower=np.maximum(lower,(self.lower-q)/.165)
            upper=np.minimum(upper,(self.upper-q)/.165)
        for _ in range(35):
            for i in range(6):
                axis=jac[:,i]
                qd[i]=np.clip(qd[i]+axis@(velocity-jac@qd)/(axis@axis+1e-10),lower[i],upper[i])
        return qd,float(np.linalg.norm(velocity-jac@qd))

    def close(self):
        self.p.disconnect(self.client)


class OnlineCatchController:
    def __init__(self,model: RobotModel,parameters):
        self.model=model
        self.parameters=dict(parameters)
        self.estimator=FlightEstimator(window=int(parameters.get("window_frames",10)),
            estimate_drag=bool(parameters.get("estimate_drag",False)),stale_s=float(parameters.get("stale_s",.075)))
        self.plan=None
        self.pending_plan=None
        self.pending_ready_at=math.inf
        self.last_replan=-math.inf
        self.events=[]
        self.rng=np.random.default_rng(74291)
        self.plan_count=0
        self.deadline_misses=0
        self.max_plan_wall_s=0.
        self.clock_valid=True
        self.late_plan_rejections=0

    def executable(self,plan):
        for fraction in np.linspace(0,1,21):
            q,qd=plan.evaluate(plan.issued_at+(plan.intercept_at-plan.issued_at)*fraction)
            if (np.max(np.abs(qd)/self.model.vmax)>1.02
                    or np.any(q<self.model.lower) or np.any(q>self.model.upper)):
                return False
        q,_=plan.evaluate(plan.intercept_at+.30,coast=float(self.parameters.get("coast_s",.04)))
        return bool(np.all(q>=self.model.lower) and np.all(q<=self.model.upper))

    def observe(self,observation,now):
        return self.estimator.observe(observation,now)

    def replan(self,now,q,qd):
        if not self.estimator.ready(now):
            return None
        started=time.perf_counter()
        current=np.array(q)
        velocity=np.array(qd)
        previous=self.plan
        predictions=[]
        for horizon in np.arange(.16,1.21,float(self.parameters.get("horizon_step_s",.06))):
            cube,cube_v=self.estimator.predict(now+float(horizon))
            if cube_v[2]>=-.1 or not .45<=cube[2]<=1.55 or np.linalg.norm(cube-self.model.base)>.98:
                continue
            predictions.append((float(horizon),cube,cube_v))
        candidates=[]
        seeds=[current]
        if previous is not None:
            seeds.append(previous.q1)
        # Model-space exploration is allowed; no old successful joint poses are loaded.
        for _ in range(int(self.parameters.get("ik_seeds",3))):
            seeds.append(np.clip(current+self.rng.normal(0,1.1,6),self.model.lower,self.model.upper))
        for horizon,cube,cube_v in predictions:
            for seed in seeds:
                goal,point,jac,rotation=self.model.fit_position(cube,seed,
                    tilt_weight=float(self.parameters.get("tilt_weight",0.)),iterations=int(self.parameters.get("ik_iterations",65)))
                residual=float(np.linalg.norm(point-cube))
                if residual>.012:
                    continue
                for i in (0,3,5):
                    equivalent=current[i]+(goal[i]-current[i]+math.pi)%(2*math.pi)-math.pi
                    if self.model.lower[i]<=equivalent<=self.model.upper[i]:
                        goal[i]=equivalent
                terminal,relative=self.model.fit_velocity(jac,cube_v,goal if self.parameters.get("strict_trajectory",False) else None)
                plan=InterceptPlan(now,now+horizon,self.estimator.history[-1].captured_at,
                    cube.tolist(),cube_v.tolist(),current.copy(),velocity.copy(),goal,terminal,relative,0.,0.)
                peak=0.
                position_ok=True
                for fraction in np.linspace(0,1,13):
                    at,speed=plan.evaluate(now+horizon*fraction)
                    peak=max(peak,float(np.max(np.abs(speed)/self.model.vmax)))
                    position_ok &= bool(np.all(at>=self.model.lower) and np.all(at<=self.model.upper))
                if not position_ok:
                    continue
                plan.peak_speed_ratio=peak
                if self.parameters.get("strict_trajectory",False) and not self.executable(plan):
                    continue
                tilt=math.acos(float(np.clip(rotation[:,2]@[0,0,-1],-1,1)))
                plan.score=relative+8*max(0.,peak-1.)+.10*np.linalg.norm(goal-current)+.15*tilt+20*residual
                if previous is not None:
                    plan.score+=float(self.parameters.get("time_hysteresis",0.))*abs(plan.intercept_at-previous.intercept_at)
                candidates.append(plan)
        best=min(candidates,key=lambda item:item.score) if candidates else None
        elapsed=time.perf_counter()-started
        self.max_plan_wall_s=max(self.max_plan_wall_s,elapsed)
        self.deadline_misses+=int(elapsed>float(self.parameters.get("replan_s",.1)))
        self.last_replan=now
        self.plan_count+=1
        if best is not None:
            # The real world keeps moving during planning. Do not apply a result
            # as if its measured computation time had been zero.
            self.pending_plan=best
            self.pending_ready_at=now+max(elapsed,float(self.parameters.get("planner_latency_s",0.)))
        self.events.append(dict(issued_at=now,latest_observation_at=self.estimator.history[-1].captured_at,
            wall_s=elapsed,candidates=len(candidates),drag=self.estimator.drag,
            plan=None if best is None else dict(intercept_at=best.intercept_at,cube=best.cube_position,
                velocity=best.cube_velocity,relative_speed=best.relative_speed,planned_speed_ratio=best.peak_speed_ratio,score=best.score)))
        return best

    def control(self,now,q,qd,dt):
        if not self.estimator.ready(now):
            # Stop extrapolating indefinitely through missing observations.
            return np.array(q),np.zeros(6),False
        if self.pending_plan is not None and now+1e-9>=self.pending_ready_at:
            if self.pending_plan.intercept_at>now+.03:
                if self.parameters.get("strict_trajectory",False):
                    # Rebase onto measured encoders when the computation actually
                    # becomes available, then check the remaining path again.
                    candidate=self.pending_plan
                    candidate.issued_at=now
                    candidate.q0=np.array(q)
                    candidate.v0=np.array(qd)
                    if self.executable(candidate):
                        self.plan=candidate
                    else:
                        self.late_plan_rejections+=1
                else:
                    self.plan=self.pending_plan
            self.pending_plan=None
        if (self.pending_plan is None
                and now-self.last_replan>=float(self.parameters.get("replan_s",.1))-1e-9):
            self.replan(now,q,qd)
        if self.plan is None:
            return np.array(q),np.zeros(6),False
        target,speed=self.plan.evaluate(now+dt,coast=float(self.parameters.get("coast_s",.04)))
        # Every issued command respects the model limits even if a candidate path was too fast.
        speed=np.clip(speed,-self.model.vmax*.98,self.model.vmax*.98)
        target=np.clip(target,self.model.lower,self.model.upper)
        close=self.plan.intercept_at-now<=float(self.parameters.get("close_lead_s",.22))
        return target,speed,close

