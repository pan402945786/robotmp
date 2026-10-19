import json
import math
import unittest
from pathlib import Path

from robotmp.throw_catch_improvement import REQUIRED_VZ, release_gate, summarize


class ThrowCatchImprovementTests(unittest.TestCase):
    def test_release_gate_requires_10m_energy(self):
        self.assertFalse(release_gate(1.095))
        self.assertFalse(release_gate(REQUIRED_VZ - 1e-9))
        self.assertTrue(release_gate(REQUIRED_VZ))

    def test_summary_uses_measured_peak_values(self):
        reports = [{"release_vz_m_s": 1.0, "apex_height_m": 1.2, "rise_from_release_m": 0.1,
                    "caught": False, "passed": False, "max_joint_velocity_ratios": [1.0]},
                   {"release_vz_m_s": 2.0, "apex_height_m": 1.4, "rise_from_release_m": 0.2,
                    "caught": True, "passed": False, "max_joint_velocity_ratios": [1.1]}]
        result = summarize(reports)
        self.assertEqual(result["max_release_vz_m_s"], 2.0)
        self.assertEqual(result["max_apex_height_m"], 1.4)
        self.assertEqual(result["caught_trials"], 1)
        self.assertEqual(result["complete_successes"], 0)


if __name__ == "__main__":
    unittest.main()
