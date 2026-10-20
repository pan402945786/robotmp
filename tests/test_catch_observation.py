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

    def test_online_drag_estimate_improves_unseen_short_horizon_prediction(self):
        vacuum=FlightEstimator()
        adaptive=FlightEstimator(estimate_drag=True)
        position=np.array([.1,.5,1.1])
        velocity=np.array([.2,-.3,4.5])
        dt=1/600
        predicted=[]
        for step in range(181):
            t=step*dt
            if step%10==0 and step<=120:
                frame=PositionObservation(t,t,tuple(position))
                for estimator in (vacuum,adaptive):
                    estimator.observe(frame,t)
                if step==120:
                    predicted=[estimator.predict(.3)[0] for estimator in (vacuum,adaptive)]
            acceleration=np.array([0,0,-9.81])-.06*(1+np.linalg.norm(velocity))*velocity
            if step==180:
                break
            position+=velocity*dt+.5*acceleration*dt**2
            velocity+=acceleration*dt
        self.assertGreater(adaptive.drag,.01)
        self.assertLess(np.linalg.norm(predicted[1]-position),np.linalg.norm(predicted[0]-position))

    def test_delayed_measurement_is_predicted_from_capture_time(self):
        estimate=FlightEstimator()
        for i in range(10):
            t=i/60
            estimate.observe(PositionObservation(t,t+.03,(t,0,1+3*t-4.905*t*t)),t+.03)
        position,_=estimate.predict(.2)
        np.testing.assert_allclose(position,[.2,0,1+.6-4.905*.04],atol=1e-9)


if __name__ == "__main__":
    unittest.main()
