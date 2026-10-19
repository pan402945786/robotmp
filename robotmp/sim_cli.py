from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .diagnosis import LLMConfig, make_diagnoser
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
    parser.add_argument("--diagnoser", choices=["auto", "rules", "llm"], default="auto")
    parser.add_argument("--llm-base-url")
    parser.add_argument("--llm-model")
    parser.add_argument("--llm-wire-api", choices=["responses", "chat"])
    parser.add_argument("--llm-timeout", type=float)
    parser.add_argument("--llm-log", help="JSONL log for model requests and responses")
    args = parser.parse_args()
    config = LLMConfig.from_env()
    if args.llm_base_url:
        config = LLMConfig(args.llm_base_url, config.model, config.wire_api, config.api_key, config.timeout_seconds, config.log_path)
    if args.llm_model:
        config = LLMConfig(config.base_url, args.llm_model, config.wire_api, config.api_key, config.timeout_seconds, config.log_path)
    if args.llm_wire_api:
        config = LLMConfig(config.base_url, config.model, args.llm_wire_api, config.api_key, config.timeout_seconds, config.log_path)
    if args.llm_timeout is not None:
        config = LLMConfig(config.base_url, config.model, config.wire_api, config.api_key, args.llm_timeout, config.log_path)
    if args.llm_log is not None:
        config = LLMConfig(config.base_url, config.model, config.wire_api, config.api_key, config.timeout_seconds, args.llm_log)
    diagnoser = make_diagnoser(args.diagnoser, config)

    events: list[dict] = []
    envs: list[PyBulletPickPlaceEnv] = []

    def factory(failure_mode: FailureMode) -> PyBulletPickPlaceEnv:
        env = PyBulletPickPlaceEnv(failure_mode, gui=args.gui, config=SimConfig(realtime=args.realtime, gripper_model=args.gripper, arm_model=args.arm))
        envs.append(env)
        return env

    try:
        if args.validate_skill:
            seed_events: list[dict] = []
            run_episode("skills", FailureMode(args.failure_mode), default_store(args.store), diagnoser=diagnoser, observer=seed_events.append, env_factory=factory)
            skill = validate_skill(default_store(args.store), FailureMode(args.failure_mode), args.trials, env_factory=factory, diagnoser=diagnoser)
            result = run_episode("skills", FailureMode(args.failure_mode), default_store(args.store), diagnoser=diagnoser, observer=events.append, env_factory=factory, close_env=False)
            print(json.dumps({"result": result.__dict__, "verified_skill": skill.__dict__, "trials": args.trials}, ensure_ascii=False, indent=2))
            if args.trace:
                args.trace.parent.mkdir(parents=True, exist_ok=True)
                args.trace.write_text(json.dumps(seed_events + events, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"telemetry: {args.trace}")
            return
        result = run_episode(args.mode, FailureMode(args.failure_mode), default_store(args.store), diagnoser=diagnoser, observer=events.append, env_factory=factory, close_env=False)
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
