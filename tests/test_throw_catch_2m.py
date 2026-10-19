import math
import unittest

from robotmp.throw_catch_2m import REQUIRED_VZ, TARGET_RISE_M, validate_parameters


class TwoMetreTargetTests(unittest.TestCase):
    def test_required_velocity_matches_two_metre_rise(self):
        self.assertEqual(TARGET_RISE_M, 2.0)
        self.assertAlmostEqual(REQUIRED_VZ, math.sqrt(2 * 9.81 * 2), places=9)

    def test_two_metre_parameter_bounds_reject_old_or_unsafe_shape(self):
        p = {"target_x_m": 0.35, "target_z_m": 1.10, "release_after_steps": 72}
        self.assertEqual(validate_parameters(p), p)
        for changed in [{"target_x_m": 0.1}, {"target_z_m": 2.0}, {"release_after_steps": 8}, {"release_after_steps": 72.5}]:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                validate_parameters({**p, **changed})


if __name__ == "__main__":
    unittest.main()
