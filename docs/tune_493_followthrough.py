from pathlib import Path
import json
from probe_493_intercept_motion import run,out

data=json.loads((out/"alternative_intercepts.json").read_text())
candidate=next(r for r in data if r["gate_m_s"]==4.85)["candidates"][0]
results=[]
for coast in (.02,.04,.06,.08):
    label=f"followthrough_{coast:.2f}"
    result=run(candidate,4.85,label,coast_s=coast)
    results.append(result)
    print(json.dumps({k:result.get(k) for k in ("label","valid","catch_gate_passed","best_within_catch_geometry","max_joint_velocity_ratios","self_penetration_detected")}),flush=True)
(out/"followthrough_results.json").write_text(json.dumps(results,indent=2)+"\n")
