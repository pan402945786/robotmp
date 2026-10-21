"""Contact confirmation must reject transient and stale tactile evidence."""
import unittest
from types import SimpleNamespace
import numpy as np
from robotmp.catch_online_control import OnlineCatchController


class ContactConfirmationTests(unittest.TestCase):
    def make_controller(self, ticks):
        model = SimpleNamespace(lower=np.full(6, -3.), upper=np.full(6, 3.))
        controller = OnlineCatchController(model, dict(contact_brake_confirmation_ticks=ticks))
        controller.estimator = SimpleNamespace(ready=lambda now: True,
            predict=lambda now: (np.zeros(3), np.array([0., 0., -1.])))
        return controller

    def test_uninterrupted_contact_is_required_before_braking(self):
        controller = self.make_controller(3)
        q, qd = np.zeros(6), np.full(6, .1)
        controller.observe_contacts(0., q, qd, {9, 12})
        controller.observe_contacts(.01, q, qd, {9, 12})
        self.assertIsNone(controller.tactile_capture_at)
        controller.observe_contacts(.02, q, qd, {9})
        controller.observe_contacts(.03, q, qd, {9, 12})
        controller.observe_contacts(.04, q, qd, {9, 12})
        self.assertIsNone(controller.tactile_capture_at)
        controller.observe_contacts(.05, q, qd, {9, 12})
        self.assertEqual(controller.tactile_capture_at, .05)
        self.assertIsNotNone(controller.fallback)

    def test_stale_observation_resets_confirmation_and_default_remains_one_tick(self):
        controller = self.make_controller(2)
        q, qd = np.zeros(6), np.full(6, .1)
        controller.observe_contacts(0., q, qd, {9, 12})
        controller.estimator.ready = lambda now: False
        controller.observe_contacts(.01, q, qd, {9, 12})
        controller.estimator.ready = lambda now: True
        controller.observe_contacts(.02, q, qd, {9, 12})
        self.assertIsNone(controller.tactile_capture_at)
        controller.observe_contacts(.03, q, qd, {9, 12})
        self.assertEqual(controller.tactile_capture_at, .03)
        default = self.make_controller(1)
        default.parameters.pop('contact_brake_confirmation_ticks')
        default.observe_contacts(0., q, qd, {9, 12})
        self.assertEqual(default.tactile_capture_at, 0.)


if __name__ == '__main__':
    unittest.main()
