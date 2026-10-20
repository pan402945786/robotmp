import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

from robotmp.sim_environment import _pybullet_data
from robotmp.throw_catch_coordination import acquire, kinematic_candidates, trial


@unittest.skipUnless(importlib.util.find_spec("pybullet"), "PyBullet required")
class CoordinationTests(unittest.TestCase):
    def test_point_jacobian_matches_pose_finite_difference_without_touching_dynamic_robot(self):
        env, offset = acquire(0.1)
        p = env.p
        client = p.connect(p.DIRECT)
        try:
            before = p.getBasePositionAndOrientation(env._cube_id, physicsClientId=env.client)
            candidates = kinematic_candidates(env, offset, 20, 123)
            self.assertTrue(candidates)
            self.assertEqual(before, p.getBasePositionAndOrientation(env._cube_id, physicsClientId=env.client))
            p.setAdditionalSearchPath(_pybullet_data.getDataPath(), physicsClientId=client)
            arm = p.loadURDF("xarm/xarm6_with_gripper.urdf", [0.1,0,0.7], useFixedBase=True, physicsClientId=client)
            candidate = candidates[0]
            for joint, value in zip(env._arm_joint_ids, candidate["q"]):
                p.resetJointState(arm, joint, value, physicsClientId=client)

            def height():
                state = p.getLinkState(arm, 6, computeForwardKinematics=True, physicsClientId=client)
                return p.multiplyTransforms(state[4], state[5], offset, [0,0,0,1])[0][2]

            for index, (joint, value) in enumerate(zip(env._arm_joint_ids, candidate["q"])):
                p.resetJointState(arm, joint, value+0.001, physicsClientId=client)
                high = height()
                p.resetJointState(arm, joint, value-0.001, physicsClientId=client)
                low = height()
                p.resetJointState(arm, joint, value, physicsClientId=client)
                self.assertAlmostEqual((high-low)/0.002, candidate["jacobian_z"][index], delta=0.0002)
        finally:
            p.disconnect(client)
            env.close()

    def test_staggered_motion_preserves_joint_limits_and_explains_point_velocity(self):
        # Frozen regression pose; actual dynamics must acquire and physically move it.
        candidate = {"q": [0.,-1.4992445845535043,-2.8759831460282608,-0.22272763178339616,
                           0.32799815400855636,-1.0203010329273017],
                     "velocity": [0.,2.983,2.983,-2.983,2.983,-2.983]}
        with tempfile.TemporaryDirectory() as temporary:
            report = trial(candidate,0.1,0.35,[0.,0.,0.04,0.06,0.08,0.1],
                           output=Path(temporary),label="test")
        self.assertTrue(report["valid"], report.get("error"))
        self.assertGreater(report["peak_vz_m_s"],4.)
        self.assertFalse(report["released"])
        self.assertLessEqual(max(report["max_joint_velocity_ratios"]),1.05)
        self.assertLessEqual(max(report["max_motor_torque_ratios"]),1.001)
        self.assertAlmostEqual(sum(report["peak_joint_vz_contributions"]),
                               report["peak_point_velocity"][2],delta=0.02)
        self.assertTrue(math.isfinite(report["peak_vz_m_s"]))


if __name__ == "__main__":
    unittest.main()
