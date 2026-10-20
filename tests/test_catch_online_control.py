import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

import numpy as np

from robotmp.catch_observation import PositionObservation
from robotmp.catch_online_control import InterceptPlan, OnlineCatchController, RobotModel
from robotmp.catch_gripper_geometry import measure_opening
from robotmp.throw_catch_online import initial_skill,run_trial


class OnlineControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=RobotModel()

    @classmethod
    def tearDownClass(cls):
        cls.model.close()

    def controller(self):
        return OnlineCatchController(self.model,dict(estimate_drag=True,ik_seeds=0,ik_iterations=15,
            horizon_step_s=.15,replan_s=.1,strict_trajectory=True))

    def feed(self,controller):
        for i in range(7):
            t=i/60
            controller.observe(PositionObservation(t,t,(.4,0,1+3*t-4.905*t*t)),t)

    def test_release_handoff_brakes_continuously_before_sensor_is_ready(self):
        controller=self.controller()
        q=np.zeros(6)
        qd=np.array([.5,.8,.7,-.7,.6,-.4])
        target,speed,closing=controller.control(0,q,qd,1/240)
        np.testing.assert_allclose(speed,qd*(1-(1/240)/.35),atol=1e-10)
        self.assertFalse(closing)
        self.assertGreater(np.linalg.norm(target-q),0)
        _,stopped,_=controller.control(.4,q,qd,1/240)
        np.testing.assert_allclose(stopped,0,atol=1e-10)

    def test_controller_cannot_read_results_or_replay_files(self):
        controller=self.controller()
        self.feed(controller)
        q=np.array([0.,-.8,-2.,0.,1.,0.])
        with patch("builtins.open",side_effect=AssertionError("file input forbidden")), \
                patch("pathlib.Path.read_text",side_effect=AssertionError("result input forbidden")):
            controller.control(.1,q,np.zeros(6),1/240)
        self.assertEqual(controller.plan_count,1)
        self.assertLessEqual(controller.events[0]["latest_observation_at"],.1)

    def test_same_delivered_prefix_produces_same_commands_when_future_flights_differ(self):
        prefix=[PositionObservation(i/60,i/60,(.4,0,1+3*i/60-4.905*(i/60)**2)) for i in range(10)]
        streams=[prefix+[PositionObservation(.5,.5,(.1,.2,.7))],
                 prefix+[PositionObservation(.5,.5,(.7,-.3,1.4))]]
        outputs=[]
        for stream in streams:
            controller=self.controller()
            cursor=0
            commands=[]
            with patch("robotmp.catch_online_control.time.perf_counter",return_value=1.):
                for step in range(40):
                    now=step/240
                    while cursor<len(stream) and stream[cursor].delivered_at<=now+1e-9:
                        controller.observe(stream[cursor],now)
                        cursor+=1
                    target,speed,closed=controller.control(now,np.array([0.,-.8,-2.,0.,1.,0.]),np.zeros(6),1/240)
                    commands.append(np.r_[target,speed,int(closed)])
            outputs.append(commands)
        np.testing.assert_array_equal(outputs[0],outputs[1])

    def test_late_plan_rebases_on_encoders_and_rejects_unreachable_remaining_path(self):
        controller=self.controller()
        self.feed(controller)
        start=np.zeros(6)
        goal=start.copy()
        goal[0]=.8
        controller.pending_plan=InterceptPlan(0,.16,0,[],[],start,np.zeros(6),goal,np.zeros(6),0.,0.,0.)
        controller.pending_ready_at=.1
        controller.last_replan=.1
        _,_,closed=controller.control(.1,start,np.zeros(6),1/240)
        self.assertEqual(controller.late_plan_rejections,1)
        self.assertIsNone(controller.plan)
        self.assertFalse(closed)

    def test_stale_observations_cancel_pending_blind_interception(self):
        controller=self.controller()
        self.feed(controller)
        start=np.zeros(6)
        controller.pending_plan=InterceptPlan(.1,.7,.1,[],[],start,start,start,start,0.,0.,0.)
        _,_,closing=controller.control(.3,start,start,1/240)
        self.assertIsNone(controller.pending_plan)
        self.assertIsNone(controller.plan)
        self.assertFalse(closing)

    def test_followthrough_must_fit_before_joint_limit(self):
        controller=self.controller()
        q=np.zeros(6)
        q[2]=self.model.lower[2]+.05
        velocity=np.zeros(6)
        velocity[2]=-2.
        plan=InterceptPlan(0,.1,0,[],[],q,velocity,q,velocity,0.,0.,0.)
        self.assertFalse(controller.executable(plan))

    def test_open_gripper_geometry_distinguishes_8cm_and_10cm_centered_boxes(self):
        self.model.set(np.zeros(6))
        geometry=measure_opening(self.model)
        boxes={round(row["box_width_m"],2):row for row in geometry["centered_box_clearance"]}
        self.assertTrue(boxes[.08]["centered_fit"])
        self.assertFalse(boxes[.10]["centered_fit"])
        self.assertLess(geometry["max_measured_gap_m"],.10)

    def test_learned_geometry_gate_prevents_an_incompatible_launch(self):
        parameters=initial_skill().parameters
        parameters["require_centered_grasp_fit"]=True
        with tempfile.TemporaryDirectory() as folder:
            report=run_trial(parameters,dict(seed=991),Path(folder),"blocked")
        self.assertTrue(report["geometry_gate_blocked"])
        self.assertFalse(report["released"])
        self.assertEqual(report["position_observations"],0)

    def test_fresh_dynamic_trial_uses_delayed_position_frames_without_attaching_object(self):
        parameters=initial_skill().parameters
        parameters.update(strict_trajectory=True,abort_on_motion_violation=True,ik_seeds=0,
                          ik_iterations=25,horizon_step_s=.1,estimate_drag=True)
        with tempfile.TemporaryDirectory() as folder:
            report=run_trial(parameters,dict(seed=992,latency_s=1/60,noise_m=.001,
                sensor_hz=60,drop_rate=.05,release_gate=4.9),Path(folder),"fresh")
        self.assertTrue(report["released"],report.get("error"))
        self.assertGreater(report["position_observations"],4)
        self.assertTrue(report["causality_passed"])
        self.assertFalse(report["truth_velocity_used_by_controller"])
        self.assertFalse(report["uses_offline_flight"])
        self.assertTrue(report["no_catch_constraint"])
        self.assertTrue(report["motion_checks_passed"])


if __name__=="__main__":
    unittest.main()
