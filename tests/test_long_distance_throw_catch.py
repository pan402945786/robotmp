import unittest

from robotmp.long_distance_throw_catch import MIN_RANGE_M, make_parameters
from robotmp.vertical_toss import make_vertical_toss


class LongDistanceThrowCatchTests(unittest.TestCase):
    def test_skill_requires_a_range_beyond_short_vertical_return(self):
        self.assertEqual(MIN_RANGE_M, 0.10)
        parameters = make_parameters(.0, duration=.6, speed_x=0., speed_z=1.2,
                                     dy=.1, speed_y=.6, close_lead=.3)
        self.assertFalse(parameters["stationary_catch"])
        self.assertTrue(parameters["descent_servo"])
        self.assertEqual(parameters["launch_profile"]["vertical_toss"]["goal_y_m"], .1)

    def test_toss_primitive_supports_horizontal_endpoint_without_state_injection(self):
        spec = make_vertical_toss([0., 0., 0.], {
            "x_m": .55, "y_m": 0., "start_z_m": 1.12,
            "goal_x_m": .55, "goal_y_m": .10, "goal_z_m": 1.35,
            "duration_s": .6, "speed_y_m_s": .6, "speed_m_s": 1.2,
        })
        self.assertAlmostEqual(spec[4]["settings"]["goal_y_m"], .1)
        self.assertLessEqual(spec[4]["planned_peak_speed_ratio"], .98 + 1e-9)


if __name__ == "__main__":
    unittest.main()
