"""Measure the loaded collision geometry in the gripper frame; no flight data."""
from __future__ import annotations

import json
import numpy as np

from .catch_online_control import RobotModel


def measure_opening(model):
    p=model.p
    p.performCollisionDetection(physicsClientId=model.client)
    state=p.getLinkState(model.arm,6,computeForwardKinematics=True,physicsClientId=model.client)
    def world(local):
        return p.multiplyTransforms(state[4],state[5],local,[0,0,0,1])[0]
    samples=[]
    for z in np.arange(.105,.176,.002):
        origin=world([0,0,float(z)])
        hits=p.rayTestBatch([origin,origin],[world([0,.15,float(z)]),world([0,-.15,float(z)])],
                            physicsClientId=model.client)
        if hits[0][0]==model.arm and hits[1][0]==model.arm and {hits[0][1],hits[1][1]}=={9,12}:
            samples.append(dict(local_z_m=float(z),gap_m=float((hits[0][2]+hits[1][2])*.15),
                                left_link=hits[0][1],right_link=hits[1][1]))
    gaps=[sample["gap_m"] for sample in samples]
    clearances=[]
    for width in (.08,.10):
        shape=p.createCollisionShape(p.GEOM_BOX,halfExtents=[width/2]*3,physicsClientId=model.client)
        center=p.multiplyTransforms(state[4],state[5],model.capture_offset,[0,0,0,1])[0]
        box=p.createMultiBody(0,shape,-1,center,state[5],physicsClientId=model.client)
        distances=[]
        for link in (9,12):
            points=p.getClosestPoints(box,model.arm,.1,linkIndexB=link,physicsClientId=model.client)
            distances.append(min((point[8] for point in points),default=.1))
        clearances.append(dict(box_width_m=width,finger_signed_distances_m=distances,
                               centered_fit=all(distance>=0 for distance in distances)))
        p.removeBody(box,physicsClientId=model.client)
    return dict(method="opposed rays from the gripper center to the inner finger collision surfaces at local x=0",
                finger_joints_rad=0.,capture_offset_m=model.capture_offset.tolist(),samples=samples,
                max_measured_gap_m=max(gaps) if gaps else None,min_measured_gap_m=min(gaps) if gaps else None,
                object_min_width_m=.10,
                centered_box_clearance=clearances,
                limitation="Measured cross-sections of this model, not a global proof over all grasp poses")


if __name__=="__main__":
    model=RobotModel()
    try:
        print(json.dumps(measure_opening(model),indent=2))
    finally:
        model.close()
