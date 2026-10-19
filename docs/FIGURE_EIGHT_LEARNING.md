# 持物竖直画 8 字：学习与执行记录

日期：2026-10-19（Asia/Shanghai）。任务：复用已验证的抓取失败恢复 Skill，抓起方块，在空中竖直画一个完整的 8 字，随后放回桌面。

## 记录 01：检查与开始

- 已检查当前代码：xArm6 已能接近、闭合、检测抬升、失败后重新定位并重抓、放下物体；尚无持物轨迹动作。
- 已有经验：`grasp_without_lift_v1`，前次 20 次固定低力度仿真验证通过，经验为“闭合不代表抓牢；确认实际抬升再搬运”。来源为 `artifacts/verification_20261019/skills.json`。
- 当前工作区有上次任务留下的 `run.cmd`、`run.ps1`、`README.md` 修改。先保存为独立 Git 提交，再实现本次任务。
- 将“竖直 8 字”定义为 Y–Z 竖直平面中的上下两环：横向位移与 `sin(2t)` 成正比，高度位移与 `sin(t)` 成正比，X 保持不变；物体中心为轨迹验收对象。
- 学习采用明确的参数候选试验、实际轨迹反馈、重复验证和持久化复用。不会把手写轨迹公式称为自主发现的新运动规律。
- 每个任务动作、每个轨迹路点及其实际位姿、误差、抓取状态和事件会立即追加到本文档及 JSONL，运行结束后补充评估。

## 验收要求

1. 读取并应用已有抓取 Skill，确认实际抬升事件后才开始画 8。
2. 物体全程被抓持，轨迹位于桌面之上，实际物体轨迹覆盖上下两个环并回到交叉点附近。
3. 按实际物体位置检查每个路点的跟踪误差；失败候选必须保留原因和全部已执行步骤。
4. 将成功参数作为候选新 Skill 保存，经过独立重复验证后才能标记 `verified`。
5. 新环境重新加载新 Skill，完成抓取、完整 8 字、放下和稳定性检查。

后续记录在开发和运行过程中追加；时间使用 Asia/Shanghai，轨迹时刻为仿真秒。

## 记录 02：接入大模型与逐步记录

- 用户指定本机 CC Switch `127.0.0.1:15723`，已确认端口正在监听。使用项目可配置模型 ID，默认 `gpt-6.1-sol`；实际模型身份以服务响应为准。
- 已增加独立学习入口 `robotmp.figure_eight`：模型提出图形幅度、抬高量、路点数与步进时长；本地严格校验参数后执行预定义轨迹，反馈实际误差，再请模型接受或修改候选。
- 新增 `after_lift` 扩展点，复用原抓取、低力度诊断、重抓和放下流程；新动作只有在实际抬升之后执行。
- 以物体中心真实位置检查双环面积、闭合、交叉点、平面偏差、跟踪误差；逐个物理步检查持物状态和离桌净空，最后检查放下位置、速度和稳定性。
- 已有 Skill 的识别改为稳定的 `skill_id`，避免模型给 Skill 起不同名称后丢失预测防护。
- 每次模型请求、完整原始响应、解析结果及错误均立即写入 `docs/FIGURE_EIGHT_LLM_CALLS.md` 和输出目录中的 JSONL；不截断响应，不记录认证头。每个任务动作和每个轨迹路点立即追加到本记录。
- 先运行离线几何与物理测试，再进行实际模型学习；不把测试替身的响应当作真实模型调用。

## 记录 03：实现阶段验证

- `run.cmd -m unittest discover -s tests -v`：19 项全部通过，无跳过，包含 5 项新增测试。
- 离线端到端测试确认：复用前置 Skill、低力度重抓、65 个轨迹路点、两个相反方向的环、放下并稳定。测试参数下最大物体跟踪误差约 0.0913 mm；这只是控制原语测试，不计入模型新 Skill 的学习证据。
- 拒绝未抓持时开始画 8；拒绝非有限值、越界参数、横向 8 字、轨迹未完成和退化为直线的结果。
- 下一阶段实际调用 CC Switch；每次调用完整输入输出将随调用立即保存。


[2026-10-19T21:36:55+08:00] 开始运行 d3f92a3928fd；输出目录 artifacts\figure_eight_20261019。


[2026-10-19T21:36:55+08:00] 载入已验证前置 Skill grasp_without_lift_v1，来源 artifacts\verification_20261019\skills.json，验证次数 20。


[2026-10-19T21:36:55+08:00] 大模型 request；request_id=fbfe59d56585478696ac19f17150ca58；完整内容已写入 docs\FIGURE_EIGHT_LLM_CALLS.md。


[2026-10-19T21:37:19+08:00] 大模型 response；request_id=fbfe59d56585478696ac19f17150ca58；完整内容已写入 docs\FIGURE_EIGHT_LLM_CALLS.md。


[2026-10-19T21:37:19+08:00] 大模型 parsed_output；request_id=fbfe59d56585478696ac19f17150ca58；完整内容已写入 docs\FIGURE_EIGHT_LLM_CALLS.md。

1. 仿真 0.000s；物体中心 (—) m；{"kind": "model_proposal_validated", "attempt": 1, "proposal": {"decision": "try", "name": "方块竖直八字搬运与放置", "description": "用于本地 PyBullet 仿真的可复用组合技能：调用已验证技能 grasp_without_lift_v1 检查抓取未抬起的情况，仅在确认方块已被稳定抬起后，使用预定义竖直八字原语运动，随后执行放置。原语保持物体中心的 x 坐标不变，在竖直平面内完成闭合八字；不生成任意航点或底层控制指令。", "prerequisite_skill_ids": ["grasp_without_lift_v1"], "parameters": {"half_width_m": 0.05, "half_height_m": 0.08, "center_raise_m": 0.1, "samples": 72, "steps_per_waypoint": 80}, "observed_facts": ["当前没有实际试验报告，因此本次仅提出试运行，不判定通过。", "已提供技能 grasp_without_lift_v1 的验证记录为20次，误报成功率为0，恢复成功率为1；其作用是识别和处理抓取后未抬起，不能据此证明本组合技能已成功。", "夹爪闭合不代表抓取成功；运输前必须有实际抬起证据。", "给定初始抬起物体中心约为[0.4526, 0, 0.9052]米，桌面高度为0.70米，方块半尺寸为0.05米。"], "hypotheses": ["将八字中心相对初始抬起中心升高0.10米，并采用水平半宽0.05米、竖直半高0.08米，预计可形成竖直方向更长的两个相反有向面积的叶瓣。", "上述参数满足竖直半高至少为水平半宽的1.3倍，以及中心抬升量不小于竖直半高的约束。", "在方块保持直立的假设下，八字段标称最低底面高度约为0.8752米，相对桌面净空约为0.1752米；这只是几何估计，仍须连续测量实际净空。", "72个采样点和每航点80步可能有利于平稳跟踪，但跟踪精度、抓持保持及放置稳定性仍需试验确认。"], "rationale": "首次采用范围内的中等幅度和较充分的执行步数，优先检验组合流程而非追求速度。先确认抬起，再由预定义原语完成中心抬升和完整八字，最后放置到试验指定目标。通过条件必须全部满足：物体中心跟踪误差不超过0.02米，交叉、闭合及平面误差各不超过0.015米，两个叶瓣有向面积符号相反，全过程底部净空连续不小于0.035米且保持抓持，放置误差不超过0.025米，放置后漂移不超过0.003米。只有实际试验报告确认这些条件全部通过，后续才能接受该技能；本提案不涉及控制器自主学习。", "recovery": ["若没有可靠抬起证据，禁止进入八字或运输阶段；调用已有技能的恢复流程，停止运输、刷新物体位姿，并在安全条件下重试抓取。", "若实际跟踪、交叉、闭合或平面误差超限，停止后续八字执行并安全放置；记录各项实测误差，再在允许范围内调整采样数、每航点步数或幅度后重新试验。", "若连续净空不足或抓持丢失，立即中止该试验并执行仿真中的安全停止与物体状态检查；依据实测最低净空和姿态，在约束内调整中心抬升量或竖直半高。", "若放置误差或漂移超限，不接受本技能；复核目标位姿、释放前稳定性与释放后测量结果，再重新验证完整流程。"]}}


[2026-10-19T21:37:19+08:00] 开始 learning_1，故障=low_grip_force，参数={"half_width_m": 0.05, "half_height_m": 0.08, "center_raise_m": 0.1, "samples": 72, "steps_per_waypoint": 80}

2. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "learning_1", "kind": "reset", "prediction": null, "comparison": null, "物体抓持": false, "实际抬升": false, "事件": []}

3. 仿真 0.042s；物体中心 (0.45000, -0.00000, 0.74991) m；{"trial": "learning_1", "kind": "retrieve", "prediction": null, "comparison": null, "skills": [{"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}], "物体抓持": false, "实际抬升": false, "事件": []}

4. 仿真 0.242s；物体中心 (0.45000, 0.00000, 0.74999) m；{"trial": "learning_1", "kind": "action", "prediction": null, "comparison": null, "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

5. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "action", "prediction": null, "comparison": null, "action": "close_gripper", "物体抓持": false, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact"]}

6. 仿真 0.442s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "prediction", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": null, "物体抓持": false, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact"]}

7. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "action", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": null, "action": "lift_object", "物体抓持": false, "实际抬升": false, "事件": []}

8. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "comparison", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "物体抓持": false, "实际抬升": false, "事件": []}


[2026-10-19T21:37:19+08:00] 大模型 request；request_id=04ead49822d54e2681534b1e22a0ec57；完整内容已写入 docs\FIGURE_EIGHT_LLM_CALLS.md。


[2026-10-19T21:37:31+08:00] 大模型 response；request_id=04ead49822d54e2681534b1e22a0ec57；完整内容已写入 docs\FIGURE_EIGHT_LLM_CALLS.md。


[2026-10-19T21:37:31+08:00] 大模型 parsed_output；request_id=04ead49822d54e2681534b1e22a0ec57；完整内容已写入 docs\FIGURE_EIGHT_LLM_CALLS.md。

9. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "diagnosis", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift_candidate_v2", "status": "candidate", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["A lift prediction requires positive object-lift evidence.", "The gripper is closed while the object is observed as not grasped and not lifted.", "The expected object_lift_detected event is absent."], "facts": ["Prediction pred-1 expected the cube to be lifted.", "The observation reports phase lift.", "The cube is visible, with grasped=false and lifted=false.", "Object observation confidence is 0.95.", "The gripper is closed and reported gripper force is 0.4.", "No events were reported.", "The comparison reports a medium-severity deviation.", "Skill grasp_without_lift_v1 was applied.", "The observation does not establish that a lift window elapsed."], "hypotheses": ["The grasp may have missed the cube because of misalignment.", "The gripper may have closed without securing the cube.", "Grip effectiveness may have been insufficient; the force reading alone does not establish this.", "The cube may have shifted before grasping; no displacement is confirmed."], "prediction_correction": ["Mark pred-1's expected lift outcome as unconfirmed and contradicted by the current object state.", "Do not infer grasp success from gripper closure or end-effector height.", "Do not infer object displacement from a single position observation.", "Require positive object-lift evidence before entering transport.", "Treat this skill revision as a candidate, not as validated by prior-version results.", "do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["Withhold transport until positive object-lift evidence is established.", "Assess the current scene for collision, contact, and object-stability risks.", "Refresh the cube pose and verify its support state.", "Reassess grasp suitability before considering another attempt.", "Retry grasping only if the scene and grasp plan are assessed as safe.", "Verify secure grasp and positive object lift before authorizing transport.", "Request assistance if safe recovery or reliable lift verification is unavailable."], "validation_trials": 0, "false_success_rate": null, "recovery_success_rate": null, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "source": "OpenAICompatibleDiagnoser", "物体抓持": false, "实际抬升": false, "事件": []}

10. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "candidate", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift_candidate_v2", "status": "candidate", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["A lift prediction requires positive object-lift evidence.", "The gripper is closed while the object is observed as not grasped and not lifted.", "The expected object_lift_detected event is absent."], "facts": ["Prediction pred-1 expected the cube to be lifted.", "The observation reports phase lift.", "The cube is visible, with grasped=false and lifted=false.", "Object observation confidence is 0.95.", "The gripper is closed and reported gripper force is 0.4.", "No events were reported.", "The comparison reports a medium-severity deviation.", "Skill grasp_without_lift_v1 was applied.", "The observation does not establish that a lift window elapsed."], "hypotheses": ["The grasp may have missed the cube because of misalignment.", "The gripper may have closed without securing the cube.", "Grip effectiveness may have been insufficient; the force reading alone does not establish this.", "The cube may have shifted before grasping; no displacement is confirmed."], "prediction_correction": ["Mark pred-1's expected lift outcome as unconfirmed and contradicted by the current object state.", "Do not infer grasp success from gripper closure or end-effector height.", "Do not infer object displacement from a single position observation.", "Require positive object-lift evidence before entering transport.", "Treat this skill revision as a candidate, not as validated by prior-version results.", "do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["Withhold transport until positive object-lift evidence is established.", "Assess the current scene for collision, contact, and object-stability risks.", "Refresh the cube pose and verify its support state.", "Reassess grasp suitability before considering another attempt.", "Retry grasping only if the scene and grasp plan are assessed as safe.", "Verify secure grasp and positive object lift before authorizing transport.", "Request assistance if safe recovery or reliable lift verification is unavailable."], "validation_trials": 0, "false_success_rate": null, "recovery_success_rate": null, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

11. 仿真 0.642s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "action", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "action": "refresh_object_pose", "物体抓持": false, "实际抬升": false, "事件": ["object_pose_refreshed"]}

12. 仿真 0.842s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "action", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "action": "retry_grasp", "物体抓持": false, "实际抬升": false, "事件": ["grasp_retry_requested"]}

13. 仿真 1.042s；物体中心 (0.45000, 0.00001, 0.74999) m；{"trial": "learning_1", "kind": "action", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

14. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "learning_1", "kind": "action", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

15. 仿真 1.242s；物体中心 (0.45265, -0.00063, 0.90524) m；{"trial": "learning_1", "kind": "lift_gate_passed", "prerequisite_skill_id": "grasp_without_lift_v1", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

16. 仿真 1.742s；物体中心 (0.45201, -0.00063, 1.00523) m；{"trial": "learning_1", "kind": "move_to_crossing", "target": [0.45264591498190104, -0.0006272425879208008, 1.0052366031601594], "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

17. 仿真 2.075s；物体中心 (0.45264, -0.00063, 1.00523) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 0, "target": [0.45264591498190104, -0.0006272425879208008, 1.0052366031601594], "tracking_error_m": 9.825228975071803e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

18. 仿真 2.408s；物体中心 (0.45264, 0.00805, 1.01220) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 1, "target": [0.45264591498190104, 0.008055166295425716, 1.012209062579972], "tracking_error_m": 1.1722698804804077e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

19. 仿真 2.742s；物体中心 (0.45264, 0.01647, 1.01912) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 2, "target": [0.45264591498190104, 0.016473764578362634, 1.0191284573735138], "tracking_error_m": 1.14159202509719e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

20. 仿真 3.075s；物体中心 (0.45264, 0.02437, 1.02593) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 3, "target": [0.45264591498190104, 0.024372757412079196, 1.025942126768361], "tracking_error_m": 1.1833336309672512e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

21. 仿真 3.408s；物体中心 (0.45264, 0.03151, 1.03259) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 4, "target": [0.45264591498190104, 0.03151213789640616, 1.032598214626213], "tracking_error_m": 1.1983316368247924e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

22. 仿真 3.742s；物体中心 (0.45264, 0.03767, 1.03904) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 5, "target": [0.45264591498190104, 0.0376749795680281, 1.0390460640994152], "tracking_error_m": 1.2019591061309376e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

23. 仿真 4.075s；物体中心 (0.45264, 0.04267, 1.04523) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 6, "target": [0.45264591498190104, 0.04267402760130113, 1.0452366031601594], "tracking_error_m": 1.1825229503351622e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

24. 仿真 4.408s；物体中心 (0.45264, 0.04636, 1.05111) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 7, "target": [0.45264591498190104, 0.04635738845137462, 1.051122718068243], "tracking_error_m": 1.1955388824130604e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

25. 仿真 4.742s；物体中心 (0.45264, 0.04861, 1.05665) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 8, "target": [0.45264591498190104, 0.0486131450626896, 1.0566596119350826], "tracking_error_m": 1.1957418835597624e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

26. 仿真 5.075s；物体中心 (0.45264, 0.04937, 1.06180) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 9, "target": [0.45264591498190104, 0.0493727574120792, 1.0618051456550832], "tracking_error_m": 1.1550893406183224e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

27. 仿真 5.408s；物体中心 (0.45264, 0.04861, 1.06651) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 10, "target": [0.45264591498190104, 0.0486131450626896, 1.0665201586096775], "tracking_error_m": 1.1597359135804862e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

28. 仿真 5.742s；物体中心 (0.45264, 0.04636, 1.07076) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 11, "target": [0.45264591498190104, 0.046357388451374625, 1.0707687667032788], "tracking_error_m": 1.1958353455549596e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

29. 仿真 6.075s；物体中心 (0.45264, 0.04267, 1.07451) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 12, "target": [0.45264591498190104, 0.04267402760130114, 1.0745186354629146], "tracking_error_m": 1.1412571619188529e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

30. 仿真 6.408s；物体中心 (0.45264, 0.03768, 1.07773) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 13, "target": [0.45264591498190104, 0.0376749795680281, 1.0777412261230914], "tracking_error_m": 1.0821092255073984e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

31. 仿真 6.742s；物体中心 (0.45264, 0.03151, 1.08040) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 14, "target": [0.45264591498190104, 0.031512137896406174, 1.0804120128230321], "tracking_error_m": 1.1188722986544236e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

32. 仿真 7.075s；物体中心 (0.45264, 0.02438, 1.08250) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 15, "target": [0.45264591498190104, 0.024372757412079216, 1.0825106692632849], "tracking_error_m": 1.0981201972020882e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

33. 仿真 7.408s；物体中心 (0.45264, 0.01648, 1.08401) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 16, "target": [0.45264591498190104, 0.01647376457836264, 1.084021223401136], "tracking_error_m": 1.1311737799280377e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

34. 仿真 7.742s；物体中心 (0.45264, 0.00806, 1.08493) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 17, "target": [0.45264591498190104, 0.008055166295425714, 1.084932179007499], "tracking_error_m": 1.1318139864966431e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

35. 仿真 8.075s；物体中心 (0.45264, -0.00062, 1.08523) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 18, "target": [0.45264591498190104, -0.0006272425879207947, 1.0852366031601595], "tracking_error_m": 1.0413441285878392e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

36. 仿真 8.408s；物体中心 (0.45265, -0.00930, 1.08493) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 19, "target": [0.45264591498190104, -0.009309651471267302, 1.084932179007499], "tracking_error_m": 1.0559154254763748e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

37. 仿真 8.742s；物体中心 (0.45265, -0.01772, 1.08402) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 20, "target": [0.45264591498190104, -0.017728249754204235, 1.084021223401136], "tracking_error_m": 9.336175789837343e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

38. 仿真 9.075s；物体中心 (0.45265, -0.02562, 1.08252) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 21, "target": [0.45264591498190104, -0.02562724258792081, 1.0825106692632849], "tracking_error_m": 9.446146197652011e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

39. 仿真 9.408s；物体中心 (0.45265, -0.03276, 1.08042) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 22, "target": [0.45264591498190104, -0.03276662307224775, 1.0804120128230321], "tracking_error_m": 8.8119922385219e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

40. 仿真 9.742s；物体中心 (0.45265, -0.03893, 1.07775) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 23, "target": [0.45264591498190104, -0.0389294647438697, 1.0777412261230914], "tracking_error_m": 8.3751925769035e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

41. 仿真 10.075s；物体中心 (0.45265, -0.04393, 1.07452) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 24, "target": [0.45264591498190104, -0.04392851277714273, 1.0745186354629146], "tracking_error_m": 8.296758761531722e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

42. 仿真 10.408s；物体中心 (0.45265, -0.04761, 1.07077) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 25, "target": [0.45264591498190104, -0.04761187362721623, 1.0707687667032788], "tracking_error_m": 8.58921841059014e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

43. 仿真 10.742s；物体中心 (0.45265, -0.04987, 1.06653) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 26, "target": [0.45264591498190104, -0.049867630238531205, 1.0665201586096775], "tracking_error_m": 8.552919869286601e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

44. 仿真 11.075s；物体中心 (0.45265, -0.05063, 1.06181) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 27, "target": [0.45264591498190104, -0.050627242587920805, 1.0618051456550832], "tracking_error_m": 8.886087807579407e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

45. 仿真 11.408s；物体中心 (0.45265, -0.04987, 1.05667) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 28, "target": [0.45264591498190104, -0.04986763023853121, 1.0566596119350826], "tracking_error_m": 8.903830642524458e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

46. 仿真 11.742s；物体中心 (0.45265, -0.04761, 1.05113) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 29, "target": [0.45264591498190104, -0.04761187362721622, 1.051122718068243], "tracking_error_m": 9.33375511517905e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

47. 仿真 12.075s；物体中心 (0.45265, -0.04393, 1.04524) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 30, "target": [0.45264591498190104, -0.043928512777142756, 1.0452366031601594], "tracking_error_m": 9.491967114500645e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

48. 仿真 12.408s；物体中心 (0.45265, -0.03893, 1.03905) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 31, "target": [0.45264591498190104, -0.03892946474386971, 1.0390460640994152], "tracking_error_m": 9.43167635753271e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

49. 仿真 12.742s；物体中心 (0.45265, -0.03277, 1.03260) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 32, "target": [0.45264591498190104, -0.032766623072247786, 1.032598214626213], "tracking_error_m": 9.19036646058306e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

50. 仿真 13.075s；物体中心 (0.45265, -0.02563, 1.02595) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 33, "target": [0.45264591498190104, -0.025627242587920786, 1.025942126768361], "tracking_error_m": 9.609982218292752e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

51. 仿真 13.408s；物体中心 (0.45265, -0.01773, 1.01913) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 34, "target": [0.45264591498190104, -0.017728249754204232, 1.0191284573735138], "tracking_error_m": 9.529714812389023e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

52. 仿真 13.742s；物体中心 (0.45265, -0.00931, 1.01221) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 35, "target": [0.45264591498190104, -0.00930965147126732, 1.012209062579972], "tracking_error_m": 9.24346807634351e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

53. 仿真 14.075s；物体中心 (0.45265, -0.00063, 1.00524) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 36, "target": [0.45264591498190104, -0.000627242587920813, 1.0052366031601594], "tracking_error_m": 9.410107499424716e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

54. 仿真 14.408s；物体中心 (0.45265, 0.00805, 0.99827) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 37, "target": [0.45264591498190104, 0.008055166295425695, 0.9982641437403468], "tracking_error_m": 8.865652875235118e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

55. 仿真 14.742s；物体中心 (0.45265, 0.01647, 0.99135) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 38, "target": [0.45264591498190104, 0.016473764578362603, 0.991344748946805], "tracking_error_m": 9.656633475830879e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

56. 仿真 15.075s；物体中心 (0.45265, 0.02437, 0.98454) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 39, "target": [0.45264591498190104, 0.024372757412079164, 0.9845310795519577], "tracking_error_m": 9.33024930354992e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

57. 仿真 15.408s；物体中心 (0.45265, 0.03151, 0.97788) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 40, "target": [0.45264591498190104, 0.03151213789640616, 0.9778749916941059], "tracking_error_m": 9.699572427609614e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

58. 仿真 15.742s；物体中心 (0.45265, 0.03767, 0.97143) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 41, "target": [0.45264591498190104, 0.03767497956802806, 0.9714271422209035], "tracking_error_m": 9.24214939319394e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

59. 仿真 16.075s；物体中心 (0.45265, 0.04267, 0.96524) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 42, "target": [0.45264591498190104, 0.042674027601301144, 0.9652366031601594], "tracking_error_m": 8.895601798084327e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

60. 仿真 16.408s；物体中心 (0.45265, 0.04635, 0.95936) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 43, "target": [0.45264591498190104, 0.046357388451374604, 0.9593504882520757], "tracking_error_m": 8.020568334976511e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

61. 仿真 16.742s；物体中心 (0.45265, 0.04861, 0.95382) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 44, "target": [0.45264591498190104, 0.04861314506268959, 0.9538135943852363], "tracking_error_m": 8.210137813706943e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

62. 仿真 17.075s；物体中心 (0.45265, 0.04937, 0.94867) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 45, "target": [0.45264591498190104, 0.0493727574120792, 0.9486680606652356], "tracking_error_m": 7.93281425994093e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

63. 仿真 17.408s；物体中心 (0.45265, 0.04861, 0.94396) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 46, "target": [0.45264591498190104, 0.04861314506268961, 0.9439530477106411], "tracking_error_m": 7.611136645372591e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

64. 仿真 17.742s；物体中心 (0.45265, 0.04636, 0.93971) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 47, "target": [0.45264591498190104, 0.0463573884513746, 0.93970443961704], "tracking_error_m": 8.108692544251485e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

65. 仿真 18.075s；物体中心 (0.45265, 0.04268, 0.93596) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 48, "target": [0.45264591498190104, 0.04267402760130116, 0.9359545708574043], "tracking_error_m": 8.498180689987163e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

66. 仿真 18.408s；物体中心 (0.45265, 0.03768, 0.93274) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 49, "target": [0.45264591498190104, 0.03767497956802814, 0.9327319801972274], "tracking_error_m": 9.51483503174602e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

67. 仿真 18.742s；物体中心 (0.45265, 0.03152, 0.93006) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 50, "target": [0.45264591498190104, 0.03151213789640615, 0.9300611934972867], "tracking_error_m": 9.574993091253927e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

68. 仿真 19.075s；物体中心 (0.45265, 0.02438, 0.92796) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 51, "target": [0.45264591498190104, 0.02437275741207919, 0.9279625370570339], "tracking_error_m": 9.657086129582539e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

69. 仿真 19.408s；物体中心 (0.45265, 0.01648, 0.92645) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 52, "target": [0.45264591498190104, 0.016473764578362634, 0.9264519829191827], "tracking_error_m": 9.499928885995933e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

70. 仿真 19.742s；物体中心 (0.45265, 0.00807, 0.92554) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 53, "target": [0.45264591498190104, 0.008055166295425725, 0.9255410273128197], "tracking_error_m": 1.0016639000704845e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

71. 仿真 20.075s；物体中心 (0.45265, -0.00062, 0.92524) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 54, "target": [0.45264591498190104, -0.0006272425879207824, 0.9252366031601594], "tracking_error_m": 1.0365636031915278e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

72. 仿真 20.408s；物体中心 (0.45264, -0.00930, 0.92554) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 55, "target": [0.45264591498190104, -0.00930965147126729, 0.9255410273128197], "tracking_error_m": 1.0533410525326592e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

73. 仿真 20.742s；物体中心 (0.45264, -0.01772, 0.92645) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 56, "target": [0.45264591498190104, -0.017728249754204204, 0.9264519829191827], "tracking_error_m": 1.0506599315497056e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

74. 仿真 21.075s；物体中心 (0.45264, -0.02562, 0.92796) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 57, "target": [0.45264591498190104, -0.025627242587920762, 0.9279625370570339], "tracking_error_m": 1.0083201997372576e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

75. 仿真 21.408s；物体中心 (0.45264, -0.03276, 0.93006) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 58, "target": [0.45264591498190104, -0.03276662307224779, 0.9300611934972867], "tracking_error_m": 1.0558042127304782e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

76. 仿真 21.742s；物体中心 (0.45264, -0.03892, 0.93273) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 59, "target": [0.45264591498190104, -0.038929464743869664, 0.9327319801972274], "tracking_error_m": 9.964669037316951e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

77. 仿真 22.075s；物体中心 (0.45264, -0.04392, 0.93595) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 60, "target": [0.45264591498190104, -0.04392851277714269, 0.9359545708574043], "tracking_error_m": 1.0012383667408977e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

78. 仿真 22.408s；物体中心 (0.45264, -0.04761, 0.93970) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 61, "target": [0.45264591498190104, -0.04761187362721623, 0.9397044396170401], "tracking_error_m": 9.98123250903834e-06, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

79. 仿真 22.742s；物体中心 (0.45264, -0.04986, 0.94395) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 62, "target": [0.45264591498190104, -0.049867630238531205, 0.9439530477106411], "tracking_error_m": 1.0051295895945696e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

80. 仿真 23.075s；物体中心 (0.45264, -0.05063, 0.94866) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 63, "target": [0.45264591498190104, -0.050627242587920805, 0.9486680606652356], "tracking_error_m": 1.060270810759323e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

81. 仿真 23.408s；物体中心 (0.45264, -0.04987, 0.95381) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 64, "target": [0.45264591498190104, -0.04986763023853121, 0.9538135943852363], "tracking_error_m": 1.0222677982051398e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

82. 仿真 23.742s；物体中心 (0.45264, -0.04761, 0.95934) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 65, "target": [0.45264591498190104, -0.047611873627216236, 0.9593504882520757], "tracking_error_m": 1.0484390290833198e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

83. 仿真 24.075s；物体中心 (0.45264, -0.04393, 0.96523) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 66, "target": [0.45264591498190104, -0.04392851277714272, 0.9652366031601595], "tracking_error_m": 1.0386497153910475e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

84. 仿真 24.408s；物体中心 (0.45264, -0.03893, 0.97142) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 67, "target": [0.45264591498190104, -0.03892946474386975, 0.9714271422209034], "tracking_error_m": 1.0633010653884269e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

85. 仿真 24.742s；物体中心 (0.45264, -0.03277, 0.97787) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 68, "target": [0.45264591498190104, -0.03276662307224776, 0.9778749916941059], "tracking_error_m": 1.1026288180352668e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

86. 仿真 25.075s；物体中心 (0.45264, -0.02563, 0.98452) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 69, "target": [0.45264591498190104, -0.025627242587920797, 0.9845310795519577], "tracking_error_m": 1.0788283690083127e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

87. 仿真 25.408s；物体中心 (0.45264, -0.01773, 0.99134) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 70, "target": [0.45264591498190104, -0.017728249754204246, 0.9913447489468049], "tracking_error_m": 1.1155896547512084e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

88. 仿真 25.742s；物体中心 (0.45264, -0.00931, 0.99826) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 71, "target": [0.45264591498190104, -0.009309651471267333, 0.9982641437403468], "tracking_error_m": 1.0847454228936114e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

89. 仿真 26.075s；物体中心 (0.45264, -0.00063, 1.00523) m；{"trial": "learning_1", "kind": "figure_eight_waypoint", "index": 72, "target": [0.45264591498190104, -0.0006272425879208253, 1.0052366031601594], "tracking_error_m": 1.1075575461633367e-05, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

90. 仿真 26.075s；物体中心 (0.45264, -0.00063, 1.00523) m；{"trial": "learning_1", "kind": "figure_eight_evaluation", "metrics": {"waypoints": 73, "max_tracking_error_m": 1.2019591061309376e-05, "rms_tracking_error_m": 1.0116421539797707e-05, "closure_error_m": 4.412914100216481e-06, "midpoint_crossing_error_m": 9.410107499429497e-06, "plane_error_m": 8.59271740649703e-06, "upper_loop_area_m2": 0.005316280373141388, "lower_loop_area_m2": -0.005316268112438575, "vertical_span_m": 0.1599971706759794, "horizontal_span_m": 0.09999990322861345, "passed": true, "samples": 5960, "min_clearance_m": 0.15596467740279674, "grasp_retained": true}, "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

91. 仿真 26.575s；物体中心 (0.45264, -0.00063, 0.90524) m；{"trial": "learning_1", "kind": "return_to_lift_height", "target": [0.45264591498190104, -0.0006272425879208008, 0.9052366031601594], "物体抓持": true, "实际抬升": true, "事件": ["held_object_waypoint_reached"]}

92. 仿真 26.775s；物体中心 (0.50177, -0.00063, 0.76742) m；{"trial": "learning_1", "kind": "action", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "action": "move_to_target", "物体抓持": true, "实际抬升": false, "事件": ["object_at_target"]}

93. 仿真 26.975s；物体中心 (0.49987, -0.00063, 0.74996) m；{"trial": "learning_1", "kind": "action", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "action": "release_object", "物体抓持": false, "实际抬升": false, "事件": ["object_released"]}

94. 仿真 26.975s；物体中心 (0.49987, -0.00063, 0.74996) m；{"trial": "learning_1", "kind": "result", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "deviation", "errors": ["expected_lift_but_not_detected", "missing_event:object_lift_detected"], "severity": "medium"}, "result": {"mode": "skills", "failure_mode": "low_grip_force", "status": "recovered", "false_success": false, "recovered": true, "applied_skill_ids": ["grasp_without_lift_v1"]}, "物体抓持": false, "实际抬升": false, "事件": ["object_released"]}

95. 仿真 27.975s；物体中心 (0.49987, -0.00061, 0.74999) m；{"trial": "learning_1", "kind": "placement_evaluation", "metrics": {"drift_m": 3.128409276385285e-05, "speed_m_s": 1.2362729741205837e-05, "target_error_m": 0.0006261867748050345, "released": true, "height_error_m": 1.1393495004896614e-05, "passed": true}, "物体抓持": false, "实际抬升": false, "事件": ["placement_settled"]}


[2026-10-19T21:37:32+08:00] learning_1 结束：{"label": "learning_1", "failure_mode": "low_grip_force", "parameters": {"half_width_m": 0.05, "half_height_m": 0.08, "center_raise_m": 0.1, "samples": 72, "steps_per_waypoint": 80}, "trajectory": {"waypoints": 73, "max_tracking_error_m": 1.2019591061309376e-05, "rms_tracking_error_m": 1.0116421539797707e-05, "closure_error_m": 4.412914100216481e-06, "midpoint_crossing_error_m": 9.410107499429497e-06, "plane_error_m": 8.59271740649703e-06, "upper_loop_area_m2": 0.005316280373141388, "lower_loop_area_m2": -0.005316268112438575, "vertical_span_m": 0.1599971706759794, "horizontal_span_m": 0.09999990322861345, "passed": true, "samples": 5960, "min_clearance_m": 0.15596467740279674, "grasp_retained": true}, "placement": {"drift_m": 3.128409276385285e-05, "speed_m_s": 1.2362729741205837e-05, "target_error_m": 0.0006261867748050345, "released": true, "height_error_m": 1.1393495004896614e-05, "passed": true}, "error": null, "applied_skill_ids": ["grasp_without_lift_v1"], "diagnosis_fallback": false, "result": {"mode": "skills", "failure_mode": "low_grip_force", "status": "recovered", "false_success": false, "recovered": true, "applied_skill_ids": ["grasp_without_lift_v1"]}, "passed": true}


[2026-10-19T21:37:32+08:00] 大模型 request；request_id=6cafdd0414b7488cb0ad231b90421446；完整内容已写入 docs\FIGURE_EIGHT_LLM_CALLS.md。
