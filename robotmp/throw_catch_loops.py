"""Repeated vertical end-point loops using bounded shoulder/elbow oscillations."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .spin_trajectory import periodic_state
from .throw_catch_2m import REQUIRED_VZ
from .throw_catch_coordination import trial


def loop_parameters(center, shoulder, elbow, turns):
    sine = [0., shoulder, 0., 0., -shoulder, 0.]
    cosine = [0., 0., elbow, 0., -elbow, 0.]
    rate = 2.983 / max(math.hypot(a, b) for a, b in zip(sine, cosine))
    return dict(center=center, sine=sine, cosine=cosine, turns=turns, rate=rate)


def coordinated_loop(amplitude, gap, turns):
    # Pass near the previously measured high-speed pose late in the final turn.
    # Small phase offsets form a closed loop instead of retracing one arc.
    pose = [0., -1.184, -2.970, -.02634, .07194, -.70457]
    signs = [0., 1., 1., -1., 1., -1.]
    shifts = [0., 0., gap, .4*gap, .8*gap, 1.2*gap]
    center = [q-sign*amplitude*math.sin(shift) for q, sign, shift in zip(pose, signs, shifts)]
    sine = [sign*amplitude*math.cos(shift+.15) for sign, shift in zip(signs, shifts)]
    cosine = [sign*amplitude*math.sin(shift+.15) for sign, shift in zip(signs, shifts)]
    return dict(center=center, sine=sine, cosine=cosine, turns=turns, rate=2.983/amplitude)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/throw_catch_spin_20261020"))
    parser.add_argument("--coordinated", action="store_true")
    args = parser.parse_args()
    summary_name = "coordinated_loop_summary.json" if args.coordinated else "loop_summary.json"
    if (args.output / summary_name).exists():
        parser.error(f"choose a directory without {summary_name}")
    args.output.mkdir(parents=True, exist_ok=True)
    geometries = [("small", [0., -.6, -1.8, 0., 1., 0.], .65, .6),
                  ("wide", [0., -.8, -1.6, 0., 1., 0.], .9, .9),
                  ("high", [0., -.6, -1.8, 0., 1., 0.], .9, .9)]
    configurations = [(name, lambda turns, c=center, a=shoulder, b=elbow: loop_parameters(c,a,b,turns))
                      for name,center,shoulder,elbow in geometries]
    if args.coordinated:
        configurations = [(f"a{a}_gap{gap}", lambda turns, a=a, g=gap: coordinated_loop(a,g,turns))
                          for a in (.7,.8) for gap in (.04,.10)]
    prefix = "coordinated" if args.coordinated else "vertical"
    reports = []
    for name, configure in configurations:
        for turns in (2, 3, 5):
            loop = configure(turns)
            candidate = {"q": periodic_state(0, **loop)[0], "velocity": [0.]*6}
            report = trial(candidate, .1, .35, [0.]*6, loop=loop,
                           label=f"{prefix}_{name}_{turns}")
            reports.append(report)
            print(json.dumps({"label": report["label"], "valid": report["valid"],
                "peak_vz_m_s": report["peak_vz_m_s"], "error": report.get("error")}), flush=True)
    valid = [r for r in reports if r["valid"]]
    best = max(valid, key=lambda r: r["peak_vz_m_s"]) if valid else None
    traces = []
    if best:
        for turns in (2, 3, 5):
            loop = dict(best["loop"], turns=turns)
            for repeat in range(2):
                traces.append(trial(best["candidate"], .1, .35, [0.]*6, loop=loop,
                    output=args.output, label=f"{prefix}_best_{turns}_{repeat+1}"))
    summary = {"required_vz_m_s": REQUIRED_VZ, "reports": reports, "best": best,
               "traces": traces, "goal_achieved": False,
               "scope": ("Joint-periodic coordinated closed 3D end-point loops near the previous best pose. "
                         if args.coordinated else "Joint-periodic closed end-point loops in vertical XZ plane; "
                         "shoulder/elbow oscillate, wrist compensates. Not an exact Cartesian circle. ") +
                        "Constant phase acceleration, original joint speed/effort/position limits. "
                        "Fixed grasp and no full self-contact response; search self checks every 8 steps, "
                        "detailed repeats every step. No complete catch/place task."}
    (args.output / summary_name).write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"best": best}), flush=True)


if __name__ == "__main__":
    main()
