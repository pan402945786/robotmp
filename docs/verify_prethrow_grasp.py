"""Compare the original model with the corrected actual pre-throw geometry."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from robotmp.throw_catch_coordination import acquire,command
from robotmp.throw_catch_spin import POSES

OUT=ROOT/"docs/prethrow_grasp_fix_20261020"
BASELINE="0f2cc612ffc7f9b287327f22e5633943ecdfa23a"


def old_acquire():
    snapshot=OUT/"before_sim_environment.py"
    if not snapshot.exists():
        source=subprocess.run(["git","show",f"{BASELINE}:robotmp/sim_environment.py"],cwd=ROOT,
                              check=True,capture_output=True).stdout
        snapshot.write_bytes(source)
    spec=importlib.util.spec_from_file_location("robotmp._before_sim",snapshot)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    env=module.PyBulletPickPlaceEnv(config=module.SimConfig(arm_model="xarm6",cube_half_extent=.025))
    p=env.p
    p.removeBody(env._table_id,physicsClientId=env.client)
    env.ground=p.loadURDF("plane.urdf",physicsClientId=env.client)
    shape=p.createCollisionShape(p.GEOM_BOX,halfExtents=[.08,.08,.02],physicsClientId=env.client)
    stand=p.createMultiBody(0,shape,-1,[.45,0,.68],physicsClientId=env.client)
    for action in ("approach_object","close_gripper","lift_object"):
        env.execute(action)
    p.removeBody(stand,physicsClientId=env.client)
    return env


def prepare(env):
    pose=POSES["best_coordination"]
    start=[max(lo+.05,min(hi-.05,q-v*.8*.35))
           for lo,hi,q,v in zip(env._arm_lower,env._arm_upper,pose["q"],pose["velocity"])]
    command(env,start,speed_scale=.25)
    for tick in range(2400):
        env._step(1)
        q=[env.p.getJointState(env._gripper_id,j,physicsClientId=env.client)[0] for j in env._arm_joint_ids]
        if tick>120 and max(abs(a-b) for a,b in zip(q,start))<.015:
            break
    env._step(120)


def snapshot(env,label):
    p=env.p
    pos=env._cube_position()
    gaps=[min((x[8] for x in p.getClosestPoints(env._cube_id,env._gripper_id,.5,linkIndexB=j,
         physicsClientId=env.client)),default=None) for j in (9,12)]
    view=p.computeViewMatrixFromYawPitchRoll(pos,.36,65,-18,0,2)
    projection=p.computeProjectionMatrixFOV(48,1.,.005,5)
    _,_,rgba,_,_=p.getCameraImage(720,720,view,projection,renderer=p.ER_TINY_RENDERER,physicsClientId=env.client)
    image=Image.fromarray(rgba[:,:,:3])
    image.save(OUT/f"{label}.png")
    return image,dict(finger_signed_distances_m=gaps,cube_position_m=pos,
        finger_angles_rad=[p.getJointState(env._gripper_id,j,physicsClientId=env.client)[0] for j in range(8,14)])


def main():
    OUT.mkdir(exist_ok=True)
    images=[]
    evidence={}
    for label in ("before","after"):
        env=old_acquire() if label=="before" else acquire(.1,cube_size_m=.05)[0]
        try:
            prepare(env)
            image,evidence[label]=snapshot(env,label)
            if label=="after":
                evidence[label]["initial_contact"]=env._initial_grasp_evidence
                evidence[label]["retained_geometry"]=env.finger_grasp_geometry()
            images.append(image)
        finally:
            env.close()
    combined=Image.new("RGB",(1440,840),"#0b1524")
    draw=ImageDraw.Draw(combined)
    font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",27)
    for index,label in enumerate(("before","after")):
        combined.paste(images[index],(720*index,120))
        draw.text((24+720*index,18),"修复前" if label=="before" else "修复后：接触确认再抬升",font=font,fill="white")
        gaps=evidence[label]["finger_signed_distances_m"]
        draw.text((24+720*index,65),f"双指表面距离：{gaps[0]*1000:+.2f} / {gaps[1]*1000:+.2f} mm",font=font,fill="#68e6ff")
    combined.save(OUT/"before_after.png")
    evidence.update(baseline_commit=BASELINE,
        baseline_source_sha256=hashlib.sha256((OUT/"before_sim_environment.py").read_bytes()).hexdigest(),
        note="Independent physical runs with the same commanded prethrow pose; no joint or object state resets. "
             "Positive signed distance is a gap; negative is contact penetration.")
    (OUT/"comparison.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(evidence))


if __name__=="__main__":
    main()
