import importlib.util
import tempfile
import unittest
from pathlib import Path

from robotmp.diagnosis import RuleBasedDiagnoser
from robotmp.environment import FailureMode
from robotmp.figure_eight import Journal, execute_trial, trajectory_metrics, validate_parameters, waypoints
from robotmp.runner import default_store, run_episode, validate_skill
from robotmp.sim_environment import PyBulletPickPlaceEnv, SimConfig


PARAMETERS = {"half_width_m": 0.05, "half_height_m": 0.08,
              "center_raise_m": 0.10, "samples": 64, "steps_per_waypoint": 48}


class FigureEightGeometryTests(unittest.TestCase):
    def test_two_vertical_lobes_pass_and_horizontal_eight_is_rejected(self):
        targets = waypoints([0.45, 0, 1.0], PARAMETERS)
        self.assertTrue(trajectory_metrics(targets, targets, PARAMETERS)["passed"])
        sideways = [[p[0], (p[2] - 1.0) * 0.625, 1.0 + p[1] * 1.6] for p in targets]
        self.assertFalse(trajectory_metrics(sideways, targets, PARAMETERS)["passed"])

    def test_incomplete_or_flat_motion_cannot_be_accepted(self):
        targets = waypoints([0.45, 0, 1.0], PARAMETERS)
        self.assertFalse(trajectory_metrics(targets[:-1], targets, PARAMETERS)["passed"])
        flat = [[p[0], p[1], 1.0] for p in targets]
        self.assertFalse(trajectory_metrics(flat, targets, PARAMETERS)["passed"])

    def test_unsafe_model_parameters_are_rejected(self):
        for changed in [{"half_height_m": float("nan")}, {"samples": 63},
                        {"steps_per_waypoint": True}, {"center_raise_m": 0.08, "half_height_m": 0.11}]:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate_parameters({**PARAMETERS, **changed})


@unittest.skipUnless(importlib.util.find_spec("pybullet"), "requires simulation environment")
class FigureEightPhysicsTests(unittest.TestCase):
    def test_grasp_required_before_motion(self):
        env = PyBulletPickPlaceEnv(config=SimConfig(arm_model="xarm6"))
        try:
            with self.assertRaises(RuntimeError):
                env.move_held_object([0.45, 0, 1.0])
            env.execute("stop")
            with self.assertRaises(RuntimeError):
                env.move_held_object([0.45, 0, 1.0])
        finally:
            env.close()

    def test_reuses_grasp_skill_traces_both_lobes_and_places(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = default_store(root / "skills.json")
            run_episode("skills", FailureMode.LOW_GRIP_FORCE, store)
            validate_skill(store, trials=1)
            journal = Journal(root, root / "steps.md", root / "calls.md")
            report = execute_trial(PARAMETERS, store, journal, "test", FailureMode.LOW_GRIP_FORCE, RuleBasedDiagnoser())
            self.assertTrue(report["passed"], report)
            self.assertTrue(report["trajectory"]["grasp_retained"])
            self.assertLess(report["trajectory"]["upper_loop_area_m2"] * report["trajectory"]["lower_loop_area_m2"], 0)
            self.assertTrue(report["placement"]["released"])
            self.assertIn("grasp_without_lift_v1", report["applied_skill_ids"])


if __name__ == "__main__":
    unittest.main()
