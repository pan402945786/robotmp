from unittest.mock import patch
import unittest

from robotmp.sim_environment import SimConfig,PyBulletPickPlaceEnv,_require_pybullet
from robotmp.throw_catch_coordination import acquire,trial
from robotmp.throw_catch_spin import POSES,DELAYS


class PrethrowGraspTests(unittest.TestCase):
    def test_contact_checked_grasp_uses_com_anchor_and_keeps_all_fingers_aligned(self):
        original=PyBulletPickPlaceEnv._create_grasp_constraint
        anchor_errors=[]
        def checked_create(env):
            original(env)
            anchor_errors.append(env.finger_grasp_geometry()["constraint_anchor_error_m"])
        p=_require_pybullet()
        with patch.object(PyBulletPickPlaceEnv,"_create_grasp_constraint",checked_create), \
                patch.object(p,"resetJointState",side_effect=AssertionError("dynamic joint reset")), \
                patch.object(p,"resetBasePositionAndOrientation",side_effect=AssertionError("object teleport")):
            env,_=acquire(.1,cube_size_m=.05)
            try:
                self.assertEqual(len(anchor_errors),1)
                self.assertLess(anchor_errors[0],2e-7)
                self.assertTrue(env._initial_grasp_evidence["verified"])
                self.assertEqual(env._initial_grasp_evidence["consecutive_contact_ticks"],12)
                self.assertEqual(env._finger_joint_ids,list(range(8,14)))
                for _ in range(4):
                    geometry=env.finger_grasp_geometry()
                    self.assertTrue(geometry["bilateral_surface_alignment"],geometry)
                    self.assertLess(geometry["constraint_anchor_error_m"],.0015)
                    for angle,target in zip(geometry["finger_angles_rad"],env._grasp_finger_targets):
                        self.assertAlmostEqual(angle,target,delta=.003)
                    env._step(60)
            finally:
                env.close()

    def test_closed_gripper_cannot_attach_a_remote_cube(self):
        env=PyBulletPickPlaceEnv(config=SimConfig(arm_model="xarm6",cube_half_extent=.025,
                                                require_bilateral_grasp=True))
        try:
            env.execute("close_gripper")  # Deliberately skip approach.
            self.assertFalse(env.observe().object.grasped)
            self.assertIsNone(env._constraint_id)
            self.assertFalse(env._initial_grasp_evidence)
        finally:
            env.close()

    def test_lost_finger_alignment_blocks_the_launch(self):
        original=PyBulletPickPlaceEnv.finger_grasp_geometry
        def displaced(env):
            geometry=original(env)
            if env._phase=="transport":
                geometry.update(bilateral_surface_alignment=False,finger_signed_distances_m=[.02,.03])
            return geometry
        with patch.object(PyBulletPickPlaceEnv,"finger_grasp_geometry",displaced):
            report=trial(POSES["best_coordination"],.1,.35,DELAYS["best_coordination"],
                         cube_size_m=.05,release_threshold=1.5)
        self.assertFalse(report["released"])
        self.assertFalse(report["pre_release_grasp_checks"]["passed"])
        self.assertIn("launch blocked",report["error"])


if __name__=="__main__":
    unittest.main()
