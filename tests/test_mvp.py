import json
import tempfile
import unittest
from pathlib import Path

from robotmp.environment import FailureMode
from robotmp.runner import default_store, run_episode, validate_skill


class MvpTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = default_store(Path(self.temp_dir.name) / "skills.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_normal_episode_succeeds(self):
        result = run_episode("feedback", FailureMode.NONE, self.store)
        self.assertEqual(result.status, "success")
        self.assertFalse(result.false_success)

    def test_failure_is_detected_and_recovered(self):
        result = run_episode("feedback", FailureMode.LOW_GRIP_FORCE, self.store)
        self.assertEqual(result.status, "recovered")
        self.assertTrue(result.recovered)
        self.assertFalse(result.false_success)

    def test_baseline_can_false_success(self):
        result = run_episode("baseline", FailureMode.LOW_GRIP_FORCE, self.store)
        self.assertEqual(result.status, "false_success")
        self.assertTrue(result.false_success)

    def test_skill_is_promoted_and_retrieved(self):
        candidate_result = run_episode("skills", FailureMode.LOW_GRIP_FORCE, self.store)
        self.assertEqual(candidate_result.status, "recovered")
        self.assertEqual(len(self.store.all()), 1)

        skill = validate_skill(self.store, trials=5)
        self.assertEqual(skill.status, "verified")
        retrieved = self.store.retrieve("pick_and_place", "cube", "grasp")
        self.assertEqual([item.skill_id for item in retrieved], ["grasp_without_lift_v1"])

        persisted = json.loads(Path(self.store.path).read_text(encoding="utf-8"))
        self.assertEqual(persisted[0]["status"], "verified")


if __name__ == "__main__":
    unittest.main()


