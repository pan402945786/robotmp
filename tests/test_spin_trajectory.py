import math
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

from robotmp.spin_trajectory import accelerate, coast_and_brake, periodic_state, plan_spin


class SpinTrajectoryTests(unittest.TestCase):
    def test_periodic_joint_loop_repeats_with_finite_difference_velocity(self):
        from robotmp.throw_catch_loops import loop_parameters

        loop = loop_parameters([0., -.8, -1.6, 0., 1., 0.], .9, .9, 5)
        duration = 4 * math.pi * loop["turns"] / loop["rate"]
        initial = periodic_state(0., **loop)[0]
        for cycle in range(1, 6):
            t = duration * math.sqrt(cycle / 5)
            q, qd, phase = periodic_state(t, **loop)
            self.assertAlmostEqual(phase, cycle * 2 * math.pi)
            for actual, expected in zip(q, initial):
                self.assertAlmostEqual(actual, expected)
            self.assertLessEqual(max(abs(v) for v in qd), 2.983+1e-9)
        t, delta = duration * .6, 1e-5
        before = periodic_state(t-delta, **loop)[0]
        after = periodic_state(t+delta, **loop)[0]
        velocity = periodic_state(t, **loop)[1]
        for low, high, speed in zip(before, after, velocity):
            self.assertAlmostEqual((high-low)/(2*delta), speed, delta=1e-7)

    def test_speed_increases_at_each_revolution_and_transition_is_continuous(self):
        distance, speed = 1.75 * 2 * math.pi, 2.983
        duration = 2 * distance / speed
        speeds = []
        for turns in (.5, 1., 1.5, 1.75):
            t = duration * math.sqrt(turns / 1.75)
            position, velocity = accelerate(t, distance, speed)
            self.assertAlmostEqual(position, turns * 2 * math.pi)
            speeds.append(velocity)
        self.assertEqual(speeds, sorted(speeds))
        self.assertEqual(accelerate(duration, distance, speed), (distance, speed))
        self.assertEqual(coast_and_brake(0, speed, .25, .2), (0., speed))
        self.assertAlmostEqual(coast_and_brake(.45, speed, .25, .2)[0], speed * .35)
        self.assertAlmostEqual(coast_and_brake(.45, speed, .25, .2)[1], 0.)
        self.assertEqual(coast_and_brake(10, speed, .25, .2), coast_and_brake(.45, speed, .25, .2))

    def test_no_angle_wrapping_and_no_two_turns_past_original_limits(self):
        lower, upper, limits = [-2*math.pi]*6, [2*math.pi]*6, [3.14]*6
        plan = plan_spin([0.]*6, lower, upper, limits, 1.75, [0], [1])
        self.assertAlmostEqual(plan["launch_q"][0]-plan["start_q"][0], 3.5*math.pi)
        self.assertGreater(plan["start_q"][0], lower[0])
        final = plan["launch_q"][0] + 2.983 * .35
        self.assertLess(final, upper[0])
        with self.assertRaisesRegex(ValueError, "angle range"):
            plan_spin([0.]*6, lower, upper, limits, 2., [0], [1])
        with self.assertRaises(ValueError):
            plan_spin([0.]*6, lower, upper, limits, 1., [1], [1])
        with self.assertRaises(ValueError):
            plan_spin([0.]*6, lower, upper, limits, 1., [0, 0], [1, 1])
        with self.assertRaises(ValueError):
            plan_spin([0.]*6, lower, upper, limits, float("inf"), [0], [1])

    @unittest.skipUnless(importlib.util.find_spec("pybullet"), "PyBullet required")
    def test_physical_turns_accelerate_without_joint_wrap_or_speed_violation(self):
        from robotmp.throw_catch_coordination import trial
        from robotmp.throw_catch_spin import POSES, DELAYS

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            report = trial(POSES["best_coordination"], .1, .35, DELAYS["best_coordination"],
                spin=dict(turns=1.75, joints=[0], directions=[1]), output=output, label="spin")
            with (output / "spin_physics.csv").open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
        self.assertTrue(report["valid"], report.get("error"))
        milestones = report["spin_milestones"]
        self.assertEqual([m["turns"] for m in milestones], [.5, 1., 1.5])
        speeds = [m["joint_speed_rad_s"] for m in milestones]
        self.assertTrue(all(a < b for a, b in zip(speeds, speeds[1:])))
        self.assertGreaterEqual(report["spin_end"]["measured_turns"][0], 1.75)
        for previous, current in zip(rows, rows[1:]):
            dt = float(current["t_s"]) - float(previous["t_s"])
            for i in range(6):
                delta = float(current[f"q{i}"]) - float(previous[f"q{i}"])
                self.assertLessEqual(abs(delta), 3.14 * 1.05 * dt + 1e-8)
                self.assertAlmostEqual(delta / dt, float(current[f"qd{i}"]), delta=1e-7)
        self.assertFalse(report["released"])


if __name__ == "__main__":
    unittest.main()
