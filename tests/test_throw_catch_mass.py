import importlib.util
import math
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from robotmp.models import ObjectState, RobotState, SceneState
from robotmp.sim_environment import PyBulletPickPlaceEnv, SimConfig
from robotmp.throw_catch_2m import REQUIRED_VZ, run_gate_trial
from robotmp.throw_catch_mass import BASE_PARAMETERS, ProbeAudit


class MassConfigurationTests(unittest.TestCase):
    def test_nonpositive_or_nonfinite_mass_cannot_make_a_static_or_invalid_cube(self):
        for mass in (0, -0.1, math.inf, math.nan, True, "0.1"):
            with self.subTest(mass=mass), self.assertRaises(ValueError):
                SimConfig(cube_mass_kg=mass)

    @unittest.skipUnless(importlib.util.find_spec("pybullet"), "PyBullet required")
    def test_configured_mass_and_inertia_survive_reset(self):
        inertias = []
        for mass in (0.1, 0.001):
            env = PyBulletPickPlaceEnv(config=SimConfig(cube_mass_kg=mass))
            try:
                for _ in range(2):
                    dynamics = env.p.getDynamicsInfo(env._cube_id, -1, physicsClientId=env.client)
                    self.assertEqual(dynamics[0], mass)
                    self.assertTrue(all(value > 0 for value in dynamics[2]))
                    env.reset()
                inertias.append(dynamics[2])
            finally:
                env.close()
        for heavy, light in zip(*inertias):
            self.assertAlmostEqual(heavy / light, 100.0)

    def test_gate_releases_at_qualified_sample_before_velocity_decays(self):
        # A historical peak must not authorize a later low-speed release.
        state = SceneState(0, "lift", ObjectState("cube", [0.4, 0, 1], True, True, True, 0.95),
                           RobotState(False, 1, [0.4, 0, 1.12]))
        ticks, releases = [], []
        env = SimpleNamespace(client=0, _cube_id=1, _gripper_id=2, _arm_joint_ids=[1], _arm_velocity=[3],
                              _constraint_id=1, stopped=False, observe=lambda: state,
                              execute=lambda action: None, _set_gripper_pose=lambda *a, **k: None,
                              _step=lambda count: ticks.append(count), close=lambda: None)
        env.p = SimpleNamespace(
            getBaseVelocity=lambda *a, **k: ([0, 0, REQUIRED_VZ + 0.1 if len(ticks) == 1 else 0.1], [0, 0, 0]),
            getJointState=lambda *a, **k: (0, 0))
        env.release_in_motion = lambda: releases.append(len(ticks))
        with tempfile.TemporaryDirectory() as temporary, patch("robotmp.throw_catch_2m.ThrowEnv", return_value=env):
            report = run_gate_trial(1, BASE_PARAMETERS, ProbeAudit(Path(temporary)), cube_mass_kg=0.001)
        self.assertNotIn("error", report)
        self.assertEqual(releases, [1])
        self.assertGreaterEqual(report["release_vz_m_s"], REQUIRED_VZ)


if __name__ == "__main__":
    unittest.main()
