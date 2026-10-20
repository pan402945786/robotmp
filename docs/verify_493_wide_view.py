from pathlib import Path
import hashlib
import json
import subprocess
import csv
import itertools
import sys
import numpy as np
import pybullet as p
import imageio_ffmpeg
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from robotmp.throw_catch_493_video import camera_matrices
folder=root/"docs/throw_catch_493_wide_video_20261020"
source=root/"docs/throw_catch_493_video_20261020"
canvas=Image.new("RGB",(1280,3*384),"white")
draw=ImageDraw.Draw(canvas)
for i,t in enumerate((14.4,14.6,14.9,15.,15.3,15.5)):
    path=folder/f"frame_{t:.1f}.png"
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),"-v","error","-y","-ss",str(t),"-i",str(folder/"xarm6_throw_493.mp4"),"-frames:v","1",str(path)],check=True)
    canvas.paste(Image.open(path).convert("RGB").resize((640,360)),((i%2)*640,(i//2)*384))
    draw.text(((i%2)*640+8,(i//2)*384+363),f"Wide view {t:.1f}s",fill="black")
canvas.save(folder/"wide_view_contact_sheet.png")
a=(source/"full_493_physics.csv").read_bytes()
b=(folder/"full_493_physics.csv").read_bytes()
result=dict(identical_physics_trace=a==b,sha256=hashlib.sha256(b).hexdigest(),video_bytes=(folder/"xarm6_throw_493.mp4").stat().st_size)
view,projection=camera_matrices(p)
matrix=np.array(projection).reshape((4,4),order="F") @ np.array(view).reshape((4,4),order="F")
pixels=[]
# A sphere of radius sqrt(3)*0.05 bounds the rotating 10 cm cube.
radius=3**.5*.05
for row in csv.DictReader((source/"full_493_physics.csv").open()):
    center=np.array([float(row[k]) for k in ("x","y","z")])
    for corner in itertools.product((-radius,radius),repeat=3):
        clip=matrix@np.r_[center+corner,1.]
        ndc=clip[:3]/clip[3]
        pixels.append([(ndc[0]+1)*480,(1-ndc[1])*360])
pixels=np.array(pixels)
result["projected_cube_bounds_px"]={"min":pixels.min(axis=0).tolist(),"max":pixels.max(axis=0).tolist()}
result["all_cube_bounds_inside_visible_scene"]=bool(np.all(pixels[:,0]>=0) and np.all(pixels[:,0]<960) and np.all(pixels[:,1]>=72) and np.all(pixels[:,1]<720))
assert result["identical_physics_trace"]
assert result["all_cube_bounds_inside_visible_scene"],result
(folder/"view_verification.json").write_text(json.dumps(result,indent=2)+"\n")
print(result)
