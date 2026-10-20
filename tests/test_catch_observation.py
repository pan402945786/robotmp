import unittest

import numpy as np

from robotmp.catch_observation import FlightEstimator, PositionObservation


class ObservationTests(unittest.TestCase):
    def test_position_only_fit_recovers_ballistic_velocity(self):
        estimate = FlightEstimator()
        velocity = np.array([.2,-.3,4.5])
        initial = np.array([.1,.5,1.1])
        for i in range(12):
            t = i/60
            position = initial+velocity*t+[0,0,-.5*9.81*t*t]
            estimate.observe(PositionObservation(t,t,tuple(position)),t)
        pos,vel = estimate.predict(.7)
        np.testing.assert_allclose(pos,initial+velocity*.7+[0,0,-.5*9.81*.7**2],atol=1e-9)
        np.testing.assert_allclose(vel,velocity+[0,0,-9.81*.7],atol=1e-9)

    def test_future_frames_are_rejected_and_stale_frames_block_control(self):
        estimate = FlightEstimator()
        with self.assertRaises(ValueError):
            estimate.observe(PositionObservation(.1,.12,(0,0,1)),.11)
        for i in range(4):
            t=i/60
            estimate.observe(PositionObservation(t,t,(0,0,1)),t)
        self.assertTrue(estimate.ready(.06))
        self.assertFalse(estimate.ready(.2))
        self.assertFalse(estimate.observe(PositionObservation(.02,.21,(0,0,1)),.21))

    def test_same_observation_prefix_has_same_predictions_despite_different_future(self):
        # The two streams diverge after the decision; future samples never enter it.
        prefix=[PositionObservation(i/60,i/60,(.1,.4,1+3*i/60-4.905*(i/60)**2)) for i in range(10)]
        futures=[[(0,0,0)]*20,[(100,100,100)]*20]
        outputs=[]
        for future in futures:
            estimate=FlightEstimator(estimate_drag=True)
            for frame in prefix:
                estimate.observe(frame,frame.delivered_at)
            outputs.append(estimate.predict(.8))
        for left,right in zip(*outputs):
            np.testing.assert_array_equal(left,right)

    def test_delayed_measurement_is_predicted_from_capture_time(self):
        estimate=FlightEstimator()
        for i in range(10):
            t=i/60
            estimate.observe(PositionObservation(t,t+.03,(t,0,1+3*t-4.905*t*t)),t+.03)
        position,_=estimate.predict(.2)
        np.testing.assert_allclose(position,[.2,0,1+.6-4.905*.04],atol=1e-9)


if __name__ == "__main__":
    unittest.main()
