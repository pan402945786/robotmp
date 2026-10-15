from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import Skill


class SkillStore:
    """JSON-backed store for the first MVP; replaceable by SQLite later."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> list[Skill]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Skill(**item) for item in raw]

    def _write(self, skills: list[Skill]) -> None:
        self.path.write_text(
            json.dumps([asdict(skill) for skill in skills], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def all(self) -> list[Skill]:
        return self._read()

    def save_candidate(self, skill: Skill) -> Skill:
        skills = self._read()
        existing = next((item for item in skills if item.skill_id == skill.skill_id), None)
        if existing is None:
            skills.append(skill)
            self._write(skills)
            return skill
        # A verified Skill is evidence-backed knowledge; a new observation must
        # not silently downgrade it. Store a new version explicitly later.
        if existing.status == "verified":
            return existing
        skills = [skill if item.skill_id == skill.skill_id else item for item in skills]
        self._write(skills)
        return skill

    def retrieve(self, task: str, object_type: str, phase: str) -> list[Skill]:
        return [
            skill
            for skill in self._read()
            if skill.status == "verified"
            and skill.task == task
            and object_type in skill.object_types
            and phase in {"observe", "grasp", "lift", "transport"}
        ]

    def promote_verified(
        self,
        skill_id: str,
        trials: int,
        false_success_rate: float,
        recovery_success_rate: float,
    ) -> Skill:
        skills = self._read()
        for skill in skills:
            if skill.skill_id == skill_id:
                skill.status = "verified"
                skill.validation_trials = trials
                skill.false_success_rate = false_success_rate
                skill.recovery_success_rate = recovery_success_rate
                self._write(skills)
                return skill
        raise KeyError(f"unknown skill: {skill_id}")
