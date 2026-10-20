"""Compare bounded, progressively accelerating rotations before an upward swing."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .throw_catch_2m import REQUIRED_VZ
from .throw_catch_coordination import trial


POSES = {
    "best_coordination": {
        "q": [0., -1.4992445845535043, -2.8759831460282608,
              -.22272763178339616, .32799815400855636, -1.0203010329273017],
        "velocity": [0., 2.983, 2.983, -2.983, 2.983, -2.983],
    },
    "wrist_clearance": {
        "q": [0., -1.6966139404377136, -2.7460454177281637,
              2.4394824534407373, 1.0510139405095462, -.08331748035886832],
        "velocity": [0., 2.983, 2.983, -2.983, -2.983, 2.983],
    },
}
DELAYS = {"best_coordination": [0., 0., .04, .06, .08, .10],
          "wrist_clearance": [0., 0., .08, .12, .16, .20]}


def specifications():
    for turns in (.5, 1., 1.5, 1.75, 2.):
        yield f"base_{turns:g}", dict(turns=turns, joints=[0], directions=[1])
    for joint in (3, 5):
        for direction in (-1, 1):
            for turns in (.5, 1., 1.5):
                yield f"J{joint+1}_{direction:+d}_{turns:g}", dict(
                    turns=turns, joints=[joint], directions=[direction])
    for turns in (.5, 1.):
        yield f"wrists_{turns:g}", dict(turns=turns, joints=[3, 5], directions=[-1, 1])
        yield f"base_wrists_{turns:g}", dict(turns=turns, joints=[0, 3, 5], directions=[1, -1, 1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/throw_catch_spin_20261020"))
    args = parser.parse_args()
    if (args.output / "summary.json").exists():
        parser.error("choose a new output directory")
    args.output.mkdir(parents=True, exist_ok=True)
    baselines, reports = [], []
    for name, pose in POSES.items():
        base = trial(pose, .1, .35, DELAYS[name], output=args.output, label=f"baseline_{name}")
        baselines.append(base)
        for label, spin in specifications():
            report = trial(pose, .1, .35, DELAYS[name], spin=spin, label=f"{name}_{label}")
            reports.append(report)
            print(json.dumps({"label": report["label"], "valid": report["valid"],
                              "peak_vz_m_s": report["peak_vz_m_s"],
                              "error": report.get("error")}), flush=True)
    valid = [r for r in reports if r["valid"]]
    best = max(valid, key=lambda r: r["peak_vz_m_s"]) if valid else None
    repeats = []
    if best:
        for mass in (.1, .001):
            for repeat in range(3):
                spin = {"turns": best["spin_plan"]["turns"],
                        "joints": [int(i) for i in best["spin_plan"]["joints"]],
                        "directions": [s["direction"] for s in best["spin_plan"]["joints"].values()]}
                repeats.append(trial(best["candidate"], mass, best["lead_s"], best["delays_s"],
                    spin=spin, output=args.output, label=f"best_spin_{mass}kg_{repeat+1}"))
    # Detailed 1.75-turn base trace makes the per-turn acceleration observable.
    long_spin = trial(POSES["best_coordination"], .1, .35, DELAYS["best_coordination"],
        spin=dict(turns=1.75, joints=[0], directions=[1]), output=args.output, label="base_1.75_turn_trace")
    summary = {"required_vz_m_s": REQUIRED_VZ, "matched_baselines": baselines,
               "reports": reports, "best": best, "repeats": repeats,
               "long_spin": long_spin, "goal_achieved": False,
               "scope": "Bounded original URDF, fixed grasp, no angle wrapping/state resets. "
                        "Constant acceleration during pre-rotation, continuous speed into swing, then braking. "
                        "Only swing samples can trigger release; no complete catch/place task. "
                        "Self penetration checked every 8 steps in search, every step in detailed runs. "
                        "No full self-contact response, no calibrated acceleration/jerk limits."}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"best": best, "summary": str(args.output / "summary.json")}), flush=True)


if __name__ == "__main__":
    main()
