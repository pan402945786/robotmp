"""Build compact, auditable metrics and a report from the stored experiments."""
from pathlib import Path
import csv
import json
import math
import numpy as np
import pybullet as p
import pybullet_data

root=Path(__file__).resolve().parents[1]
out=root/"docs/throw_catch_493_recovery_20261020"
baseline=json.loads((out/"baseline_diagnosis.json").read_text())
alternatives=json.loads((out/"alternative_intercepts.json").read_text())
dynamic=json.loads((out/"dynamic_intercepts.json").read_text())
follow=json.loads((out/"followthrough_results.json").read_text())
selected=follow[0]
event=selected["catch_gate_passed"]
rows=list(csv.DictReader((out/(selected["label"]+"_physics.csv")).open()))
row=min(rows,key=lambda r:abs(float(r["t_s"])-(selected["release_time_s"]+event["time_s"])))
client=p.connect(p.DIRECT)
p.setAdditionalSearchPath(pybullet_data.getDataPath(),physicsClientId=client)
arm=p.loadURDF("xarm/xarm6_with_gripper.urdf",[.1,0,.7],useFixedBase=True,physicsClientId=client)
for j in range(1,7):
    p.resetJointState(arm,j,float(row[f"q{j-1}"]),physicsClientId=client)
state=p.getLinkState(arm,6,computeForwardKinematics=True,physicsClientId=client)
inv=p.invertTransform(state[4],state[5])
local=p.multiplyTransforms(*inv,event["cube"],[0,0,0,1])[0]
matrix=p.getMatrixFromQuaternion(state[5])
axis=np.array([matrix[2],matrix[5],matrix[8]])
tilt=math.degrees(math.acos(float(np.clip(axis@[0,0,-1],-1,1))))
p.disconnect(client)
metrics=dict(original_nearest=baseline["nearest_descending"],
    original_instantaneous_search_best=min((r for a in alternatives if a["gate_m_s"]==4.9 for r in a["candidates"]),key=lambda r:r["relative_speed_m_s"]),
    alternative_release=dict(time_s=selected["release_time_s"],position=selected["release_position"],velocity=selected["release_velocity"]),
    alternative_interception=event,alternative_actual_joint_speed_ratios=selected["max_joint_velocity_ratios"],
    alternative_cube_in_ee_frame_m=list(local),gripper_axis_tilt_from_down_deg=tilt,
    full_catch_validated=False,scope="Position/velocity interception research, not finger-contact capture or real-hardware validation")
(out/"research_summary.json").write_text(json.dumps(metrics,indent=2)+"\n")
print(json.dumps(metrics,indent=2))
