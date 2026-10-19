from __future__ import annotations

import argparse
import json
from dataclasses import replace

from .diagnosis import LLMConfig, make_diagnoser
from .environment import FailureMode
from .runner import default_store, run_ab_experiment, run_episode, validate_skill


def add_diagnoser_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--diagnoser", choices=["auto", "rules", "llm"], default="auto")
    parser.add_argument("--llm-base-url", help="OpenAI-compatible API base, e.g. http://127.0.0.1:15723/v1")
    parser.add_argument("--llm-model", help="Model id accepted by the configured provider")
    parser.add_argument("--llm-wire-api", choices=["responses", "chat"], help="HTTP API shape")
    parser.add_argument("--llm-timeout", type=float, help="LLM request timeout in seconds")


def build_diagnoser(args: argparse.Namespace):
    values = {key: value for key, value in {
        "base_url": args.llm_base_url,
        "model": args.llm_model,
        "wire_api": args.llm_wire_api,
        "timeout_seconds": args.llm_timeout,
    }.items() if value is not None}
    config = replace(LLMConfig.from_env(), **values) if values else None
    return make_diagnoser(args.diagnoser, config)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the robotmp predictive-failure MVP")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run one episode")
    demo.add_argument("--mode", choices=["baseline", "feedback", "skills"], default="skills")
    demo.add_argument("--failure-mode", choices=[item.value for item in FailureMode], default="low_grip_force")
    demo.add_argument("--store", default="artifacts/skills.json")
    add_diagnoser_args(demo)

    validate = sub.add_parser("validate", help="validate and promote the grasp-without-lift Skill")
    validate.add_argument("--trials", type=int, default=20)
    validate.add_argument("--store", default="artifacts/skills.json")
    add_diagnoser_args(validate)

    experiment = sub.add_parser("experiment", help="run the A/B/C comparison")
    experiment.add_argument("--trials", type=int, default=20)
    experiment.add_argument("--failure-mode", choices=[item.value for item in FailureMode], default="low_grip_force")
    experiment.add_argument("--root", default="artifacts/experiment")
    add_diagnoser_args(experiment)

    args = parser.parse_args()
    diagnoser = build_diagnoser(args)

    if args.command == "demo":
        result = run_episode(args.mode, FailureMode(args.failure_mode), default_store(args.store), diagnoser=diagnoser)
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    elif args.command == "validate":
        skill = validate_skill(default_store(args.store), trials=args.trials, diagnoser=diagnoser)
        print(json.dumps(skill.__dict__, ensure_ascii=False, indent=2))
    elif args.command == "experiment":
        summary = run_ab_experiment(FailureMode(args.failure_mode), args.trials, args.root, diagnoser=diagnoser)
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
