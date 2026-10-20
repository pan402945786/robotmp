import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from robotmp.catch_best_video import RecordedExperiment,select_best


class RecordedVisualizationTests(unittest.TestCase):
    def test_selection_excludes_post_contact_distance_and_invalid_motion(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            audit={"trials":[]}
            for label,causal,motion,distance in (("a",True,True,.08),("b",True,True,.09),
                                                ("c",True,False,.01),("d",False,True,.01)):
                path=root/f"{label}.json"
                path.write_text(json.dumps(dict(label=label,first_robot_contact_time_s=1.)))
                trace=[dict(time_s=.9,truth_velocity=[0,0,-3],contacts=[],cube=[0,0,1],
                            distance_m=distance,relative_speed_m_s=2.),
                       dict(time_s=1.1,truth_velocity=[0,0,-.1],contacts=[],cube=[0,0,1],
                            distance_m=.001,relative_speed_m_s=.1)]
                path.with_name(label+"_control_trace.json").write_text(json.dumps(trace))
                audit["trials"].append(dict(active_causal=causal,motion_checks=motion,report=path.name))
            with patch("robotmp.catch_best_video.ROOT",root):
                ranked=select_best(audit)
        self.assertEqual([row["label"] for row in ranked],["a","b"])
        self.assertEqual(ranked[0]["distance_m"],.08)
        self.assertEqual(ranked[0]["time_s"],.9)

    def test_visualization_only_reveals_delivered_observations_and_computed_candidates(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"a.json").write_text(json.dumps(dict(label="a",release_time_s=10.)))
            trace=[dict(time_s=t,cube=[t,0,1],capture_point=[t,0,.9],closing=False) for t in (.1,.2)]
            (root/"a_control_trace.json").write_text(json.dumps(trace))
            (root/"a_observations.json").write_text(json.dumps([dict(received_at=t,position=[t,0,1]) for t in (.1,.18)]))
            (root/"a_decisions.json").write_text(json.dumps([dict(issued_at=.1,wall_s=.05,plan={"cube":[0,0,1]})]))
            header="t_s,phase,x,y,z,"+",".join(f"q{i}" for i in range(6))+"\n"
            lines=[f"{10+t},flight,{t},0,1,"+",".join(["0"]*6) for t in (.1,.2)]
            (root/"a_physics.csv").write_text(header+"\n".join(lines)+"\n")
            with patch("robotmp.catch_best_video.ROOT",root):
                data=RecordedExperiment(dict(report="a.json"))
                self.assertEqual(data.state(.12)["obs_count"],1)
                self.assertIsNone(data.state(.12)["plan"])
                self.assertIsNotNone(data.state(.16)["plan"])
                self.assertEqual(data.state(.19)["obs_count"],2)
                self.assertEqual(data.physics_trace_max_error,0.)


if __name__=="__main__":
    unittest.main()
