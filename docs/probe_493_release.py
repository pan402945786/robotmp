"""Measure alternative release gates with the original physical launch."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from robotmp.throw_catch_coordination import trial
from robotmp.throw_catch_493_video import MASS_KG,LEAD_S,DELAYS_493,SPIN_493
from robotmp.throw_catch_spin import POSES

reports=[]
def released(env, report, sample, offset):
    pass
for threshold in (4.6,4.7,4.8,4.85,4.9,4.92,4.925):
    r=trial(POSES["best_coordination"],MASS_KG,LEAD_S,DELAYS_493,spin=SPIN_493,
            release_threshold=threshold,release_handler=released)
    reports.append(r)
    print(json.dumps({k:r.get(k) for k in ("release_threshold_m_s","release_position","release_velocity","release_time_s","valid")}),flush=True)
(Path(__file__).resolve().parent/"throw_catch_493_recovery_20261020/release_gates.json").write_text(json.dumps(reports,indent=2)+"\n")
