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
