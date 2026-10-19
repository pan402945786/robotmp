# 抛高至少 10 米、接住并平稳放地：实验记录

日期：2026-10-19；时间均使用 Asia/Shanghai。

用户目标：复用 `artifacts/verification_20261019/skills.json`，尝试学习“抓起物体 → 抛入空中至少 10 米 → 接住 → 平稳放在地面”。逐步记录事件，持续更新文档和 Git，保留每次实验程序调用大模型的完整输入输出。

实验开始时 Git：`f6e731f`，工作区干净。

1. 检查项目说明、环境、控制器、已有技能和历史学习流程。
2. 指定文件仅含已验证技能 `grasp_without_lift_v1`：20 次验证、误报成功率 0、恢复成功率 1。复用核心约束：未观察到真实抬升，不得进入后续动作。
3. 现有 xArm6 使用 URDF 关节限制和位置控制；抓持通过固定约束近似，机器人与方块碰撞被屏蔽。已有动作不包含抛掷与接球。新增实验必须保留该边界，不能称为真实硬件或摩擦夹持验证。
4. 当前没有项目 `.venv/python.exe`，接下来检查 `run.cmd` 的 Conda `py311` 回退环境。

验收：分别记录世界坐标离地高度和相对离手点上升高度；为消除“10 米高”的歧义，成功需两者均至少 10 米。飞行阶段不得重置物体位置、速度或施加外部发射力。接球必须有下降、位置接近和相对速度证据；放地必须在真实地面接触后释放，并检查静置漂移与速度。任何未完成阶段均明确记为未完成。

日志范围：实验程序发出的模型 HTTP 请求、原始响应、解析结果和错误全部落盘；本次 Codex 会话内部的隐藏推理及平台未提供的底层请求不在程序可访问范围内，不冒称已导出。

每个控制步骤写事件文档；每个物理时间步写 CSV；每个模型请求发出前、响应落盘后及每次试验结束后创建本地 Git 检查点。原始已有技能只读使用。


[2026-10-19T22:28:25+08:00] 开始运行 9a838c5b6239；输出目录 docs\throw_catch_evidence。

1. 仿真 0.000s；物体中心 (—) m；{"kind": "capability_inspection", "source_sha256": "1480ab7df263cab82d7df41eb84c92a961c2b70a2d8b7bb2cb8c02f94a1f7383", "time_step_s": 0.004166666666666667, "gravity_m_s2": 9.81, "joint_velocity_limits_rad_s": [3.14, 3.14, 3.14, 3.14, 3.14, 3.14], "joint_effort_limits_Nm": [50.0, 50.0, 32.0, 32.0, 32.0, 20.0], "joint_lower_rad": [-6.28318530718, -2.059, -3.927, -6.28318530718, -1.69297, -6.28318530718], "joint_upper_rad": [6.28318530718, 2.0944, 0.19198, 6.28318530718, 3.14159265359, 6.28318530718], "cube_mass_kg": 0.1, "required_vz_for_10m_rise_m_s": 14.007141035914502, "grasp_model": "fixed constraint; robot-cube collision disabled; idealized acquisition", "ground_z_m": 0, "table_z_m": 0.7}


[2026-10-19T22:28:25+08:00] 大模型 request；request_id=72ff113db1d143d09be1e7c0eba9c666；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:28:46+08:00] 大模型 response；request_id=72ff113db1d143d09be1e7c0eba9c666；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:28:46+08:00] 大模型 parsed_output；request_id=72ff113db1d143d09be1e7c0eba9c666；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

2. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 12}, "observed_facts": ["尚无实际试验报告，当前不能确认抛高、接取或放地能力。", "仿真重力为9.81米每二次方秒，物理步长为1/240秒；本次将在运动开始后0.05秒解除抓取约束。", "忽略空气阻力时，从释放位置再上升10米需要约14.007米每秒的释放竖直速度。", "已有技能grasp_without_lift_v1验证的是未抬升识别与恢复，不是成功抓取或抛接能力；夹爪闭合不能作为抓取成功证据。", "局部原语仅向单个笛卡尔IK目标运动，受URDF关节限制约束；尚无该原语的实测释放速度。"], "hypotheses": ["选择允许范围内最高目标高度，可能增加释放前的向上运动，但实际释放速度与峰值高度必须测量。", "12步释放可作为较早释放的初始采样点，不能据此保证达到所需竖直速度。", "关节速度、力矩及工作空间限制可能使本原语无法达到10米相对上升要求，需根据试验评估。"], "rationale": "先进行一次受限参数试验建立实测基线。复用已有技能检测抓取后未抬升的情况，若未取得可靠抬升证据则停止后续运输并恢复。仅使用规定的单目标运动与定时释放，不注入物体位置或速度、不施加发射外力、不改变重力。原语执行结束不等于任务成功。", "next_requirements": ["刷新物体位姿并确认安全抓取；取得物体随夹持运动且离开桌面的证据后，才能认定抓取与抬升成功。", "记录实际释放时刻、释放位置、物体线速度及关节限制触发情况。", "记录真实自由飞行峰值，分别核验峰值世界高度至少10米、峰值相对释放位置上升至少10米；任一不满足均记为失败。", "仅在物体下降、与接取点距离不超过0.13米且相对速度不超过1米每秒时允许建立接取固定约束，并记录三项条件的实测值。", "接住后将物体放至z=0的地面而非z=0.70米的桌面，解除夹持后观察稳定支撑与残余运动。", "失败后根据实测结果修改允许参数或停止并给出有证据的能力评估，不将有限采样失败解释为所有控制器都不可能完成。", "至少取得3次独立、完整且各阶段均通过的成功试验，才可接受该技能。"]}}


[2026-10-19T22:28:47+08:00] 开始 attempt_01；参数 {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 12}；故障 none。

3. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_01", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_01_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

4. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_01", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

5. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_01", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

6. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_01", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

7. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

8. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "match", "errors": [], "severity": "none"}, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

9. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

10. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "upward_sweep_commanded", "object_target": [0.4, -0.0006344299818815758, 1.35], "steps": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

11. 仿真 0.646s；物体中心 (0.45176, -0.00063, 0.90540) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

12. 仿真 0.650s；物体中心 (0.45122, -0.00064, 0.90547) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

13. 仿真 0.654s；物体中心 (0.45127, -0.00064, 0.90540) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

14. 仿真 0.658s；物体中心 (0.45192, -0.00064, 0.90521) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

15. 仿真 0.662s；物体中心 (0.45293, -0.00064, 0.90482) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 5, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

16. 仿真 0.667s；物体中心 (0.45394, -0.00064, 0.90442) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 6, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

17. 仿真 0.671s；物体中心 (0.45495, -0.00064, 0.90401) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 7, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

18. 仿真 0.675s；物体中心 (0.45594, -0.00064, 0.90358) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 8, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

19. 仿真 0.679s；物体中心 (0.45694, -0.00064, 0.90313) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 9, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

20. 仿真 0.683s；物体中心 (0.45793, -0.00064, 0.90268) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 10, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

21. 仿真 0.687s；物体中心 (0.45891, -0.00064, 0.90221) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 11, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

22. 仿真 0.692s；物体中心 (0.45988, -0.00064, 0.90172) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

23. 仿真 0.692s；物体中心 (0.45988, -0.00064, 0.90172) m；{"trial": "attempt_01", "kind": "release_measured", "release_height_m": 0.9017215268868598, "release_velocity_m_s": [0.23417894587522584, -2.3119526700296428e-05, -0.11624652392026795], "release_vz_m_s": -0.11624652392026795, "ideal_vacuum_rise_m": 0.0, "required_vz_for_10m_rise_m_s": 14.007141035914502, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

24. 仿真 0.696s；物体中心 (0.46086, -0.00064, 0.90107) m；{"trial": "attempt_01", "kind": "apex_or_initial_descent", "measured_height_m": 0.9017215268868598, "vz_m_s": -0.15709708417159265, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

25. 仿真 0.696s；物体中心 (0.46086, -0.00064, 0.90107) m；{"trial": "attempt_01", "kind": "flight_observation", "velocity_m_s": [0.23412971193351964, -2.3114666035194434e-05, -0.15709708417159265], "ee_velocity_m_s": [0.535275936126709, -0.015766220167279243, -0.18442153930664062], "catch_distance_m": 0.10864519577447743, "relative_speed_m_s": 0.3027928657763674, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

26. 仿真 0.696s；物体中心 (0.46086, -0.00064, 0.90107) m；{"trial": "attempt_01", "kind": "catch_gate_passed", "distance_m": 0.10864519577447743, "relative_speed_m_s": 0.3027928657763674, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

27. 仿真 1.696s；物体中心 (0.79640, -0.00127, 0.95720) m；{"trial": "attempt_01", "kind": "carry_outside_table", "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

28. 仿真 1.696s；物体中心 (0.79640, -0.00127, 0.95720) m；{"trial": "attempt_01", "kind": "trial_error", "error": "RuntimeError: ground placement unreachable outside table; retain grasp", "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}


[2026-10-19T22:28:47+08:00] attempt_01 结束：{"label": "attempt_01", "failure_mode": "none", "parameters": {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 12}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": true, "free_flight": true, "placement": {"passed": false, "status": "not_reached"}, "release_height_m": 0.9017215268868598, "release_velocity_m_s": [0.23417894587522584, -2.3119526700296428e-05, -0.11624652392026795], "release_vz_m_s": -0.11624652392026795, "ideal_vacuum_rise_m": 0.0, "required_vz_for_10m_rise_m_s": 14.007141035914502, "apex_height_m": 0.9017215268868598, "rise_from_release_m": 0.0, "flight_ticks": 1, "flight_contact_before_catch": false, "error": "RuntimeError: ground placement unreachable outside table; retain grasp", "physics_samples": 397, "max_joint_velocity_ratios": [0.013428830567758978, 1.0000051798173062, 1.2673443017955222, 0.004974643768526298, 1.3014425531205767, 0.0134993003230321], "passed": false}


[2026-10-19T22:28:48+08:00] 大模型 request；request_id=a63647bebe55400e8eedd468082bbc8a；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:29:42+08:00] 大模型 response；request_id=a63647bebe55400e8eedd468082bbc8a；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:29:43+08:00] 大模型 parsed_output；request_id=a63647bebe55400e8eedd468082bbc8a；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

29. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 48}, "observed_facts": ["attempt_01未完成：抓取与接取报告为真，但放地失败，状态为not_reached。", "attempt_01的释放高度为0.9017米，低于目标高度1.35米。", "attempt_01的释放竖直速度为-0.1162米每秒，理想上升高度为0米，峰值高度为0.9017米。", "attempt_01未达到世界高度至少10米，也未达到相对释放位置上升至少10米。", "attempt_01在释放后仅观测到1个飞行tick，未形成满足目标的自由飞行证据。", "attempt_01报告的失败原因为地面放置位置超出可达区域；物体被保留在夹持状态。", "attempt_01的最大关节速度比部分超过1，说明该次运动存在关节速度限制压力。", "当前尚无任何完整成功试验，因此不能接受技能。"], "hypotheses": ["将release_after_steps从12增加到48，可能使单目标运动在释放前获得更充分的上行位移或不同的释放速度。", "attempt_01的负竖直释放速度表明12步释放时不具备抛高能力，但单次失败不能证明所有允许参数或控制器均不可行。", "即使释放后获得上行速度，目标仍需实测同时满足世界z至少10米和相对释放位置上升至少10米；不能用原语完成或目标高度代替飞行证据。", "当前放地失败可能与接取点或地面可达性有关，下一次必须选择并验证地面z=0的可达放置过程。", "再次试验仍需验证下降阶段、接取距离不超过0.13米以及相对速度不超过1米每秒后，才可建立固定约束。"], "rationale": "继续进行一次参数修订后的受限试验。上一试验在release_after_steps=12时实测释放竖直速度为负，且只产生0米理想上升高度，因此本次保持允许范围内的最高目标高度1.35米和相同横向目标，将释放步数增加到48，以采样更充分的单目标运动时序。此选择不注入物体位置或速度、不施加发射力、不改变重力。试验必须记录真实释放状态和完整自由飞行峰值；任一10米高度条件不满足即判定失败。即使本次成功，也仍需另外至少两次独立完整成功试验后才能接受。", "next_requirements": ["确认grasp_without_lift_v1后物体确实被固定约束持有，并记录物体随夹持器运动及离开桌面的证据。", "记录实际释放时刻、释放位置、三维线速度、自由飞行持续时间、峰值世界z以及相对释放位置的最大上升量。", "严格核验峰值世界z至少10米且相对释放位置上升至少10米；任一条件失败均记录为失败。", "仅在物体下降、接取距离不超过0.13米且相对速度不超过1米每秒时建立固定约束，并记录三项实测值。", "接取后将物体放到地面z=0，验证解除约束后稳定支撑；不得将桌面z=0.70米视为合格放置。", "若本次仍未达到抛高要求，应基于实测释放速度、峰值高度和关节限制压力继续修改允许参数或停止；不得将有限采样失败宣称为所有控制器不可行。", "只有至少3次独立、完整且抛高、接取、地面放置全部通过的试验后，才可将decision设为accept。"]}}


[2026-10-19T22:29:44+08:00] 开始 attempt_02；参数 {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 48}；故障 low_grip_force。

30. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_02", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_02_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

31. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_02", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

32. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

33. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "close_gripper", "物体抓持": false, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact"]}

34. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "lift_object", "物体抓持": false, "实际抬升": false, "事件": []}

35. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-2", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "物体抓持": false, "实际抬升": false, "事件": []}

36. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "grasp_recovery_from_existing_skill", "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "物体抓持": false, "实际抬升": false, "事件": []}

37. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "refresh_object_pose", "物体抓持": false, "实际抬升": false, "事件": ["object_pose_refreshed"]}

38. 仿真 0.842s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "retry_grasp", "物体抓持": false, "实际抬升": false, "事件": ["grasp_retry_requested"]}

39. 仿真 1.042s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

40. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

41. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

42. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "upward_sweep_commanded", "object_target": [0.4, -0.0006272425879208008, 1.35], "steps": 48, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

43. 仿真 1.246s；物体中心 (0.45150, -0.00063, 0.90547) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

44. 仿真 1.250s；物体中心 (0.45096, -0.00063, 0.90558) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

45. 仿真 1.254s；物体中心 (0.45102, -0.00063, 0.90556) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

46. 仿真 1.258s；物体中心 (0.45168, -0.00063, 0.90541) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

47. 仿真 1.262s；物体中心 (0.45268, -0.00063, 0.90504) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 5, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

48. 仿真 1.267s；物体中心 (0.45367, -0.00063, 0.90465) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 6, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

49. 仿真 1.271s；物体中心 (0.45466, -0.00063, 0.90425) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 7, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

50. 仿真 1.275s；物体中心 (0.45565, -0.00063, 0.90383) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 8, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

51. 仿真 1.279s；物体中心 (0.45662, -0.00063, 0.90340) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 9, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

52. 仿真 1.283s；物体中心 (0.45759, -0.00063, 0.90295) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 10, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

53. 仿真 1.287s；物体中心 (0.45856, -0.00063, 0.90249) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 11, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

54. 仿真 1.292s；物体中心 (0.45952, -0.00063, 0.90202) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

55. 仿真 1.296s；物体中心 (0.46047, -0.00063, 0.90154) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 13, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

56. 仿真 1.300s；物体中心 (0.46144, -0.00063, 0.90136) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 14, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

57. 仿真 1.304s；物体中心 (0.46238, -0.00063, 0.90151) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 15, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

58. 仿真 1.308s；物体中心 (0.46330, -0.00063, 0.90196) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 16, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

59. 仿真 1.312s；物体中心 (0.46423, -0.00063, 0.90271) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 17, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

60. 仿真 1.317s；物体中心 (0.46516, -0.00063, 0.90375) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 18, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

61. 仿真 1.321s；物体中心 (0.46612, -0.00063, 0.90505) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 19, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

62. 仿真 1.325s；物体中心 (0.46710, -0.00063, 0.90661) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 20, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

63. 仿真 1.329s；物体中心 (0.46813, -0.00063, 0.90843) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 21, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

64. 仿真 1.333s；物体中心 (0.46919, -0.00063, 0.91049) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 22, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

65. 仿真 1.337s；物体中心 (0.47030, -0.00063, 0.91278) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 23, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

66. 仿真 1.342s；物体中心 (0.47147, -0.00063, 0.91531) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 24, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

67. 仿真 1.346s；物体中心 (0.47269, -0.00063, 0.91806) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 25, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

68. 仿真 1.350s；物体中心 (0.47397, -0.00063, 0.92102) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 26, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

69. 仿真 1.354s；物体中心 (0.47530, -0.00063, 0.92421) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 27, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

70. 仿真 1.358s；物体中心 (0.47663, -0.00063, 0.92754) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 28, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

71. 仿真 1.362s；物体中心 (0.47793, -0.00063, 0.93098) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 29, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

72. 仿真 1.367s；物体中心 (0.47920, -0.00063, 0.93452) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 30, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

73. 仿真 1.371s；物体中心 (0.48044, -0.00063, 0.93817) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 31, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

74. 仿真 1.375s；物体中心 (0.48164, -0.00063, 0.94190) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 32, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

75. 仿真 1.379s；物体中心 (0.48280, -0.00063, 0.94571) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 33, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

76. 仿真 1.383s；物体中心 (0.48392, -0.00063, 0.94960) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 34, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

77. 仿真 1.387s；物体中心 (0.48500, -0.00063, 0.95356) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 35, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

78. 仿真 1.392s；物体中心 (0.48602, -0.00063, 0.95758) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 36, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

79. 仿真 1.396s；物体中心 (0.48700, -0.00063, 0.96165) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 37, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

80. 仿真 1.400s；物体中心 (0.48794, -0.00063, 0.96578) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 38, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

81. 仿真 1.404s；物体中心 (0.48881, -0.00063, 0.96995) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 39, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

82. 仿真 1.408s；物体中心 (0.48964, -0.00063, 0.97417) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 40, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

83. 仿真 1.412s；物体中心 (0.49041, -0.00063, 0.97843) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 41, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

84. 仿真 1.417s；物体中心 (0.49113, -0.00063, 0.98272) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 42, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

85. 仿真 1.421s；物体中心 (0.49180, -0.00063, 0.98705) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 43, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

86. 仿真 1.425s；物体中心 (0.49240, -0.00063, 0.99141) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 44, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

87. 仿真 1.429s；物体中心 (0.49296, -0.00063, 0.99579) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 45, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

88. 仿真 1.433s；物体中心 (0.49345, -0.00063, 1.00020) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 46, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

89. 仿真 1.437s；物体中心 (0.49388, -0.00063, 1.00463) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 47, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

90. 仿真 1.442s；物体中心 (0.49426, -0.00063, 1.00908) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 48, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

91. 仿真 1.442s；物体中心 (0.49426, -0.00063, 1.00908) m；{"trial": "attempt_02", "kind": "release_measured", "release_height_m": 1.0090771573095734, "release_velocity_m_s": [0.09054882644499834, 6.899041455148656e-06, 1.0678278974652755], "release_vz_m_s": 1.0678278974652755, "ideal_vacuum_rise_m": 0.058117044781096375, "required_vz_for_10m_rise_m_s": 14.007141035914502, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

92. 仿真 1.446s；物体中心 (0.49464, -0.00063, 1.01335) m；{"trial": "attempt_02", "kind": "flight_observation", "velocity_m_s": [0.09051756204624595, 6.8966593769756816e-06, 1.0265842013871926], "ee_velocity_m_s": [0.3629922866821289, 2.7366913855075836e-05, 1.0458755493164062], "catch_distance_m": 0.11086284477791208, "relative_speed_m_s": 0.2731567903043187, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

93. 仿真 1.496s；物体中心 (0.49916, -0.00063, 1.05131) m；{"trial": "attempt_02", "kind": "flight_observation", "velocity_m_s": [0.09019124923582464, 6.871797148553426e-06, 0.5331546268616963], "ee_velocity_m_s": [0.022172927856445312, 5.51808625459671e-06, 0.4271221160888672], "catch_distance_m": 0.1113984166188688, "relative_speed_m_s": 0.12597374879668857, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

94. 仿真 1.546s；物体中心 (0.50366, -0.00063, 1.06465) m；{"trial": "attempt_02", "kind": "flight_observation", "velocity_m_s": [0.0899526570925221, 6.853618480180328e-06, 0.041801760629148726], "ee_velocity_m_s": [0.002574920654296875, 2.7241185307502747e-06, 0.12207984924316406], "catch_distance_m": 0.10858009684867005, "relative_speed_m_s": 0.11865681756073025, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

95. 仿真 1.554s；物体中心 (0.50441, -0.00063, 1.06449) m；{"trial": "attempt_02", "kind": "apex_or_initial_descent", "measured_height_m": 1.064656974133551, "vz_m_s": -0.03995606435223744, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

96. 仿真 1.558s；物体中心 (0.50478, -0.00063, 1.06415) m；{"trial": "attempt_02", "kind": "catch_gate_passed", "distance_m": 0.10969343387059124, "relative_speed_m_s": 0.07656434369477019, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

97. 仿真 2.558s；物体中心 (0.75992, -0.00125, 0.99747) m；{"trial": "attempt_02", "kind": "carry_outside_table", "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

98. 仿真 2.558s；物体中心 (0.75992, -0.00125, 0.99747) m；{"trial": "attempt_02", "kind": "trial_error", "error": "RuntimeError: ground placement unreachable outside table; retain grasp", "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}


[2026-10-19T22:29:44+08:00] attempt_02 结束：{"label": "attempt_02", "failure_mode": "low_grip_force", "parameters": {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 48}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": true, "free_flight": true, "placement": {"passed": false, "status": "not_reached"}, "release_height_m": 1.0090771573095734, "release_velocity_m_s": [0.09054882644499834, 6.899041455148656e-06, 1.0678278974652755], "release_vz_m_s": 1.0678278974652755, "ideal_vacuum_rise_m": 0.058117044781096375, "required_vz_for_10m_rise_m_s": 14.007141035914502, "apex_height_m": 1.064656974133551, "rise_from_release_m": 0.05557981682397761, "flight_ticks": 28, "flight_contact_before_catch": false, "error": "RuntimeError: ground placement unreachable outside table; retain grasp", "physics_samples": 604, "max_joint_velocity_ratios": [0.011562299634202695, 1.0003102348422792, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.011579889179544632], "passed": false}


[2026-10-19T22:29:45+08:00] 大模型 request；request_id=94fa6720ec50458aacc2d5af8c27ae96；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:30:35+08:00] 大模型 response；request_id=94fa6720ec50458aacc2d5af8c27ae96；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:30:36+08:00] 大模型 parsed_output；request_id=94fa6720ec50458aacc2d5af8c27ae96；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

99. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.25, "target_z_m": 1.35, "release_after_steps": 32}, "observed_facts": ["两次已有试验均失败，完整成功次数为0。", "attempt_01释放竖直速度为-0.1162米/秒，峰值世界高度为0.9017米，相对释放位置上升为0米。", "attempt_02释放竖直速度为1.0678米/秒，峰值世界高度为1.0647米，相对释放位置上升为0.05558米；两个10米条件均未满足。", "在重力9.81米/秒²下，相对释放位置上升10米所需的理想初始竖直速度约为14.0071米/秒，显著高于目前实测值。", "两次报告均标记已抓起、存在自由飞行且已接取，但未提供接取瞬间下降、距离和相对速度的完整数值证据。", "两次地面放置均未完成，报告地面放置位置不可达并保留夹持。", "两次试验的部分最大关节速度比超过1，必须核查实际运动是否满足URDF限制。"], "hypotheses": ["将横向目标缩至0.25米并在32步释放，可能改变单一笛卡尔目标运动的构型与释放时序，从而采样不同的上行速度；目前没有证据保证速度会提高。", "此前12步和48步的结果不能排除中间释放时刻存在速度峰值，但当前实测速度与10米上升需求差距很大。", "地面放置不可达可能是独立于抛高的能力瓶颈，改变释放参数不能视为已经解决此问题。", "有限参数采样只能支持对当前原语和已测条件的能力评估，不能数学证明所有控制器均不可行。"], "rationale": "进行一次修订后的局部能力探测：保持最高允许目标高度，改变横向目标并采用未测的中间释放时刻。该选择仅使用允许的三个参数，由既定原语在URDF限制下向单一笛卡尔IK目标运动，不注入物体位置或速度、不施加发射力、不改变重力。已有两次结果距10米目标甚远，且地面放置尚未完成，因此本次仅用于补充能力证据，不预期或宣称成功。若仍出现低高度或限制违规，应优先停止当前实验并报告实测能力缺口，而不是把原语执行结束当作成功。", "next_requirements": ["复用grasp_without_lift_v1的失败检测与恢复逻辑；夹爪闭合不等于抓取成功，必须确认真实持有及离桌抬升后才进入释放阶段。", "确认已恢复到独立试验的起始条件，记录测得的持物位姿、实际释放步数、释放位置和三维速度。", "记录真实自由飞行峰值；必须同时满足世界z至少10米及相对释放位置上升至少10米，任一不足即失败。", "核查关节位置、速度和力矩限制；不得依赖超限运动获得抛高结果。", "仅在物体下降、接取距离不超过0.13米且相对速度不超过1米/秒时建立接取固定约束，并保存三项实测证据。", "核验接取后的地面放置可达性；若不可达则保留安全夹持并判定失败，不得用桌面z=0.70米替代地面z=0。", "放地必须验证解除约束后物体在地面稳定支撑，不能仅凭到达放置目标判定成功。", "若本次仍明显未达高度要求，依据全部实测结果停止或提出有证据支持的参数修订；停止结论应限定于当前原语与已测条件。", "只有至少3次独立试验完整通过抓起、双重高度条件、合规接取和稳定放地，才允许接受。"]}}


[2026-10-19T22:30:36+08:00] 开始 attempt_03；参数 {"target_x_m": 0.25, "target_z_m": 1.35, "release_after_steps": 32}；故障 none。

100. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_03", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_03_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

101. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_03", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

102. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_03", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

103. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_03", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

104. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

105. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-3", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "match", "errors": [], "severity": "none"}, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

106. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

107. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "upward_sweep_commanded", "object_target": [0.25, -0.0006344299818815758, 1.35], "steps": 32, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

108. 仿真 0.646s；物体中心 (0.45114, -0.00064, 0.90591) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

109. 仿真 0.650s；物体中心 (0.44937, -0.00064, 0.90698) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

110. 仿真 0.654s；物体中心 (0.44759, -0.00064, 0.90841) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

111. 仿真 0.658s；物体中心 (0.44581, -0.00064, 0.91018) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

112. 仿真 0.662s；物体中心 (0.44402, -0.00064, 0.91231) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 5, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

113. 仿真 0.667s；物体中心 (0.44223, -0.00064, 0.91479) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 6, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

114. 仿真 0.671s；物体中心 (0.44043, -0.00064, 0.91760) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 7, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

115. 仿真 0.675s；物体中心 (0.43866, -0.00064, 0.92073) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 8, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

116. 仿真 0.679s；物体中心 (0.43720, -0.00064, 0.92398) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 9, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

117. 仿真 0.683s；物体中心 (0.43601, -0.00064, 0.92736) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 10, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

118. 仿真 0.687s；物体中心 (0.43509, -0.00064, 0.93087) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 11, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

119. 仿真 0.692s；物体中心 (0.43440, -0.00064, 0.93453) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

120. 仿真 0.696s；物体中心 (0.43392, -0.00064, 0.93835) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 13, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

121. 仿真 0.700s；物体中心 (0.43365, -0.00064, 0.94233) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 14, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

122. 仿真 0.704s；物体中心 (0.43356, -0.00064, 0.94647) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 15, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

123. 仿真 0.708s；物体中心 (0.43363, -0.00064, 0.95078) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 16, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

124. 仿真 0.712s；物体中心 (0.43386, -0.00064, 0.95527) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 17, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

125. 仿真 0.717s；物体中心 (0.43423, -0.00064, 0.95993) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 18, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

126. 仿真 0.721s；物体中心 (0.43472, -0.00064, 0.96478) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 19, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

127. 仿真 0.725s；物体中心 (0.43533, -0.00064, 0.96981) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 20, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

128. 仿真 0.729s；物体中心 (0.43604, -0.00064, 0.97503) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 21, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

129. 仿真 0.733s；物体中心 (0.43678, -0.00064, 0.98036) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 22, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

130. 仿真 0.737s；物体中心 (0.43745, -0.00064, 0.98563) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 23, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

131. 仿真 0.742s；物体中心 (0.43804, -0.00064, 0.99084) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 24, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

132. 仿真 0.746s；物体中心 (0.43856, -0.00064, 0.99599) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 25, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

133. 仿真 0.750s；物体中心 (0.43900, -0.00064, 1.00109) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 26, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

134. 仿真 0.754s；物体中心 (0.43937, -0.00064, 1.00614) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 27, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

135. 仿真 0.758s；物体中心 (0.43968, -0.00064, 1.01116) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 28, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

136. 仿真 0.762s；物体中心 (0.43992, -0.00064, 1.01613) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 29, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

137. 仿真 0.767s；物体中心 (0.44009, -0.00064, 1.02107) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 30, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

138. 仿真 0.771s；物体中心 (0.44020, -0.00064, 1.02598) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 31, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

139. 仿真 0.775s；物体中心 (0.44025, -0.00064, 1.03086) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 32, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

140. 仿真 0.775s；物体中心 (0.44025, -0.00064, 1.03086) m；{"trial": "attempt_03", "kind": "release_measured", "release_height_m": 1.0308607468802158, "release_velocity_m_s": [0.011277934976860256, 2.391236676514579e-06, 1.1710205139188867], "release_vz_m_s": 1.1710205139188867, "ideal_vacuum_rise_m": 0.06989240795203128, "required_vz_for_10m_rise_m_s": 14.007141035914502, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

141. 仿真 0.779s；物体中心 (0.44029, -0.00064, 1.03557) m；{"trial": "attempt_03", "kind": "flight_observation", "velocity_m_s": [0.01127385410350838, 2.3903714175774384e-06, 1.1297217850696286], "ee_velocity_m_s": [0.21347522735595703, 2.270098775625229e-05, 1.0508251190185547], "catch_distance_m": 0.10831373272372159, "relative_speed_m_s": 0.2170485652375336, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

142. 仿真 0.829s；物体中心 (0.44086, -0.00064, 1.07866) m；{"trial": "attempt_03", "kind": "flight_observation", "velocity_m_s": [0.011231017005519844, 2.3812887583817786e-06, 0.6357439561555855], "ee_velocity_m_s": [-0.05401611328125, 1.0449439287185669e-05, -0.24524688720703125], "catch_distance_m": 0.07228154823127993, "relative_speed_m_s": 0.8834036756571305, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

143. 仿真 0.879s；物体中心 (0.44142, -0.00064, 1.09713) m；{"trial": "attempt_03", "kind": "flight_observation", "velocity_m_s": [0.011199377193753768, 2.37458023607798e-06, 0.14404675240275877], "ee_velocity_m_s": [-0.016357898712158203, 2.9616057872772217e-06, -0.06903648376464844], "catch_distance_m": 0.047344231737127596, "relative_speed_m_s": 0.21485778783016962, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

144. 仿真 0.896s；物体中心 (0.44160, -0.00064, 1.09782) m；{"trial": "attempt_03", "kind": "apex_or_initial_descent", "measured_height_m": 1.0979051211484174, "vz_m_s": -0.019514376176276216, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

145. 仿真 0.900s；物体中心 (0.44165, -0.00064, 1.09757) m；{"trial": "attempt_03", "kind": "catch_gate_passed", "distance_m": 0.04533421740630646, "relative_speed_m_s": 0.22588757675084536, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

146. 仿真 1.900s；物体中心 (0.78533, -0.00127, 1.04883) m；{"trial": "attempt_03", "kind": "carry_outside_table", "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

147. 仿真 1.900s；物体中心 (0.78533, -0.00127, 1.04883) m；{"trial": "attempt_03", "kind": "trial_error", "error": "RuntimeError: ground placement unreachable outside table; retain grasp", "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}


[2026-10-19T22:30:37+08:00] attempt_03 结束：{"label": "attempt_03", "failure_mode": "none", "parameters": {"target_x_m": 0.25, "target_z_m": 1.35, "release_after_steps": 32}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": true, "free_flight": true, "placement": {"passed": false, "status": "not_reached"}, "release_height_m": 1.0308607468802158, "release_velocity_m_s": [0.011277934976860256, 2.391236676514579e-06, 1.1710205139188867], "release_vz_m_s": 1.1710205139188867, "ideal_vacuum_rise_m": 0.06989240795203128, "required_vz_for_10m_rise_m_s": 14.007141035914502, "apex_height_m": 1.0979051211484174, "rise_from_release_m": 0.06704437426820165, "flight_ticks": 30, "flight_contact_before_catch": false, "error": "RuntimeError: ground placement unreachable outside table; retain grasp", "physics_samples": 446, "max_joint_velocity_ratios": [0.01405152748253903, 1.0002610217551637, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.014067260465545203], "passed": false}


[2026-10-19T22:30:37+08:00] 大模型 request；request_id=4862ba0578ca409b9aa12f9b17545300；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


## 2026-10-19 22:35 ����

�� 1��2 �����е�ԭʼ������ caught=true �ǹ����ż������ĺ�ѡ״̬���� 1 ��������ֱ�ٶ�Ϊ -0.116 m/s��δ�������� 2 ��Ϊ 1.068 m/s�������� 0.0556 m�����Ѱѽ����ż��ս�Ϊ���ȹ۲쵽��ʵ�������ٹ۲��½������� 10 �����ɷ��в������½�ʱ���������ٶȴ�ꣻ��ʷԭʼ JSON �����ǣ������������һ��������Ч��



[2026-10-19T22:33:04+08:00] 开始运行 ac5c19cb1463；输出目录 docs\throw_catch_evidence_v2。

1. 仿真 0.000s；物体中心 (—) m；{"kind": "capability_inspection", "source_sha256": "1480ab7df263cab82d7df41eb84c92a961c2b70a2d8b7bb2cb8c02f94a1f7383", "time_step_s": 0.004166666666666667, "gravity_m_s2": 9.81, "joint_velocity_limits_rad_s": [3.14, 3.14, 3.14, 3.14, 3.14, 3.14], "joint_effort_limits_Nm": [50.0, 50.0, 32.0, 32.0, 32.0, 20.0], "joint_lower_rad": [-6.28318530718, -2.059, -3.927, -6.28318530718, -1.69297, -6.28318530718], "joint_upper_rad": [6.28318530718, 2.0944, 0.19198, 6.28318530718, 3.14159265359, 6.28318530718], "cube_mass_kg": 0.1, "required_vz_for_10m_rise_m_s": 14.007141035914502, "grasp_model": "fixed constraint; robot-cube collision disabled; idealized acquisition", "ground_z_m": 0, "table_z_m": 0.7}


[2026-10-19T22:33:04+08:00] 大模型 request；request_id=b0cbff6a3a554c26806a6736b0e82bcc；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:33:38+08:00] 大模型 response；request_id=b0cbff6a3a554c26806a6736b0e82bcc；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:33:38+08:00] 大模型 parsed_output；request_id=b0cbff6a3a554c26806a6736b0e82bcc；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

2. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 4}, "observed_facts": ["当前尚无实际试验报告", "目标要求物体释放后世界坐标z达到至少10米，且相对释放点上升至少10米", "达到10米上升在无额外注入条件下需要释放竖直速度至少14.0071410359米每秒", "释放后必须观测真实飞行、下降、接近距离不超过0.13米且相对速度不超过1米每秒后才能固定约束接住", "接住后还必须将方块平稳放置到z=0地面"], "hypotheses": ["较高的笛卡尔目标高度和较短的保持步数可能保留较大的释放竖直速度", "现有抓取技能已验证，但其事实明确表明闭合夹爪不等于抓取成功，因此必须先确认物体确实被抬起", "单次试验无法证明控制器对10米抛掷目标不可行或可行"], "rationale": "首次试验必须执行。选择允许范围内的最高目标高度1.35米和最短释放等待4步，以优先测试是否能产生足够的真实释放速度；不注入物体状态、外力或重力变化。试验必须依次验证抓取、抬升、释放、世界z至少10米、相对释放点上升至少10米、下降阶段满足接球条件、接住以及最终放地。", "next_requirements": ["执行抓取并记录物体是否实际抬离桌面", "记录释放时物体位置和速度", "记录飞行最高世界z以及相对释放点的上升高度", "若未达到任一10米条件，基于测得结果调整target_x_m、target_z_m或release_after_steps，或在证据充分时停止", "若达到高度，必须继续验证下降、距离不超过0.13米、相对速度不超过1米每秒、成功接住和放置到地面", "至少完成3次彼此独立且所有阶段均成功的完整试验后，才允许将decision设为accept"]}}


[2026-10-19T22:33:39+08:00] 开始 attempt_01；参数 {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 4}；故障 none。

3. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_01", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_01_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

4. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_01", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

5. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_01", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

6. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_01", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

7. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

8. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "match", "errors": [], "severity": "none"}, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

9. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

10. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "upward_sweep_commanded", "object_target": [0.4, -0.0006344299818815758, 1.35], "steps": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

11. 仿真 0.646s；物体中心 (0.45176, -0.00063, 0.90540) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

12. 仿真 0.650s；物体中心 (0.45122, -0.00064, 0.90547) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

13. 仿真 0.654s；物体中心 (0.45127, -0.00064, 0.90540) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

14. 仿真 0.658s；物体中心 (0.45192, -0.00064, 0.90521) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

15. 仿真 0.658s；物体中心 (0.45192, -0.00064, 0.90521) m；{"trial": "attempt_01", "kind": "release_measured", "release_height_m": 0.9052091631266603, "release_velocity_m_s": [0.15504038585519203, -5.918020048293559e-05, -0.04685120369801475], "release_vz_m_s": -0.04685120369801475, "ideal_vacuum_rise_m": 0.0, "required_vz_for_10m_rise_m_s": 14.007141035914502, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

16. 仿真 0.662s；物体中心 (0.45256, -0.00064, 0.90484) m；{"trial": "attempt_01", "kind": "flight_observation", "velocity_m_s": [0.15501036061360998, -5.91687395993305e-05, -0.08771713045750594], "ee_velocity_m_s": [0.2922677993774414, -0.015239166095852852, -0.08677482604980469], "catch_distance_m": 0.10866512316912393, "relative_speed_m_s": 0.13809751899777045, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

17. 仿真 0.712s；物体中心 (0.46030, -0.00064, 0.88719) m；{"trial": "attempt_01", "kind": "flight_observation", "velocity_m_s": [0.15459060244105163, -5.900851442529387e-05, -0.577336248979839], "ee_velocity_m_s": [0.04502534866333008, -0.004272465594112873, 0.6937694549560547], "catch_distance_m": 0.14661120775232472, "relative_speed_m_s": 1.275826010329897, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

18. 仿真 0.762s；物体中心 (0.46802, -0.00064, 0.84511) m；{"trial": "attempt_01", "kind": "flight_observation", "velocity_m_s": [0.1540300001234902, -5.8794527873586815e-05, -1.064888061499136], "ee_velocity_m_s": [0.11230230331420898, -0.0012345006689429283, 0.19806861877441406], "catch_distance_m": 0.2074885468526167, "relative_speed_m_s": 1.263646374273089, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

19. 仿真 0.812s；物体中心 (0.47570, -0.00064, 0.77873) m；{"trial": "attempt_01", "kind": "flight_observation", "velocity_m_s": [0.1533240224457422, -5.852505034181243e-05, -1.5494370391104157], "ee_velocity_m_s": [0.14113426208496094, -0.00039496924728155136, 0.05679130554199219], "catch_distance_m": 0.2792422765697944, "relative_speed_m_s": 1.606274633621899, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}

20. 仿真 0.825s；物体中心 (0.47624, -0.00064, 0.76533) m；{"trial": "attempt_01", "kind": "missed_catch_object_contacted_environment", "contact_body_ids": [0, 0], "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}

21. 仿真 0.825s；物体中心 (0.47624, -0.00064, 0.76533) m；{"trial": "attempt_01", "kind": "placement_not_reached", "reason": "未通过接球门槛，不能声明已接住后平稳放地", "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}

22. 仿真 2.825s；物体中心 (0.43845, -0.00067, 0.74999) m；{"trial": "attempt_01", "kind": "post_failure_settled_observation", "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}


[2026-10-19T22:33:39+08:00] attempt_01 结束：{"label": "attempt_01", "failure_mode": "none", "parameters": {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 4}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": false, "free_flight": true, "placement": {"passed": false, "status": "not_reached"}, "release_height_m": 0.9052091631266603, "release_velocity_m_s": [0.15504038585519203, -5.918020048293559e-05, -0.04685120369801475], "release_vz_m_s": -0.04685120369801475, "ideal_vacuum_rise_m": 0.0, "required_vz_for_10m_rise_m_s": 14.007141035914502, "apex_height_m": 0.9052091631266603, "rise_from_release_m": 0.0, "flight_ticks": 40, "flight_contact_before_catch": true, "physics_samples": 668, "max_joint_velocity_ratios": [0.013735447109538, 1.000000300449022, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.013755876736676552], "passed": false}


[2026-10-19T22:33:40+08:00] 大模型 request；request_id=9bb37dc913d74efca083372401fbfda0；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:34:00+08:00] 大模型 response；request_id=9bb37dc913d74efca083372401fbfda0；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:34:00+08:00] 大模型 parsed_output；request_id=9bb37dc913d74efca083372401fbfda0；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

23. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 24}, "observed_facts": ["attempt_01已确认抬升并发生真实自由飞行，但完整试验失败；failure_mode为none不能替代阶段指标判定。", "释放高度为0.905209米，释放竖直速度为-0.046851米每秒，释放时未向上运动。", "最高世界高度为0.905209米，相对释放点上升为0米，两个高度条件均未达标。", "试验未接住方块，放地阶段未到达，接住前已发生接触。", "部分关节的最大速度比接近或略高于URDF速度上限，不能据此假设仍有大幅增加驱动速度的余量。", "重力为9.81米每二次方秒时，自由飞行上升10米所需初始向上速度约为14.007141米每秒。", "目前独立完整成功试验数为0。"], "hypotheses": ["4步约为0.0167秒，可能在初始运动过渡期间就释放；延长至24步约0.1秒可能采样到不同的向上运动阶段。", "保持相同笛卡尔目标、仅修改释放步数，有助于区分释放时机与目标选择的影响。", "当前测量显示该参数组合远未达到目标，但单次失败不足以证明所有允许参数或所有控制器均不可行。"], "rationale": "修正已失败的过早释放时机，保持目标位置不变，将释放等待由4步增加至24步，检验真实释放竖直速度是否改善。这是对局部原语能力的进一步测量，不预期仅凭执行完成即可认定成功。继续遵守URDF限制，不注入物体位置或速度、不施加发射外力、不改变重力。", "next_requirements": ["从独立重置的初始状态执行，复用grasp_without_lift_v1；必须测得实际抬升，不能以夹爪闭合或约束建立替代抬升证据。", "按所选单一笛卡尔IK目标执行局部原语，在24个物理步后释放约束，记录释放位置、速度及关节限制符合情况。", "观测真实飞行，分别记录最高世界z和相对释放点上升高度；只有两者均至少10米才通过高度阶段。", "若高度达标，仅在物体下降、距离不超过0.13米且相对速度不超过1米每秒时建立接球固定约束。", "接住后验证方块平稳放置到z=0地面，而非z=0.70米桌面。", "若再次失败，依据释放速度、飞行高度和关节限幅数据继续调整允许参数，或停止并给出限定于已测原语和参数的能力评估。", "至少3次彼此独立的完整试验通过全部阶段后，才允许accept。"]}}


[2026-10-19T22:34:01+08:00] 开始 attempt_02；参数 {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 24}；故障 low_grip_force。

24. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_02", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_02_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

25. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_02", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

26. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

27. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "close_gripper", "物体抓持": false, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact"]}

28. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "lift_object", "物体抓持": false, "实际抬升": false, "事件": []}

29. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-2", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "物体抓持": false, "实际抬升": false, "事件": []}

30. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "grasp_recovery_from_existing_skill", "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "物体抓持": false, "实际抬升": false, "事件": []}

31. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "refresh_object_pose", "物体抓持": false, "实际抬升": false, "事件": ["object_pose_refreshed"]}

32. 仿真 0.842s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "retry_grasp", "物体抓持": false, "实际抬升": false, "事件": ["grasp_retry_requested"]}

33. 仿真 1.042s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

34. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

35. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

36. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "upward_sweep_commanded", "object_target": [0.4, -0.0006272425879208008, 1.35], "steps": 24, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

37. 仿真 1.246s；物体中心 (0.45150, -0.00063, 0.90547) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

38. 仿真 1.250s；物体中心 (0.45096, -0.00063, 0.90558) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

39. 仿真 1.254s；物体中心 (0.45102, -0.00063, 0.90556) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

40. 仿真 1.258s；物体中心 (0.45168, -0.00063, 0.90541) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

41. 仿真 1.262s；物体中心 (0.45268, -0.00063, 0.90504) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 5, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

42. 仿真 1.267s；物体中心 (0.45367, -0.00063, 0.90465) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 6, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

43. 仿真 1.271s；物体中心 (0.45466, -0.00063, 0.90425) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 7, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

44. 仿真 1.275s；物体中心 (0.45565, -0.00063, 0.90383) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 8, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

45. 仿真 1.279s；物体中心 (0.45662, -0.00063, 0.90340) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 9, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

46. 仿真 1.283s；物体中心 (0.45759, -0.00063, 0.90295) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 10, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

47. 仿真 1.287s；物体中心 (0.45856, -0.00063, 0.90249) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 11, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

48. 仿真 1.292s；物体中心 (0.45952, -0.00063, 0.90202) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

49. 仿真 1.296s；物体中心 (0.46047, -0.00063, 0.90154) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 13, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

50. 仿真 1.300s；物体中心 (0.46144, -0.00063, 0.90136) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 14, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

51. 仿真 1.304s；物体中心 (0.46238, -0.00063, 0.90151) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 15, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

52. 仿真 1.308s；物体中心 (0.46330, -0.00063, 0.90196) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 16, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

53. 仿真 1.312s；物体中心 (0.46423, -0.00063, 0.90271) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 17, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

54. 仿真 1.317s；物体中心 (0.46516, -0.00063, 0.90375) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 18, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

55. 仿真 1.321s；物体中心 (0.46612, -0.00063, 0.90505) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 19, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

56. 仿真 1.325s；物体中心 (0.46710, -0.00063, 0.90661) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 20, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

57. 仿真 1.329s；物体中心 (0.46813, -0.00063, 0.90843) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 21, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

58. 仿真 1.333s；物体中心 (0.46919, -0.00063, 0.91049) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 22, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

59. 仿真 1.337s；物体中心 (0.47030, -0.00063, 0.91278) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 23, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

60. 仿真 1.342s；物体中心 (0.47147, -0.00063, 0.91531) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 24, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

61. 仿真 1.342s；物体中心 (0.47147, -0.00063, 0.91531) m；{"trial": "attempt_02", "kind": "release_measured", "release_height_m": 0.9153060201623955, "release_velocity_m_s": [0.27958119678816823, 2.2375635490230166e-06, 0.6059879144477811], "release_vz_m_s": 0.6059879144477811, "ideal_vacuum_rise_m": 0.018716684630824224, "required_vz_for_10m_rise_m_s": 14.007141035914502, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

62. 仿真 1.346s；物体中心 (0.47263, -0.00063, 0.91766) m；{"trial": "attempt_02", "kind": "flight_observation", "velocity_m_s": [0.279503502423765, 2.2369417401183033e-06, 0.5649445131161109], "ee_velocity_m_s": [0.529940128326416, 3.810971975326538e-05, 0.5329799652099609], "catch_distance_m": 0.11061634157880844, "relative_speed_m_s": 0.25246828950029576, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

63. 仿真 1.396s；物体中心 (0.48659, -0.00063, 0.93259) m；{"trial": "attempt_02", "kind": "flight_observation", "velocity_m_s": [0.27869430008107143, 2.230465476025454e-06, 0.07343049534590884], "ee_velocity_m_s": [0.07856369018554688, 1.00722536444664e-05, 0.4288673400878906], "catch_distance_m": 0.12635016264141344, "relative_speed_m_s": 0.407906376119305, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

64. 仿真 1.404s；物体中心 (0.48891, -0.00063, 0.93269) m；{"trial": "attempt_02", "kind": "apex_or_initial_descent", "measured_height_m": 0.9327239691695093, "vz_m_s": -0.008342214924119282, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

65. 仿真 1.446s；物体中心 (0.50050, -0.00063, 0.92298) m；{"trial": "attempt_02", "kind": "flight_observation", "velocity_m_s": [0.2779477569282885, 2.2244906902901113e-06, -0.41664699696758944], "ee_velocity_m_s": [-0.07880687713623047, -0.0057624466717243195, -0.02826690673828125], "catch_distance_m": 0.13808617681627042, "relative_speed_m_s": 0.5273956720021934, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

66. 仿真 1.496s；物体中心 (0.51437, -0.00063, 0.88892) m；{"trial": "attempt_02", "kind": "flight_observation", "velocity_m_s": [0.2770038975718547, 2.216936729882107e-06, -0.9049321742844834], "ee_velocity_m_s": [0.1760387420654297, -0.0016021309420466423, -0.0066089630126953125], "catch_distance_m": 0.1715701762865044, "relative_speed_m_s": 0.9039807124425887, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

67. 仿真 1.546s；物体中心 (0.52819, -0.00063, 0.83050) m；{"trial": "attempt_02", "kind": "flight_observation", "velocity_m_s": [0.27580869684561526, 2.2073712168593382e-06, -1.390518682840148], "ee_velocity_m_s": [0.24805068969726562, -0.00046213623136281967, -0.0006866455078125], "catch_distance_m": 0.22991265832657293, "relative_speed_m_s": 1.3901092815211253, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

68. 仿真 1.592s；物体中心 (0.53907, -0.00063, 0.76360) m；{"trial": "attempt_02", "kind": "missed_catch_object_contacted_environment", "contact_body_ids": [0, 0], "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}

69. 仿真 1.592s；物体中心 (0.53907, -0.00063, 0.76360) m；{"trial": "attempt_02", "kind": "placement_not_reached", "reason": "未通过接球门槛，不能声明已接住后平稳放地", "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}

70. 仿真 3.592s；物体中心 (0.50197, -0.00065, 0.74999) m；{"trial": "attempt_02", "kind": "post_failure_settled_observation", "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}


[2026-10-19T22:34:01+08:00] attempt_02 结束：{"label": "attempt_02", "failure_mode": "low_grip_force", "parameters": {"target_x_m": 0.4, "target_z_m": 1.35, "release_after_steps": 24}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": false, "free_flight": true, "placement": {"passed": false, "status": "not_reached"}, "release_height_m": 0.9153060201623955, "release_velocity_m_s": [0.27958119678816823, 2.2375635490230166e-06, 0.6059879144477811], "release_vz_m_s": 0.6059879144477811, "ideal_vacuum_rise_m": 0.018716684630824224, "required_vz_for_10m_rise_m_s": 14.007141035914502, "apex_height_m": 0.9327239691695093, "rise_from_release_m": 0.017417949007113798, "flight_ticks": 60, "flight_contact_before_catch": true, "physics_samples": 852, "max_joint_velocity_ratios": [0.01249522034475362, 1.0000027788425723, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.012535803649798576], "passed": false}


[2026-10-19T22:34:02+08:00] 大模型 request；request_id=f96d0904f93c4702b8e4ca632ac4073a；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:35:01+08:00] 大模型 response；request_id=f96d0904f93c4702b8e4ca632ac4073a；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:35:02+08:00] 大模型 parsed_output；request_id=f96d0904f93c4702b8e4ca632ac4073a；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

71. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.55, "target_z_m": 1.35, "release_after_steps": 48}, "observed_facts": ["前两次独立试验均确认方块被抬升并发生真实自由飞行，但均未接住、未放置，完整成功试验数为0。", "第一次释放步数为4，释放竖直速度为-0.046851米每秒，释放高度为0.905209米，未产生上升。", "第二次释放步数为24，释放竖直速度为0.605988米每秒，释放高度为0.915306米，实际相对释放点上升仅0.017418米。", "第二次试验的实测释放速度远低于达到10米上升所需的约14.007141米每秒，且最高世界高度仅0.932724米。", "目标高度1.35米在前两次试验中未对应达到相同的实测末端释放高度，说明原语的实际释放状态仍需继续测量。", "部分关节最大速度比接近或略高于URDF速度上限，不能假设存在足够的速度余量。", "根据固定约束接球条件，必须观测到下降、距离不超过0.13米且相对速度不超过1米每秒；前两次均未满足完整接球与放地阶段。"], "hypotheses": ["将释放步数从24增加到48，可能使局部原语在更接近目标运动状态时释放，从而测试释放竖直速度是否继续提高。", "将target_x_m调整到0.55米，可能改变末端轨迹与释放时刻的速度状态，但现有数据不足以证明该改变能达到所需14.007141米每秒。", "即使本次释放速度提高，当前原语是否能实现10米上升仍未知；本次试验只能提供新的实测能力证据。", "前两次失败不能数学上证明所有允许参数或所有控制器均不可行。"], "rationale": "继续进行一次受限参数试验，以区分更长释放等待和横向目标改变对实际释放速度的影响。选择允许范围内的最大target_z_m与release_after_steps，并将target_x_m改为0.55米；不注入物体位置或速度，不施加发射力，不改变重力。只有在实测最高世界z至少10米且相对释放点上升至少10米后，才进入下降状态下的接球判定；接住后还必须验证方块平稳放置于z=0地面。本次不预先宣称成功。", "next_requirements": ["从独立重置状态复用grasp_without_lift_v1，并确认实际抬升证据。", "使用单一Cartesian IK目标target_x_m=0.55米、target_z_m=1.35米，在48个物理步后释放约束。", "记录实际释放位置、三维速度、竖直释放速度、最高世界z、相对释放点上升高度、飞行接触情况及关节速度限制。", "仅当物体下降、与捕获位置距离不超过0.13米且相对速度不超过1米每秒时建立固定约束。", "接住后将方块平稳放置到z=0地面，并记录完整阶段均通过。", "若再次失败，依据实际释放速度、最高高度、上升高度、接球条件和关节限幅决定继续调整允许参数或停止；不能仅因原语执行完成而判定成功。", "至少3次彼此独立且通过抬升、10米世界高度、10米相对上升、接球和落地全部阶段的完整成功试验后，才可返回accept。"]}}


[2026-10-19T22:35:03+08:00] 开始 attempt_03；参数 {"target_x_m": 0.55, "target_z_m": 1.35, "release_after_steps": 48}；故障 none。

72. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_03", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_03_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

73. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_03", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

74. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_03", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

75. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_03", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

76. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

77. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-3", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "match", "errors": [], "severity": "none"}, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

78. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

79. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "upward_sweep_commanded", "object_target": [0.55, -0.0006344299818815758, 1.35], "steps": 48, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

80. 仿真 0.646s；物体中心 (0.45176, -0.00063, 0.90540) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

81. 仿真 0.650s；物体中心 (0.45122, -0.00063, 0.90547) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

82. 仿真 0.654s；物体中心 (0.45127, -0.00063, 0.90540) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

83. 仿真 0.658s；物体中心 (0.45192, -0.00063, 0.90521) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

84. 仿真 0.662s；物体中心 (0.45293, -0.00063, 0.90482) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 5, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

85. 仿真 0.667s；物体中心 (0.45394, -0.00064, 0.90442) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 6, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

86. 仿真 0.671s；物体中心 (0.45495, -0.00064, 0.90401) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 7, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

87. 仿真 0.675s；物体中心 (0.45594, -0.00064, 0.90358) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 8, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

88. 仿真 0.679s；物体中心 (0.45694, -0.00064, 0.90313) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 9, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

89. 仿真 0.683s；物体中心 (0.45793, -0.00064, 0.90268) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 10, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

90. 仿真 0.687s；物体中心 (0.45891, -0.00064, 0.90221) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 11, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

91. 仿真 0.692s；物体中心 (0.45988, -0.00064, 0.90172) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

92. 仿真 0.696s；物体中心 (0.46085, -0.00064, 0.90122) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 13, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

93. 仿真 0.700s；物体中心 (0.46182, -0.00064, 0.90071) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 14, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

94. 仿真 0.704s；物体中心 (0.46277, -0.00064, 0.90019) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 15, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

95. 仿真 0.708s；物体中心 (0.46372, -0.00064, 0.89965) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 16, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

96. 仿真 0.712s；物体中心 (0.46466, -0.00064, 0.89911) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 17, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

97. 仿真 0.717s；物体中心 (0.46560, -0.00064, 0.89854) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 18, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

98. 仿真 0.721s；物体中心 (0.46653, -0.00064, 0.89797) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 19, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

99. 仿真 0.725s；物体中心 (0.46745, -0.00064, 0.89739) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 20, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

100. 仿真 0.729s；物体中心 (0.46836, -0.00064, 0.89679) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 21, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

101. 仿真 0.733s；物体中心 (0.46926, -0.00064, 0.89618) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 22, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

102. 仿真 0.737s；物体中心 (0.47016, -0.00064, 0.89556) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 23, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

103. 仿真 0.742s；物体中心 (0.47105, -0.00064, 0.89493) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 24, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

104. 仿真 0.746s；物体中心 (0.47193, -0.00064, 0.89428) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 25, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

105. 仿真 0.750s；物体中心 (0.47280, -0.00064, 0.89363) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 26, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

106. 仿真 0.754s；物体中心 (0.47366, -0.00064, 0.89296) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 27, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

107. 仿真 0.758s；物体中心 (0.47451, -0.00064, 0.89228) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 28, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

108. 仿真 0.762s；物体中心 (0.47536, -0.00064, 0.89159) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 29, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

109. 仿真 0.767s；物体中心 (0.47619, -0.00064, 0.89089) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 30, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

110. 仿真 0.771s；物体中心 (0.47702, -0.00064, 0.89018) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 31, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

111. 仿真 0.775s；物体中心 (0.47784, -0.00064, 0.88946) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 32, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

112. 仿真 0.779s；物体中心 (0.47864, -0.00064, 0.88872) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 33, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

113. 仿真 0.783s；物体中心 (0.47944, -0.00064, 0.88798) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 34, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

114. 仿真 0.787s；物体中心 (0.48023, -0.00064, 0.88723) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 35, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

115. 仿真 0.792s；物体中心 (0.48101, -0.00064, 0.88646) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 36, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

116. 仿真 0.796s；物体中心 (0.48178, -0.00064, 0.88569) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 37, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

117. 仿真 0.800s；物体中心 (0.48253, -0.00064, 0.88490) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 38, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

118. 仿真 0.804s；物体中心 (0.48328, -0.00064, 0.88411) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 39, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

119. 仿真 0.808s；物体中心 (0.48402, -0.00064, 0.88330) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 40, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

120. 仿真 0.812s；物体中心 (0.48474, -0.00064, 0.88249) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 41, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

121. 仿真 0.817s；物体中心 (0.48546, -0.00064, 0.88167) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 42, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

122. 仿真 0.821s；物体中心 (0.48616, -0.00064, 0.88084) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 43, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

123. 仿真 0.825s；物体中心 (0.48686, -0.00064, 0.88000) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 44, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

124. 仿真 0.829s；物体中心 (0.48754, -0.00064, 0.87915) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 45, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

125. 仿真 0.833s；物体中心 (0.48827, -0.00064, 0.87855) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 46, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

126. 仿真 0.837s；物体中心 (0.48905, -0.00064, 0.87820) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 47, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

127. 仿真 0.842s；物体中心 (0.48988, -0.00064, 0.87810) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 48, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

128. 仿真 0.842s；物体中心 (0.48988, -0.00064, 0.87810) m；{"trial": "attempt_03", "kind": "release_measured", "release_height_m": 0.8781009419052067, "release_velocity_m_s": [0.198482440600153, -7.501653232046476e-07, -0.02456770780568293], "release_vz_m_s": -0.02456770780568293, "ideal_vacuum_rise_m": 0.0, "required_vz_for_10m_rise_m_s": 14.007141035914502, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

129. 仿真 0.846s；物体中心 (0.49071, -0.00064, 0.87783) m；{"trial": "attempt_03", "kind": "flight_observation", "velocity_m_s": [0.19844274420790353, -7.500152905023499e-07, -0.06543779427598845], "ee_velocity_m_s": [0.5823898315429688, -0.017561903223395348, -0.3607320785522461], "catch_distance_m": 0.10846576487023031, "relative_speed_m_s": 0.48468801749301166, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

130. 仿真 0.896s；物体中心 (0.50061, -0.00064, 0.86129) m；{"trial": "attempt_03", "kind": "flight_observation", "velocity_m_s": [0.1979028871418614, -7.479748981673553e-07, -0.5551168237665942], "ee_velocity_m_s": [-0.4755878448486328, -0.0039791688323020935, -0.013132095336914062], "catch_distance_m": 0.09822200432779979, "relative_speed_m_s": 0.8644958298109972, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

131. 仿真 0.946s；物体中心 (0.51049, -0.00064, 0.82031) m；{"trial": "attempt_03", "kind": "flight_observation", "velocity_m_s": [0.19718991672465422, -7.452802231026875e-07, -1.0427682599065085], "ee_velocity_m_s": [-0.21022796630859375, -0.0006876932457089424, 0.7064151763916016], "catch_distance_m": 0.15179400259082432, "relative_speed_m_s": 1.796004592737019, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

132. 仿真 0.992s；物体中心 (0.52043, -0.00064, 0.76735) m；{"trial": "attempt_03", "kind": "missed_catch_object_contacted_environment", "contact_body_ids": [0, 0], "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}

133. 仿真 0.992s；物体中心 (0.52043, -0.00064, 0.76735) m；{"trial": "attempt_03", "kind": "placement_not_reached", "reason": "未通过接球门槛，不能声明已接住后平稳放地", "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}

134. 仿真 2.992s；物体中心 (0.58117, -0.00055, 0.74999) m；{"trial": "attempt_03", "kind": "post_failure_settled_observation", "物体抓持": false, "实际抬升": false, "事件": ["object_released_in_motion"]}


[2026-10-19T22:35:03+08:00] attempt_03 结束：{"label": "attempt_03", "failure_mode": "none", "parameters": {"target_x_m": 0.55, "target_z_m": 1.35, "release_after_steps": 48}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": false, "free_flight": true, "placement": {"passed": false, "status": "not_reached"}, "release_height_m": 0.8781009419052067, "release_velocity_m_s": [0.198482440600153, -7.501653232046476e-07, -0.02456770780568293], "release_vz_m_s": -0.02456770780568293, "ideal_vacuum_rise_m": 0.0, "required_vz_for_10m_rise_m_s": 14.007141035914502, "apex_height_m": 0.8781009419052067, "rise_from_release_m": 0.0, "flight_ticks": 36, "flight_contact_before_catch": true, "physics_samples": 708, "max_joint_velocity_ratios": [0.012384297909808935, 1.000005749516485, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.012477739758737845], "passed": false}


[2026-10-19T22:35:04+08:00] 大模型 request；request_id=12967003a3bc4bb2987d98f097074d94；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:36:17+08:00] 大模型 response；request_id=12967003a3bc4bb2987d98f097074d94；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:36:17+08:00] 大模型 parsed_output；request_id=12967003a3bc4bb2987d98f097074d94；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

135. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.25, "target_z_m": 1.35, "release_after_steps": 48}, "observed_facts": ["已有3次独立试验确认方块被抬升并发生真实自由飞行，但0次完成接球和放地，完整成功试验数为0。", "release_after_steps为4和48的试验均未产生有效上升；release_after_steps为24时相对释放点上升仅0.017418米。", "已观测到的最高世界高度为0.932724米，远低于10米；已观测到的最大释放竖直速度为0.605988米每秒，远低于达到10米上升所需的约14.007141米每秒。", "改变target_x_m至0.55米且release_after_steps为48时，释放竖直速度仍为-0.024568米每秒，说明该参数组合未产生有效抛升。", "所有已有试验均未满足下降、距离不超过0.13米且相对速度不超过1米每秒的固定约束接球条件，也未完成平稳落地。", "已有失败样本不足以数学上证明所有允许参数或所有控制器均不可行。"], "hypotheses": ["在保持最大释放等待步数的同时，将target_x_m改为允许范围下界0.25米，可能改变末端运动轨迹和释放时刻的竖直速度。", "target_z_m为1.35米仍是允许范围内的最高目标，但实际释放高度此前仅约0.878至0.915米，因此必须继续以实测释放状态而非目标值判断能力。", "若本次仍无法获得接近14.007141米每秒的竖直释放速度或10米上升高度，则当前原语在已采样参数附近的抛升能力证据仍然不足。", "即使原语完成运动并确认抬升，也不能据此判定10米抛升、接球或放地成功。"], "rationale": "继续进行一次独立的受限参数试验，以区分横向Cartesian IK目标对实际释放速度的影响。选择target_x_m=0.25米、target_z_m=1.35米和release_after_steps=48，均在允许范围内；不注入物体位置或速度，不施加发射力，不改变重力。试验必须记录真实释放位置和速度、最高世界z、相对释放点上升高度及自由飞行状态。只有同时达到世界z至少10米和相对释放点上升至少10米，随后在下降阶段满足固定约束接球条件，并最终平稳放置于z=0地面，才算完整成功。本次不预先宣称成功。", "next_requirements": ["从独立重置状态复用grasp_without_lift_v1，并确认实际抬升证据。", "使用单一Cartesian IK目标target_x_m=0.25米、target_z_m=1.35米，在48个物理步后释放约束。", "记录实际释放位置、三维释放速度、释放竖直速度、最高世界z、相对释放点上升高度、飞行接触情况和关节速度限制。", "仅在物体处于下降状态、与捕获位置距离不超过0.13米且相对速度不超过1米每秒时建立固定约束。", "接住后将方块平稳放置到z=0地面，并记录抬升、抛升、接球和放置各阶段结果。", "若本次仍失败，依据实测释放速度、最高高度、相对上升高度、接球条件和关节限幅决定继续调整允许参数或停止；不能仅因原语执行完成而判定成功。", "只有至少3次彼此独立且完整通过抬升、世界z至少10米、相对释放点上升至少10米、接球和落地的试验，才可返回accept。"]}}


[2026-10-19T22:36:18+08:00] 开始 attempt_04；参数 {"target_x_m": 0.25, "target_z_m": 1.35, "release_after_steps": 48}；故障 none。

136. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_04", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_04_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

137. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_04", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

138. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_04", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

139. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_04", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

140. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_04", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

141. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_04", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-4", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "match", "errors": [], "severity": "none"}, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

142. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_04", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

143. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_04", "kind": "upward_sweep_commanded", "object_target": [0.25, -0.0006344299818815758, 1.35], "steps": 48, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

144. 仿真 0.646s；物体中心 (0.45114, -0.00064, 0.90591) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

145. 仿真 0.650s；物体中心 (0.44937, -0.00064, 0.90698) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

146. 仿真 0.654s；物体中心 (0.44759, -0.00064, 0.90841) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

147. 仿真 0.658s；物体中心 (0.44581, -0.00064, 0.91018) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

148. 仿真 0.662s；物体中心 (0.44402, -0.00064, 0.91231) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 5, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

149. 仿真 0.667s；物体中心 (0.44223, -0.00064, 0.91479) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 6, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

150. 仿真 0.671s；物体中心 (0.44043, -0.00064, 0.91760) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 7, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

151. 仿真 0.675s；物体中心 (0.43866, -0.00064, 0.92073) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 8, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

152. 仿真 0.679s；物体中心 (0.43720, -0.00064, 0.92398) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 9, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

153. 仿真 0.683s；物体中心 (0.43601, -0.00064, 0.92736) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 10, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

154. 仿真 0.687s；物体中心 (0.43509, -0.00064, 0.93087) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 11, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

155. 仿真 0.692s；物体中心 (0.43440, -0.00064, 0.93453) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

156. 仿真 0.696s；物体中心 (0.43392, -0.00064, 0.93835) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 13, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

157. 仿真 0.700s；物体中心 (0.43365, -0.00064, 0.94233) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 14, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

158. 仿真 0.704s；物体中心 (0.43356, -0.00064, 0.94647) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 15, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

159. 仿真 0.708s；物体中心 (0.43363, -0.00064, 0.95078) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 16, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

160. 仿真 0.712s；物体中心 (0.43386, -0.00064, 0.95527) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 17, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

161. 仿真 0.717s；物体中心 (0.43423, -0.00064, 0.95993) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 18, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

162. 仿真 0.721s；物体中心 (0.43472, -0.00064, 0.96478) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 19, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

163. 仿真 0.725s；物体中心 (0.43533, -0.00064, 0.96981) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 20, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

164. 仿真 0.729s；物体中心 (0.43604, -0.00064, 0.97503) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 21, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

165. 仿真 0.733s；物体中心 (0.43678, -0.00064, 0.98036) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 22, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

166. 仿真 0.737s；物体中心 (0.43745, -0.00064, 0.98563) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 23, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

167. 仿真 0.742s；物体中心 (0.43804, -0.00064, 0.99084) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 24, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

168. 仿真 0.746s；物体中心 (0.43856, -0.00064, 0.99599) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 25, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

169. 仿真 0.750s；物体中心 (0.43900, -0.00064, 1.00109) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 26, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

170. 仿真 0.754s；物体中心 (0.43937, -0.00064, 1.00614) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 27, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

171. 仿真 0.758s；物体中心 (0.43968, -0.00064, 1.01116) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 28, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

172. 仿真 0.762s；物体中心 (0.43992, -0.00064, 1.01613) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 29, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

173. 仿真 0.767s；物体中心 (0.44009, -0.00064, 1.02107) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 30, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

174. 仿真 0.771s；物体中心 (0.44020, -0.00064, 1.02598) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 31, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

175. 仿真 0.775s；物体中心 (0.44025, -0.00064, 1.03086) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 32, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

176. 仿真 0.779s；物体中心 (0.44023, -0.00064, 1.03571) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 33, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

177. 仿真 0.783s；物体中心 (0.44015, -0.00064, 1.04054) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 34, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

178. 仿真 0.787s；物体中心 (0.44002, -0.00064, 1.04534) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 35, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

179. 仿真 0.792s；物体中心 (0.43982, -0.00064, 1.05012) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 36, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

180. 仿真 0.796s；物体中心 (0.43956, -0.00064, 1.05488) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 37, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

181. 仿真 0.800s；物体中心 (0.43924, -0.00064, 1.05962) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 38, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

182. 仿真 0.804s；物体中心 (0.43886, -0.00064, 1.06434) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 39, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

183. 仿真 0.808s；物体中心 (0.43842, -0.00064, 1.06904) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 40, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

184. 仿真 0.812s；物体中心 (0.43793, -0.00064, 1.07372) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 41, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

185. 仿真 0.817s；物体中心 (0.43737, -0.00064, 1.07839) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 42, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

186. 仿真 0.821s；物体中心 (0.43675, -0.00064, 1.08303) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 43, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

187. 仿真 0.825s；物体中心 (0.43608, -0.00064, 1.08766) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 44, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

188. 仿真 0.829s；物体中心 (0.43535, -0.00064, 1.09228) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 45, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

189. 仿真 0.833s；物体中心 (0.43455, -0.00064, 1.09687) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 46, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

190. 仿真 0.837s；物体中心 (0.43370, -0.00064, 1.10145) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 47, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

191. 仿真 0.842s；物体中心 (0.43280, -0.00064, 1.10601) m；{"trial": "attempt_04", "kind": "sweep_step", "index": 48, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

192. 仿真 0.842s；物体中心 (0.43280, -0.00064, 1.10601) m；{"trial": "attempt_04", "kind": "release_measured", "release_height_m": 1.1060131365270789, "release_velocity_m_s": [-0.2178904615844586, 1.0255614984150026e-05, 1.0948054494013788], "release_vz_m_s": 1.0948054494013788, "ideal_vacuum_rise_m": 0.061090671357744895, "required_vz_for_10m_rise_m_s": 14.007141035914502, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

193. 仿真 0.846s；物体中心 (0.43189, -0.00064, 1.11040) m；{"trial": "attempt_04", "kind": "flight_observation", "velocity_m_s": [-0.21781360880972453, 1.0251997696534935e-05, 1.0535442974056988], "ee_velocity_m_s": [0.024404525756835938, 2.3636966943740845e-05, 0.9930896759033203], "catch_distance_m": 0.10834716576500504, "relative_speed_m_s": 0.24964852523709735, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

194. 仿真 0.896s；物体中心 (0.42102, -0.00064, 1.14970) m；{"trial": "attempt_04", "kind": "flight_observation", "velocity_m_s": [-0.2170064671134301, 1.0214007348473552e-05, 0.559935205521618], "ee_velocity_m_s": [-0.00947713851928711, 8.996576070785522e-06, -0.22461891174316406], "catch_distance_m": 0.0748113737677645, "relative_speed_m_s": 0.8115377903371718, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

195. 仿真 0.946s；物体中心 (0.41019, -0.00064, 1.16438) m；{"trial": "attempt_04", "kind": "flight_observation", "velocity_m_s": [-0.21639655501083013, 1.0185300154716865e-05, 0.0684614053116443], "ee_velocity_m_s": [-0.0036406517028808594, 2.4167820811271667e-06, -0.0634002685546875], "catch_distance_m": 0.05687481998718706, "relative_speed_m_s": 0.25030496496786114, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

196. 仿真 0.954s；物体中心 (0.40839, -0.00064, 1.16444) m；{"trial": "attempt_04", "kind": "apex_or_initial_descent", "measured_height_m": 1.1644947330048958, "vz_m_s": -0.013308192346967444, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

197. 仿真 0.958s；物体中心 (0.40748, -0.00064, 1.16421) m；{"trial": "attempt_04", "kind": "catch_gate_passed", "distance_m": 0.05693366293545239, "relative_speed_m_s": 0.2572663284572365, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

198. 仿真 1.958s；物体中心 (0.74480, -0.00126, 1.08398) m；{"trial": "attempt_04", "kind": "carry_outside_table", "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

199. 仿真 1.958s；物体中心 (0.74480, -0.00126, 1.08398) m；{"trial": "attempt_04", "kind": "trial_error", "error": "RuntimeError: ground placement unreachable outside table; retain grasp", "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}


[2026-10-19T22:36:18+08:00] attempt_04 结束：{"label": "attempt_04", "failure_mode": "none", "parameters": {"target_x_m": 0.25, "target_z_m": 1.35, "release_after_steps": 48}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": true, "free_flight": true, "placement": {"passed": false, "status": "not_reached"}, "release_height_m": 1.1060131365270789, "release_velocity_m_s": [-0.2178904615844586, 1.0255614984150026e-05, 1.0948054494013788], "release_vz_m_s": 1.0948054494013788, "ideal_vacuum_rise_m": 0.061090671357744895, "required_vz_for_10m_rise_m_s": 14.007141035914502, "apex_height_m": 1.1644947330048958, "rise_from_release_m": 0.05848159647781692, "flight_ticks": 28, "flight_contact_before_catch": false, "error": "RuntimeError: ground placement unreachable outside table; retain grasp", "physics_samples": 460, "max_joint_velocity_ratios": [0.018373981790996214, 1.0004128137152917, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.01839738756322752], "passed": false}


[2026-10-19T22:36:19+08:00] 大模型 request；request_id=efba0683edfc412284b60cd2524e399c；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:38:39+08:00] 大模型 response；request_id=efba0683edfc412284b60cd2524e399c；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T22:38:40+08:00] 大模型 parsed_output；request_id=efba0683edfc412284b60cd2524e399c；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

200. 仿真 0.000s；物体中心 (—) m；{"kind": "final_model_review", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.25, "target_z_m": 1.35, "release_after_steps": 24}, "observed_facts": ["已有4次独立试验均确认方块被抬升并进入真实自由飞行，但完整成功试验数为0。", "此前release_after_steps为24时，释放竖直速度为0.605988米每秒，相对释放点上升仅0.017418米，远低于达到10米上升所需的约14.007141米每秒。", "此前release_after_steps为4和48时均未产生有效竖直上升；release_after_steps为48、target_x_m为0.25米的试验虽成功接球，但释放竖直速度仅1.094805米每秒。", "已观测最高世界高度为0.932724米，远低于10米；此前最高相对释放点上升高度为0.058482米，远低于10米。", "尚无试验同时满足世界z至少10米、相对释放点上升至少10米、下降阶段接球、接球后平稳放置到z=0地面。", "已有失败样本不足以数学上证明所有允许参数或所有控制器均不可行。"], "hypotheses": ["将target_x_m改为0.25米并保留target_z_m为允许范围最高值1.35米，可能改变末端轨迹和释放时刻，从而改善竖直释放速度。", "release_after_steps为24此前产生了已观测参数中相对较高的正竖直释放速度，因此再次采用该等待步数并改变横向目标可用于区分横向目标与释放时序的影响。", "即使原语确认抬升并完成释放，仍需以实际飞行测量确认世界最高高度和相对释放点上升高度，不能用目标高度替代实测高度。", "若本次仍仅产生约1米每秒量级或更低的竖直释放速度，则当前采样附近实现10米抛升的能力证据仍然很弱，但不能据此断言所有允许参数均不可行。"], "rationale": "继续进行一次独立的受限参数试验，以测试target_x_m从0.4米改变为0.25米且release_after_steps保持为24步时的实际释放效果。仅使用允许的Cartesian IK目标和释放步数，不注入物体位置或速度，不施加发射力，不改变重力。必须先复用grasp_without_lift_v1并确认实际抬升，再记录真实释放位置、三维释放速度、最高世界z、相对释放点上升高度和自由飞行状态。只有物体达到世界z至少10米且相对释放点上升至少10米，并在下降、距离不超过0.13米、相对速度不超过1米每秒时接住，随后平稳放置于z=0地面，才可计为完整成功。本次不预先宣称成功。", "next_requirements": ["从独立重置状态执行grasp_without_lift_v1，并确认实际抬升证据。", "使用target_x_m=0.25米、target_z_m=1.35米，经过24个物理步后释放固定约束。", "记录实际释放位置、三维释放速度、释放竖直速度、最高世界z、相对释放点上升高度、下降状态、飞行接触情况和关节速度限制。", "仅在物体下降、捕获距离不超过0.13米且相对速度不超过1米每秒时建立固定约束。", "接住后将方块平稳放置到z=0地面，并分别记录抬升、抛升、接球和放置结果。", "若本次失败，依据实际释放速度、最高高度、相对上升高度及接球和放置条件，决定继续尝试其他允许参数或停止。", "至少需要3次彼此独立且完整通过抬升、世界z至少10米、相对释放点上升至少10米、接球和落地的试验后，才可返回accept。"]}}


[2026-10-19T22:38:40+08:00] 实验结束：goal_achieved=False，试验数=4，新技能状态 candidate；原技能保持不变。汇总：docs\throw_catch_evidence_v2\summary.json


## ��Ƶ�ط�

�Ѵ� attempt_04 ��ʵ������ CSV ���� [�����Ƶ](throw_catch_evidence_v2/attempt_04_audit.mp4)����Ƶ��ʾ x-z ʵ��켣�����桢���桢10 ��Ŀ���ߡ���צλ�á��ͷ��ٶȡ���߸߶ȡ�����ͷŵ��ж������ǹ켣��ƻطţ����������ԭʼ¼��

## 2026-10-19 改进验证

基于 4 次抛掷数据完成失败原因分析，并新增“释放竖直速度门控”验证。达到相对上升 10 m 需要 `14.007142 m/s`；历史最高释放竖直速度 `1.094805 m/s`。新增 3 次门控试验的最大实测速度为 `1.280、1.070、0.048 m/s`，均阻止释放、保留抓持并安全停止。候选 Skill 更新为版本 2，仍为 `candidate`，未宣称完成目标。详见 `docs/THROW_CATCH_ANALYSIS.md`。


[2026-10-19T23:19:18+08:00] 开始运行 38f6096108bf；输出目录 docs\throw_catch_2m_20261019。


[2026-10-19T23:19:18+08:00] 目标改为释放后相对上升 2.0 m；要求竖直释放速度 6.264184 m/s。


[2026-10-19T23:19:18+08:00] 大模型 request；request_id=6a542f95d01a49bdbb9cec8607d23bd2；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:19:51+08:00] 大模型 response；request_id=6a542f95d01a49bdbb9cec8607d23bd2；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:19:51+08:00] 大模型 parsed_output；request_id=6a542f95d01a49bdbb9cec8607d23bd2；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:19:51+08:00] 模型提案不可用，使用已测最佳参数作为保守回退：ValueError: parameters must have exactly ['target_x_m', 'target_z_m', 'release_after_steps']

1. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": 1, "kind": "reset", "物体抓持": false, "实际抬升": false, "事件": []}

2. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": 1, "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

3. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": 1, "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

4. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": 1, "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

5. 仿真 0.646s；物体中心 (0.45114, -0.00063, 0.90591) m；{"trial": 1, "kind": "trace_step", "index": 1, "vz_m_s": 0.16959663633775043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

6. 仿真 0.650s；物体中心 (0.44937, -0.00063, 0.90698) m；{"trial": 1, "kind": "trace_step", "index": 2, "vz_m_s": 0.25664421153982736, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

7. 仿真 0.654s；物体中心 (0.44759, -0.00064, 0.90841) m；{"trial": 1, "kind": "trace_step", "index": 3, "vz_m_s": 0.3424130142861954, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

8. 仿真 0.658s；物体中心 (0.44581, -0.00064, 0.91018) m；{"trial": 1, "kind": "trace_step", "index": 4, "vz_m_s": 0.4270507829486157, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

9. 仿真 0.662s；物体中心 (0.44402, -0.00064, 0.91231) m；{"trial": 1, "kind": "trace_step", "index": 5, "vz_m_s": 0.5106981842298295, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

10. 仿真 0.667s；物体中心 (0.44223, -0.00064, 0.91479) m；{"trial": 1, "kind": "trace_step", "index": 6, "vz_m_s": 0.5934901686225933, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

11. 仿真 0.671s；物体中心 (0.44043, -0.00064, 0.91760) m；{"trial": 1, "kind": "trace_step", "index": 7, "vz_m_s": 0.675556997505673, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

12. 仿真 0.675s；物体中心 (0.43863, -0.00064, 0.92075) m；{"trial": 1, "kind": "trace_step", "index": 8, "vz_m_s": 0.7570249654533997, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

13. 仿真 0.679s；物体中心 (0.43682, -0.00064, 0.92425) m；{"trial": 1, "kind": "trace_step", "index": 9, "vz_m_s": 0.83801683395043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

14. 仿真 0.683s；物体中心 (0.43500, -0.00064, 0.92807) m；{"trial": 1, "kind": "trace_step", "index": 10, "vz_m_s": 0.9186519834775123, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

15. 仿真 0.687s；物体中心 (0.43330, -0.00064, 0.93215) m；{"trial": 1, "kind": "trace_step", "index": 11, "vz_m_s": 0.9787439744260048, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

16. 仿真 0.692s；物体中心 (0.43172, -0.00064, 0.93646) m；{"trial": 1, "kind": "trace_step", "index": 12, "vz_m_s": 1.0344197283689107, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

17. 仿真 0.696s；物体中心 (0.43028, -0.00064, 0.94101) m；{"trial": 1, "kind": "trace_step", "index": 13, "vz_m_s": 1.0905367232662437, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

18. 仿真 0.700s；物体中心 (0.42894, -0.00064, 0.94579) m；{"trial": 1, "kind": "trace_step", "index": 14, "vz_m_s": 1.1470940206481604, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

19. 仿真 0.704s；物体中心 (0.42771, -0.00064, 0.95080) m；{"trial": 1, "kind": "trace_step", "index": 15, "vz_m_s": 1.204086173806357, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

20. 仿真 0.708s；物体中心 (0.42657, -0.00064, 0.95606) m；{"trial": 1, "kind": "trace_step", "index": 16, "vz_m_s": 1.2615024015336285, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

21. 仿真 0.712s；物体中心 (0.42550, -0.00064, 0.96156) m；{"trial": 1, "kind": "trace_step", "index": 17, "vz_m_s": 1.3193259144602993, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

22. 仿真 0.717s；物体中心 (0.42450, -0.00064, 0.96730) m；{"trial": 1, "kind": "trace_step", "index": 18, "vz_m_s": 1.3775333618017076, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

23. 仿真 0.721s；物体中心 (0.42355, -0.00064, 0.97328) m；{"trial": 1, "kind": "trace_step", "index": 19, "vz_m_s": 1.4360943749847168, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

24. 仿真 0.725s；物体中心 (0.42263, -0.00064, 0.97951) m；{"trial": 1, "kind": "trace_step", "index": 20, "vz_m_s": 1.4949711883738097, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

25. 仿真 0.729s；物体中心 (0.42174, -0.00064, 0.98598) m；{"trial": 1, "kind": "trace_step", "index": 21, "vz_m_s": 1.5541183206748135, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

26. 仿真 0.733s；物体中心 (0.42085, -0.00064, 0.99271) m；{"trial": 1, "kind": "trace_step", "index": 22, "vz_m_s": 1.6134823088322803, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

27. 仿真 0.737s；物体中心 (0.41996, -0.00064, 0.99968) m；{"trial": 1, "kind": "trace_step", "index": 23, "vz_m_s": 1.6730014744869435, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

28. 仿真 0.742s；物体中心 (0.41904, -0.00064, 1.00690) m；{"trial": 1, "kind": "trace_step", "index": 24, "vz_m_s": 1.7326057221318263, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

29. 仿真 0.746s；物体中心 (0.41808, -0.00064, 1.01436) m；{"trial": 1, "kind": "trace_step", "index": 25, "vz_m_s": 1.7922163562564952, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

30. 仿真 0.750s；物体中心 (0.41707, -0.00064, 1.02208) m；{"trial": 1, "kind": "trace_step", "index": 26, "vz_m_s": 1.8517459175870126, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

31. 仿真 0.754s；物体中心 (0.41598, -0.00064, 1.03004) m；{"trial": 1, "kind": "trace_step", "index": 27, "vz_m_s": 1.9110983494568095, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

32. 仿真 0.758s；物体中心 (0.41481, -0.00064, 1.03825) m；{"trial": 1, "kind": "trace_step", "index": 28, "vz_m_s": 1.9701674693338915, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

33. 仿真 0.762s；物体中心 (0.41357, -0.00064, 1.04670) m；{"trial": 1, "kind": "trace_step", "index": 29, "vz_m_s": 2.0272624143442903, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

34. 仿真 0.767s；物体中心 (0.41212, -0.00064, 1.05449) m；{"trial": 1, "kind": "trace_step", "index": 30, "vz_m_s": 1.8689142861356713, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

35. 仿真 0.771s；物体中心 (0.41047, -0.00064, 1.06161) m；{"trial": 1, "kind": "trace_step", "index": 31, "vz_m_s": 1.7089773904539207, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

36. 仿真 0.775s；物体中心 (0.40866, -0.00064, 1.06806) m；{"trial": 1, "kind": "trace_step", "index": 32, "vz_m_s": 1.5480263826162874, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

37. 仿真 0.779s；物体中心 (0.40669, -0.00064, 1.07383) m；{"trial": 1, "kind": "trace_step", "index": 33, "vz_m_s": 1.3865696572050359, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

38. 仿真 0.783s；物体中心 (0.40458, -0.00064, 1.07894) m；{"trial": 1, "kind": "trace_step", "index": 34, "vz_m_s": 1.2250547994723178, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

39. 仿真 0.787s；物体中心 (0.40236, -0.00064, 1.08337) m；{"trial": 1, "kind": "trace_step", "index": 35, "vz_m_s": 1.063874609665528, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

40. 仿真 0.792s；物体中心 (0.40002, -0.00064, 1.08714) m；{"trial": 1, "kind": "trace_step", "index": 36, "vz_m_s": 0.9033735008830288, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

41. 仿真 0.796s；物体中心 (0.39758, -0.00064, 1.09024) m；{"trial": 1, "kind": "trace_step", "index": 37, "vz_m_s": 0.7438541652482743, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

42. 仿真 0.800s；物体中心 (0.39504, -0.00064, 1.09268) m；{"trial": 1, "kind": "trace_step", "index": 38, "vz_m_s": 0.58558434675802, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

43. 仿真 0.804s；物体中心 (0.39241, -0.00064, 1.09446) m；{"trial": 1, "kind": "trace_step", "index": 39, "vz_m_s": 0.4288032561120959, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

44. 仿真 0.808s；物体中心 (0.38970, -0.00064, 1.09568) m；{"trial": 1, "kind": "trace_step", "index": 40, "vz_m_s": 0.29224732820813604, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

45. 仿真 0.812s；物体中心 (0.38700, -0.00064, 1.09664) m；{"trial": 1, "kind": "trace_step", "index": 41, "vz_m_s": 0.22968403893816203, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

46. 仿真 0.817s；物体中心 (0.38430, -0.00064, 1.09736) m；{"trial": 1, "kind": "trace_step", "index": 42, "vz_m_s": 0.1745132711866592, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

47. 仿真 0.821s；物体中心 (0.38160, -0.00064, 1.09789) m；{"trial": 1, "kind": "trace_step", "index": 43, "vz_m_s": 0.12598848642336483, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

48. 仿真 0.825s；物体中心 (0.37890, -0.00063, 1.09824) m；{"trial": 1, "kind": "trace_step", "index": 44, "vz_m_s": 0.08340379304914602, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

49. 仿真 0.829s；物体中心 (0.37620, -0.00063, 1.09843) m；{"trial": 1, "kind": "trace_step", "index": 45, "vz_m_s": 0.0461631308374237, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

50. 仿真 0.833s；物体中心 (0.37357, -0.00063, 1.09852) m；{"trial": 1, "kind": "trace_step", "index": 46, "vz_m_s": 0.02079913985193649, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

51. 仿真 0.837s；物体中心 (0.37118, -0.00063, 1.09861) m；{"trial": 1, "kind": "trace_step", "index": 47, "vz_m_s": 0.0219223679239112, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

52. 仿真 0.842s；物体中心 (0.36903, -0.00063, 1.09870) m；{"trial": 1, "kind": "trace_step", "index": 48, "vz_m_s": 0.022294490627478566, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

53. 仿真 0.846s；物体中心 (0.36708, -0.00063, 1.09879) m；{"trial": 1, "kind": "trace_step", "index": 49, "vz_m_s": 0.022116744131858043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

54. 仿真 0.850s；物体中心 (0.36533, -0.00063, 1.09888) m；{"trial": 1, "kind": "trace_step", "index": 50, "vz_m_s": 0.021558395303166614, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

55. 仿真 0.854s；物体中心 (0.36374, -0.00063, 1.09897) m；{"trial": 1, "kind": "trace_step", "index": 51, "vz_m_s": 0.020677345948972563, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

56. 仿真 0.858s；物体中心 (0.36231, -0.00063, 1.09905) m；{"trial": 1, "kind": "trace_step", "index": 52, "vz_m_s": 0.019665270831656038, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

57. 仿真 0.862s；物体中心 (0.36103, -0.00063, 1.09913) m；{"trial": 1, "kind": "trace_step", "index": 53, "vz_m_s": 0.018554222303069304, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

58. 仿真 0.867s；物体中心 (0.35986, -0.00063, 1.09920) m；{"trial": 1, "kind": "trace_step", "index": 54, "vz_m_s": 0.017387947800578552, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

59. 仿真 0.871s；物体中心 (0.35882, -0.00063, 1.09927) m；{"trial": 1, "kind": "trace_step", "index": 55, "vz_m_s": 0.016192914462753737, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

60. 仿真 0.875s；物体中心 (0.35787, -0.00063, 1.09933) m；{"trial": 1, "kind": "trace_step", "index": 56, "vz_m_s": 0.015009129837144922, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

61. 仿真 0.879s；物体中心 (0.35702, -0.00063, 1.09939) m；{"trial": 1, "kind": "trace_step", "index": 57, "vz_m_s": 0.013868750678738193, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

62. 仿真 0.883s；物体中心 (0.35625, -0.00063, 1.09944) m；{"trial": 1, "kind": "trace_step", "index": 58, "vz_m_s": 0.012761817178448733, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

63. 仿真 0.887s；物体中心 (0.35556, -0.00063, 1.09949) m；{"trial": 1, "kind": "trace_step", "index": 59, "vz_m_s": 0.011709754693356892, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

64. 仿真 0.892s；物体中心 (0.35494, -0.00063, 1.09953) m；{"trial": 1, "kind": "trace_step", "index": 60, "vz_m_s": 0.010718189164597148, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

65. 仿真 0.896s；物体中心 (0.35438, -0.00063, 1.09957) m；{"trial": 1, "kind": "trace_step", "index": 61, "vz_m_s": 0.009789968059967177, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

66. 仿真 0.900s；物体中心 (0.35388, -0.00063, 1.09961) m；{"trial": 1, "kind": "trace_step", "index": 62, "vz_m_s": 0.008925888474757091, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

67. 仿真 0.904s；物体中心 (0.35342, -0.00063, 1.09965) m；{"trial": 1, "kind": "trace_step", "index": 63, "vz_m_s": 0.00812525159415628, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

68. 仿真 0.908s；物体中心 (0.35301, -0.00063, 1.09968) m；{"trial": 1, "kind": "trace_step", "index": 64, "vz_m_s": 0.007386291188536315, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

69. 仿真 0.912s；物体中心 (0.35265, -0.00063, 1.09970) m；{"trial": 1, "kind": "trace_step", "index": 65, "vz_m_s": 0.006706507565756595, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

70. 仿真 0.917s；物体中心 (0.35231, -0.00063, 1.09973) m；{"trial": 1, "kind": "trace_step", "index": 66, "vz_m_s": 0.006082920867305858, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

71. 仿真 0.921s；物体中心 (0.35202, -0.00063, 1.09975) m；{"trial": 1, "kind": "trace_step", "index": 67, "vz_m_s": 0.005512264075632496, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

72. 仿真 0.925s；物体中心 (0.35175, -0.00063, 1.09977) m；{"trial": 1, "kind": "trace_step", "index": 68, "vz_m_s": 0.004991128018489624, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

73. 仿真 0.929s；物体中心 (0.35151, -0.00063, 1.09979) m；{"trial": 1, "kind": "trace_step", "index": 69, "vz_m_s": 0.004516068827137017, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

74. 仿真 0.933s；物体中心 (0.35129, -0.00063, 1.09981) m；{"trial": 1, "kind": "trace_step", "index": 70, "vz_m_s": 0.004083686157987099, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

75. 仿真 0.937s；物体中心 (0.35109, -0.00063, 1.09982) m；{"trial": 1, "kind": "trace_step", "index": 71, "vz_m_s": 0.0036906787338864683, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

76. 仿真 0.942s；物体中心 (0.35092, -0.00063, 1.09984) m；{"trial": 1, "kind": "trace_step", "index": 72, "vz_m_s": 0.0033338824519965407, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

77. 仿真 0.942s；物体中心 (0.35092, -0.00063, 1.09984) m；{"trial": 1, "kind": "release_gate_blocked", "measured_max_vz_m_s": 2.0272624143442903, "reason": "measured velocity cannot support a 2m rise", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}

78. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": 2, "kind": "reset", "物体抓持": false, "实际抬升": false, "事件": []}

79. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": 2, "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

80. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": 2, "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

81. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": 2, "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

82. 仿真 0.646s；物体中心 (0.45114, -0.00063, 0.90591) m；{"trial": 2, "kind": "trace_step", "index": 1, "vz_m_s": 0.16959663633775043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

83. 仿真 0.650s；物体中心 (0.44937, -0.00063, 0.90698) m；{"trial": 2, "kind": "trace_step", "index": 2, "vz_m_s": 0.25664421153982736, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

84. 仿真 0.654s；物体中心 (0.44759, -0.00064, 0.90841) m；{"trial": 2, "kind": "trace_step", "index": 3, "vz_m_s": 0.3424130142861954, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

85. 仿真 0.658s；物体中心 (0.44581, -0.00064, 0.91018) m；{"trial": 2, "kind": "trace_step", "index": 4, "vz_m_s": 0.4270507829486157, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

86. 仿真 0.662s；物体中心 (0.44402, -0.00064, 0.91231) m；{"trial": 2, "kind": "trace_step", "index": 5, "vz_m_s": 0.5106981842298295, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

87. 仿真 0.667s；物体中心 (0.44223, -0.00064, 0.91479) m；{"trial": 2, "kind": "trace_step", "index": 6, "vz_m_s": 0.5934901686225933, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

88. 仿真 0.671s；物体中心 (0.44043, -0.00064, 0.91760) m；{"trial": 2, "kind": "trace_step", "index": 7, "vz_m_s": 0.675556997505673, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

89. 仿真 0.675s；物体中心 (0.43863, -0.00064, 0.92075) m；{"trial": 2, "kind": "trace_step", "index": 8, "vz_m_s": 0.7570249654533997, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

90. 仿真 0.679s；物体中心 (0.43682, -0.00064, 0.92425) m；{"trial": 2, "kind": "trace_step", "index": 9, "vz_m_s": 0.83801683395043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

91. 仿真 0.683s；物体中心 (0.43500, -0.00064, 0.92807) m；{"trial": 2, "kind": "trace_step", "index": 10, "vz_m_s": 0.9186519834775123, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

92. 仿真 0.687s；物体中心 (0.43330, -0.00064, 0.93215) m；{"trial": 2, "kind": "trace_step", "index": 11, "vz_m_s": 0.9787439744260048, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

93. 仿真 0.692s；物体中心 (0.43172, -0.00064, 0.93646) m；{"trial": 2, "kind": "trace_step", "index": 12, "vz_m_s": 1.0344197283689107, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

94. 仿真 0.696s；物体中心 (0.43028, -0.00064, 0.94101) m；{"trial": 2, "kind": "trace_step", "index": 13, "vz_m_s": 1.0905367232662437, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

95. 仿真 0.700s；物体中心 (0.42894, -0.00064, 0.94579) m；{"trial": 2, "kind": "trace_step", "index": 14, "vz_m_s": 1.1470940206481604, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

96. 仿真 0.704s；物体中心 (0.42771, -0.00064, 0.95080) m；{"trial": 2, "kind": "trace_step", "index": 15, "vz_m_s": 1.204086173806357, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

97. 仿真 0.708s；物体中心 (0.42657, -0.00064, 0.95606) m；{"trial": 2, "kind": "trace_step", "index": 16, "vz_m_s": 1.2615024015336285, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

98. 仿真 0.712s；物体中心 (0.42550, -0.00064, 0.96156) m；{"trial": 2, "kind": "trace_step", "index": 17, "vz_m_s": 1.3193259144602993, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

99. 仿真 0.717s；物体中心 (0.42450, -0.00064, 0.96730) m；{"trial": 2, "kind": "trace_step", "index": 18, "vz_m_s": 1.3775333618017076, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

100. 仿真 0.721s；物体中心 (0.42355, -0.00064, 0.97328) m；{"trial": 2, "kind": "trace_step", "index": 19, "vz_m_s": 1.4360943749847168, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

101. 仿真 0.725s；物体中心 (0.42263, -0.00064, 0.97951) m；{"trial": 2, "kind": "trace_step", "index": 20, "vz_m_s": 1.4949711883738097, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

102. 仿真 0.729s；物体中心 (0.42174, -0.00064, 0.98598) m；{"trial": 2, "kind": "trace_step", "index": 21, "vz_m_s": 1.5541183206748135, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

103. 仿真 0.733s；物体中心 (0.42085, -0.00064, 0.99271) m；{"trial": 2, "kind": "trace_step", "index": 22, "vz_m_s": 1.6134823088322803, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

104. 仿真 0.737s；物体中心 (0.41996, -0.00064, 0.99968) m；{"trial": 2, "kind": "trace_step", "index": 23, "vz_m_s": 1.6730014744869435, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

105. 仿真 0.742s；物体中心 (0.41904, -0.00064, 1.00690) m；{"trial": 2, "kind": "trace_step", "index": 24, "vz_m_s": 1.7326057221318263, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

106. 仿真 0.746s；物体中心 (0.41808, -0.00064, 1.01436) m；{"trial": 2, "kind": "trace_step", "index": 25, "vz_m_s": 1.7922163562564952, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

107. 仿真 0.750s；物体中心 (0.41707, -0.00064, 1.02208) m；{"trial": 2, "kind": "trace_step", "index": 26, "vz_m_s": 1.8517459175870126, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

108. 仿真 0.754s；物体中心 (0.41598, -0.00064, 1.03004) m；{"trial": 2, "kind": "trace_step", "index": 27, "vz_m_s": 1.9110983494568095, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

109. 仿真 0.758s；物体中心 (0.41481, -0.00064, 1.03825) m；{"trial": 2, "kind": "trace_step", "index": 28, "vz_m_s": 1.9701674693338915, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

110. 仿真 0.762s；物体中心 (0.41357, -0.00064, 1.04670) m；{"trial": 2, "kind": "trace_step", "index": 29, "vz_m_s": 2.0272624143442903, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

111. 仿真 0.767s；物体中心 (0.41212, -0.00064, 1.05449) m；{"trial": 2, "kind": "trace_step", "index": 30, "vz_m_s": 1.8689142861356713, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

112. 仿真 0.771s；物体中心 (0.41047, -0.00064, 1.06161) m；{"trial": 2, "kind": "trace_step", "index": 31, "vz_m_s": 1.7089773904539207, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

113. 仿真 0.775s；物体中心 (0.40866, -0.00064, 1.06806) m；{"trial": 2, "kind": "trace_step", "index": 32, "vz_m_s": 1.5480263826162874, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

114. 仿真 0.779s；物体中心 (0.40669, -0.00064, 1.07383) m；{"trial": 2, "kind": "trace_step", "index": 33, "vz_m_s": 1.3865696572050359, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

115. 仿真 0.783s；物体中心 (0.40458, -0.00064, 1.07894) m；{"trial": 2, "kind": "trace_step", "index": 34, "vz_m_s": 1.2250547994723178, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

116. 仿真 0.787s；物体中心 (0.40236, -0.00064, 1.08337) m；{"trial": 2, "kind": "trace_step", "index": 35, "vz_m_s": 1.063874609665528, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

117. 仿真 0.792s；物体中心 (0.40002, -0.00064, 1.08714) m；{"trial": 2, "kind": "trace_step", "index": 36, "vz_m_s": 0.9033735008830288, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

118. 仿真 0.796s；物体中心 (0.39758, -0.00064, 1.09024) m；{"trial": 2, "kind": "trace_step", "index": 37, "vz_m_s": 0.7438541652482743, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

119. 仿真 0.800s；物体中心 (0.39504, -0.00064, 1.09268) m；{"trial": 2, "kind": "trace_step", "index": 38, "vz_m_s": 0.58558434675802, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

120. 仿真 0.804s；物体中心 (0.39241, -0.00064, 1.09446) m；{"trial": 2, "kind": "trace_step", "index": 39, "vz_m_s": 0.4288032561120959, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

121. 仿真 0.808s；物体中心 (0.38970, -0.00064, 1.09568) m；{"trial": 2, "kind": "trace_step", "index": 40, "vz_m_s": 0.29224732820813604, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

122. 仿真 0.812s；物体中心 (0.38700, -0.00064, 1.09664) m；{"trial": 2, "kind": "trace_step", "index": 41, "vz_m_s": 0.22968403893816203, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

123. 仿真 0.817s；物体中心 (0.38430, -0.00064, 1.09736) m；{"trial": 2, "kind": "trace_step", "index": 42, "vz_m_s": 0.1745132711866592, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

124. 仿真 0.821s；物体中心 (0.38160, -0.00064, 1.09789) m；{"trial": 2, "kind": "trace_step", "index": 43, "vz_m_s": 0.12598848642336483, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

125. 仿真 0.825s；物体中心 (0.37890, -0.00063, 1.09824) m；{"trial": 2, "kind": "trace_step", "index": 44, "vz_m_s": 0.08340379304914602, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

126. 仿真 0.829s；物体中心 (0.37620, -0.00063, 1.09843) m；{"trial": 2, "kind": "trace_step", "index": 45, "vz_m_s": 0.0461631308374237, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

127. 仿真 0.833s；物体中心 (0.37357, -0.00063, 1.09852) m；{"trial": 2, "kind": "trace_step", "index": 46, "vz_m_s": 0.02079913985193649, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

128. 仿真 0.837s；物体中心 (0.37118, -0.00063, 1.09861) m；{"trial": 2, "kind": "trace_step", "index": 47, "vz_m_s": 0.0219223679239112, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

129. 仿真 0.842s；物体中心 (0.36903, -0.00063, 1.09870) m；{"trial": 2, "kind": "trace_step", "index": 48, "vz_m_s": 0.022294490627478566, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

130. 仿真 0.846s；物体中心 (0.36708, -0.00063, 1.09879) m；{"trial": 2, "kind": "trace_step", "index": 49, "vz_m_s": 0.022116744131858043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

131. 仿真 0.850s；物体中心 (0.36533, -0.00063, 1.09888) m；{"trial": 2, "kind": "trace_step", "index": 50, "vz_m_s": 0.021558395303166614, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

132. 仿真 0.854s；物体中心 (0.36374, -0.00063, 1.09897) m；{"trial": 2, "kind": "trace_step", "index": 51, "vz_m_s": 0.020677345948972563, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

133. 仿真 0.858s；物体中心 (0.36231, -0.00063, 1.09905) m；{"trial": 2, "kind": "trace_step", "index": 52, "vz_m_s": 0.019665270831656038, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

134. 仿真 0.862s；物体中心 (0.36103, -0.00063, 1.09913) m；{"trial": 2, "kind": "trace_step", "index": 53, "vz_m_s": 0.018554222303069304, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

135. 仿真 0.867s；物体中心 (0.35986, -0.00063, 1.09920) m；{"trial": 2, "kind": "trace_step", "index": 54, "vz_m_s": 0.017387947800578552, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

136. 仿真 0.871s；物体中心 (0.35882, -0.00063, 1.09927) m；{"trial": 2, "kind": "trace_step", "index": 55, "vz_m_s": 0.016192914462753737, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

137. 仿真 0.875s；物体中心 (0.35787, -0.00063, 1.09933) m；{"trial": 2, "kind": "trace_step", "index": 56, "vz_m_s": 0.015009129837144922, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

138. 仿真 0.879s；物体中心 (0.35702, -0.00063, 1.09939) m；{"trial": 2, "kind": "trace_step", "index": 57, "vz_m_s": 0.013868750678738193, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

139. 仿真 0.883s；物体中心 (0.35625, -0.00063, 1.09944) m；{"trial": 2, "kind": "trace_step", "index": 58, "vz_m_s": 0.012761817178448733, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

140. 仿真 0.887s；物体中心 (0.35556, -0.00063, 1.09949) m；{"trial": 2, "kind": "trace_step", "index": 59, "vz_m_s": 0.011709754693356892, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

141. 仿真 0.892s；物体中心 (0.35494, -0.00063, 1.09953) m；{"trial": 2, "kind": "trace_step", "index": 60, "vz_m_s": 0.010718189164597148, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

142. 仿真 0.896s；物体中心 (0.35438, -0.00063, 1.09957) m；{"trial": 2, "kind": "trace_step", "index": 61, "vz_m_s": 0.009789968059967177, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

143. 仿真 0.900s；物体中心 (0.35388, -0.00063, 1.09961) m；{"trial": 2, "kind": "trace_step", "index": 62, "vz_m_s": 0.008925888474757091, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

144. 仿真 0.904s；物体中心 (0.35342, -0.00063, 1.09965) m；{"trial": 2, "kind": "trace_step", "index": 63, "vz_m_s": 0.00812525159415628, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

145. 仿真 0.908s；物体中心 (0.35301, -0.00063, 1.09968) m；{"trial": 2, "kind": "trace_step", "index": 64, "vz_m_s": 0.007386291188536315, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

146. 仿真 0.912s；物体中心 (0.35265, -0.00063, 1.09970) m；{"trial": 2, "kind": "trace_step", "index": 65, "vz_m_s": 0.006706507565756595, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

147. 仿真 0.917s；物体中心 (0.35231, -0.00063, 1.09973) m；{"trial": 2, "kind": "trace_step", "index": 66, "vz_m_s": 0.006082920867305858, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

148. 仿真 0.921s；物体中心 (0.35202, -0.00063, 1.09975) m；{"trial": 2, "kind": "trace_step", "index": 67, "vz_m_s": 0.005512264075632496, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

149. 仿真 0.925s；物体中心 (0.35175, -0.00063, 1.09977) m；{"trial": 2, "kind": "trace_step", "index": 68, "vz_m_s": 0.004991128018489624, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

150. 仿真 0.929s；物体中心 (0.35151, -0.00063, 1.09979) m；{"trial": 2, "kind": "trace_step", "index": 69, "vz_m_s": 0.004516068827137017, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

151. 仿真 0.933s；物体中心 (0.35129, -0.00063, 1.09981) m；{"trial": 2, "kind": "trace_step", "index": 70, "vz_m_s": 0.004083686157987099, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

152. 仿真 0.937s；物体中心 (0.35109, -0.00063, 1.09982) m；{"trial": 2, "kind": "trace_step", "index": 71, "vz_m_s": 0.0036906787338864683, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

153. 仿真 0.942s；物体中心 (0.35092, -0.00063, 1.09984) m；{"trial": 2, "kind": "trace_step", "index": 72, "vz_m_s": 0.0033338824519965407, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

154. 仿真 0.942s；物体中心 (0.35092, -0.00063, 1.09984) m；{"trial": 2, "kind": "release_gate_blocked", "measured_max_vz_m_s": 2.0272624143442903, "reason": "measured velocity cannot support a 2m rise", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}

155. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": 3, "kind": "reset", "物体抓持": false, "实际抬升": false, "事件": []}

156. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": 3, "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

157. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": 3, "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

158. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": 3, "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

159. 仿真 0.646s；物体中心 (0.45114, -0.00063, 0.90591) m；{"trial": 3, "kind": "trace_step", "index": 1, "vz_m_s": 0.16959663633775043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

160. 仿真 0.650s；物体中心 (0.44937, -0.00063, 0.90698) m；{"trial": 3, "kind": "trace_step", "index": 2, "vz_m_s": 0.25664421153982736, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

161. 仿真 0.654s；物体中心 (0.44759, -0.00064, 0.90841) m；{"trial": 3, "kind": "trace_step", "index": 3, "vz_m_s": 0.3424130142861954, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

162. 仿真 0.658s；物体中心 (0.44581, -0.00064, 0.91018) m；{"trial": 3, "kind": "trace_step", "index": 4, "vz_m_s": 0.4270507829486157, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

163. 仿真 0.662s；物体中心 (0.44402, -0.00064, 0.91231) m；{"trial": 3, "kind": "trace_step", "index": 5, "vz_m_s": 0.5106981842298295, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

164. 仿真 0.667s；物体中心 (0.44223, -0.00064, 0.91479) m；{"trial": 3, "kind": "trace_step", "index": 6, "vz_m_s": 0.5934901686225933, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

165. 仿真 0.671s；物体中心 (0.44043, -0.00064, 0.91760) m；{"trial": 3, "kind": "trace_step", "index": 7, "vz_m_s": 0.675556997505673, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

166. 仿真 0.675s；物体中心 (0.43863, -0.00064, 0.92075) m；{"trial": 3, "kind": "trace_step", "index": 8, "vz_m_s": 0.7570249654533997, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

167. 仿真 0.679s；物体中心 (0.43682, -0.00064, 0.92425) m；{"trial": 3, "kind": "trace_step", "index": 9, "vz_m_s": 0.83801683395043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

168. 仿真 0.683s；物体中心 (0.43500, -0.00064, 0.92807) m；{"trial": 3, "kind": "trace_step", "index": 10, "vz_m_s": 0.9186519834775123, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

169. 仿真 0.687s；物体中心 (0.43330, -0.00064, 0.93215) m；{"trial": 3, "kind": "trace_step", "index": 11, "vz_m_s": 0.9787439744260048, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

170. 仿真 0.692s；物体中心 (0.43172, -0.00064, 0.93646) m；{"trial": 3, "kind": "trace_step", "index": 12, "vz_m_s": 1.0344197283689107, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

171. 仿真 0.696s；物体中心 (0.43028, -0.00064, 0.94101) m；{"trial": 3, "kind": "trace_step", "index": 13, "vz_m_s": 1.0905367232662437, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

172. 仿真 0.700s；物体中心 (0.42894, -0.00064, 0.94579) m；{"trial": 3, "kind": "trace_step", "index": 14, "vz_m_s": 1.1470940206481604, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

173. 仿真 0.704s；物体中心 (0.42771, -0.00064, 0.95080) m；{"trial": 3, "kind": "trace_step", "index": 15, "vz_m_s": 1.204086173806357, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

174. 仿真 0.708s；物体中心 (0.42657, -0.00064, 0.95606) m；{"trial": 3, "kind": "trace_step", "index": 16, "vz_m_s": 1.2615024015336285, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

175. 仿真 0.712s；物体中心 (0.42550, -0.00064, 0.96156) m；{"trial": 3, "kind": "trace_step", "index": 17, "vz_m_s": 1.3193259144602993, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

176. 仿真 0.717s；物体中心 (0.42450, -0.00064, 0.96730) m；{"trial": 3, "kind": "trace_step", "index": 18, "vz_m_s": 1.3775333618017076, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

177. 仿真 0.721s；物体中心 (0.42355, -0.00064, 0.97328) m；{"trial": 3, "kind": "trace_step", "index": 19, "vz_m_s": 1.4360943749847168, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

178. 仿真 0.725s；物体中心 (0.42263, -0.00064, 0.97951) m；{"trial": 3, "kind": "trace_step", "index": 20, "vz_m_s": 1.4949711883738097, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

179. 仿真 0.729s；物体中心 (0.42174, -0.00064, 0.98598) m；{"trial": 3, "kind": "trace_step", "index": 21, "vz_m_s": 1.5541183206748135, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

180. 仿真 0.733s；物体中心 (0.42085, -0.00064, 0.99271) m；{"trial": 3, "kind": "trace_step", "index": 22, "vz_m_s": 1.6134823088322803, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

181. 仿真 0.737s；物体中心 (0.41996, -0.00064, 0.99968) m；{"trial": 3, "kind": "trace_step", "index": 23, "vz_m_s": 1.6730014744869435, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

182. 仿真 0.742s；物体中心 (0.41904, -0.00064, 1.00690) m；{"trial": 3, "kind": "trace_step", "index": 24, "vz_m_s": 1.7326057221318263, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

183. 仿真 0.746s；物体中心 (0.41808, -0.00064, 1.01436) m；{"trial": 3, "kind": "trace_step", "index": 25, "vz_m_s": 1.7922163562564952, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

184. 仿真 0.750s；物体中心 (0.41707, -0.00064, 1.02208) m；{"trial": 3, "kind": "trace_step", "index": 26, "vz_m_s": 1.8517459175870126, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

185. 仿真 0.754s；物体中心 (0.41598, -0.00064, 1.03004) m；{"trial": 3, "kind": "trace_step", "index": 27, "vz_m_s": 1.9110983494568095, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

186. 仿真 0.758s；物体中心 (0.41481, -0.00064, 1.03825) m；{"trial": 3, "kind": "trace_step", "index": 28, "vz_m_s": 1.9701674693338915, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

187. 仿真 0.762s；物体中心 (0.41357, -0.00064, 1.04670) m；{"trial": 3, "kind": "trace_step", "index": 29, "vz_m_s": 2.0272624143442903, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

188. 仿真 0.767s；物体中心 (0.41212, -0.00064, 1.05449) m；{"trial": 3, "kind": "trace_step", "index": 30, "vz_m_s": 1.8689142861356713, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

189. 仿真 0.771s；物体中心 (0.41047, -0.00064, 1.06161) m；{"trial": 3, "kind": "trace_step", "index": 31, "vz_m_s": 1.7089773904539207, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

190. 仿真 0.775s；物体中心 (0.40866, -0.00064, 1.06806) m；{"trial": 3, "kind": "trace_step", "index": 32, "vz_m_s": 1.5480263826162874, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

191. 仿真 0.779s；物体中心 (0.40669, -0.00064, 1.07383) m；{"trial": 3, "kind": "trace_step", "index": 33, "vz_m_s": 1.3865696572050359, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

192. 仿真 0.783s；物体中心 (0.40458, -0.00064, 1.07894) m；{"trial": 3, "kind": "trace_step", "index": 34, "vz_m_s": 1.2250547994723178, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

193. 仿真 0.787s；物体中心 (0.40236, -0.00064, 1.08337) m；{"trial": 3, "kind": "trace_step", "index": 35, "vz_m_s": 1.063874609665528, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

194. 仿真 0.792s；物体中心 (0.40002, -0.00064, 1.08714) m；{"trial": 3, "kind": "trace_step", "index": 36, "vz_m_s": 0.9033735008830288, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

195. 仿真 0.796s；物体中心 (0.39758, -0.00064, 1.09024) m；{"trial": 3, "kind": "trace_step", "index": 37, "vz_m_s": 0.7438541652482743, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

196. 仿真 0.800s；物体中心 (0.39504, -0.00064, 1.09268) m；{"trial": 3, "kind": "trace_step", "index": 38, "vz_m_s": 0.58558434675802, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

197. 仿真 0.804s；物体中心 (0.39241, -0.00064, 1.09446) m；{"trial": 3, "kind": "trace_step", "index": 39, "vz_m_s": 0.4288032561120959, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

198. 仿真 0.808s；物体中心 (0.38970, -0.00064, 1.09568) m；{"trial": 3, "kind": "trace_step", "index": 40, "vz_m_s": 0.29224732820813604, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

199. 仿真 0.812s；物体中心 (0.38700, -0.00064, 1.09664) m；{"trial": 3, "kind": "trace_step", "index": 41, "vz_m_s": 0.22968403893816203, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

200. 仿真 0.817s；物体中心 (0.38430, -0.00064, 1.09736) m；{"trial": 3, "kind": "trace_step", "index": 42, "vz_m_s": 0.1745132711866592, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

201. 仿真 0.821s；物体中心 (0.38160, -0.00064, 1.09789) m；{"trial": 3, "kind": "trace_step", "index": 43, "vz_m_s": 0.12598848642336483, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

202. 仿真 0.825s；物体中心 (0.37890, -0.00063, 1.09824) m；{"trial": 3, "kind": "trace_step", "index": 44, "vz_m_s": 0.08340379304914602, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

203. 仿真 0.829s；物体中心 (0.37620, -0.00063, 1.09843) m；{"trial": 3, "kind": "trace_step", "index": 45, "vz_m_s": 0.0461631308374237, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

204. 仿真 0.833s；物体中心 (0.37357, -0.00063, 1.09852) m；{"trial": 3, "kind": "trace_step", "index": 46, "vz_m_s": 0.02079913985193649, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

205. 仿真 0.837s；物体中心 (0.37118, -0.00063, 1.09861) m；{"trial": 3, "kind": "trace_step", "index": 47, "vz_m_s": 0.0219223679239112, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

206. 仿真 0.842s；物体中心 (0.36903, -0.00063, 1.09870) m；{"trial": 3, "kind": "trace_step", "index": 48, "vz_m_s": 0.022294490627478566, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

207. 仿真 0.846s；物体中心 (0.36708, -0.00063, 1.09879) m；{"trial": 3, "kind": "trace_step", "index": 49, "vz_m_s": 0.022116744131858043, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

208. 仿真 0.850s；物体中心 (0.36533, -0.00063, 1.09888) m；{"trial": 3, "kind": "trace_step", "index": 50, "vz_m_s": 0.021558395303166614, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

209. 仿真 0.854s；物体中心 (0.36374, -0.00063, 1.09897) m；{"trial": 3, "kind": "trace_step", "index": 51, "vz_m_s": 0.020677345948972563, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

210. 仿真 0.858s；物体中心 (0.36231, -0.00063, 1.09905) m；{"trial": 3, "kind": "trace_step", "index": 52, "vz_m_s": 0.019665270831656038, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

211. 仿真 0.862s；物体中心 (0.36103, -0.00063, 1.09913) m；{"trial": 3, "kind": "trace_step", "index": 53, "vz_m_s": 0.018554222303069304, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

212. 仿真 0.867s；物体中心 (0.35986, -0.00063, 1.09920) m；{"trial": 3, "kind": "trace_step", "index": 54, "vz_m_s": 0.017387947800578552, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

213. 仿真 0.871s；物体中心 (0.35882, -0.00063, 1.09927) m；{"trial": 3, "kind": "trace_step", "index": 55, "vz_m_s": 0.016192914462753737, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

214. 仿真 0.875s；物体中心 (0.35787, -0.00063, 1.09933) m；{"trial": 3, "kind": "trace_step", "index": 56, "vz_m_s": 0.015009129837144922, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

215. 仿真 0.879s；物体中心 (0.35702, -0.00063, 1.09939) m；{"trial": 3, "kind": "trace_step", "index": 57, "vz_m_s": 0.013868750678738193, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

216. 仿真 0.883s；物体中心 (0.35625, -0.00063, 1.09944) m；{"trial": 3, "kind": "trace_step", "index": 58, "vz_m_s": 0.012761817178448733, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

217. 仿真 0.887s；物体中心 (0.35556, -0.00063, 1.09949) m；{"trial": 3, "kind": "trace_step", "index": 59, "vz_m_s": 0.011709754693356892, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

218. 仿真 0.892s；物体中心 (0.35494, -0.00063, 1.09953) m；{"trial": 3, "kind": "trace_step", "index": 60, "vz_m_s": 0.010718189164597148, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

219. 仿真 0.896s；物体中心 (0.35438, -0.00063, 1.09957) m；{"trial": 3, "kind": "trace_step", "index": 61, "vz_m_s": 0.009789968059967177, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

220. 仿真 0.900s；物体中心 (0.35388, -0.00063, 1.09961) m；{"trial": 3, "kind": "trace_step", "index": 62, "vz_m_s": 0.008925888474757091, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

221. 仿真 0.904s；物体中心 (0.35342, -0.00063, 1.09965) m；{"trial": 3, "kind": "trace_step", "index": 63, "vz_m_s": 0.00812525159415628, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

222. 仿真 0.908s；物体中心 (0.35301, -0.00063, 1.09968) m；{"trial": 3, "kind": "trace_step", "index": 64, "vz_m_s": 0.007386291188536315, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

223. 仿真 0.912s；物体中心 (0.35265, -0.00063, 1.09970) m；{"trial": 3, "kind": "trace_step", "index": 65, "vz_m_s": 0.006706507565756595, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

224. 仿真 0.917s；物体中心 (0.35231, -0.00063, 1.09973) m；{"trial": 3, "kind": "trace_step", "index": 66, "vz_m_s": 0.006082920867305858, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

225. 仿真 0.921s；物体中心 (0.35202, -0.00063, 1.09975) m；{"trial": 3, "kind": "trace_step", "index": 67, "vz_m_s": 0.005512264075632496, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

226. 仿真 0.925s；物体中心 (0.35175, -0.00063, 1.09977) m；{"trial": 3, "kind": "trace_step", "index": 68, "vz_m_s": 0.004991128018489624, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

227. 仿真 0.929s；物体中心 (0.35151, -0.00063, 1.09979) m；{"trial": 3, "kind": "trace_step", "index": 69, "vz_m_s": 0.004516068827137017, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

228. 仿真 0.933s；物体中心 (0.35129, -0.00063, 1.09981) m；{"trial": 3, "kind": "trace_step", "index": 70, "vz_m_s": 0.004083686157987099, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

229. 仿真 0.937s；物体中心 (0.35109, -0.00063, 1.09982) m；{"trial": 3, "kind": "trace_step", "index": 71, "vz_m_s": 0.0036906787338864683, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

230. 仿真 0.942s；物体中心 (0.35092, -0.00063, 1.09984) m；{"trial": 3, "kind": "trace_step", "index": 72, "vz_m_s": 0.0033338824519965407, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

231. 仿真 0.942s；物体中心 (0.35092, -0.00063, 1.09984) m；{"trial": 3, "kind": "release_gate_blocked", "measured_max_vz_m_s": 2.0272624143442903, "reason": "measured velocity cannot support a 2m rise", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}


[2026-10-19T23:19:52+08:00] 2米目标实验结束：门控验证=True；完整目标完成=False；Skill 保持 candidate。

## 2026-10-19 两米目标继续实验

用户将目标从 10 m 改为释放后相对上升至少 2 m。两米目标要求的最低竖直释放速度为 `6.264184 m/s`。参数探测得到较好组合 `(target_x=0.35 m, target_z=1.10 m, release_after_steps=72)`，最大实测速度 `2.027 m/s`，仍低于门槛。大模型建议停止解除抓持；遵照用户继续指令，完成了 3 次非释放安全门控验证，均保留抓持并安全停止。新增 `throw_2m_catch_ground_v1` Skill，状态为 `candidate`。详见 `docs/THROW_CATCH_2M_ANALYSIS.md`。


[2026-10-19T23:43:34+08:00] 开始运行 67586c959c16；输出目录 docs\throw_catch_05m_20261019。

1. 仿真 0.000s；物体中心 (—) m；{"kind": "capability_inspection", "source_sha256": "1480ab7df263cab82d7df41eb84c92a961c2b70a2d8b7bb2cb8c02f94a1f7383", "time_step_s": 0.004166666666666667, "gravity_m_s2": 9.81, "joint_velocity_limits_rad_s": [3.14, 3.14, 3.14, 3.14, 3.14, 3.14], "joint_effort_limits_Nm": [50.0, 50.0, 32.0, 32.0, 32.0, 20.0], "joint_lower_rad": [-6.28318530718, -2.059, -3.927, -6.28318530718, -1.69297, -6.28318530718], "joint_upper_rad": [6.28318530718, 2.0944, 0.19198, 6.28318530718, 3.14159265359, 6.28318530718], "cube_mass_kg": 0.1, "target_rise_m": 0.5, "required_vz_for_target_rise_m_s": 3.132091952673165, "grasp_model": "fixed constraint; robot-cube collision disabled; idealized acquisition", "ground_z_m": 0, "table_z_m": 0.7}


[2026-10-19T23:43:34+08:00] 大模型 request；request_id=33f73a0d16f94d7d9b12829650fa3ec5；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:44:03+08:00] 大模型 response；request_id=33f73a0d16f94d7d9b12829650fa3ec5；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:44:04+08:00] 大模型 parsed_output；request_id=33f73a0d16f94d7d9b12829650fa3ec5；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

2. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.4, "target_z_m": 1.6, "release_after_steps": 4}, "observed_facts": ["尚无实际试验报告", "抓取技能已验证，但夹爪闭合不等于物体抓取成功", "释放前必须测得物体向上速度至少为3.132092米每秒", "成功必须同时满足世界高度z至少0.5米和相对释放点上升至少0.5米", "接取要求物体处于下降阶段、距离不超过0.13米且相对速度不超过1米每秒", "最终必须将物体放置到地面z=0"], "hypotheses": ["较高的IK目标高度可能提供更有利的向上运动空间", "较短的释放步数可能在保持向上速度时释放物体", "当前参数能否达到释放速度阈值尚未验证", "单次试验不能证明或否定该控制器的整体可行性"], "rationale": "首次试验必须执行。选择允许范围内的较高目标高度和较短释放延迟，以优先检验释放时是否能达到规定的最小向上速度，并观察完整的抓取、抛掷、飞行、接取和落地过程。不得预先宣称成功，需依据测得的释放速度、最高高度、上升高度、下降接取条件及最终落地结果判定。", "next_requirements": ["执行一次完整试验并记录抓取是否成功", "记录释放瞬间的实际物体位置和向上速度", "记录飞行最高世界z高度及相对释放点的上升高度", "记录接取时是否满足下降、距离不超过0.13米和相对速度不超过1米每秒", "记录接取后是否成功将物体平稳放置于地面", "若失败，基于具体失败证据调整target_x_m、target_z_m或release_after_steps；若成功，仍需至少再完成两次独立完整成功试验后才能接受"]}}


[2026-10-19T23:44:05+08:00] 开始 attempt_01；参数 {"target_x_m": 0.4, "target_z_m": 1.6, "release_after_steps": 4}；故障 none。

3. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_01", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_01_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

4. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_01", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

5. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_01", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

6. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_01", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

7. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

8. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "match", "errors": [], "severity": "none"}, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

9. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

10. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_01", "kind": "upward_sweep_commanded", "object_target": [0.4, -0.0006344299818815758, 1.6], "steps": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

11. 仿真 0.646s；物体中心 (0.45176, -0.00063, 0.90540) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

12. 仿真 0.650s；物体中心 (0.45122, -0.00064, 0.90547) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

13. 仿真 0.654s；物体中心 (0.45127, -0.00064, 0.90540) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

14. 仿真 0.658s；物体中心 (0.45192, -0.00064, 0.90521) m；{"trial": "attempt_01", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

15. 仿真 0.658s；物体中心 (0.45192, -0.00064, 0.90521) m；{"trial": "attempt_01", "kind": "release_gate_blocked", "measured_max_vz_m_s": 0.04812257312860297, "required_vz_m_s": 3.132091952673165, "target_rise_m": 0.5, "reason": "measured upward speed cannot support 0.5m rise", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}

16. 仿真 1.158s；物体中心 (0.41311, -0.00064, 1.26643) m；{"trial": "attempt_01", "kind": "post_gate_safety_observation", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}


[2026-10-19T23:44:05+08:00] attempt_01 结束：{"label": "attempt_01", "failure_mode": "none", "parameters": {"target_x_m": 0.4, "target_z_m": 1.6, "release_after_steps": 4}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": false, "free_flight": false, "placement": {"passed": false, "status": "not_reached"}, "max_measured_vz_m_s": 0.04812257312860297, "release_vz_m_s": 0.04812257312860297, "flight_contact_before_catch": false, "gate_blocked": true, "physics_samples": 268, "max_joint_velocity_ratios": [0.00023204837765660306, 1.0000040175524212, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.0020906403557826516], "passed": false}


[2026-10-19T23:44:07+08:00] 大模型 request；request_id=b0f6c8abaa6c43c796eaf198d59e33fc；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:45:35+08:00] 大模型 response；request_id=b0f6c8abaa6c43c796eaf198d59e33fc；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:45:36+08:00] 大模型 parsed_output；request_id=b0f6c8abaa6c43c796eaf198d59e33fc；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

17. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.4, "target_z_m": 1.6, "release_after_steps": 120}, "observed_facts": ["先前试验已确认抓取约束建立，但释放前向上速度仅为0.048122573米每秒", "先前试验在4个物理步后释放，未达到3.132092米每秒的最低释放速度门槛", "先前试验未发生自由飞行、接取或最终放置", "先前试验的部分关节速度比接近或略高于1，说明目标运动已触及速度限制", "先前单次失败不能数学证明该控制器整体不可行", "本次仅调整允许参数release_after_steps，延长受约束运动时间，以检验能否建立足够的向上速度"], "hypotheses": ["将释放延迟从4步增加至120步可能使物体在释放时达到规定的最低向上速度", "保持较高的目标高度1.6米可能提供更长的向上运动路径", "即使释放速度达标，仍需独立测量世界最高高度是否至少0.5米以及相对释放点上升是否至少0.5米", "达到释放速度并不保证能够满足下降阶段、距离不超过0.13米和相对速度不超过1米每秒的接取条件", "本次结果仍不足以对控制器整体可行性作出最终结论"], "rationale": "上次试验的主要失败证据是释放速度远低于门槛，且释放仅发生在4个物理步后。选择保持目标位置不变并将release_after_steps增加到允许范围上限，以优先验证延长受约束运动是否能提升释放速度。必须记录真实释放位姿与速度、最高世界z、相对释放点上升高度、自由飞行状态、下降接取条件及最终地面放置结果；任何一个阶段失败都不得判为成功。", "next_requirements": ["执行本次完整试验并确认抓取是否真实成立", "记录释放瞬间物体世界位置、向上速度及是否达到3.132092米每秒", "记录自由飞行期间最高世界z高度和相对释放点的上升高度", "确认物体在接取时处于下降阶段、与接取点距离不超过0.13米且相对速度不超过1米每秒", "确认接取后物体最终稳定放置在地面z=0", "若本次失败，依据具体失败阶段和测量值继续调整允许参数或在有充分证据时停止", "只有至少3次相互独立且完成全部阶段的成功试验后才能接受"]}}


[2026-10-19T23:45:37+08:00] 开始 attempt_02；参数 {"target_x_m": 0.4, "target_z_m": 1.6, "release_after_steps": 120}；故障 low_grip_force。

18. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_02", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_02_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

19. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_02", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

20. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

21. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "close_gripper", "物体抓持": false, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact"]}

22. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "lift_object", "物体抓持": false, "实际抬升": false, "事件": []}

23. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-2", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "物体抓持": false, "实际抬升": false, "事件": []}

24. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "grasp_recovery_from_existing_skill", "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "物体抓持": false, "实际抬升": false, "事件": []}

25. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "refresh_object_pose", "物体抓持": false, "实际抬升": false, "事件": ["object_pose_refreshed"]}

26. 仿真 0.842s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "retry_grasp", "物体抓持": false, "实际抬升": false, "事件": ["grasp_retry_requested"]}

27. 仿真 1.042s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_02", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

28. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

29. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

30. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "attempt_02", "kind": "upward_sweep_commanded", "object_target": [0.4, -0.0006272425879208008, 1.6], "steps": 120, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

31. 仿真 1.246s；物体中心 (0.45150, -0.00063, 0.90547) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

32. 仿真 1.250s；物体中心 (0.45096, -0.00063, 0.90558) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

33. 仿真 1.254s；物体中心 (0.45102, -0.00063, 0.90556) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

34. 仿真 1.258s；物体中心 (0.45168, -0.00063, 0.90541) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

35. 仿真 1.262s；物体中心 (0.45268, -0.00063, 0.90504) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 5, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

36. 仿真 1.267s；物体中心 (0.45367, -0.00063, 0.90465) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 6, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

37. 仿真 1.271s；物体中心 (0.45466, -0.00063, 0.90425) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 7, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

38. 仿真 1.275s；物体中心 (0.45565, -0.00063, 0.90383) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 8, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

39. 仿真 1.279s；物体中心 (0.45662, -0.00063, 0.90340) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 9, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

40. 仿真 1.283s；物体中心 (0.45759, -0.00063, 0.90295) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 10, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

41. 仿真 1.287s；物体中心 (0.45856, -0.00063, 0.90249) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 11, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

42. 仿真 1.292s；物体中心 (0.45952, -0.00063, 0.90202) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

43. 仿真 1.296s；物体中心 (0.46047, -0.00063, 0.90154) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 13, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

44. 仿真 1.300s；物体中心 (0.46142, -0.00063, 0.90104) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 14, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

45. 仿真 1.304s；物体中心 (0.46236, -0.00063, 0.90053) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 15, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

46. 仿真 1.308s；物体中心 (0.46330, -0.00063, 0.90001) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 16, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

47. 仿真 1.312s；物体中心 (0.46422, -0.00063, 0.89948) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 17, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

48. 仿真 1.317s；物体中心 (0.46514, -0.00063, 0.89893) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 18, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

49. 仿真 1.321s；物体中心 (0.46606, -0.00063, 0.89837) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 19, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

50. 仿真 1.325s；物体中心 (0.46696, -0.00063, 0.89780) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 20, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

51. 仿真 1.329s；物体中心 (0.46786, -0.00063, 0.89722) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 21, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

52. 仿真 1.333s；物体中心 (0.46875, -0.00063, 0.89662) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 22, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

53. 仿真 1.337s；物体中心 (0.46963, -0.00063, 0.89602) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 23, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

54. 仿真 1.342s；物体中心 (0.47050, -0.00063, 0.89540) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 24, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

55. 仿真 1.346s；物体中心 (0.47137, -0.00063, 0.89477) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 25, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

56. 仿真 1.350s；物体中心 (0.47224, -0.00063, 0.89444) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 26, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

57. 仿真 1.354s；物体中心 (0.47311, -0.00063, 0.89440) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 27, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

58. 仿真 1.358s；物体中心 (0.47399, -0.00063, 0.89464) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 28, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

59. 仿真 1.362s；物体中心 (0.47487, -0.00063, 0.89516) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 29, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

60. 仿真 1.367s；物体中心 (0.47575, -0.00063, 0.89596) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 30, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

61. 仿真 1.371s；物体中心 (0.47664, -0.00063, 0.89703) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 31, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

62. 仿真 1.375s；物体中心 (0.47753, -0.00063, 0.89837) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 32, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

63. 仿真 1.379s；物体中心 (0.47842, -0.00063, 0.89997) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 33, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

64. 仿真 1.383s；物体中心 (0.47932, -0.00063, 0.90183) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 34, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

65. 仿真 1.387s；物体中心 (0.48021, -0.00063, 0.90395) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 35, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

66. 仿真 1.392s；物体中心 (0.48111, -0.00063, 0.90632) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 36, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

67. 仿真 1.396s；物体中心 (0.48201, -0.00063, 0.90894) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 37, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

68. 仿真 1.400s；物体中心 (0.48298, -0.00063, 0.91177) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 38, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

69. 仿真 1.404s；物体中心 (0.48403, -0.00063, 0.91480) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 39, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

70. 仿真 1.408s；物体中心 (0.48516, -0.00063, 0.91804) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 40, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

71. 仿真 1.412s；物体中心 (0.48636, -0.00063, 0.92147) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 41, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

72. 仿真 1.417s；物体中心 (0.48764, -0.00063, 0.92511) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 42, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

73. 仿真 1.421s；物体中心 (0.48890, -0.00063, 0.92884) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 43, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

74. 仿真 1.425s；物体中心 (0.49012, -0.00063, 0.93265) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 44, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

75. 仿真 1.429s；物体中心 (0.49129, -0.00063, 0.93654) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 45, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

76. 仿真 1.433s；物体中心 (0.49243, -0.00063, 0.94049) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 46, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

77. 仿真 1.437s；物体中心 (0.49352, -0.00063, 0.94451) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 47, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

78. 仿真 1.442s；物体中心 (0.49456, -0.00063, 0.94858) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 48, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

79. 仿真 1.446s；物体中心 (0.49555, -0.00063, 0.95270) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 49, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

80. 仿真 1.450s；物体中心 (0.49649, -0.00063, 0.95687) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 50, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

81. 仿真 1.454s；物体中心 (0.49739, -0.00063, 0.96109) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 51, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

82. 仿真 1.458s；物体中心 (0.49822, -0.00063, 0.96534) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 52, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

83. 仿真 1.462s；物体中心 (0.49901, -0.00063, 0.96963) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 53, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

84. 仿真 1.467s；物体中心 (0.49974, -0.00063, 0.97395) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 54, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

85. 仿真 1.471s；物体中心 (0.50041, -0.00063, 0.97830) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 55, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

86. 仿真 1.475s；物体中心 (0.50103, -0.00063, 0.98268) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 56, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

87. 仿真 1.479s；物体中心 (0.50159, -0.00063, 0.98709) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 57, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

88. 仿真 1.483s；物体中心 (0.50210, -0.00063, 0.99151) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 58, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

89. 仿真 1.487s；物体中心 (0.50254, -0.00063, 0.99596) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 59, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

90. 仿真 1.492s；物体中心 (0.50293, -0.00063, 1.00043) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 60, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

91. 仿真 1.496s；物体中心 (0.50326, -0.00063, 1.00491) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 61, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

92. 仿真 1.500s；物体中心 (0.50353, -0.00063, 1.00940) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 62, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

93. 仿真 1.504s；物体中心 (0.50374, -0.00063, 1.01391) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 63, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

94. 仿真 1.508s；物体中心 (0.50389, -0.00063, 1.01843) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 64, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

95. 仿真 1.512s；物体中心 (0.50399, -0.00063, 1.02295) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 65, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

96. 仿真 1.517s；物体中心 (0.50402, -0.00063, 1.02749) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 66, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

97. 仿真 1.521s；物体中心 (0.50399, -0.00063, 1.03203) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 67, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

98. 仿真 1.525s；物体中心 (0.50390, -0.00063, 1.03657) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 68, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

99. 仿真 1.529s；物体中心 (0.50376, -0.00063, 1.04112) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 69, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

100. 仿真 1.533s；物体中心 (0.50355, -0.00063, 1.04567) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 70, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

101. 仿真 1.537s；物体中心 (0.50328, -0.00063, 1.05022) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 71, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

102. 仿真 1.542s；物体中心 (0.50296, -0.00063, 1.05477) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 72, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

103. 仿真 1.546s；物体中心 (0.50257, -0.00063, 1.05932) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 73, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

104. 仿真 1.550s；物体中心 (0.50212, -0.00063, 1.06387) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 74, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

105. 仿真 1.554s；物体中心 (0.50162, -0.00063, 1.06841) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 75, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

106. 仿真 1.558s；物体中心 (0.50105, -0.00063, 1.07295) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 76, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

107. 仿真 1.562s；物体中心 (0.50043, -0.00063, 1.07749) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 77, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

108. 仿真 1.567s；物体中心 (0.49974, -0.00063, 1.08201) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 78, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

109. 仿真 1.571s；物体中心 (0.49899, -0.00063, 1.08653) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 79, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

110. 仿真 1.575s；物体中心 (0.49819, -0.00063, 1.09104) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 80, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

111. 仿真 1.579s；物体中心 (0.49733, -0.00063, 1.09554) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 81, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

112. 仿真 1.583s；物体中心 (0.49640, -0.00063, 1.10003) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 82, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

113. 仿真 1.587s；物体中心 (0.49542, -0.00063, 1.10451) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 83, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

114. 仿真 1.592s；物体中心 (0.49438, -0.00063, 1.10898) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 84, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

115. 仿真 1.596s；物体中心 (0.49328, -0.00063, 1.11343) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 85, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

116. 仿真 1.600s；物体中心 (0.49212, -0.00063, 1.11787) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 86, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

117. 仿真 1.604s；物体中心 (0.49091, -0.00063, 1.12230) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 87, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

118. 仿真 1.608s；物体中心 (0.48963, -0.00063, 1.12670) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 88, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

119. 仿真 1.612s；物体中心 (0.48830, -0.00063, 1.13110) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 89, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

120. 仿真 1.617s；物体中心 (0.48691, -0.00063, 1.13547) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 90, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

121. 仿真 1.621s；物体中心 (0.48546, -0.00063, 1.13983) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 91, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

122. 仿真 1.625s；物体中心 (0.48396, -0.00063, 1.14417) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 92, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

123. 仿真 1.629s；物体中心 (0.48240, -0.00063, 1.14849) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 93, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

124. 仿真 1.633s；物体中心 (0.48078, -0.00063, 1.15279) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 94, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

125. 仿真 1.637s；物体中心 (0.47911, -0.00063, 1.15706) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 95, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

126. 仿真 1.642s；物体中心 (0.47738, -0.00063, 1.16132) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 96, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

127. 仿真 1.646s；物体中心 (0.47560, -0.00063, 1.16555) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 97, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

128. 仿真 1.650s；物体中心 (0.47376, -0.00063, 1.16976) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 98, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

129. 仿真 1.654s；物体中心 (0.47186, -0.00063, 1.17394) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 99, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

130. 仿真 1.658s；物体中心 (0.46991, -0.00063, 1.17810) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 100, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

131. 仿真 1.662s；物体中心 (0.46791, -0.00063, 1.18224) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 101, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

132. 仿真 1.667s；物体中心 (0.46585, -0.00063, 1.18635) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 102, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

133. 仿真 1.671s；物体中心 (0.46374, -0.00063, 1.19043) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 103, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

134. 仿真 1.675s；物体中心 (0.46157, -0.00063, 1.19448) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 104, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

135. 仿真 1.679s；物体中心 (0.45936, -0.00063, 1.19850) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 105, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

136. 仿真 1.683s；物体中心 (0.45709, -0.00063, 1.20250) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 106, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

137. 仿真 1.687s；物体中心 (0.45476, -0.00063, 1.20646) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 107, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

138. 仿真 1.692s；物体中心 (0.45239, -0.00063, 1.21040) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 108, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

139. 仿真 1.696s；物体中心 (0.44996, -0.00063, 1.21430) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 109, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

140. 仿真 1.700s；物体中心 (0.44749, -0.00063, 1.21817) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 110, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

141. 仿真 1.704s；物体中心 (0.44496, -0.00063, 1.22201) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 111, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

142. 仿真 1.708s；物体中心 (0.44239, -0.00063, 1.22582) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 112, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

143. 仿真 1.712s；物体中心 (0.43976, -0.00063, 1.22959) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 113, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

144. 仿真 1.717s；物体中心 (0.43708, -0.00063, 1.23332) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 114, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

145. 仿真 1.721s；物体中心 (0.43436, -0.00063, 1.23702) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 115, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

146. 仿真 1.725s；物体中心 (0.43159, -0.00063, 1.24069) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 116, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

147. 仿真 1.729s；物体中心 (0.42877, -0.00063, 1.24432) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 117, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

148. 仿真 1.733s；物体中心 (0.42590, -0.00063, 1.24791) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 118, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

149. 仿真 1.737s；物体中心 (0.42299, -0.00063, 1.25146) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 119, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

150. 仿真 1.742s；物体中心 (0.42003, -0.00063, 1.25498) m；{"trial": "attempt_02", "kind": "sweep_step", "index": 120, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

151. 仿真 1.742s；物体中心 (0.42003, -0.00063, 1.25498) m；{"trial": "attempt_02", "kind": "release_gate_blocked", "measured_max_vz_m_s": 1.0923311784257084, "required_vz_m_s": 3.132091952673165, "target_rise_m": 0.5, "reason": "measured upward speed cannot support 0.5m rise", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}

152. 仿真 2.242s；物体中心 (0.34406, -0.00063, 1.38076) m；{"trial": "attempt_02", "kind": "post_gate_safety_observation", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}


[2026-10-19T23:45:38+08:00] attempt_02 结束：{"label": "attempt_02", "failure_mode": "low_grip_force", "parameters": {"target_x_m": 0.4, "target_z_m": 1.6, "release_after_steps": 120}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": false, "free_flight": false, "placement": {"passed": false, "status": "not_reached"}, "max_measured_vz_m_s": 1.0923311784257084, "release_vz_m_s": 1.0923311784257084, "flight_contact_before_catch": false, "gate_blocked": true, "physics_samples": 528, "max_joint_velocity_ratios": [0.00023204837765660306, 1.0000028946242665, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.0020906403557826516], "passed": false}


[2026-10-19T23:45:39+08:00] 大模型 request；request_id=a61ede8ee547488c96b49e4309540fc4；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:46:32+08:00] 大模型 response；request_id=a61ede8ee547488c96b49e4309540fc4；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:46:33+08:00] 大模型 parsed_output；request_id=a61ede8ee547488c96b49e4309540fc4；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。

153. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "proposal": {"decision": "try", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"target_x_m": 0.55, "target_z_m": 1.6, "release_after_steps": 120}, "observed_facts": ["已有两次完整试验均未通过释放速度门槛，因此尚未进入自由飞行、接取或放置阶段", "试验一在4个物理步后释放，释放时向上速度为0.048122573米每秒", "试验二在120个物理步后释放，释放时向上速度为1.092331178米每秒，仍低于3.132091952673165米每秒", "两次试验均确认抓取约束建立，但均未确认达到目标释放速度", "两次试验的部分关节速度比接近或略高于1，表明当前目标运动受到关节速度限制影响", "截至目前没有任何一次试验同时完成达标释放、世界最高z至少0.5米、相对释放点上升至少0.5米、下降接取和地面放置", "现有失败样本不足以数学证明所有允许目标参数下的控制器均不可行"], "hypotheses": ["在释放步数已达到允许上限的情况下，改变target_x_m可能改变受约束运动的逆运动学路径和速度分配，从而提高释放时向上速度", "将target_x_m调整至0.55米、保持target_z_m为1.6米，可能比此前的0.4米目标产生更有利的末端向上运动", "即使释放速度达到门槛，仍必须独立验证自由飞行最高世界z至少0.5米以及相对释放点上升至少0.5米", "达到释放速度不保证接取成功；接取仍必须满足下降阶段、距离不超过0.13米和相对速度不超过1米每秒", "接取后仍需确认物体稳定放置于地面z=0"], "rationale": "继续尝试而不接受，因为目前没有任何一次完整成功试验。release_after_steps已经达到允许上限120，试验二的释放速度仍明显低于门槛，因此本次保持最大目标高度和最大释放延迟，仅将target_x_m从0.4米调整到允许范围内的0.55米，以检验不同横向IK目标是否能改变受关节速度限制影响的向上速度。必须记录真实抓取状态、释放位姿与速度、最高世界z、相对释放点上升高度、自由飞行状态、下降接取条件以及最终地面放置结果；任一阶段失败均不得判定成功。", "next_requirements": ["执行参数为target_x_m=0.55米、target_z_m=1.6米、release_after_steps=120的完整独立试验", "确认抓取约束真实建立并记录释放瞬间物体位置和向上速度", "确认释放瞬间向上速度至少为3.132091952673165米每秒，否则记录门槛失败", "若释放成功，记录自由飞行期间最高世界z，并确认至少为0.5米", "记录相对释放点的最大上升高度，并确认至少为0.5米", "确认接取发生在下降阶段，接取距离不超过0.13米且相对速度不超过1米每秒", "确认接取后物体最终稳定放置在地面z=0", "若本次失败，根据具体失败阶段和测量值继续调整允许参数或在有充分证据时停止", "只有至少3次相互独立且完成全部阶段的成功试验后才能将decision设为accept"]}}


[2026-10-19T23:46:35+08:00] 开始 attempt_03；参数 {"target_x_m": 0.55, "target_z_m": 1.6, "release_after_steps": 120}；故障 none。

154. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_03", "kind": "scene_ready", "ground_body_id": 3, "physics_trace": "attempt_03_physics.csv", "model": "xarm6", "ground_z_m": 0, "table_z_m": 0.7, "cube_dynamics": [0.1, 0.5, [0.0001666666666666667, 0.0001666666666666667, 0.0001666666666666667], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0], 0.0, 0.0, 0.0, -1.0, -1.0, 2, 0.001], "物体抓持": false, "实际抬升": false, "事件": []}

155. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "attempt_03", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

156. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "attempt_03", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

157. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "attempt_03", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

158. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

159. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-3", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "match", "errors": [], "severity": "none"}, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

160. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

161. 仿真 0.642s；物体中心 (0.45290, -0.00063, 0.90520) m；{"trial": "attempt_03", "kind": "upward_sweep_commanded", "object_target": [0.55, -0.0006344299818815758, 1.6], "steps": 120, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

162. 仿真 0.646s；物体中心 (0.45176, -0.00063, 0.90540) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 1, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

163. 仿真 0.650s；物体中心 (0.45122, -0.00063, 0.90547) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 2, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

164. 仿真 0.654s；物体中心 (0.45127, -0.00063, 0.90540) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 3, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

165. 仿真 0.658s；物体中心 (0.45192, -0.00064, 0.90521) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 4, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

166. 仿真 0.662s；物体中心 (0.45293, -0.00064, 0.90482) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 5, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

167. 仿真 0.667s；物体中心 (0.45394, -0.00064, 0.90442) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 6, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

168. 仿真 0.671s；物体中心 (0.45495, -0.00064, 0.90401) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 7, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

169. 仿真 0.675s；物体中心 (0.45594, -0.00064, 0.90358) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 8, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

170. 仿真 0.679s；物体中心 (0.45694, -0.00064, 0.90313) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 9, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

171. 仿真 0.683s；物体中心 (0.45793, -0.00064, 0.90268) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 10, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

172. 仿真 0.687s；物体中心 (0.45891, -0.00064, 0.90221) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 11, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

173. 仿真 0.692s；物体中心 (0.45988, -0.00064, 0.90172) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 12, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

174. 仿真 0.696s；物体中心 (0.46085, -0.00064, 0.90122) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 13, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

175. 仿真 0.700s；物体中心 (0.46182, -0.00064, 0.90071) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 14, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

176. 仿真 0.704s；物体中心 (0.46277, -0.00064, 0.90019) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 15, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

177. 仿真 0.708s；物体中心 (0.46372, -0.00064, 0.89965) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 16, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

178. 仿真 0.712s；物体中心 (0.46466, -0.00064, 0.89911) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 17, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

179. 仿真 0.717s；物体中心 (0.46560, -0.00064, 0.89854) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 18, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

180. 仿真 0.721s；物体中心 (0.46653, -0.00064, 0.89797) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 19, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

181. 仿真 0.725s；物体中心 (0.46745, -0.00064, 0.89739) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 20, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

182. 仿真 0.729s；物体中心 (0.46836, -0.00064, 0.89679) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 21, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

183. 仿真 0.733s；物体中心 (0.46926, -0.00064, 0.89618) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 22, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

184. 仿真 0.737s；物体中心 (0.47016, -0.00064, 0.89556) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 23, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

185. 仿真 0.742s；物体中心 (0.47105, -0.00064, 0.89493) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 24, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

186. 仿真 0.746s；物体中心 (0.47193, -0.00064, 0.89428) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 25, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

187. 仿真 0.750s；物体中心 (0.47280, -0.00064, 0.89363) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 26, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

188. 仿真 0.754s；物体中心 (0.47366, -0.00064, 0.89296) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 27, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

189. 仿真 0.758s；物体中心 (0.47451, -0.00064, 0.89228) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 28, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

190. 仿真 0.762s；物体中心 (0.47536, -0.00064, 0.89159) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 29, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

191. 仿真 0.767s；物体中心 (0.47619, -0.00064, 0.89089) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 30, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

192. 仿真 0.771s；物体中心 (0.47702, -0.00064, 0.89018) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 31, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

193. 仿真 0.775s；物体中心 (0.47784, -0.00064, 0.88946) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 32, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

194. 仿真 0.779s；物体中心 (0.47864, -0.00064, 0.88872) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 33, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

195. 仿真 0.783s；物体中心 (0.47944, -0.00064, 0.88798) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 34, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

196. 仿真 0.787s；物体中心 (0.48023, -0.00064, 0.88723) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 35, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

197. 仿真 0.792s；物体中心 (0.48101, -0.00064, 0.88646) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 36, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

198. 仿真 0.796s；物体中心 (0.48178, -0.00064, 0.88569) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 37, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

199. 仿真 0.800s；物体中心 (0.48256, -0.00064, 0.88502) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 38, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

200. 仿真 0.804s；物体中心 (0.48337, -0.00064, 0.88462) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 39, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

201. 仿真 0.808s；物体中心 (0.48422, -0.00064, 0.88449) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 40, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

202. 仿真 0.812s；物体中心 (0.48510, -0.00064, 0.88461) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 41, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

203. 仿真 0.817s；物体中心 (0.48602, -0.00064, 0.88499) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 42, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

204. 仿真 0.821s；物体中心 (0.48697, -0.00064, 0.88563) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 43, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

205. 仿真 0.825s；物体中心 (0.48796, -0.00064, 0.88651) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 44, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

206. 仿真 0.829s；物体中心 (0.48898, -0.00064, 0.88763) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 45, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

207. 仿真 0.833s；物体中心 (0.49004, -0.00064, 0.88899) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 46, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

208. 仿真 0.837s；物体中心 (0.49113, -0.00064, 0.89059) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 47, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

209. 仿真 0.842s；物体中心 (0.49226, -0.00064, 0.89243) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 48, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

210. 仿真 0.846s；物体中心 (0.49341, -0.00064, 0.89450) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 49, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

211. 仿真 0.850s；物体中心 (0.49460, -0.00064, 0.89679) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 50, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

212. 仿真 0.854s；物体中心 (0.49581, -0.00064, 0.89931) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 51, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

213. 仿真 0.858s；物体中心 (0.49706, -0.00064, 0.90206) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 52, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

214. 仿真 0.862s；物体中心 (0.49833, -0.00064, 0.90502) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 53, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

215. 仿真 0.867s；物体中心 (0.49961, -0.00064, 0.90821) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 54, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

216. 仿真 0.871s；物体中心 (0.50088, -0.00064, 0.91160) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 55, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

217. 仿真 0.875s；物体中心 (0.50214, -0.00064, 0.91520) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 56, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

218. 仿真 0.879s；物体中心 (0.50338, -0.00064, 0.91901) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 57, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

219. 仿真 0.883s；物体中心 (0.50460, -0.00064, 0.92302) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 58, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

220. 仿真 0.887s；物体中心 (0.50579, -0.00064, 0.92722) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 59, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

221. 仿真 0.892s；物体中心 (0.50693, -0.00064, 0.93163) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 60, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

222. 仿真 0.896s；物体中心 (0.50804, -0.00064, 0.93622) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 61, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

223. 仿真 0.900s；物体中心 (0.50909, -0.00064, 0.94096) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 62, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

224. 仿真 0.904s；物体中心 (0.51007, -0.00064, 0.94568) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 63, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

225. 仿真 0.908s；物体中心 (0.51099, -0.00064, 0.95039) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 64, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

226. 仿真 0.912s；物体中心 (0.51184, -0.00064, 0.95510) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 65, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

227. 仿真 0.917s；物体中心 (0.51263, -0.00064, 0.95979) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 66, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

228. 仿真 0.921s；物体中心 (0.51335, -0.00064, 0.96448) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 67, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

229. 仿真 0.925s；物体中心 (0.51401, -0.00064, 0.96917) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 68, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

230. 仿真 0.929s；物体中心 (0.51461, -0.00064, 0.97385) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 69, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

231. 仿真 0.933s；物体中心 (0.51514, -0.00064, 0.97853) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 70, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

232. 仿真 0.937s；物体中心 (0.51562, -0.00064, 0.98320) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 71, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

233. 仿真 0.942s；物体中心 (0.51603, -0.00064, 0.98787) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 72, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

234. 仿真 0.946s；物体中心 (0.51638, -0.00064, 0.99253) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 73, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

235. 仿真 0.950s；物体中心 (0.51666, -0.00064, 0.99719) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 74, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

236. 仿真 0.954s；物体中心 (0.51689, -0.00064, 1.00185) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 75, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

237. 仿真 0.958s；物体中心 (0.51706, -0.00064, 1.00650) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 76, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

238. 仿真 0.962s；物体中心 (0.51716, -0.00064, 1.01115) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 77, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

239. 仿真 0.967s；物体中心 (0.51720, -0.00064, 1.01579) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 78, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

240. 仿真 0.971s；物体中心 (0.51719, -0.00064, 1.02043) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 79, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

241. 仿真 0.975s；物体中心 (0.51711, -0.00064, 1.02507) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 80, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

242. 仿真 0.979s；物体中心 (0.51697, -0.00064, 1.02970) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 81, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

243. 仿真 0.983s；物体中心 (0.51678, -0.00064, 1.03432) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 82, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

244. 仿真 0.987s；物体中心 (0.51652, -0.00064, 1.03894) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 83, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

245. 仿真 0.992s；物体中心 (0.51620, -0.00064, 1.04355) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 84, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

246. 仿真 0.996s；物体中心 (0.51582, -0.00064, 1.04815) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 85, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

247. 仿真 1.000s；物体中心 (0.51539, -0.00064, 1.05275) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 86, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

248. 仿真 1.004s；物体中心 (0.51489, -0.00064, 1.05734) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 87, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

249. 仿真 1.008s；物体中心 (0.51433, -0.00064, 1.06192) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 88, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

250. 仿真 1.012s；物体中心 (0.51371, -0.00064, 1.06649) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 89, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

251. 仿真 1.017s；物体中心 (0.51304, -0.00064, 1.07105) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 90, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

252. 仿真 1.021s；物体中心 (0.51230, -0.00064, 1.07559) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 91, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

253. 仿真 1.025s；物体中心 (0.51151, -0.00064, 1.08013) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 92, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

254. 仿真 1.029s；物体中心 (0.51065, -0.00064, 1.08466) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 93, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

255. 仿真 1.033s；物体中心 (0.50974, -0.00064, 1.08917) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 94, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

256. 仿真 1.037s；物体中心 (0.50877, -0.00064, 1.09367) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 95, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

257. 仿真 1.042s；物体中心 (0.50774, -0.00064, 1.09816) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 96, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

258. 仿真 1.046s；物体中心 (0.50665, -0.00064, 1.10263) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 97, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

259. 仿真 1.050s；物体中心 (0.50550, -0.00064, 1.10709) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 98, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

260. 仿真 1.054s；物体中心 (0.50430, -0.00064, 1.11153) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 99, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

261. 仿真 1.058s；物体中心 (0.50303, -0.00064, 1.11595) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 100, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

262. 仿真 1.062s；物体中心 (0.50171, -0.00064, 1.12036) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 101, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

263. 仿真 1.067s；物体中心 (0.50033, -0.00064, 1.12475) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 102, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

264. 仿真 1.071s；物体中心 (0.49890, -0.00064, 1.12912) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 103, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

265. 仿真 1.075s；物体中心 (0.49741, -0.00064, 1.13347) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 104, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

266. 仿真 1.079s；物体中心 (0.49586, -0.00064, 1.13780) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 105, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

267. 仿真 1.083s；物体中心 (0.49425, -0.00064, 1.14211) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 106, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

268. 仿真 1.087s；物体中心 (0.49259, -0.00064, 1.14640) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 107, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

269. 仿真 1.092s；物体中心 (0.49087, -0.00064, 1.15066) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 108, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

270. 仿真 1.096s；物体中心 (0.48910, -0.00064, 1.15490) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 109, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

271. 仿真 1.100s；物体中心 (0.48742, -0.00064, 1.15909) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 110, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

272. 仿真 1.104s；物体中心 (0.48596, -0.00064, 1.16318) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 111, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

273. 仿真 1.108s；物体中心 (0.48468, -0.00064, 1.16720) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 112, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

274. 仿真 1.112s；物体中心 (0.48356, -0.00064, 1.17114) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 113, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

275. 仿真 1.117s；物体中心 (0.48258, -0.00064, 1.17502) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 114, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

276. 仿真 1.121s；物体中心 (0.48172, -0.00064, 1.17884) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 115, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

277. 仿真 1.125s；物体中心 (0.48097, -0.00064, 1.18260) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 116, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

278. 仿真 1.129s；物体中心 (0.48031, -0.00064, 1.18632) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 117, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

279. 仿真 1.133s；物体中心 (0.47973, -0.00064, 1.18999) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 118, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

280. 仿真 1.137s；物体中心 (0.47922, -0.00064, 1.19363) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 119, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

281. 仿真 1.142s；物体中心 (0.47876, -0.00064, 1.19723) m；{"trial": "attempt_03", "kind": "sweep_step", "index": 120, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

282. 仿真 1.142s；物体中心 (0.47876, -0.00064, 1.19723) m；{"trial": "attempt_03", "kind": "release_gate_blocked", "measured_max_vz_m_s": 1.1358311036051483, "required_vz_m_s": 3.132091952673165, "target_rise_m": 0.5, "reason": "measured upward speed cannot support 0.5m rise", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}

283. 仿真 1.642s；物体中心 (0.44331, -0.00063, 1.35071) m；{"trial": "attempt_03", "kind": "post_gate_safety_observation", "物体抓持": true, "实际抬升": true, "事件": ["safety_stop"]}


[2026-10-19T23:46:35+08:00] attempt_03 结束：{"label": "attempt_03", "failure_mode": "none", "parameters": {"target_x_m": 0.55, "target_z_m": 1.6, "release_after_steps": 120}, "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": false, "free_flight": false, "placement": {"passed": false, "status": "not_reached"}, "max_measured_vz_m_s": 1.1358311036051483, "release_vz_m_s": 1.1358311036051483, "flight_contact_before_catch": false, "gate_blocked": true, "physics_samples": 384, "max_joint_velocity_ratios": [0.00023204837765660306, 1.0000043531560845, 1.0001727100481232, 0.0013030638137488748, 1.0048781476881663, 0.0020906403557826516], "passed": false}


[2026-10-19T23:46:37+08:00] 大模型 request；request_id=110ca5636a0542a5a6eac9a7bea7b120；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:47:33+08:00] 大模型 response；request_id=110ca5636a0542a5a6eac9a7bea7b120；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。


[2026-10-19T23:47:34+08:00] 大模型 parsed_output；request_id=110ca5636a0542a5a6eac9a7bea7b120；完整内容已写入 docs\THROW_CATCH_LLM_CALLS.md。
