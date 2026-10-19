from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from .models import ComparisonResult, Prediction, SceneState, Skill


class RuleBasedDiagnoser:
    """Deterministic local substitute for an LLM during MVP development."""

    def generate(
        self,
        prediction: Prediction,
        observation: SceneState,
        comparison: ComparisonResult,
        skill_context: list[Skill],
    ) -> Skill:
        if "expected_lift_but_not_detected" not in comparison.errors:
            raise ValueError("no grasp-without-lift diagnosis applies")
        return Skill(
            skill_id="grasp_without_lift_v1",
            name="grasp_without_lift",
            status="candidate",
            version=1,
            task="pick_and_place",
            object_types=[observation.object.object_id],
            trigger_conditions=[
                "gripper_closed == true",
                "lift_window_elapsed == true",
                "object_lifted == false",
            ],
            facts=[
                "gripper_closed_does_not_imply_grasp_success",
                "object_lift_was_not_detected",
                "object_may_have_been_displaced_before_grasp",
            ],
            hypotheses=[
                "grasp_point_may_be_misaligned",
                "insufficient_grip_force",
            ],
            prediction_correction=[
                "do_not_enter_transport_phase",
                "require_lift_evidence_before_transport",
            ],
            recovery=[
                "stop_transport_motion",
                "refresh_object_pose",
                "retry_grasp_if_safe",
            ],
        )


@dataclass(frozen=True)
class LLMConfig:
    """Portable OpenAI-compatible local or remote model configuration."""

    base_url: str = "http://127.0.0.1:15723/v1"
    model: str = "gpt-6.1-sol"
    wire_api: str = "responses"
    api_key: str | None = None
    timeout_seconds: float = 90.0

    def __post_init__(self) -> None:
        if self.wire_api not in {"responses", "chat"}:
            raise ValueError("wire_api must be 'responses' or 'chat'")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            base_url=os.getenv("ROBOTMP_LLM_BASE_URL", cls.base_url).rstrip("/"),
            model=os.getenv("ROBOTMP_LLM_MODEL", cls.model),
            wire_api=os.getenv("ROBOTMP_LLM_WIRE_API", cls.wire_api).lower(),
            api_key=os.getenv("ROBOTMP_LLM_API_KEY") or None,
            timeout_seconds=float(os.getenv("ROBOTMP_LLM_TIMEOUT", str(cls.timeout_seconds))),
        )

    @property
    def endpoint(self) -> str:
        path = "responses" if self.wire_api == "responses" else "chat/completions"
        return f"{self.base_url}/{path}"


class LLMUnavailable(RuntimeError):
    """Raised when the configured model cannot produce a diagnosis."""


class OpenAICompatibleDiagnoser:
    """Generate a structured Skill through an OpenAI-compatible HTTP endpoint.

    The client only asks the model for diagnosis data. It never sends joint,
    motor, trajectory, or other low-level control commands to the endpoint.
    """

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig.from_env()

    def generate(
        self,
        prediction: Prediction,
        observation: SceneState,
        comparison: ComparisonResult,
        skill_context: list[Skill],
    ) -> Skill:
        if "expected_lift_but_not_detected" not in comparison.errors:
            raise ValueError("no grasp-without-lift diagnosis applies")
        payload = self._request(self._build_request(prediction, observation, comparison, skill_context))
        return self._skill_from_payload(payload, observation)

    def _build_request(
        self,
        prediction: Prediction,
        observation: SceneState,
        comparison: ComparisonResult,
        skill_context: list[Skill],
    ) -> dict[str, Any]:
        context = {
            "task": "pick_and_place",
            "prediction": prediction.__dict__,
            "observation": {
                "timestamp": observation.timestamp,
                "phase": observation.phase,
                "object": observation.object.__dict__,
                "robot": observation.robot.__dict__,
                "events": observation.events,
            },
            "comparison": comparison.__dict__,
            "related_skills": [skill.__dict__ for skill in skill_context],
        }
        instructions = (
            "You are a robotics failure diagnosis module. Return only a JSON object. "
            "Separate observed facts from hypotheses. Create a reusable candidate Skill "
            "for this grasp-without-lift failure. Do not output executable code, joint "
            "commands, motor commands, torque, velocity, trajectory, or controller settings. "
            "The recovery field must contain only semantic, safety-reviewed intents. "
            "Required JSON keys: name, trigger_conditions, facts, hypotheses, "
            "prediction_correction, recovery. Every value must be an array of short strings "
            "except name, which is a string. Preserve the safety rule that transport requires "
            "positive lift evidence."
        )
        if self.config.wire_api == "responses":
            return {
                "model": self.config.model,
                "instructions": instructions,
                "input": "Return a JSON object only.\n" + json.dumps(context, ensure_ascii=False),
                "text": {"format": {"type": "json_object"}},
                "store": False,
            }
        return {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": instructions},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False)},
            ],
            "response_format": {"type": "json_object"},
        }

    def _request(self, body: dict[str, Any]) -> dict[str, Any]:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        req = request.Request(self.config.endpoint, data=encoded, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except (error.HTTPError, error.URLError, TimeoutError) as exc:
            detail = ""
            if isinstance(exc, error.HTTPError):
                detail = exc.read().decode("utf-8", errors="replace")[:1000]
            raise LLMUnavailable(f"LLM request failed at {self.config.endpoint}: {exc} {detail}") from exc
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LLMUnavailable("LLM returned invalid JSON envelope") from exc
        text = _extract_text(result)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMUnavailable(f"LLM diagnosis was not valid JSON: {text[:500]}") from exc
        if not isinstance(parsed, dict):
            raise LLMUnavailable("LLM diagnosis must be a JSON object")
        return parsed

    @staticmethod
    def _skill_from_payload(payload: dict[str, Any], observation: SceneState) -> Skill:
        required = ["trigger_conditions", "facts", "hypotheses", "prediction_correction", "recovery"]
        for key in required:
            value = payload.get(key)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
                raise LLMUnavailable(f"LLM diagnosis field {key!r} must be a non-empty string array")
        forbidden = ("joint", "motor", "torque", "trajectory", "position_control", "velocity")
        low_level = " ".join(item for key in required for item in payload[key]).lower()
        if any(term in low_level for term in forbidden):
            raise LLMUnavailable("LLM diagnosis contained low-level control instructions")
        corrections = list(payload["prediction_correction"])
        for invariant in ("do_not_enter_transport_phase", "require_lift_evidence_before_transport"):
            if invariant not in corrections:
                corrections.append(invariant)
        return Skill(
            skill_id="grasp_without_lift_v1",
            name=str(payload.get("name") or "grasp_without_lift"),
            status="candidate",
            version=1,
            task="pick_and_place",
            object_types=[observation.object.object_id],
            trigger_conditions=list(payload["trigger_conditions"]),
            facts=list(payload["facts"]),
            hypotheses=list(payload["hypotheses"]),
            prediction_correction=corrections,
            recovery=list(payload["recovery"]),
        )


def _extract_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    for item in response.get("output", []):
        for content in item.get("content", []) if isinstance(item, dict) else []:
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                if isinstance(content.get("text"), str):
                    return content["text"]
    choices = response.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if isinstance(content, str):
            return content
    raise LLMUnavailable("LLM response did not contain text output")


def make_diagnoser(mode: str = "auto", config: LLMConfig | None = None):
    """Create the requested diagnoser without making network calls by default."""
    if mode == "rules":
        return RuleBasedDiagnoser()
    if mode == "llm":
        return OpenAICompatibleDiagnoser(config)
    if mode == "auto" and os.getenv("ROBOTMP_LLM_ENABLED", "0").lower() in {"1", "true", "yes", "on"}:
        return OpenAICompatibleDiagnoser(config)
    return RuleBasedDiagnoser()
