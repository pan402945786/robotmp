import importlib.util
import tempfile
import unittest
from pathlib import Path

from robotmp.environment import FailureMode
from robotmp.runner import default_store, run_episode
from robotmp.sim_environment import PyBulletPickPlaceEnv, SimConfig


@unittest.skipUnless(importlib.util.find_spec("pybullet"), "PyBullet is installed only in the simulation environment")
class SimulationTests(unittest.TestCase):
    def test_physics_backend_recovers_low_grip_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            result = run_episode("feedback", FailureMode.LOW_GRIP_FORCE, default_store(Path(tmp) / "skills.json"), observer=events.append, env_factory=lambda failure: PyBulletPickPlaceEnv(failure, gui=False))
        self.assertEqual(result.status, "recovered")
        self.assertTrue(result.recovered)
        self.assertTrue(any("object_lift_detected" in e["state"]["events"] for e in events))

    def test_physics_backend_exposes_actual_positions(self):
        env = PyBulletPickPlaceEnv(FailureMode.NONE, gui=False)
        try:
            initial = env.observe().object.position_m
            env.execute("approach_object")
            env.execute("close_gripper")
            env.execute("lift_object")
            lifted = env.observe().object.position_m
        finally:
            env.close()
        self.assertLess(initial[2], lifted[2])
        self.assertTrue(env._closed)

    def test_six_dof_arm_moves_end_effector_with_ik(self):
        env = PyBulletPickPlaceEnv(FailureMode.NONE, gui=False, config=SimConfig(arm_model="arm6dof"))
        try:
            env.execute("approach_object")
            env.execute("close_gripper")
            before = env.observe().robot.end_effector_position_m
            env.execute("lift_object")
            after = env.observe().robot.end_effector_position_m
            joints = [env.p.getJointState(env._gripper_id, i, physicsClientId=env.client)[0] for i in range(6)]
        finally:
            env.close()
        self.assertGreater(after[2], before[2] + 0.04)
        self.assertEqual(len(joints), 6)
        self.assertGreater(max(abs(value) for value in joints), 0.01)

    def test_xarm6_uses_urdf_limits_and_recovers(self):
        env = PyBulletPickPlaceEnv(FailureMode.LOW_GRIP_FORCE, gui=False, config=SimConfig(arm_model="xarm6"))
        try:
            env.execute("approach_object")
            limits = [env.p.getJointInfo(env._gripper_id, i, physicsClientId=env.client)[8:12] for i in range(1, 7)]
            env.execute("close_gripper")
            env.execute("lift_object")
            lifted = env.observe().object.lifted
        finally:
            env.close()
        self.assertTrue(all(lower < upper and effort > 0 and velocity > 0 for lower, upper, effort, velocity in limits))
        self.assertFalse(lifted)

    def test_xarm6_grasp_is_aligned_before_lift(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            result = run_episode(
                "feedback",
                FailureMode.NONE,
                default_store(Path(tmp) / "skills.json"),
                observer=events.append,
                env_factory=lambda failure: PyBulletPickPlaceEnv(failure, gui=False, config=SimConfig(arm_model="xarm6")),
            )
        close = next(event for event in events if event.get("action") == "close_gripper")["state"]
        lift = next(event for event in events if event.get("action") == "lift_object")["state"]
        x_delta = abs(close["object"]["position_m"][0] - close["robot"]["end_effector_position_m"][0])
        self.assertEqual(result.status, "success")
        self.assertLess(x_delta, 0.02)
        self.assertTrue(close["object"]["grasped"])
        self.assertTrue(lift["object"]["lifted"])
        self.assertIn("grasp_constraint_created", close["events"])

    def test_xarm6_starts_clear_and_places_normal_pick(self):
        with tempfile.TemporaryDirectory() as tmp:
            events = []
            result = run_episode(
                "feedback",
                FailureMode.NONE,
                default_store(Path(tmp) / "skills.json"),
                observer=events.append,
                env_factory=lambda failure: PyBulletPickPlaceEnv(failure, gui=False, config=SimConfig(arm_model="xarm6")),
            )
        reset = events[0]["state"]["object"]["position_m"]
        approach = next(event for event in events if event.get("action") == "approach_object")["state"]["object"]["position_m"]
        self.assertEqual(result.status, "success")
        self.assertLess(sum((a - b) ** 2 for a, b in zip(reset, approach)) ** 0.5, 0.005)
        self.assertEqual(events[-1]["state"]["phase"], "finished")


if __name__ == "__main__":
    unittest.main()
