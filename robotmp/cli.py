from __future__ import annotations

import argparse
import json

from .environment import FailureMode
from .runner import default_store, run_ab_experiment, run_episode, validate_skill


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the robotmp predictive-failure MVP")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run one episode")
    demo.add_argument("--mode", choices=["baseline", "feedback", "skills"], default="skills")
    demo.add_argument("--failure-mode", choices=[item.value for item in FailureMode], default="low_grip_force")
    demo.add_argument("--store", default="artifacts/skills.json")

    validate = sub.add_parser("validate", help="validate and promote the grasp-without-lift Skill")
    validate.add_argument("--trials", type=int, default=20)
    validate.add_argument("--store", default="artifacts/skills.json")

    experiment = sub.add_parser("experiment", help="run the A/B/C comparison")
    experiment.add_argument("--trials", type=int, default=20)
    experiment.add_argument("--failure-mode", choices=[item.value for item in FailureMode], default="low_grip_force")
    experiment.add_argument("--root", default="artifacts/experiment")

    args = parser.parse_args()

    if args.command == "demo":
        store = default_store(args.store)
        result = run_episode(args.mode, FailureMode(args.failure_mode), store)
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    elif args.command == "validate":
        store = default_store(args.store)
        skill = validate_skill(store, trials=args.trials)
        print(json.dumps(skill.__dict__, ensure_ascii=False, indent=2))
    elif args.command == "experiment":
        summary = run_ab_experiment(FailureMode(args.failure_mode), args.trials, args.root)
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
