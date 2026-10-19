import importlib.util
import math
import unittest
from unittest.mock import patch

from robotmp.sim_environment import SimConfig
from robotmp.throw_catch import ThrowEnv, acceptance, catch_gate, validate_parameters


class ThrowEvidenceTests(unittest.TestCase):
    def test_height_alone_and_table_placement_cannot_pass(self):
        full = {"lift_confirmed": True, "release_vz_m_s": 15, "free_flight": True,
                "apex_height_m": 12, "rise_from_release_m": 11, "caught": True,
                "placement": {"passed": True}}
        self.assertTrue(acceptance(full))
        for key, value in [("lift_confirmed", False), ("release_vz_m_s", 0),
                           ("free_flight", False), ("apex_height_m", 9.99),
                           ("rise_from_release_m", 9.99), ("caught", False),
                           ("placement", {"passed": False})]:
            with self.subTest(key=key):
                self.assertFalse(acceptance({**full, key: value}))

    def test_catch_rejects_fast_upward_distant_or_contacted_object(self):
        args = ([0, 0, 1], [0, 0, -0.5], [0, 0, 1.1], [0, 0, 0])
        self.assertTrue(catch_gate(*args, had_apex=True, flight_contact=False))
        self.assertFalse(catch_gate(*args, had_apex=False, flight_contact=False))
        self.assertFalse(catch_gate(*args, had_apex=True, flight_contact=True))
        for pos, vel in [([1, 0, 1], [0, 0, -0.5]), ([0, 0, 1], [0, 0, -14]),
                         ([0, 0, 1], [0, 0, 0.5])]:
            self.assertFalse(catch_gate(pos, vel, args[2], args[3], had_apex=True, flight_contact=False))

    def test_model_parameter_validation_rejects_nonfinite_and_extra_controls(self):
        params = {"target_x_m": 0.4, "target_z_m": 1.2, "release_after_steps": 12}
        self.assertEqual(validate_parameters(params), params)
        for changed in [{"target_z_m": math.nan}, {"target_z_m": 10},
                        {"release_after_steps": True}, {"release_after_steps": 12.5},
                        {"launch_velocity": 14}]:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate_parameters({**params, **changed})


@unittest.skipUnless(importlib.util.find_spec("pybullet"), "requires simulation environment")
class ThrowPhysicsTests(unittest.TestCase):
    def test_release_requires_lift_and_preserves_actual_velocity_without_state_reset(self):
        env = ThrowEnv(config=SimConfig(arm_model="xarm6"))
        try:
            with self.assertRaises(RuntimeError):
                env.release_in_motion()
            for action in ["approach_object", "close_gripper", "lift_object"]:
                env.execute(action)
            self.assertTrue(env.observe().object.lifted)
            env._set_gripper_pose([0.35, 0, 1.3], open_gripper=False)
            env._step(10)
            velocity = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)
            position = env._cube_position()
            with patch.object(env.p, "resetBaseVelocity", side_effect=AssertionError("velocity injection")), \
                 patch.object(env.p, "resetBasePositionAndOrientation", side_effect=AssertionError("position injection")):
                env.release_in_motion()
                self.assertIsNone(env._constraint_id)
                self.assertFalse(env.observe().object.grasped)
                self.assertEqual(env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client), velocity)
                self.assertEqual(env._cube_position(), position)
                env._step(12)
            new_v = env.p.getBaseVelocity(env._cube_id, physicsClientId=env.client)[0]
            self.assertLess(new_v[2], velocity[0][2])
            self.assertFalse(env.p.getContactPoints(env._cube_id, physicsClientId=env.client))
        finally:
            env.close()


if __name__ == "__main__":
    unittest.main()
