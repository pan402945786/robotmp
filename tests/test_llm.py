from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import tempfile

from robotmp.diagnosis import LLMConfig, LLMUnavailable, OpenAICompatibleDiagnoser, RuleBasedDiagnoser
from robotmp.environment import FailureMode
from robotmp.runner import default_store, run_episode


class _Handler(BaseHTTPRequestHandler):
    response_payload = {
        "output": [{"content": [{"type": "output_text", "text": json.dumps({
            "name": "llm_grasp_without_lift",
            "trigger_conditions": ["gripper_closed == true", "object_lifted == false"],
            "facts": ["lift evidence was absent"],
            "hypotheses": ["grip force was insufficient"],
            "prediction_correction": ["require_lift_evidence_before_transport"],
            "recovery": ["stop transport motion", "retry grasp if safe"],
        })}]}]
    }
    requests: list[dict] = []

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        self.__class__.requests.append(json.loads(self.rfile.read(length)))
        raw = json.dumps(self.response_payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *_args):
        pass


class LLMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_responses_client_builds_structured_skill(self):
        _Handler.requests.clear()
        temp_dir = Path(tempfile.mkdtemp())
        config = LLMConfig(base_url=f"http://127.0.0.1:{self.server.server_port}", model="test-model", log_path=str(temp_dir / "llm.jsonl"))
        store = default_store(temp_dir / "skills.json")
        result = run_episode("skills", FailureMode.LOW_GRIP_FORCE, store, diagnoser=OpenAICompatibleDiagnoser(config))
        self.assertEqual(result.status, "recovered")
        self.assertEqual(store.all()[0].name, "llm_grasp_without_lift")
        self.assertEqual(_Handler.requests[0]["model"], "test-model")
        self.assertEqual(_Handler.requests[0]["text"]["format"]["type"], "json_object")
        records = [json.loads(line) for line in (temp_dir / "llm.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([record["event"] for record in records], ["request", "response", "parsed_output"])
        self.assertEqual(records[0]["input"]["model"], "test-model")
        self.assertIn("output", records[1])
        self.assertEqual(records[2]["skill"]["name"], "llm_grasp_without_lift")

    def test_low_level_model_output_is_rejected(self):
        old = _Handler.response_payload
        try:
            _Handler.response_payload = {"output": [{"content": [{"type": "output_text", "text": json.dumps({
                "name": "unsafe", "trigger_conditions": ["a"], "facts": ["b"],
                "hypotheses": ["c"], "prediction_correction": ["joint command: move"], "recovery": ["d"],
            })}]}]}
            temp_dir = Path(tempfile.mkdtemp())
            config = LLMConfig(base_url=f"http://127.0.0.1:{self.server.server_port}", model="test-model", log_path=str(temp_dir / "llm.jsonl"))
            store = default_store(temp_dir / "skills.json")
            events = []
            result = run_episode("feedback", FailureMode.LOW_GRIP_FORCE, store, diagnoser=OpenAICompatibleDiagnoser(config), observer=events.append)
            self.assertEqual(result.status, "recovered")
            self.assertTrue(any(event["kind"] == "diagnosis_fallback" for event in events))
        finally:
            _Handler.response_payload = old


if __name__ == "__main__":
    unittest.main()
