import copy
import unittest

from robotmp.throw_catch_005m import acceptance, catch_gate, validate_parameters


class FiveCentimeterGates(unittest.TestCase):
    def test_catch_requires_apex_height_flight_and_finger_clearance(self):
        args = ([0.4, 0, 0.32], [0, 0, -0.4], [0.4, 0, 0.43], [0, 0, 0])
        facts = dict(had_apex=True, rise=0.055, ticks=35, contact=False)
        self.assertTrue(catch_gate(*args, **facts))
        for key, value in [('had_apex', False), ('rise', 0.0499), ('ticks', 9), ('contact', True)]:
            self.assertFalse(catch_gate(*args, **{**facts, key: value}))
        self.assertFalse(catch_gate(args[0], args[1], [0.4, 0, 0.36], args[3], **facts))
        self.assertFalse(catch_gate(args[0], [0, 0, -1.1], args[2], args[3], **facts))

    def test_success_cannot_skip_any_stage_or_velocity_limits(self):
        report = dict(lift_confirmed=True, release_vz_m_s=1.06, free_flight=True,
                      rise_from_release_m=0.055, had_apex=True, flight_contact_before_catch=False,
                      caught=True, catch_hold_passed=True, placement={'passed': True},
                      max_joint_velocity_ratios=[1.01] * 6)
        self.assertTrue(acceptance(report))
        for key, value in [('lift_confirmed', False), ('release_vz_m_s', -0.1),
                           ('free_flight', False), ('rise_from_release_m', 0.0499),
                           ('had_apex', False), ('flight_contact_before_catch', True),
                           ('caught', False), ('catch_hold_passed', False),
                           ('placement', {'passed': False}), ('max_joint_velocity_ratios', [1.051])]:
            modified = copy.deepcopy(report)
            modified[key] = value
            self.assertFalse(acceptance(modified), key)

    def test_reject_nonfinite_and_out_of_bounds_parameters(self):
        raw = dict(target_x_m=0.4, target_z_m=0.65, release_min_vz_m_s=1.06,
                   max_sweep_steps=160, catch_lead_s=0.04)
        self.assertEqual(validate_parameters(raw), raw)
        for key, value in [('target_z_m', float('nan')), ('target_x_m', True),
                           ('release_min_vz_m_s', 0.98), ('max_sweep_steps', 30.5)]:
            with self.assertRaises(ValueError):
                validate_parameters({**raw, key: value})


if __name__ == '__main__':
    unittest.main()
