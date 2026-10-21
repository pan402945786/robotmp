import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from robotmp.catch_observation import PositionObservation
from robotmp.catch_online_control import OnlineCatchController,RobotModel
from robotmp.throw_catch_online import initial_skill,run_trial


class ShortVerticalCatchTests(unittest.TestCase):
    def test_closure_waits_for_observed_separation_and_descent(self):
        model=RobotModel()
        try:
            q=np.array([0.,-.4,-1.,3.14,2.,0.])
            point=model.state(q)[0]
            controller=OnlineCatchController(model,dict(stationary_catch=True,
                require_observed_separation=True,observed_separation_m=.06))
            for i in range(14):
                t=i/60
                pos=point+np.array([0.,0.,.02+1.5*t-4.905*t*t])
                controller.observe(PositionObservation(t,t,tuple(pos)),t)
                _,_,closing=controller.control(t,q,np.zeros(6),1/240)
                if t<=.1:
                    self.assertFalse(closing)
            self.assertTrue(controller.observed_separation)
            self.assertTrue(closing)
            self.assertEqual(len(controller.events),1)
            self.assertLessEqual(controller.events[0]["latest_observation_at"],controller.events[0]["issued_at"])
            self.assertEqual(controller.plan_count,0)  # This is a measured closure policy, not an IK intercept.
            self.assertIsInstance(closing,bool)
            _,_,closing=controller.control(.5,q,np.zeros(6),1/240)
            self.assertFalse(closing)  # Position-only stale data does not trigger a blind catch.
        finally:
            model.close()

    def test_delayed_noisy_vertical_throw_physically_catches_and_holds_without_constraint(self):
        parameters=initial_skill().parameters
        parameters.update(stationary_catch=True,require_observed_separation=True,observed_separation_m=.06,
            handoff_brake_s=.04,open_finger_angle_rad=.1,hold_duration_s=1.)
        scene=dict(seed=4801,cube_size_m=.05,release_gate=1.45,pre_spin=False,
            noise_m=.001,latency_s=1/60,drop_rate=.05,
            vertical_toss=dict(duration_s=.28,speed_m_s=1.8))
        post_release_constraints=[]
        class Observer:
            latest={}
            def __call__(self,env,phase,tick):
                if phase=="flight":
                    post_release_constraints.append(env.p.getNumConstraints(physicsClientId=env.client))
        with tempfile.TemporaryDirectory() as folder:
            report=run_trial(parameters,scene,Path(folder),"catch",observer=Observer())
            trace=json.loads((Path(folder)/"catch_control_trace.json").read_text())
        self.assertTrue(report["complete_success"],report.get("error",report.get("failure_reason")))
        self.assertTrue(report["initial_grasp_evidence"]["verified"])
        self.assertTrue(report["pre_release_grasp_checks"]["passed"])
        self.assertTrue(report["free_flight_separation_verified"])
        self.assertGreaterEqual(report["collision_clearance_at_enable_m"],.015)
        self.assertGreaterEqual(report["continuous_hold_duration_s"],1.)
        self.assertLess(report["hold_final_speed_m_s"],.05)
        self.assertTrue(report["causality_passed"])
        self.assertTrue(report["no_catch_constraint"])
        self.assertTrue(post_release_constraints)
        self.assertEqual(set(post_release_constraints),{0})
        held=[row for row in trace if row["time_s"]>=report["capture_contact_time_s"]-1e-8]
        self.assertTrue(all({9,12}.issubset(row["contacts"]) and row["collision_enabled"] for row in held))


if __name__=="__main__":
    unittest.main()
