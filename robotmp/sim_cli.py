from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .environment import FailureMode
from .runner import default_store, run_episode, validate_skill
from .sim_environment import PyBulletPickPlaceEnv, SimConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the robotmp PyBullet simulation backend")
    parser.add_argument("--mode", choices=["baseline", "feedback", "skills"], default="feedback")
    parser.add_argument("--failure-mode", choices=[item.value for item in FailureMode], default="low_grip_force")
    parser.add_argument("--gui", action="store_true", help="open the PyBullet GUI")
    parser.add_argument("--realtime", action="store_true", help="pace simulation steps at one simulated second")
    parser.add_argument("--hold", type=float, default=0.0, help="keep the GUI open after the episode")
    parser.add_argument("--gripper", choices=["urdf", "procedural"], default="urdf")
    parser.add_argument("--arm", choices=["none", "arm6dof", "xarm6"], default="xarm6")
    parser.add_argument("--store", default="artifacts/sim_skills.json")
    parser.add_argument("--trace", type=Path, help="write telemetry JSON")
    parser.add_argument("--validate-skill", action="store_true", help="generate and physically validate the grasp Skill")
    parser.add_argument("--trials", type=int, default=20)
    args = parser.parse_args()

    events: list[dict] = []
    envs: list[PyBulletPickPlaceEnv] = []

    def factory(failure_mode: FailureMode) -> PyBulletPickPlaceEnv:
        env = PyBulletPickPlaceEnv(failure_mode, gui=args.gui, config=SimConfig(realtime=args.realtime, gripper_model=args.gripper, arm_model=args.arm))
        envs.append(env)
        return env

    try:
        if args.validate_skill:
            seed_events: list[dict] = []
            run_episode("skills", FailureMode(args.failure_mode), default_store(args.store), observer=seed_events.append, env_factory=factory)
            skill = validate_skill(default_store(args.store), FailureMode(args.failure_mode), args.trials, env_factory=factory)
            result = run_episode("skills", FailureMode(args.failure_mode), default_store(args.store), observer=events.append, env_factory=factory, close_env=False)
            print(json.dumps({"result": result.__dict__, "verified_skill": skill.__dict__, "trials": args.trials}, ensure_ascii=False, indent=2))
            if args.trace:
                args.trace.parent.mkdir(parents=True, exist_ok=True)
                args.trace.write_text(json.dumps(seed_events + events, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"telemetry: {args.trace}")
            return
        result = run_episode(args.mode, FailureMode(args.failure_mode), default_store(args.store), observer=events.append, env_factory=factory, close_env=False)
        if args.gui and args.hold > 0:
            time.sleep(args.hold)
    finally:
        for env in envs:
            env.close()

    print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    if args.trace:
        args.trace.parent.mkdir(parents=True, exist_ok=True)
        args.trace.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"telemetry: {args.trace}")


if __name__ == "__main__":
    main()
