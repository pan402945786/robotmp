# 0.05 米抛接技能学习记录

日期：2026-10-19（Asia/Shanghai）。用户目标：复用 `artifacts/verification_20261019/skills.json`，抓起物体，向上抛起至少 0.05 米，接住后平稳放到地面；逐步记录事件，及时提交 Git，保存每次实验大模型调用的完整输入和输出，成功则生成演示视频。

## 验收约定

- 采用 PyBullet xArm6 仿真，复用 `grasp_without_lift_v1` 的实际抬升检测和重新定位抓取恢复规则。
- 高度取相对于解除抓持约束瞬间的物体中心：自由飞行最高点减释放点至少 0.05 米；仅夹持抬高不计入。
- 飞行期间不存在抓持约束，也不允许给物体注入速度、位置、抛射外力或修改重力。释放前检查当时实测向上速度，历史最大值不能替代当前速度。
- 上升、顶点、下降必须实际观测；下降接住须通过距离、相对速度和无环境碰撞检查。
- 接住后缓慢下降，低速释放，再检查真实地面接触、位移、线速度、角速度与中心高度。
- 学习与正式验证分开；至少三次独立完整成功才将新技能标为 verified，并从保存的技能文件重载演示。
- 现有抓持与接球采用固定约束，机械臂与物体碰撞关闭；这是理想抓持模型上的动作参数学习与技能组合，不代表真实硬件抓持验证或神经网络训练。

## 初始检查

1. Git 工作区干净，起点提交 `bb814b4`。未发现适用的 AGENTS.md。
2. 来源技能已 verified，历史验证 20 次；包含 `require_lift_evidence_before_transport`，恢复要求刷新物体位置并重试抓取。
3. 历史 `throw_catch_05m.py` 是 0.5 米目标，并残留 10 米中文提示；历史场景的 0.70 米桌面阻碍放地。本次新建独立入口与文档，明确 0.05 米目标，采用地面可达场景。
4. 实验请求、原始响应、解析输出和错误将立即写入本次模型日志；实验阶段与每次模型日志事件形成 Git 检查点。此处“模型调用日志”记录项目实际发出的 API 请求与响应；当前助手服务内部推理和服务端隐藏上下文不可导出。

后续每一步由实验日志器实时追加。

实现事件：本地仿真与视频依赖检查通过（Conda py311）。新入口修正历史最大速度放行问题，按释放当时速度触发；独立实现地面支撑反馈下降与正式验证。首次命令行校准因 Windows 批处理剥离 JSON 引号而在运行物理试验前报 JSONDecodeError，已改为从 JSON 文件读取参数。

校准 01 结果：自由飞行升高 0.054878 m，28 个无抓持约束物理步后下降接住，接球相对速度 0.141446 m/s，持续抓持检查通过。放地失败：反馈下降每 4 步重设过小目标，实际每轮仅下降约 0.00027 m，700 轮预算耗尽时物体仍在 z=0.22786 m；这属于控制进度不足。另观测到接球后立方体倾斜，增加用腕部 IK 缓慢扶正的动作，再以每轮最多 0.002 m、12 步跟踪下降，避免倾斜物体释放后翻倒。全程保持原重力与关节限速。


[2026-10-19T23:59:09+08:00] 开始运行 f3f10b4b876a；输出目录 docs\throw_catch_005m_calibration_01。

1. 仿真 0.000s；物体中心 (—) m；{"kind": "source_verified", "source_path": "artifacts\\verification_20261019\\skills.json", "sha256": "1480ab7df263cab82d7df41eb84c92a961c2b70a2d8b7bb2cb8c02f94a1f7383", "target_rise_m": 0.05, "ground_z_m": 0}


[2026-10-19T23:59:24+08:00] 开始运行 c72361043d70；输出目录 docs\throw_catch_005m_calibration_01。

1. 仿真 0.000s；物体中心 (—) m；{"kind": "source_verified", "source_path": "artifacts\\verification_20261019\\skills.json", "sha256": "1480ab7df263cab82d7df41eb84c92a961c2b70a2d8b7bb2cb8c02f94a1f7383", "target_rise_m": 0.05, "ground_z_m": 0}


[2026-10-19T23:59:25+08:00] 开始 calibration：参数 {"target_x_m": 0.4, "target_z_m": 0.65, "release_min_vz_m_s": 1.06, "max_sweep_steps": 160, "catch_lead_s": 0.04}；故障 none。

2. 仿真 0.142s；物体中心 (0.45000, -0.00000, 0.04998) m；{"trial": "calibration", "kind": "ground_scene_ready", "ground_z_m": 0, "ideal_grasp_model": "fixed_constraint", "物体抓持": false, "实际抬升": false, "事件": []}

3. 仿真 0.142s；物体中心 (0.45000, -0.00000, 0.04998) m；{"trial": "calibration", "kind": "prerequisite_retrieved", "skill": {"skill_id": "grasp_without_lift_v1", "name": "grasp_without_lift", "status": "verified", "version": 1, "task": "pick_and_place", "object_types": ["cube"], "trigger_conditions": ["gripper_closed == true", "lift_window_elapsed == true", "object_lifted == false"], "facts": ["gripper_closed_does_not_imply_grasp_success", "object_lift_was_not_detected", "object_may_have_been_displaced_before_grasp"], "hypotheses": ["grasp_point_may_be_misaligned", "insufficient_grip_force"], "prediction_correction": ["do_not_enter_transport_phase", "require_lift_evidence_before_transport"], "recovery": ["stop_transport_motion", "refresh_object_pose", "retry_grasp_if_safe"], "validation_trials": 20, "false_success_rate": 0.0, "recovery_success_rate": 1.0, "prerequisite_skill_ids": [], "parameters": {}, "validation_success_rate": null, "validation_metrics": {}}, "物体抓持": false, "实际抬升": false, "事件": []}

4. 仿真 0.342s；物体中心 (0.45000, 0.00000, 0.04999) m；{"trial": "calibration", "kind": "action", "action": "approach_object", "物体抓持": false, "实际抬升": false, "事件": ["object_approached"]}

5. 仿真 0.542s；物体中心 (0.45000, 0.00001, 0.04999) m；{"trial": "calibration", "kind": "action", "action": "close_gripper", "物体抓持": true, "实际抬升": false, "事件": ["gripper_closed", "gripper_contact", "grasp_constraint_created"]}

6. 仿真 0.742s；物体中心 (0.45297, -0.00063, 0.20518) m；{"trial": "calibration", "kind": "action", "action": "lift_object", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

7. 仿真 0.742s；物体中心 (0.45297, -0.00063, 0.20518) m；{"trial": "calibration", "kind": "lift_comparison", "prediction": {"prediction_id": "pred-1", "action": "lift_object", "expected_phase": "lift", "expected_events": ["object_lift_detected"], "expected_object_lifted": true, "position_tolerance_m": 0.03, "confidence": 0.9, "applied_skill_ids": ["grasp_without_lift_v1"], "requires_lift_evidence": true}, "comparison": {"status": "match", "errors": [], "severity": "none"}, "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

8. 仿真 0.742s；物体中心 (0.45297, -0.00063, 0.20518) m；{"trial": "calibration", "kind": "lift_gate_passed", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

9. 仿真 1.742s；物体中心 (0.39936, -0.00000, 0.21997) m；{"trial": "calibration", "kind": "launch_start_settled", "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

10. 仿真 1.742s；物体中心 (0.39936, -0.00000, 0.21997) m；{"trial": "calibration", "kind": "upward_sweep_commanded", "target": [0.4, 0, 0.65], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

11. 仿真 1.746s；物体中心 (0.39795, -0.00000, 0.21975) m；{"trial": "calibration", "kind": "sweep_step", "tick": 0, "velocity": [-0.33813516353783174, -0.0008000826906696858, -0.05207066723031338], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

12. 仿真 1.750s；物体中心 (0.39703, -0.00001, 0.21948) m；{"trial": "calibration", "kind": "sweep_step", "tick": 1, "velocity": [-0.21952716891458124, -0.0005303331465012651, -0.06541424538259803], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

13. 仿真 1.754s；物体中心 (0.39661, -0.00001, 0.21915) m；{"trial": "calibration", "kind": "sweep_step", "tick": 2, "velocity": [-0.1011224713294312, -0.00027114883142498916, -0.07792928921965922], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

14. 仿真 1.758s；物体中心 (0.39669, -0.00001, 0.21878) m；{"trial": "calibration", "kind": "sweep_step", "tick": 3, "velocity": [0.01838450438920962, -1.7666925975547978e-05, -0.08980835277572419], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

15. 仿真 1.762s；物体中心 (0.39695, -0.00001, 0.21861) m；{"trial": "calibration", "kind": "sweep_step", "tick": 4, "velocity": [0.062490874356857566, 7.334960260376263e-05, -0.04105993249543835], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

16. 仿真 1.767s；物体中心 (0.39738, -0.00001, 0.21865) m；{"trial": "calibration", "kind": "sweep_step", "tick": 5, "velocity": [0.10356944977017309, 0.0001669132780705598, 0.009285621553865989], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

17. 仿真 1.771s；物体中心 (0.39799, -0.00000, 0.21889) m；{"trial": "calibration", "kind": "sweep_step", "tick": 6, "velocity": [0.14516370188152916, 0.00026108406235090793, 0.058350503925917965], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

18. 仿真 1.775s；物体中心 (0.39877, -0.00000, 0.21933) m；{"trial": "calibration", "kind": "sweep_step", "tick": 7, "velocity": [0.18714711284533658, 0.000359970239377023, 0.10620187084327712], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

19. 仿真 1.779s；物体中心 (0.39957, -0.00000, 0.21979) m；{"trial": "calibration", "kind": "sweep_step", "tick": 8, "velocity": [0.19391202345594183, 0.00038767075579004747, 0.1097291391226469], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

20. 仿真 1.783s；物体中心 (0.40039, -0.00000, 0.22023) m；{"trial": "calibration", "kind": "sweep_step", "tick": 9, "velocity": [0.19541988022908083, 0.0003936899342846022, 0.10692840971787679], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

21. 仿真 1.787s；物体中心 (0.40121, 0.00000, 0.22067) m；{"trial": "calibration", "kind": "sweep_step", "tick": 10, "velocity": [0.1968772577575022, 0.0003993952715351512, 0.10416075228283564], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

22. 仿真 1.792s；物体中心 (0.40203, 0.00000, 0.22109) m；{"trial": "calibration", "kind": "sweep_step", "tick": 11, "velocity": [0.19825952140768438, 0.0004025599030614351, 0.10140403829630572], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

23. 仿真 1.796s；物体中心 (0.40287, 0.00000, 0.22150) m；{"trial": "calibration", "kind": "sweep_step", "tick": 12, "velocity": [0.19962023631685194, 0.0004077720110198101, 0.09867254846170645], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

24. 仿真 1.800s；物体中心 (0.40370, 0.00001, 0.22190) m；{"trial": "calibration", "kind": "sweep_step", "tick": 13, "velocity": [0.20093492876449454, 0.00041260961594752327, 0.09594931115680587], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

25. 仿真 1.804s；物体中心 (0.40455, 0.00001, 0.22229) m；{"trial": "calibration", "kind": "sweep_step", "tick": 14, "velocity": [0.20220571672158552, 0.0004171114380883452, 0.0932297531685927], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

26. 仿真 1.808s；物体中心 (0.40539, 0.00001, 0.22267) m；{"trial": "calibration", "kind": "sweep_step", "tick": 15, "velocity": [0.20343428233893623, 0.00042131049558124546, 0.09051031835044529], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

27. 仿真 1.812s；物体中心 (0.40625, 0.00001, 0.22303) m；{"trial": "calibration", "kind": "sweep_step", "tick": 16, "velocity": [0.20462193490630315, 0.0004252350416572886, 0.08778825483599281], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

28. 仿真 1.817s；物体中心 (0.40710, 0.00001, 0.22339) m；{"trial": "calibration", "kind": "sweep_step", "tick": 17, "velocity": [0.20576968661425202, 0.0004289093244859416, 0.08506145464413983], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

29. 仿真 1.821s；物体中心 (0.40797, 0.00002, 0.22373) m；{"trial": "calibration", "kind": "sweep_step", "tick": 18, "velocity": [0.20687831319974193, 0.00043235421527216384, 0.08232832535806739], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

30. 仿真 1.825s；物体中心 (0.40883, 0.00002, 0.22406) m；{"trial": "calibration", "kind": "sweep_step", "tick": 19, "velocity": [0.20794840247164986, 0.0004355877291692836, 0.07958768745329542], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

31. 仿真 1.829s；物体中心 (0.40970, 0.00002, 0.22438) m；{"trial": "calibration", "kind": "sweep_step", "tick": 20, "velocity": [0.2089803931333728, 0.0004386254580231909, 0.07683869214270686], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

32. 仿真 1.833s；物体中心 (0.41058, 0.00002, 0.22469) m；{"trial": "calibration", "kind": "sweep_step", "tick": 21, "velocity": [0.20997460584868297, 0.00044148093132191055, 0.07408075563685623], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

33. 仿真 1.837s；物体中心 (0.41146, 0.00002, 0.22499) m；{"trial": "calibration", "kind": "sweep_step", "tick": 22, "velocity": [0.2109312680994234, 0.00044416591799282536, 0.07131350653563828], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

34. 仿真 1.842s；物体中心 (0.41234, 0.00002, 0.22527) m；{"trial": "calibration", "kind": "sweep_step", "tick": 23, "velocity": [0.21185053407677115, 0.0004466906795696665, 0.068536743725011], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

35. 仿真 1.846s；物体中心 (0.41323, 0.00003, 0.22555) m；{"trial": "calibration", "kind": "sweep_step", "tick": 24, "velocity": [0.21273250059910037, 0.00044906418315597546, 0.06575040267791338], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

36. 仿真 1.850s；物体中心 (0.41412, 0.00003, 0.22581) m；{"trial": "calibration", "kind": "sweep_step", "tick": 25, "velocity": [0.21357721985092293, 0.0004512942812709573, 0.06295452847799284], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

37. 仿真 1.854s；物体中心 (0.41501, 0.00003, 0.22606) m；{"trial": "calibration", "kind": "sweep_step", "tick": 26, "velocity": [0.2143847095783282, 0.0004533878640487928, 0.06014925422204786], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

38. 仿真 1.858s；物体中心 (0.41591, 0.00003, 0.22630) m；{"trial": "calibration", "kind": "sweep_step", "tick": 27, "velocity": [0.21515496124949893, 0.000455350988562973, 0.05733478372490312], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

39. 仿真 1.862s；物体中心 (0.41681, 0.00003, 0.22653) m；{"trial": "calibration", "kind": "sweep_step", "tick": 28, "velocity": [0.21588794658622376, 0.0004571889888349666, 0.054511377666217935], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

40. 仿真 1.867s；物体中心 (0.41771, 0.00004, 0.22674) m；{"trial": "calibration", "kind": "sweep_step", "tick": 29, "velocity": [0.21658362279561513, 0.00045890657081285074, 0.051679342491734], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

41. 仿真 1.871s；物体中心 (0.41858, 0.00004, 0.22725) m；{"trial": "calibration", "kind": "sweep_step", "tick": 30, "velocity": [0.20997477231970774, 0.00041318914516862707, 0.12169852744464152], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

42. 仿真 1.875s；物体中心 (0.41943, 0.00004, 0.22804) m；{"trial": "calibration", "kind": "sweep_step", "tick": 31, "velocity": [0.2031072714321784, 0.0004227978562365436, 0.1903794966661334], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

43. 仿真 1.879s；物体中心 (0.42025, 0.00004, 0.22912) m；{"trial": "calibration", "kind": "sweep_step", "tick": 32, "velocity": [0.1959249530862406, 0.00040869303957528566, 0.2578384202263989], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

44. 仿真 1.883s；物体中心 (0.42105, 0.00004, 0.23046) m；{"trial": "calibration", "kind": "sweep_step", "tick": 33, "velocity": [0.1928792056174888, 0.00040381230183109633, 0.32202959150800947], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

45. 仿真 1.887s；物体中心 (0.42186, 0.00004, 0.23205) m；{"trial": "calibration", "kind": "sweep_step", "tick": 34, "velocity": [0.19404863536890965, 0.0004074955044279385, 0.3830409931927164], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

46. 仿真 1.892s；物体中心 (0.42268, 0.00005, 0.23390) m；{"trial": "calibration", "kind": "sweep_step", "tick": 35, "velocity": [0.19755864176255278, 0.00041584108763161515, 0.44185614005368634], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

47. 仿真 1.896s；物体中心 (0.42353, 0.00005, 0.23597) m；{"trial": "calibration", "kind": "sweep_step", "tick": 36, "velocity": [0.2030990710503876, 0.00042835441584944796, 0.498704452244331], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

48. 仿真 1.900s；物体中心 (0.42440, 0.00005, 0.23828) m；{"trial": "calibration", "kind": "sweep_step", "tick": 37, "velocity": [0.21037105656632646, 0.00044440893833568826, 0.5537985154453886], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

49. 仿真 1.904s；物体中心 (0.42532, 0.00005, 0.24081) m；{"trial": "calibration", "kind": "sweep_step", "tick": 38, "velocity": [0.21908829683885764, 0.0004634040100665128, 0.6073346834633704], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

50. 仿真 1.908s；物体中心 (0.42627, 0.00005, 0.24356) m；{"trial": "calibration", "kind": "sweep_step", "tick": 39, "velocity": [0.22897777085396254, 0.0004847665340867099, 0.6594936980772911], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

51. 仿真 1.912s；物体中心 (0.42727, 0.00006, 0.24652) m；{"trial": "calibration", "kind": "sweep_step", "tick": 40, "velocity": [0.23977870393134748, 0.0005075280857569499, 0.7104418301655335], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

52. 仿真 1.917s；物体中心 (0.42832, 0.00006, 0.24969) m；{"trial": "calibration", "kind": "sweep_step", "tick": 41, "velocity": [0.25123974565983037, 0.0005305108277959366, 0.7603326456606124], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

53. 仿真 1.921s；物体中心 (0.42940, 0.00006, 0.25304) m；{"trial": "calibration", "kind": "sweep_step", "tick": 42, "velocity": [0.2593457697341855, 0.0005646043982905564, 0.805431105170146], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

54. 仿真 1.925s；物体中心 (0.43045, 0.00006, 0.25652) m；{"trial": "calibration", "kind": "sweep_step", "tick": 43, "velocity": [0.25235719721130045, 0.0005472328736947879, 0.8336569594377902], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

55. 仿真 1.929s；物体中心 (0.43147, 0.00007, 0.26010) m；{"trial": "calibration", "kind": "sweep_step", "tick": 44, "velocity": [0.24443214892708698, 0.0005278980317218178, 0.8593970922161672], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

56. 仿真 1.933s；物体中心 (0.43245, 0.00007, 0.26378) m；{"trial": "calibration", "kind": "sweep_step", "tick": 45, "velocity": [0.23571810810491184, 0.0005078928889120181, 0.8828763213417069], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

57. 仿真 1.937s；物体中心 (0.43339, 0.00007, 0.26754) m；{"trial": "calibration", "kind": "sweep_step", "tick": 46, "velocity": [0.22623522134460156, 0.00048292622565152156, 0.9042793968461318], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

58. 仿真 1.942s；物体中心 (0.43429, 0.00007, 0.27139) m；{"trial": "calibration", "kind": "sweep_step", "tick": 47, "velocity": [0.21613502431684886, 0.00046152736647789023, 0.9237950386386665], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

59. 仿真 1.946s；物体中心 (0.43515, 0.00007, 0.27532) m；{"trial": "calibration", "kind": "sweep_step", "tick": 48, "velocity": [0.2054490793121441, 0.0004389556192044622, 0.941577890626513], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

60. 仿真 1.950s；物体中心 (0.43596, 0.00007, 0.27931) m；{"trial": "calibration", "kind": "sweep_step", "tick": 49, "velocity": [0.19424310328470745, 0.0004153200177543307, 0.9577724993026404], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

61. 仿真 1.954s；物体中心 (0.43672, 0.00008, 0.28336) m；{"trial": "calibration", "kind": "sweep_step", "tick": 50, "velocity": [0.18257675561042155, 0.00039072527432556186, 0.9725098255885848], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

62. 仿真 1.958s；物体中心 (0.43743, 0.00008, 0.28747) m；{"trial": "calibration", "kind": "sweep_step", "tick": 51, "velocity": [0.1705039436907242, 0.0003651377868415932, 0.9859085423269096], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

63. 仿真 1.962s；物体中心 (0.43809, 0.00008, 0.29163) m；{"trial": "calibration", "kind": "sweep_step", "tick": 52, "velocity": [0.1580371599425949, 0.0003367572749391701, 0.9980684821429386], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

64. 仿真 1.967s；物体中心 (0.43869, 0.00008, 0.29583) m；{"trial": "calibration", "kind": "sweep_step", "tick": 53, "velocity": [0.14529791966182315, 0.00031018747913805444, 1.009100939487649], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

65. 仿真 1.971s；物体中心 (0.43924, 0.00008, 0.30008) m；{"trial": "calibration", "kind": "sweep_step", "tick": 54, "velocity": [0.13228265342306295, 0.00028298372418702214, 1.0190888636240363], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

66. 仿真 1.975s；物体中心 (0.43974, 0.00008, 0.30436) m；{"trial": "calibration", "kind": "sweep_step", "tick": 55, "velocity": [0.11902656051464104, 0.0002552150581937641, 1.0281124115897615], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

67. 仿真 1.979s；物体中心 (0.44018, 0.00008, 0.30868) m；{"trial": "calibration", "kind": "sweep_step", "tick": 56, "velocity": [0.1055612215560325, 0.00022695134457073203, 1.0362443231228549], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

68. 仿真 1.983s；物体中心 (0.44056, 0.00008, 0.31303) m；{"trial": "calibration", "kind": "sweep_step", "tick": 57, "velocity": [0.09191482970778905, 0.00019825583449660506, 1.0435505957089575], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

69. 仿真 1.987s；物体中心 (0.44089, 0.00009, 0.31740) m；{"trial": "calibration", "kind": "sweep_step", "tick": 58, "velocity": [0.07811253166907348, 0.0001691856185365338, 1.050091110796108], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

70. 仿真 1.992s；物体中心 (0.44116, 0.00009, 0.32180) m；{"trial": "calibration", "kind": "sweep_step", "tick": 59, "velocity": [0.0641767428262667, 0.00013979211271298046, 1.05592020078185], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

71. 仿真 1.996s；物体中心 (0.44136, 0.00009, 0.32622) m；{"trial": "calibration", "kind": "sweep_step", "tick": 60, "velocity": [0.05012743644590001, 0.0001101215396272239, 1.0610871628118803], "物体抓持": true, "实际抬升": true, "事件": ["object_lift_detected"]}

72. 仿真 1.996s；物体中心 (0.44136, 0.00009, 0.32622) m；{"trial": "calibration", "kind": "release_measured", "velocity": [0.05012743644590001, 0.0001101215396272239, 1.0610871628118803], "required_vz_m_s": 0.9904544411531507, "constraint_active": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

73. 仿真 2.000s；物体中心 (0.44157, 0.00009, 0.33047) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.05011020705689396, 0.00011008368955990138, 1.0198474546840839], "ee_velocity": [0.292203426361084, 0.0006286986172199249, 0.8323216438293457], "catch_distance_m": 0.10789589095215293, "relative_speed_m_s": 0.3062275714746092, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

74. 仿真 2.004s；物体中心 (0.44178, 0.00009, 0.33455) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.05009332761942313, 0.00011004660827719235, 0.9786289228499093], "ee_velocity": [0.049223899841308594, 0.00012715347111225128, 0.7164788246154785], "catch_distance_m": 0.10693098323567836, "relative_speed_m_s": 0.26215154052880907, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

75. 仿真 2.008s；物体中心 (0.44199, 0.00009, 0.33846) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.05007679757173995, 0.00011001029454503195, 0.9374309899658784], "ee_velocity": [-0.18654584884643555, -0.0003727152943611145, 0.5999994277954102], "catch_distance_m": 0.10522596704804547, "relative_speed_m_s": 0.41212931098229066, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

76. 仿真 2.012s；物体中心 (0.44220, 0.00009, 0.34219) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.050060616360208164, 0.00010997474714717452, 0.8962530798382216], "ee_velocity": [-0.41198015213012695, -0.0008612126111984253, 0.48317670822143555], "catch_distance_m": 0.1028037988725738, "relative_speed_m_s": 0.619769879665117, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

77. 仿真 2.017s；物体中心 (0.44241, 0.00009, 0.34575) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.05004478343848128, 0.00010993996488338884, 0.8550946173902475], "ee_velocity": [-0.4568624496459961, -0.0009438302367925644, 0.35065412521362305], "catch_distance_m": 0.09996558230819666, "relative_speed_m_s": 0.7151337382143244, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

78. 仿真 2.021s；物体中心 (0.44262, 0.00009, 0.34915) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.050029298266496054, 0.00010990594656724682, 0.8139550286298584], "ee_velocity": [-0.49972057342529297, -0.0010422198101878166, 0.21821022033691406], "catch_distance_m": 0.096715756437794, "relative_speed_m_s": 0.8106405648787228, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

79. 仿真 2.025s；物体中心 (0.44282, 0.00009, 0.35237) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.05001416030922496, 0.00010987269102338308, 0.7728337406172152], "ee_velocity": [-0.534825325012207, -0.0011248234659433365, 0.10582208633422852], "catch_distance_m": 0.09314401629837916, "relative_speed_m_s": 0.8870982442858086, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

80. 仿真 2.029s；物体中心 (0.44303, 0.00009, 0.35541) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.049999369035111305, 0.000109840197084057, 0.7317301814325547], "ee_velocity": [-0.5362057685852051, -0.001124306581914425, 0.09869098663330078], "catch_distance_m": 0.08970779652435454, "relative_speed_m_s": 0.8627726285892559, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

81. 仿真 2.033s；物体中心 (0.44324, 0.00009, 0.35829) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.049984923914080576, 0.00010980846358478414, 0.6906437801441663], "ee_velocity": [-0.5374574661254883, -0.001127980649471283, 0.09166717529296875], "catch_distance_m": 0.08641134873653523, "relative_speed_m_s": 0.8389654741980489, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

82. 仿真 2.037s；物体中心 (0.44345, 0.00009, 0.36100) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04997082441497813, 0.00010977748935870719, 0.6495739667765399], "ee_velocity": [-0.5386018753051758, -0.0011313613504171371, 0.08462905883789062], "catch_distance_m": 0.08325902828258555, "relative_speed_m_s": 0.8158321593853107, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

83. 仿真 2.042s；物体中心 (0.44366, 0.00009, 0.36353) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.049957070002217635, 0.00010974727322923308, 0.608520172278708], "ee_velocity": [-0.5396676063537598, -0.0011344626545906067, 0.07758378982543945], "catch_distance_m": 0.08025581075909415, "relative_speed_m_s": 0.7934432867185902, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

84. 仿真 2.046s；物体中心 (0.44387, 0.00009, 0.36590) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.049943660131324154, 0.00010971781400024205, 0.5674818284928139], "ee_velocity": [-0.5406403541564941, -0.0011373404413461685, 0.07051706314086914], "catch_distance_m": 0.07740731898157105, "relative_speed_m_s": 0.7718581547719242, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

85. 仿真 2.050s；物体中心 (0.44407, 0.00009, 0.36809) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04993059424289847, 0.0001096891104428282, 0.5264583681229653], "ee_velocity": [-0.5415129661560059, -0.0011399388313293457, 0.06343603134155273], "catch_distance_m": 0.07471990733616975, "relative_speed_m_s": 0.7511303023216711, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

86. 仿真 2.054s；物体中心 (0.44428, 0.00009, 0.37011) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.049917871754274735, 0.00010966116127697275, 0.48544922470446866], "ee_velocity": [-0.542292594909668, -0.001142187975347042, 0.05635499954223633], "catch_distance_m": 0.0722006630824983, "relative_speed_m_s": 0.7313252751137227, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

87. 仿真 2.058s；物体中心 (0.44449, 0.00009, 0.37197) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04990549204772139, 0.00010963396514562344, 0.44445383257361076], "ee_velocity": [-0.5429935455322266, -0.0011442974209785461, 0.049245357513427734], "catch_distance_m": 0.06985719582041318, "relative_speed_m_s": 0.71254514233594, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

88. 仿真 2.062s；物体中心 (0.44470, 0.00009, 0.37365) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.049893454453308, 0.00010960752057705584, 0.40347162683828036], "ee_velocity": [-0.5435800552368164, -0.0011460855603218079, 0.042150020599365234], "catch_distance_m": 0.06769790770594752, "relative_speed_m_s": 0.6948134185550083, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

89. 仿真 2.067s；物体中心 (0.44491, 0.00009, 0.37516) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04988175822325862, 0.00010958182592853212, 0.36250204334997294], "ee_velocity": [-0.5440950393676758, -0.0011476082727313042, 0.03502607345581055], "catch_distance_m": 0.06573142569091037, "relative_speed_m_s": 0.678270246628472, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

90. 仿真 2.071s；物体中心 (0.44511, 0.00009, 0.37650) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04987040249216973, 0.0001095568792989064, 0.32154451867822753], "ee_velocity": [-0.5445027351379395, -0.001148977316915989, 0.027909278869628906], "catch_distance_m": 0.06396682737868645, "relative_speed_m_s": 0.6629499714925983, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

91. 仿真 2.075s；物体中心 (0.44532, 0.00010, 0.37767) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04985938621263418, 0.00010953267838720154, 0.2805984900896486], "ee_velocity": [-0.5448246002197266, -0.001149228774011135, 0.020763874053955078], "catch_distance_m": 0.062413041688311466, "relative_speed_m_s": 0.6489719993111371, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

92. 仿真 2.079s；物体中心 (0.44553, 0.00010, 0.37867) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04984870804559927, 0.00010950922025174411, 0.23966339553625512], "ee_velocity": [-0.5450534820556641, -0.0011502206325531006, 0.01363992691040039], "catch_distance_m": 0.061078925682279246, "relative_speed_m_s": 0.6363935976078361, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

93. 仿真 2.083s；物体中心 (0.44574, 0.00010, 0.37949) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04983836616147448, 0.00010948650087323174, 0.19873867366456038], "ee_velocity": [-0.5212926864624023, -0.0011038267984986305, -0.042214393615722656], "catch_distance_m": 0.05978143979067558, "relative_speed_m_s": 0.6198794495966103, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

94. 仿真 2.087s；物体中心 (0.44594, 0.00010, 0.38015) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04982835784946021, 0.00010946451429649406, 0.15782376387600727], "ee_velocity": [-0.4674553871154785, -0.0009931577369570732, -0.15885114669799805], "catch_distance_m": 0.058270663951776575, "relative_speed_m_s": 0.6065201460527383, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

95. 仿真 2.092s；物体中心 (0.44615, 0.00010, 0.38064) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.0498186786668858, 0.00010944325076173148, 0.11691810653366114], "ee_velocity": [-0.4153633117675781, -0.0008809659630060196, -0.2552175521850586], "catch_distance_m": 0.05660996369195485, "relative_speed_m_s": 0.595718233416601, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

96. 仿真 2.096s；物体中心 (0.44636, 0.00010, 0.38096) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.049809320314988755, 0.00010942269203795976, 0.07602114367126982], "ee_velocity": [-0.3354978561401367, -0.0007075304165482521, -0.21614313125610352], "catch_distance_m": 0.05534801052930546, "relative_speed_m_s": 0.48355170476800163, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

97. 仿真 2.100s；物体中心 (0.44657, 0.00010, 0.38110) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.0498002642700371, 0.00010940279743165797, 0.03513232194292641], "ee_velocity": [-0.26395082473754883, -0.0005560554563999176, -0.17915725708007812], "catch_distance_m": 0.05445234257125213, "relative_speed_m_s": 0.37994764424324334, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

98. 仿真 2.104s；物体中心 (0.44677, 0.00010, 0.38108) m；{"trial": "calibration", "kind": "apex_observed", "apex_height_m": 0.38110157701001374, "rise_m": 0.054878205302841765, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

99. 仿真 2.104s；物体中心 (0.44677, 0.00010, 0.38108) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04979145837555733, 0.00010938345236383363, -0.0057488903036227584], "ee_velocity": [-0.1999211311340332, -0.0004204781726002693, -0.1444101333618164], "catch_distance_m": 0.053894953913924376, "relative_speed_m_s": 0.2856284272256008, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

100. 仿真 2.108s；物体中心 (0.44698, 0.00010, 0.38088) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04978274385511765, 0.0001093643080293938, -0.04662288413060252], "ee_velocity": [-0.14269351959228516, -0.0002992479130625725, -0.11188030242919922], "catch_distance_m": 0.053652675465834285, "relative_speed_m_s": 0.2032383074068943, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

101. 仿真 2.112s；物体中心 (0.44719, 0.00010, 0.38052) m；{"trial": "calibration", "kind": "flight_step", "velocity": [0.04977388081962192, 0.00010934483743237625, -0.08748958365849183], "ee_velocity": [-0.09154558181762695, -0.0001910235732793808, -0.08151054382324219], "catch_distance_m": 0.05370682013285851, "relative_speed_m_s": 0.14144620765016797, "constraint_active": false, "contact": false, "物体抓持": false, "实际抬升": true, "事件": ["object_released_in_motion"]}

102. 仿真 2.112s；物体中心 (0.44719, 0.00010, 0.38052) m；{"trial": "calibration", "kind": "descending_catch_gate_passed", "distance_m": 0.05370682013285851, "relative_speed_m_s": 0.14144620765016797, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

103. 仿真 2.613s；物体中心 (0.45524, -0.00052, 0.41891) m；{"trial": "calibration", "kind": "catch_hold_evaluation", "passed": true, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

104. 仿真 2.629s；物体中心 (0.45565, -0.00052, 0.41872) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 0, "support_height_m": 0.0660140849993841, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

105. 仿真 2.646s；物体中心 (0.45592, -0.00052, 0.41850) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 1, "support_height_m": 0.06577594384028855, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

106. 仿真 2.663s；物体中心 (0.45609, -0.00052, 0.41827) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 2, "support_height_m": 0.06561669918832384, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

107. 仿真 2.679s；物体中心 (0.45621, -0.00052, 0.41802) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 3, "support_height_m": 0.06551091223656613, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

108. 仿真 2.696s；物体中心 (0.45628, -0.00052, 0.41777) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 4, "support_height_m": 0.06544094430722698, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

109. 仿真 2.713s；物体中心 (0.45633, -0.00052, 0.41750) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 5, "support_height_m": 0.06539476697372144, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

110. 仿真 2.729s；物体中心 (0.45637, -0.00052, 0.41724) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 6, "support_height_m": 0.0653643996962937, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

111. 仿真 2.746s；物体中心 (0.45639, -0.00052, 0.41697) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 7, "support_height_m": 0.06534442859671266, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

112. 仿真 2.763s；物体中心 (0.45641, -0.00052, 0.41670) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 8, "support_height_m": 0.06533130488956568, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

113. 仿真 2.779s；物体中心 (0.45642, -0.00052, 0.41643) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 9, "support_height_m": 0.06532265096693678, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

114. 仿真 2.796s；物体中心 (0.45643, -0.00052, 0.41616) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 10, "support_height_m": 0.06531700925659353, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

115. 仿真 2.813s；物体中心 (0.45643, -0.00052, 0.41588) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 11, "support_height_m": 0.06531330305106853, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

116. 仿真 2.829s；物体中心 (0.45644, -0.00052, 0.41561) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 12, "support_height_m": 0.06531086856816914, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

117. 仿真 2.846s；物体中心 (0.45644, -0.00052, 0.41534) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 13, "support_height_m": 0.06530927094327015, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

118. 仿真 2.863s；物体中心 (0.45645, -0.00052, 0.41506) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 14, "support_height_m": 0.06530819655516325, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

119. 仿真 2.879s；物体中心 (0.45645, -0.00052, 0.41479) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 15, "support_height_m": 0.06530751981917562, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

120. 仿真 2.896s；物体中心 (0.45645, -0.00052, 0.41452) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 16, "support_height_m": 0.06530707461612922, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

121. 仿真 2.913s；物体中心 (0.45645, -0.00052, 0.41424) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 17, "support_height_m": 0.06530678137437826, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

122. 仿真 2.929s；物体中心 (0.45646, -0.00052, 0.41397) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 18, "support_height_m": 0.06530656376852814, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

123. 仿真 2.946s；物体中心 (0.45646, -0.00052, 0.41370) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 19, "support_height_m": 0.06530644866792457, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

124. 仿真 2.963s；物体中心 (0.45646, -0.00052, 0.41342) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 20, "support_height_m": 0.06530637086935168, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

125. 仿真 2.979s；物体中心 (0.45646, -0.00052, 0.41315) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 21, "support_height_m": 0.06530631874608726, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

126. 仿真 2.996s；物体中心 (0.45647, -0.00052, 0.41288) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 22, "support_height_m": 0.06530625513241889, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

127. 仿真 3.013s；物体中心 (0.45647, -0.00052, 0.41260) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 23, "support_height_m": 0.06530624611475733, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

128. 仿真 3.029s；物体中心 (0.45647, -0.00052, 0.41233) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 24, "support_height_m": 0.06530623748967969, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

129. 仿真 3.046s；物体中心 (0.45647, -0.00052, 0.41205) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 25, "support_height_m": 0.0653062305817802, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

130. 仿真 3.063s；物体中心 (0.45648, -0.00052, 0.41178) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 26, "support_height_m": 0.06530622539709106, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

131. 仿真 3.079s；物体中心 (0.45648, -0.00052, 0.41151) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 27, "support_height_m": 0.06530619684522493, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

132. 仿真 3.096s；物体中心 (0.45648, -0.00052, 0.41123) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 28, "support_height_m": 0.0653062059192817, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

133. 仿真 3.113s；物体中心 (0.45648, -0.00052, 0.41096) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 29, "support_height_m": 0.06530620973816058, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

134. 仿真 3.129s；物体中心 (0.45649, -0.00052, 0.41069) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 30, "support_height_m": 0.06530621123180985, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

135. 仿真 3.146s；物体中心 (0.45649, -0.00052, 0.41041) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 31, "support_height_m": 0.06530618763911882, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

136. 仿真 3.163s；物体中心 (0.45649, -0.00052, 0.41014) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 32, "support_height_m": 0.06530619924659398, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

137. 仿真 3.179s；物体中心 (0.45649, -0.00052, 0.40986) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 33, "support_height_m": 0.06530620466721081, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

138. 仿真 3.196s；物体中心 (0.45650, -0.00052, 0.40959) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 34, "support_height_m": 0.0653062083669139, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

139. 仿真 3.213s；物体中心 (0.45650, -0.00052, 0.40932) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 35, "support_height_m": 0.06530617686469879, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

140. 仿真 3.229s；物体中心 (0.45650, -0.00052, 0.40904) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 36, "support_height_m": 0.06530619430282517, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

141. 仿真 3.246s；物体中心 (0.45650, -0.00052, 0.40877) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 37, "support_height_m": 0.06530620257189874, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

142. 仿真 3.263s；物体中心 (0.45651, -0.00052, 0.40850) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 38, "support_height_m": 0.0653062065489453, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

143. 仿真 3.279s；物体中心 (0.45651, -0.00052, 0.40822) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 39, "support_height_m": 0.06530620843087545, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

144. 仿真 3.296s；物体中心 (0.45651, -0.00052, 0.40795) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 40, "support_height_m": 0.06530618558261377, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

145. 仿真 3.313s；物体中心 (0.45651, -0.00052, 0.40768) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 41, "support_height_m": 0.06530619730335645, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

146. 仿真 3.329s；物体中心 (0.45652, -0.00052, 0.40740) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 42, "support_height_m": 0.06530620285408782, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

147. 仿真 3.346s；物体中心 (0.45652, -0.00052, 0.40713) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 43, "support_height_m": 0.06530620548901027, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

148. 仿真 3.363s；物体中心 (0.45652, -0.00052, 0.40686) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 44, "support_height_m": 0.06530617892258199, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

149. 仿真 3.379s；物体中心 (0.45652, -0.00052, 0.40658) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 45, "support_height_m": 0.06530619299353287, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

150. 仿真 3.396s；物体中心 (0.45653, -0.00052, 0.40631) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 46, "support_height_m": 0.06530619963702494, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

151. 仿真 3.413s；物体中心 (0.45653, -0.00052, 0.40603) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 47, "support_height_m": 0.06530620280269357, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

152. 仿真 3.429s；物体中心 (0.45653, -0.00052, 0.40576) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 48, "support_height_m": 0.06530620425913707, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

153. 仿真 3.446s；物体中心 (0.45653, -0.00052, 0.40549) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 49, "support_height_m": 0.06530618153870923, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

154. 仿真 3.463s；物体中心 (0.45654, -0.00052, 0.40521) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 50, "support_height_m": 0.06530619295635558, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

155. 仿真 3.479s；物体中心 (0.45654, -0.00052, 0.40494) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 51, "support_height_m": 0.06530619835351263, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

156. 仿真 3.496s；物体中心 (0.45654, -0.00052, 0.40467) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 52, "support_height_m": 0.06530620090771358, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

157. 仿真 3.513s；物体中心 (0.45654, -0.00052, 0.40439) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 53, "support_height_m": 0.06530616969468735, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

158. 仿真 3.529s；物体中心 (0.45655, -0.00052, 0.40412) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 54, "support_height_m": 0.06530618616797426, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

159. 仿真 3.546s；物体中心 (0.45655, -0.00052, 0.40384) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 55, "support_height_m": 0.06530619391482002, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

160. 仿真 3.563s；物体中心 (0.45655, -0.00052, 0.40357) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 56, "support_height_m": 0.06530619760244182, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

161. 仿真 3.579s；物体中心 (0.45655, -0.00052, 0.40330) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 57, "support_height_m": 0.06530619932207632, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

162. 仿真 3.596s；物体中心 (0.45656, -0.00052, 0.40302) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 58, "support_height_m": 0.06530617829547923, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

163. 仿真 3.613s；物体中心 (0.45656, -0.00052, 0.40275) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 59, "support_height_m": 0.06530619041407136, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

164. 仿真 3.629s；物体中心 (0.45656, -0.00052, 0.40248) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 60, "support_height_m": 0.06530619629905912, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

165. 仿真 3.646s；物体中心 (0.45656, -0.00052, 0.40220) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 61, "support_height_m": 0.0653061991867868, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

166. 仿真 3.663s；物体中心 (0.45657, -0.00052, 0.40193) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 62, "support_height_m": 0.065306168679678, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

167. 仿真 3.679s；物体中心 (0.45657, -0.00052, 0.40166) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 63, "support_height_m": 0.06530618506400283, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

168. 仿真 3.696s；物体中心 (0.45657, -0.00052, 0.40138) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 64, "support_height_m": 0.06530619280284662, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

169. 仿真 3.713s；物体中心 (0.45657, -0.00052, 0.40111) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 65, "support_height_m": 0.06530619650740657, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

170. 仿真 3.729s；物体中心 (0.45658, -0.00052, 0.40083) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 66, "support_height_m": 0.06530619824802152, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

171. 仿真 3.746s；物体中心 (0.45658, -0.00052, 0.40056) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 67, "support_height_m": 0.0653061763668857, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

172. 仿真 3.763s；物体中心 (0.45658, -0.00052, 0.40029) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 68, "support_height_m": 0.06530618755294858, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

173. 仿真 3.779s；物体中心 (0.45658, -0.00052, 0.40001) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 69, "support_height_m": 0.06530619286178006, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

174. 仿真 3.796s；物体中心 (0.45659, -0.00052, 0.39974) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 70, "support_height_m": 0.06530619539008711, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

175. 仿真 3.813s；物体中心 (0.45659, -0.00052, 0.39947) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 71, "support_height_m": 0.06530619653268291, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

176. 仿真 3.829s；物体中心 (0.45659, -0.00052, 0.39919) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 72, "support_height_m": 0.0653061739329354, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

177. 仿真 3.846s；物体中心 (0.45659, -0.00052, 0.39892) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 73, "support_height_m": 0.06530618498112158, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

178. 仿真 3.863s；物体中心 (0.45660, -0.00052, 0.39865) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 74, "support_height_m": 0.06530619027188861, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

179. 仿真 3.879s；物体中心 (0.45660, -0.00052, 0.39837) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 75, "support_height_m": 0.06530619281977516, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

180. 仿真 3.896s；物体中心 (0.45660, -0.00052, 0.39810) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 76, "support_height_m": 0.06530616283650642, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

181. 仿真 3.913s；物体中心 (0.45660, -0.00052, 0.39782) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 77, "support_height_m": 0.06530617874293551, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

182. 仿真 3.929s；物体中心 (0.45661, -0.00052, 0.39755) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 78, "support_height_m": 0.06530618624530833, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

183. 仿真 3.946s；物体中心 (0.45661, -0.00052, 0.39728) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 79, "support_height_m": 0.06530618983356339, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

184. 仿真 3.963s；物体中心 (0.45661, -0.00052, 0.39700) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 80, "support_height_m": 0.06530619152060178, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

185. 仿真 3.979s；物体中心 (0.45661, -0.00052, 0.39673) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 81, "support_height_m": 0.0653061661270951, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

186. 仿真 3.996s；物体中心 (0.45662, -0.00052, 0.39646) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 82, "support_height_m": 0.06530618039057937, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

187. 仿真 4.013s；物体中心 (0.45662, -0.00052, 0.39618) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 83, "support_height_m": 0.06530618734861829, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

188. 仿真 4.029s；物体中心 (0.45662, -0.00052, 0.39591) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 84, "support_height_m": 0.0653061908116898, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

189. 仿真 4.046s；物体中心 (0.45662, -0.00052, 0.39563) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 85, "support_height_m": 0.06530619251186771, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

190. 仿真 4.063s；物体中心 (0.45663, -0.00052, 0.39536) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 86, "support_height_m": 0.06530617133528686, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

191. 仿真 4.079s；物体中心 (0.45663, -0.00052, 0.39509) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 87, "support_height_m": 0.06530618223441947, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

192. 仿真 4.096s；物体中心 (0.45663, -0.00052, 0.39481) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 88, "support_height_m": 0.06530618742914777, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

193. 仿真 4.113s；物体中心 (0.45663, -0.00052, 0.39454) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 89, "support_height_m": 0.06530618991857058, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

194. 仿真 4.129s；物体中心 (0.45664, -0.00052, 0.39427) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 90, "support_height_m": 0.06530619105532691, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

195. 仿真 4.146s；物体中心 (0.45664, -0.00052, 0.39399) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 91, "support_height_m": 0.06530616912244579, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

196. 仿真 4.163s；物体中心 (0.45664, -0.00052, 0.39372) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 92, "support_height_m": 0.06530617987175003, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

197. 仿真 4.179s；物体中心 (0.45665, -0.00052, 0.39345) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 93, "support_height_m": 0.06530618503167696, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

198. 仿真 4.196s；物体中心 (0.45665, -0.00052, 0.39317) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 94, "support_height_m": 0.06530618752417686, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

199. 仿真 4.213s；物体中心 (0.45665, -0.00052, 0.39290) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 95, "support_height_m": 0.06530615844415769, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

200. 仿真 4.229s；物体中心 (0.45665, -0.00052, 0.39262) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 96, "support_height_m": 0.0653061738868042, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

201. 仿真 4.246s；物体中心 (0.45666, -0.00052, 0.39235) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 97, "support_height_m": 0.0653061811831583, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

202. 仿真 4.263s；物体中心 (0.45666, -0.00052, 0.39208) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 98, "support_height_m": 0.06530618468322338, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

203. 仿真 4.279s；物体中心 (0.45666, -0.00052, 0.39180) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 99, "support_height_m": 0.06530618633425567, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

204. 仿真 4.296s；物体中心 (0.45666, -0.00052, 0.39153) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 100, "support_height_m": 0.06530616169134111, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

205. 仿真 4.313s；物体中心 (0.45667, -0.00052, 0.39126) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 101, "support_height_m": 0.06530617433551515, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

206. 仿真 4.329s；物体中心 (0.45667, -0.00052, 0.39098) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 102, "support_height_m": 0.06530619512119888, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

207. 仿真 4.346s；物体中心 (0.45667, -0.00052, 0.39071) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 103, "support_height_m": 0.06530620547780407, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

208. 仿真 4.363s；物体中心 (0.45667, -0.00052, 0.39043) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 104, "support_height_m": 0.0653062107991535, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

209. 仿真 4.379s；物体中心 (0.45667, -0.00052, 0.39016) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 105, "support_height_m": 0.06530619164522171, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

210. 仿真 4.396s；物体中心 (0.45668, -0.00052, 0.38989) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 106, "support_height_m": 0.06530620353783564, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

211. 仿真 4.413s；物体中心 (0.45668, -0.00052, 0.38961) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 107, "support_height_m": 0.06530621069893064, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

212. 仿真 4.429s；物体中心 (0.45668, -0.00052, 0.38934) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 108, "support_height_m": 0.06530622691302833, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

213. 仿真 4.446s；物体中心 (0.45669, -0.00052, 0.38907) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 109, "support_height_m": 0.06530621407302016, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

214. 仿真 4.463s；物体中心 (0.45669, -0.00052, 0.38879) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 110, "support_height_m": 0.06530622878138685, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

215. 仿真 4.479s；物体中心 (0.45669, -0.00052, 0.38852) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 111, "support_height_m": 0.06530623620271403, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

216. 仿真 4.496s；物体中心 (0.45669, -0.00052, 0.38824) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 112, "support_height_m": 0.06530624002760109, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

217. 仿真 4.513s；物体中心 (0.45670, -0.00052, 0.38797) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 113, "support_height_m": 0.06530622090678768, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

218. 仿真 4.529s；物体中心 (0.45670, -0.00052, 0.38770) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 114, "support_height_m": 0.06530623205605866, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

219. 仿真 4.546s；物体中心 (0.45670, -0.00052, 0.38742) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 115, "support_height_m": 0.06530624790592472, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

220. 仿真 4.563s；物体中心 (0.45670, -0.00052, 0.38715) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 116, "support_height_m": 0.06530625595924713, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

221. 仿真 4.579s；物体中心 (0.45671, -0.00052, 0.38688) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 117, "support_height_m": 0.06530623858691512, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

222. 仿真 4.596s；物体中心 (0.45671, -0.00052, 0.38660) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 118, "support_height_m": 0.06530625106975552, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

223. 仿真 4.613s；物体中心 (0.45671, -0.00052, 0.38633) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 119, "support_height_m": 0.06530625728004155, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

224. 仿真 4.629s；物体中心 (0.45671, -0.00052, 0.38605) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 120, "support_height_m": 0.06530621679174858, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

225. 仿真 4.646s；物体中心 (0.45671, -0.00052, 0.38578) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 121, "support_height_m": 0.0653062398806461, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

226. 仿真 4.663s；物体中心 (0.45672, -0.00052, 0.38551) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 122, "support_height_m": 0.0653062509382708, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

227. 仿真 4.679s；物体中心 (0.45672, -0.00053, 0.38523) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 123, "support_height_m": 0.06530625636525927, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

228. 仿真 4.696s；物体中心 (0.45672, -0.00053, 0.38496) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 124, "support_height_m": 0.06530622235959326, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

229. 仿真 4.713s；物体中心 (0.45672, -0.00053, 0.38469) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 125, "support_height_m": 0.06530624155814059, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

230. 仿真 4.729s；物体中心 (0.45673, -0.00053, 0.38441) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 126, "support_height_m": 0.06530625078955325, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

231. 仿真 4.746s；物体中心 (0.45673, -0.00053, 0.38414) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 127, "support_height_m": 0.06530625533467198, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

232. 仿真 4.763s；物体中心 (0.45673, -0.00053, 0.38386) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 128, "support_height_m": 0.06530622664402112, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

233. 仿真 4.779s；物体中心 (0.45673, -0.00053, 0.38359) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 129, "support_height_m": 0.06530624259939553, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

234. 仿真 4.796s；物体中心 (0.45674, -0.00053, 0.38332) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 130, "support_height_m": 0.06530625167500957, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

235. 仿真 4.813s；物体中心 (0.45674, -0.00053, 0.38304) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 131, "support_height_m": 0.06530625637065225, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

236. 仿真 4.829s；物体中心 (0.45674, -0.00053, 0.38277) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 132, "support_height_m": 0.06530623769039566, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

237. 仿真 4.846s；物体中心 (0.45674, -0.00053, 0.38249) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 133, "support_height_m": 0.06530624899371026, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

238. 仿真 4.863s；物体中心 (0.45675, -0.00053, 0.38222) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 134, "support_height_m": 0.06530625455058979, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

239. 仿真 4.879s；物体中心 (0.45675, -0.00053, 0.38195) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 135, "support_height_m": 0.06530621456851553, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

240. 仿真 4.896s；物体中心 (0.45675, -0.00053, 0.38167) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 136, "support_height_m": 0.06530623699085895, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

241. 仿真 4.913s；物体中心 (0.45675, -0.00053, 0.38140) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 137, "support_height_m": 0.06530624771104425, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

242. 仿真 4.929s；物体中心 (0.45676, -0.00053, 0.38113) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 138, "support_height_m": 0.06530625296296402, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

243. 仿真 4.946s；物体中心 (0.45676, -0.00053, 0.38085) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 139, "support_height_m": 0.06530621304461587, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

244. 仿真 4.963s；物体中心 (0.45676, -0.00053, 0.38058) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 140, "support_height_m": 0.06530623525318653, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

245. 仿真 4.979s；物体中心 (0.45676, -0.00053, 0.38030) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 141, "support_height_m": 0.06530624586250065, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

246. 仿真 4.996s；物体中心 (0.45677, -0.00053, 0.38003) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 142, "support_height_m": 0.06530625105670489, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

247. 仿真 5.013s；物体中心 (0.45677, -0.00053, 0.37976) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 143, "support_height_m": 0.065306217846577, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

248. 仿真 5.029s；物体中心 (0.45677, -0.00053, 0.37948) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 144, "support_height_m": 0.06530623652020426, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

249. 仿真 5.046s；物体中心 (0.45677, -0.00053, 0.37921) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 145, "support_height_m": 0.06530624550804918, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

250. 仿真 5.063s；物体中心 (0.45678, -0.00053, 0.37894) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 146, "support_height_m": 0.06530624993924306, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

251. 仿真 5.079s；物体中心 (0.45678, -0.00053, 0.37866) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 147, "support_height_m": 0.06530622196039733, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

252. 仿真 5.096s；物体中心 (0.45678, -0.00053, 0.37839) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 148, "support_height_m": 0.06530623752043933, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

253. 仿真 5.113s；物体中心 (0.45678, -0.00053, 0.37811) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 149, "support_height_m": 0.06530624507247333, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

254. 仿真 5.129s；物体中心 (0.45679, -0.00053, 0.37784) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 150, "support_height_m": 0.06530624881222577, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

255. 仿真 5.146s；物体中心 (0.45679, -0.00053, 0.37757) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 151, "support_height_m": 0.06530622064294551, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

256. 仿真 5.163s；物体中心 (0.45679, -0.00053, 0.37729) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 152, "support_height_m": 0.06530623594122367, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

257. 仿真 5.179s；物体中心 (0.45679, -0.00053, 0.37702) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 153, "support_height_m": 0.06530624335603695, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

258. 仿真 5.196s；物体中心 (0.45680, -0.00053, 0.37675) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 154, "support_height_m": 0.06530624843376481, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

259. 仿真 5.213s；物体中心 (0.45680, -0.00053, 0.37647) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 155, "support_height_m": 0.06530623067070077, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

260. 仿真 5.229s；物体中心 (0.45680, -0.00053, 0.37620) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 156, "support_height_m": 0.06530624185983051, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

261. 仿真 5.246s；物体中心 (0.45680, -0.00053, 0.37592) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 157, "support_height_m": 0.06530624741186489, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

262. 仿真 5.263s；物体中心 (0.45681, -0.00053, 0.37565) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 158, "support_height_m": 0.06530620873051197, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

263. 仿真 5.279s；物体中心 (0.45681, -0.00053, 0.37538) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 159, "support_height_m": 0.06530623054943827, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

264. 仿真 5.296s；物体中心 (0.45681, -0.00053, 0.37510) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 160, "support_height_m": 0.06530624101230187, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

265. 仿真 5.313s；物体中心 (0.45681, -0.00053, 0.37483) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 161, "support_height_m": 0.06530624615894597, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

266. 仿真 5.329s；物体中心 (0.45682, -0.00053, 0.37456) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 162, "support_height_m": 0.06530620745573926, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

267. 仿真 5.346s；物体中心 (0.45682, -0.00053, 0.37428) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 163, "support_height_m": 0.06530622902538304, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

268. 仿真 5.363s；物体中心 (0.45682, -0.00053, 0.37401) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 164, "support_height_m": 0.06530623935310775, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

269. 仿真 5.379s；物体中心 (0.45682, -0.00053, 0.37373) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 165, "support_height_m": 0.06530624442503564, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

270. 仿真 5.396s；物体中心 (0.45683, -0.00053, 0.37346) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 166, "support_height_m": 0.06530620588736023, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

271. 仿真 5.413s；物体中心 (0.45683, -0.00053, 0.37319) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 167, "support_height_m": 0.06530622732688617, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

272. 仿真 5.429s；物体中心 (0.45683, -0.00053, 0.37291) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 168, "support_height_m": 0.0653062375911581, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

273. 仿真 5.446s；物体中心 (0.45683, -0.00053, 0.37264) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 169, "support_height_m": 0.06530624263348382, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

274. 仿真 5.463s；物体中心 (0.45684, -0.00053, 0.37237) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 170, "support_height_m": 0.06530621057021511, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

275. 仿真 5.479s；物体中心 (0.45684, -0.00053, 0.37209) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 171, "support_height_m": 0.06530622861854748, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

276. 仿真 5.496s；物体中心 (0.45684, -0.00053, 0.37182) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 172, "support_height_m": 0.065306237327513, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

277. 仿真 5.513s；物体中心 (0.45684, -0.00053, 0.37154) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 173, "support_height_m": 0.06530624163821401, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

278. 仿真 5.529s；物体中心 (0.45685, -0.00053, 0.37127) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 174, "support_height_m": 0.06530620938755193, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

279. 仿真 5.546s；物体中心 (0.45685, -0.00053, 0.37100) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 175, "support_height_m": 0.06530622716455063, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

280. 仿真 5.563s；物体中心 (0.45685, -0.00053, 0.37072) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 176, "support_height_m": 0.0653062372306079, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

281. 仿真 5.579s；物体中心 (0.45685, -0.00053, 0.37045) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 177, "support_height_m": 0.06530624244444472, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

282. 仿真 5.596s；物体中心 (0.45686, -0.00053, 0.37018) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 178, "support_height_m": 0.0653062109616224, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

283. 仿真 5.613s；物体中心 (0.45686, -0.00053, 0.36990) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 179, "support_height_m": 0.06530622905081918, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

284. 仿真 5.629s；物体中心 (0.45686, -0.00053, 0.36963) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 180, "support_height_m": 0.06530623784158505, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

285. 仿真 5.646s；物体中心 (0.45686, -0.00053, 0.36935) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 181, "support_height_m": 0.06530624223245803, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

286. 仿真 5.662s；物体中心 (0.45687, -0.00053, 0.36908) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 182, "support_height_m": 0.06530621038013916, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

287. 仿真 5.679s；物体中心 (0.45687, -0.00053, 0.36881) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 183, "support_height_m": 0.06530622803673784, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

288. 仿真 5.696s；物体中心 (0.45687, -0.00053, 0.36853) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 184, "support_height_m": 0.06530623656235372, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

289. 仿真 5.712s；物体中心 (0.45687, -0.00053, 0.36826) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 185, "support_height_m": 0.06530624078674076, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

290. 仿真 5.729s；物体中心 (0.45688, -0.00053, 0.36799) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 186, "support_height_m": 0.06530621414064751, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

291. 仿真 5.746s；物体中心 (0.45688, -0.00053, 0.36771) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 187, "support_height_m": 0.06530622897098737, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

292. 仿真 5.762s；物体中心 (0.45688, -0.00053, 0.36744) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 188, "support_height_m": 0.06530623619591451, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

293. 仿真 5.779s；物体中心 (0.45688, -0.00053, 0.36716) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 189, "support_height_m": 0.06530623979635934, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

294. 仿真 5.796s；物体中心 (0.45688, -0.00053, 0.36689) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 190, "support_height_m": 0.06530621297032382, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

295. 仿真 5.812s；物体中心 (0.45689, -0.00053, 0.36662) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 191, "support_height_m": 0.0653062275651612, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

296. 仿真 5.829s；物体中心 (0.45689, -0.00053, 0.36634) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 192, "support_height_m": 0.06530623466861499, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

297. 仿真 5.846s；物体中心 (0.45689, -0.00053, 0.36607) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 193, "support_height_m": 0.06530623820167274, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

298. 仿真 5.862s；物体中心 (0.45689, -0.00053, 0.36580) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 194, "support_height_m": 0.06530621147188516, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

299. 仿真 5.879s；物体中心 (0.45690, -0.00053, 0.36552) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 195, "support_height_m": 0.06530622598084386, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

300. 仿真 5.896s；物体中心 (0.45690, -0.00053, 0.36525) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 196, "support_height_m": 0.06530623304208695, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

301. 仿真 5.912s；物体中心 (0.45690, -0.00053, 0.36498) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 197, "support_height_m": 0.06530623655489509, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

302. 仿真 5.929s；物体中心 (0.45690, -0.00053, 0.36470) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 198, "support_height_m": 0.06530620994691642, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

303. 仿真 5.946s；物体中心 (0.45691, -0.00053, 0.36443) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 199, "support_height_m": 0.06530622598222341, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

304. 仿真 5.962s；物体中心 (0.45691, -0.00053, 0.36415) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 200, "support_height_m": 0.0653062340527426, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

305. 仿真 5.979s；物体中心 (0.45691, -0.00053, 0.36388) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 201, "support_height_m": 0.06530623823613134, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

306. 仿真 5.996s；物体中心 (0.45691, -0.00053, 0.36361) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 202, "support_height_m": 0.06530621220219326, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

307. 仿真 6.012s；物体中心 (0.45692, -0.00053, 0.36333) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 203, "support_height_m": 0.0653062268687805, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

308. 仿真 6.029s；物体中心 (0.45692, -0.00053, 0.36306) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 204, "support_height_m": 0.06530623406028811, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

309. 仿真 6.046s；物体中心 (0.45692, -0.00053, 0.36279) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 205, "support_height_m": 0.06530623767205947, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

310. 仿真 6.062s；物体中心 (0.45692, -0.00053, 0.36251) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 206, "support_height_m": 0.06530621139466102, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

311. 仿真 6.079s；物体中心 (0.45693, -0.00053, 0.36224) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 207, "support_height_m": 0.06530622575686743, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

312. 仿真 6.096s；物体中心 (0.45693, -0.00053, 0.36197) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 208, "support_height_m": 0.06530623276388785, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

313. 仿真 6.112s；物体中心 (0.45693, -0.00053, 0.36169) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 209, "support_height_m": 0.06530623626196738, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

314. 仿真 6.129s；物体中心 (0.45693, -0.00053, 0.36142) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 210, "support_height_m": 0.06530621003808572, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

315. 仿真 6.146s；物体中心 (0.45694, -0.00053, 0.36114) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 211, "support_height_m": 0.06530622429416542, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

316. 仿真 6.162s；物体中心 (0.45694, -0.00053, 0.36087) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 212, "support_height_m": 0.06530623124533479, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

317. 仿真 6.179s；物体中心 (0.45694, -0.00053, 0.36060) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 213, "support_height_m": 0.06530623471360908, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

318. 仿真 6.196s；物体中心 (0.45694, -0.00053, 0.36032) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 214, "support_height_m": 0.06530620859868828, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

319. 仿真 6.212s；物体中心 (0.45694, -0.00053, 0.36005) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 215, "support_height_m": 0.06530622278651531, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

320. 仿真 6.229s；物体中心 (0.45695, -0.00053, 0.35978) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 216, "support_height_m": 0.06530622970565826, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

321. 仿真 6.246s；物体中心 (0.45695, -0.00053, 0.35950) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 217, "support_height_m": 0.06530623315972996, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

322. 仿真 6.262s；物体中心 (0.45695, -0.00053, 0.35923) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 218, "support_height_m": 0.0653062071611089, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

323. 仿真 6.279s；物体中心 (0.45695, -0.00053, 0.35895) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 219, "support_height_m": 0.06530622128671675, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

324. 仿真 6.296s；物体中心 (0.45696, -0.00053, 0.35868) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 220, "support_height_m": 0.06530622817840304, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

325. 仿真 6.312s；物体中心 (0.45696, -0.00053, 0.35841) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 221, "support_height_m": 0.06530623333432975, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

326. 仿真 6.329s；物体中心 (0.45696, -0.00053, 0.35813) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 222, "support_height_m": 0.06530620857342395, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

327. 仿真 6.346s；物体中心 (0.45696, -0.00053, 0.35786) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 223, "support_height_m": 0.06530622337005354, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

328. 仿真 6.362s；物体中心 (0.45697, -0.00053, 0.35759) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 224, "support_height_m": 0.0653062307168175, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

329. 仿真 6.379s；物体中心 (0.45697, -0.00053, 0.35731) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 225, "support_height_m": 0.06530623446308913, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

330. 仿真 6.396s；物体中心 (0.45697, -0.00053, 0.35704) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 226, "support_height_m": 0.06530620890282461, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

331. 仿真 6.412s；物体中心 (0.45697, -0.00053, 0.35677) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 227, "support_height_m": 0.06530622304068678, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

332. 仿真 6.429s；物体中心 (0.45697, -0.00053, 0.35649) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 228, "support_height_m": 0.06530622996822855, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

333. 仿真 6.446s；物体中心 (0.45698, -0.00053, 0.35622) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 229, "support_height_m": 0.06530623344571722, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

334. 仿真 6.462s；物体中心 (0.45698, -0.00053, 0.35595) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 230, "support_height_m": 0.0653062029511234, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

335. 仿真 6.479s；物体中心 (0.45698, -0.00053, 0.35567) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 231, "support_height_m": 0.06530621945650998, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

336. 仿真 6.496s；物体中心 (0.45698, -0.00053, 0.35540) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 232, "support_height_m": 0.0653062274439523, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

337. 仿真 6.512s；物体中心 (0.45699, -0.00053, 0.35513) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 233, "support_height_m": 0.06530623141744199, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

338. 仿真 6.529s；物体中心 (0.45699, -0.00053, 0.35485) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 234, "support_height_m": 0.06530620130457082, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

339. 仿真 6.546s；物体中心 (0.45699, -0.00053, 0.35458) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 235, "support_height_m": 0.06530621786756642, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

340. 仿真 6.562s；物体中心 (0.45699, -0.00053, 0.35431) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 236, "support_height_m": 0.06530622589699685, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

341. 仿真 6.579s；物体中心 (0.45699, -0.00053, 0.35403) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 237, "support_height_m": 0.06530622989814185, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

342. 仿真 6.596s；物体中心 (0.45700, -0.00053, 0.35376) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 238, "support_height_m": 0.06530619993867331, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

343. 仿真 6.612s；物体中心 (0.45700, -0.00053, 0.35348) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 239, "support_height_m": 0.0653062164475635, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

344. 仿真 6.629s；物体中心 (0.45700, -0.00053, 0.35321) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 240, "support_height_m": 0.06530622445528653, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

345. 仿真 6.646s；物体中心 (0.45700, -0.00053, 0.35294) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 241, "support_height_m": 0.06530622844977306, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

346. 仿真 6.662s；物体中心 (0.45701, -0.00053, 0.35266) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 242, "support_height_m": 0.06530619862396156, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

347. 仿真 6.679s；物体中心 (0.45701, -0.00053, 0.35239) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 243, "support_height_m": 0.06530621692019438, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

348. 仿真 6.696s；物体中心 (0.45701, -0.00053, 0.35212) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 244, "support_height_m": 0.06530622610848365, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

349. 仿真 6.712s；物体中心 (0.45701, -0.00053, 0.35184) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 245, "support_height_m": 0.06530623088527236, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

350. 仿真 6.729s；物体中心 (0.45701, -0.00053, 0.35157) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 246, "support_height_m": 0.06530619598149771, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

351. 仿真 6.746s；物体中心 (0.45702, -0.00053, 0.35130) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 247, "support_height_m": 0.06530621568230428, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

352. 仿真 6.762s；物体中心 (0.45702, -0.00053, 0.35102) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 248, "support_height_m": 0.06530622522694077, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

353. 仿真 6.779s；物体中心 (0.45702, -0.00053, 0.35075) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 249, "support_height_m": 0.0653062299929346, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

354. 仿真 6.796s；物体中心 (0.45702, -0.00053, 0.35048) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 250, "support_height_m": 0.06530619513561058, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

355. 仿真 6.812s；物体中心 (0.45703, -0.00053, 0.35020) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 251, "support_height_m": 0.06530621464615409, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

356. 仿真 6.829s；物体中心 (0.45703, -0.00053, 0.34993) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 252, "support_height_m": 0.0653062240676343, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

357. 仿真 6.846s；物体中心 (0.45703, -0.00053, 0.34966) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 253, "support_height_m": 0.06530622875325931, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

358. 仿真 6.862s；物体中心 (0.45703, -0.00053, 0.34938) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 254, "support_height_m": 0.06530623111613122, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

359. 仿真 6.879s；物体中心 (0.45703, -0.00053, 0.34911) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 255, "support_height_m": 0.0653062140620263, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

360. 仿真 6.896s；物体中心 (0.45704, -0.00053, 0.34884) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 256, "support_height_m": 0.06530622324299849, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

361. 仿真 6.912s；物体中心 (0.45704, -0.00053, 0.34856) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 257, "support_height_m": 0.06530622775296965, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

362. 仿真 6.929s；物体中心 (0.45704, -0.00053, 0.34829) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 258, "support_height_m": 0.0653062299944072, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

363. 仿真 6.946s；物体中心 (0.45704, -0.00053, 0.34802) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 259, "support_height_m": 0.06530621293232484, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

364. 仿真 6.962s；物体中心 (0.45704, -0.00053, 0.34774) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 260, "support_height_m": 0.06530622202406654, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

365. 仿真 6.979s；物体中心 (0.45705, -0.00053, 0.34747) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 261, "support_height_m": 0.06530622648413162, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

366. 仿真 6.996s；物体中心 (0.45705, -0.00053, 0.34720) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 262, "support_height_m": 0.06530622869675844, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

367. 仿真 7.012s；物体中心 (0.45705, -0.00053, 0.34692) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 263, "support_height_m": 0.0653062116922432, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

368. 仿真 7.029s；物体中心 (0.45705, -0.00053, 0.34665) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 264, "support_height_m": 0.06530622073993296, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

369. 仿真 7.046s；物体中心 (0.45706, -0.00053, 0.34638) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 265, "support_height_m": 0.06530622517924006, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

370. 仿真 7.062s；物体中心 (0.45706, -0.00053, 0.34610) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 266, "support_height_m": 0.06530622939739864, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

371. 仿真 7.079s；物体中心 (0.45706, -0.00053, 0.34583) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 267, "support_height_m": 0.06530621377414726, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

372. 仿真 7.096s；物体中心 (0.45706, -0.00053, 0.34556) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 268, "support_height_m": 0.06530622364894516, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

373. 仿真 7.112s；物体中心 (0.45706, -0.00053, 0.34528) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 269, "support_height_m": 0.0653062286376924, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

374. 仿真 7.129s；物体中心 (0.45707, -0.00053, 0.34501) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 270, "support_height_m": 0.06530623120646976, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

375. 仿真 7.146s；物体中心 (0.45707, -0.00053, 0.34474) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 271, "support_height_m": 0.06530620627673309, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

376. 仿真 7.162s；物体中心 (0.45707, -0.00053, 0.34446) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 272, "support_height_m": 0.06530621947219636, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

377. 仿真 7.179s；物体中心 (0.45707, -0.00053, 0.34419) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 273, "support_height_m": 0.06530622594139888, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

378. 仿真 7.196s；物体中心 (0.45707, -0.00053, 0.34392) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 274, "support_height_m": 0.06530622919539561, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

379. 仿真 7.212s；物体中心 (0.45708, -0.00053, 0.34364) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 275, "support_height_m": 0.06530620469656614, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

380. 仿真 7.229s；物体中心 (0.45708, -0.00053, 0.34337) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 276, "support_height_m": 0.06530621801296303, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

381. 仿真 7.246s；物体中心 (0.45708, -0.00053, 0.34310) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 277, "support_height_m": 0.06530622455189639, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

382. 仿真 7.262s；物体中心 (0.45708, -0.00053, 0.34282) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 278, "support_height_m": 0.06530622785080782, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

383. 仿真 7.279s；物体中心 (0.45708, -0.00053, 0.34255) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 279, "support_height_m": 0.06530619885450274, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

384. 仿真 7.296s；物体中心 (0.45709, -0.00053, 0.34228) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 280, "support_height_m": 0.06530621453848058, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

385. 仿真 7.312s；物体中心 (0.45709, -0.00053, 0.34200) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 281, "support_height_m": 0.06530622216717763, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

386. 仿真 7.329s；物体中心 (0.45709, -0.00053, 0.34173) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 282, "support_height_m": 0.06530622599261203, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

387. 仿真 7.346s；物体中心 (0.45709, -0.00053, 0.34146) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 283, "support_height_m": 0.06530619737909973, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

388. 仿真 7.362s；物体中心 (0.45709, -0.00053, 0.34118) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 284, "support_height_m": 0.0653062131501544, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

389. 仿真 7.379s；物体中心 (0.45709, -0.00053, 0.34091) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 285, "support_height_m": 0.06530622083581823, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

390. 仿真 7.396s；物体中心 (0.45710, -0.00053, 0.34064) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 286, "support_height_m": 0.06530622469821278, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

391. 仿真 7.412s；物体中心 (0.45710, -0.00053, 0.34036) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 287, "support_height_m": 0.06530619074294895, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

392. 仿真 7.429s；物体中心 (0.45710, -0.00053, 0.34009) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 288, "support_height_m": 0.06530620932440151, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

393. 仿真 7.446s；物体中心 (0.45710, -0.00053, 0.33982) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 289, "support_height_m": 0.06530621831030846, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

394. 仿真 7.462s；物体中心 (0.45710, -0.00053, 0.33954) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 290, "support_height_m": 0.06530622279192402, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

395. 仿真 7.479s；物体中心 (0.45711, -0.00053, 0.33927) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 291, "support_height_m": 0.06530622726684897, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

396. 仿真 7.496s；物体中心 (0.45711, -0.00053, 0.33900) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 292, "support_height_m": 0.06530621227057634, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

397. 仿真 7.512s；物体中心 (0.45711, -0.00053, 0.33873) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 293, "support_height_m": 0.06530622207092406, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

398. 仿真 7.529s；物体中心 (0.45711, -0.00053, 0.33845) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 294, "support_height_m": 0.06530622706479658, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

399. 仿真 7.546s；物体中心 (0.45711, -0.00053, 0.33818) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 295, "support_height_m": 0.06530622966582054, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

400. 仿真 7.562s；物体中心 (0.45711, -0.00053, 0.33791) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 296, "support_height_m": 0.06530621350654027, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

401. 仿真 7.579s；物体中心 (0.45712, -0.00053, 0.33763) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 297, "support_height_m": 0.06530622246893537, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

402. 仿真 7.596s；物体中心 (0.45712, -0.00053, 0.33736) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 298, "support_height_m": 0.06530622691961034, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

403. 仿真 7.612s；物体中心 (0.45712, -0.00053, 0.33709) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 299, "support_height_m": 0.065306229167976, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

404. 仿真 7.629s；物体中心 (0.45712, -0.00053, 0.33681) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 300, "support_height_m": 0.06530620475028065, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

405. 仿真 7.646s；物体中心 (0.45712, -0.00053, 0.33654) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 301, "support_height_m": 0.06530621748038361, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

406. 仿真 7.662s；物体中心 (0.45713, -0.00053, 0.33627) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 302, "support_height_m": 0.06530622372556227, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

407. 仿真 7.679s；物体中心 (0.45713, -0.00053, 0.33600) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 303, "support_height_m": 0.06530622687429745, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

408. 仿真 7.696s；物体中心 (0.45713, -0.00053, 0.33572) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 304, "support_height_m": 0.06530619851555768, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

409. 仿真 7.712s；物体中心 (0.45713, -0.00053, 0.33545) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 305, "support_height_m": 0.06530621380326168, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

410. 仿真 7.729s；物体中心 (0.45713, -0.00053, 0.33518) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 306, "support_height_m": 0.06530622125589546, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

411. 仿真 7.746s；物体中心 (0.45713, -0.00053, 0.33490) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 307, "support_height_m": 0.06530622500620381, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

412. 仿真 7.762s；物体中心 (0.45713, -0.00053, 0.33463) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 308, "support_height_m": 0.06530619706787459, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

413. 仿真 7.779s；物体中心 (0.45714, -0.00053, 0.33436) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 309, "support_height_m": 0.06530621247926326, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

414. 仿真 7.796s；物体中心 (0.45714, -0.00053, 0.33408) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 310, "support_height_m": 0.06530622001063156, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

415. 仿真 7.812s；物体中心 (0.45714, -0.00053, 0.33381) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 311, "support_height_m": 0.06530622381350899, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

416. 仿真 7.829s；物体中心 (0.45714, -0.00053, 0.33354) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 312, "support_height_m": 0.06530619066829986, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

417. 仿真 7.846s；物体中心 (0.45714, -0.00053, 0.33326) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 313, "support_height_m": 0.06530620882751119, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

418. 仿真 7.862s；物体中心 (0.45714, -0.00053, 0.33299) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 314, "support_height_m": 0.06530621763288758, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

419. 仿真 7.879s；物体中心 (0.45715, -0.00053, 0.33272) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 315, "support_height_m": 0.06530622204382282, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

420. 仿真 7.896s；物体中心 (0.45715, -0.00053, 0.33245) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 316, "support_height_m": 0.06530622429504758, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

421. 仿真 7.912s；物体中心 (0.45715, -0.00053, 0.33217) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 317, "support_height_m": 0.06530620826305158, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

422. 仿真 7.929s；物体中心 (0.45715, -0.00053, 0.33190) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 318, "support_height_m": 0.06530621693629134, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

423. 仿真 7.946s；物体中心 (0.45715, -0.00053, 0.33163) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 319, "support_height_m": 0.06530622123950927, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

424. 仿真 7.962s；物体中心 (0.45715, -0.00053, 0.33135) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 320, "support_height_m": 0.06530622341433555, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

425. 仿真 7.979s；物体中心 (0.45715, -0.00053, 0.33108) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 321, "support_height_m": 0.06530620738713659, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

426. 仿真 7.996s；物体中心 (0.45716, -0.00053, 0.33081) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 322, "support_height_m": 0.0653062159941849, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

427. 仿真 8.012s；物体中心 (0.45716, -0.00053, 0.33053) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 323, "support_height_m": 0.06530622026077858, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

428. 仿真 8.029s；物体中心 (0.45716, -0.00053, 0.33026) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 324, "support_height_m": 0.0653062248320765, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

429. 仿真 8.046s；物体中心 (0.45716, -0.00053, 0.32999) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 325, "support_height_m": 0.06530620250206502, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

430. 仿真 8.062s；物体中心 (0.45716, -0.00053, 0.32972) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 326, "support_height_m": 0.06530621597373369, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

431. 仿真 8.079s；物体中心 (0.45716, -0.00053, 0.32944) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 327, "support_height_m": 0.06530622277092046, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

432. 仿真 8.096s；物体中心 (0.45716, -0.00053, 0.32917) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 328, "support_height_m": 0.06530622631560844, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

433. 仿真 8.112s；物体中心 (0.45717, -0.00053, 0.32890) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 329, "support_height_m": 0.06530619888924293, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

434. 仿真 8.129s；物体中心 (0.45717, -0.00053, 0.32863) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 330, "support_height_m": 0.06530621404080718, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

435. 仿真 8.146s；物体中心 (0.45717, -0.00053, 0.32835) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 331, "support_height_m": 0.06530622148174105, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

436. 仿真 8.162s；物体中心 (0.45717, -0.00053, 0.32808) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 332, "support_height_m": 0.06530622526327695, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

437. 仿真 8.179s；物体中心 (0.45717, -0.00053, 0.32781) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 333, "support_height_m": 0.06530619277278563, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

438. 仿真 8.196s；物体中心 (0.45717, -0.00053, 0.32753) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 334, "support_height_m": 0.06530621061399686, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

439. 仿真 8.212s；物体中心 (0.45717, -0.00053, 0.32726) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 335, "support_height_m": 0.06530621928863599, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

440. 仿真 8.229s；物体中心 (0.45717, -0.00053, 0.32699) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 336, "support_height_m": 0.06530622365242467, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

441. 仿真 8.246s；物体中心 (0.45717, -0.00053, 0.32672) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 337, "support_height_m": 0.06530622589462913, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

442. 仿真 8.262s；物体中心 (0.45718, -0.00053, 0.32644) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 338, "support_height_m": 0.06530621017986196, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

443. 仿真 8.279s；物体中心 (0.45718, -0.00053, 0.32617) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 339, "support_height_m": 0.06530621871303853, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

444. 仿真 8.296s；物体中心 (0.45718, -0.00053, 0.32590) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 340, "support_height_m": 0.06530622296359499, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

445. 仿真 8.312s；物体中心 (0.45718, -0.00053, 0.32562) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 341, "support_height_m": 0.06530622512521578, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

446. 仿真 8.329s；物体中心 (0.45718, -0.00053, 0.32535) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 342, "support_height_m": 0.06530620158537137, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

447. 仿真 8.346s；物体中心 (0.45718, -0.00053, 0.32508) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 343, "support_height_m": 0.06530621386151225, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

448. 仿真 8.362s；物体中心 (0.45718, -0.00053, 0.32481) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 344, "support_height_m": 0.06530621991736828, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

449. 仿真 8.379s；物体中心 (0.45718, -0.00053, 0.32453) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 345, "support_height_m": 0.06530622299826276, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

450. 仿真 8.396s；物体中心 (0.45718, -0.00053, 0.32426) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 346, "support_height_m": 0.06530619569731462, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

451. 仿真 8.412s；物体中心 (0.45719, -0.00053, 0.32399) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 347, "support_height_m": 0.06530621045318326, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

452. 仿真 8.429s；物体中心 (0.45719, -0.00053, 0.32372) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 348, "support_height_m": 0.06530621768560271, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

453. 仿真 8.446s；物体中心 (0.45719, -0.00053, 0.32344) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 349, "support_height_m": 0.06530622135690793, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

454. 仿真 8.462s；物体中心 (0.45719, -0.00053, 0.32317) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 350, "support_height_m": 0.06530618930148711, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

455. 仿真 8.479s；物体中心 (0.45719, -0.00053, 0.32290) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 351, "support_height_m": 0.06530620686205686, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

456. 仿真 8.496s；物体中心 (0.45719, -0.00053, 0.32262) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 352, "support_height_m": 0.06530621541035131, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

457. 仿真 8.512s；物体中心 (0.45719, -0.00053, 0.32235) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 353, "support_height_m": 0.06530621972111209, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

458. 仿真 8.529s；物体中心 (0.45719, -0.00053, 0.32208) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 354, "support_height_m": 0.06530622194609294, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

459. 仿真 8.546s；物体中心 (0.45719, -0.00053, 0.32181) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 355, "support_height_m": 0.06530620646596468, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

460. 仿真 8.562s；物体中心 (0.45719, -0.00053, 0.32153) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 356, "support_height_m": 0.06530621489104126, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

461. 仿真 8.579s；物体中心 (0.45719, -0.00053, 0.32126) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 357, "support_height_m": 0.06530621910069445, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

462. 仿真 8.596s；物体中心 (0.45720, -0.00053, 0.32099) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 358, "support_height_m": 0.06530622125213083, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

463. 仿真 8.612s；物体中心 (0.45720, -0.00053, 0.32072) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 359, "support_height_m": 0.06530619804928975, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

464. 仿真 8.629s；物体中心 (0.45720, -0.00053, 0.32044) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 360, "support_height_m": 0.06530621016964432, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

465. 仿真 8.646s；物体中心 (0.45720, -0.00053, 0.32017) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 361, "support_height_m": 0.06530621616324606, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

466. 仿真 8.662s；物体中心 (0.45720, -0.00053, 0.31990) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 362, "support_height_m": 0.0653062192254011, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

467. 仿真 8.679s；物体中心 (0.45720, -0.00053, 0.31962) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 363, "support_height_m": 0.0653061923181996, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

468. 仿真 8.696s；物体中心 (0.45720, -0.00053, 0.31935) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 364, "support_height_m": 0.06530620688284867, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

469. 仿真 8.712s；物体中心 (0.45720, -0.00053, 0.31908) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 365, "support_height_m": 0.06530621403859632, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

470. 仿真 8.729s；物体中心 (0.45720, -0.00053, 0.31881) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 366, "support_height_m": 0.06530621768203985, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

471. 仿真 8.746s；物体中心 (0.45720, -0.00053, 0.31853) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 367, "support_height_m": 0.06530618608736016, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

472. 仿真 8.762s；物体中心 (0.45720, -0.00053, 0.31826) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 368, "support_height_m": 0.06530620341335873, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

473. 仿真 8.779s；物体中心 (0.45720, -0.00053, 0.31799) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 369, "support_height_m": 0.06530621186551193, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

474. 仿真 8.796s；物体中心 (0.45720, -0.00053, 0.31772) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 370, "support_height_m": 0.06530621614200612, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

475. 仿真 8.812s；物体中心 (0.45720, -0.00053, 0.31744) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 371, "support_height_m": 0.06530621836119659, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

476. 仿真 8.829s；物体中心 (0.45720, -0.00053, 0.31717) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 372, "support_height_m": 0.06530620311089542, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

477. 仿真 8.846s；物体中心 (0.45720, -0.00053, 0.31690) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 373, "support_height_m": 0.06530621143642154, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

478. 仿真 8.862s；物体中心 (0.45720, -0.00053, 0.31663) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 374, "support_height_m": 0.06530621561132888, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

479. 仿真 8.879s；物体中心 (0.45721, -0.00053, 0.31635) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 375, "support_height_m": 0.06530621775584894, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

480. 仿真 8.896s；物体中心 (0.45721, -0.00053, 0.31608) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 376, "support_height_m": 0.06530619487284284, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

481. 仿真 8.912s；物体中心 (0.45721, -0.00053, 0.31581) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 377, "support_height_m": 0.06530620684576958, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

482. 仿真 8.929s；物体中心 (0.45721, -0.00053, 0.31553) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 378, "support_height_m": 0.06530621278176559, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

483. 仿真 8.946s；物体中心 (0.45721, -0.00053, 0.31526) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 379, "support_height_m": 0.06530621582830776, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

484. 仿真 8.962s；物体中心 (0.45721, -0.00053, 0.31499) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 380, "support_height_m": 0.06530618929511543, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

485. 仿真 8.979s；物体中心 (0.45721, -0.00053, 0.31472) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 381, "support_height_m": 0.06530620367722835, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

486. 仿真 8.996s；物体中心 (0.45721, -0.00053, 0.31444) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 382, "support_height_m": 0.06530621075931309, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

487. 仿真 9.012s；物体中心 (0.45721, -0.00053, 0.31417) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 383, "support_height_m": 0.06530621437947408, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

488. 仿真 9.029s；物体中心 (0.45721, -0.00053, 0.31390) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 384, "support_height_m": 0.06530618322437762, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

489. 仿真 9.046s；物体中心 (0.45721, -0.00053, 0.31363) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 385, "support_height_m": 0.0653062003291535, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

490. 仿真 9.062s；物体中心 (0.45721, -0.00053, 0.31335) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 386, "support_height_m": 0.06530620869139911, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

491. 仿真 9.079s；物体中心 (0.45721, -0.00053, 0.31308) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 387, "support_height_m": 0.06530621293598159, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

492. 仿真 9.096s；物体中心 (0.45721, -0.00053, 0.31281) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 388, "support_height_m": 0.06530621514979855, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

493. 仿真 9.112s；物体中心 (0.45721, -0.00053, 0.31254) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 389, "support_height_m": 0.06530619255678409, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

494. 仿真 9.129s；物体中心 (0.45721, -0.00053, 0.31226) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 390, "support_height_m": 0.06530620445773509, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

495. 仿真 9.146s；物体中心 (0.45721, -0.00053, 0.31199) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 391, "support_height_m": 0.06530621037666583, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

496. 仿真 9.162s；物体中心 (0.45721, -0.00053, 0.31172) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 392, "support_height_m": 0.06530621342617154, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

497. 仿真 9.179s；物体中心 (0.45721, -0.00053, 0.31145) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 393, "support_height_m": 0.0653061871793446, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

498. 仿真 9.196s；物体中心 (0.45721, -0.00053, 0.31117) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 394, "support_height_m": 0.06530620143558878, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

499. 仿真 9.212s；物体中心 (0.45721, -0.00053, 0.31090) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 395, "support_height_m": 0.06530620847036699, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

500. 仿真 9.229s；物体中心 (0.45721, -0.00053, 0.31063) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 396, "support_height_m": 0.06530621207693943, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

501. 仿真 9.246s；物体中心 (0.45721, -0.00053, 0.31035) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 397, "support_height_m": 0.06530618124924073, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

502. 仿真 9.262s；物体中心 (0.45721, -0.00053, 0.31008) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 398, "support_height_m": 0.06530619819312282, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

503. 仿真 9.279s；物体中心 (0.45721, -0.00053, 0.30981) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 399, "support_height_m": 0.06530620649128528, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

504. 仿真 9.296s；物体中心 (0.45721, -0.00053, 0.30954) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 400, "support_height_m": 0.06530621071345423, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

505. 仿真 9.312s；物体中心 (0.45721, -0.00053, 0.30926) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 401, "support_height_m": 0.0653062129256654, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

506. 仿真 9.329s；物体中心 (0.45721, -0.00053, 0.30899) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 402, "support_height_m": 0.0653061905604363, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

507. 仿真 9.346s；物体中心 (0.45721, -0.00053, 0.30872) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 403, "support_height_m": 0.06530620235745853, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

508. 仿真 9.362s；物体中心 (0.45721, -0.00053, 0.30845) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 404, "support_height_m": 0.06530620823827903, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

509. 仿真 9.379s；物体中心 (0.45721, -0.00053, 0.30817) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 405, "support_height_m": 0.06530621127845196, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

510. 仿真 9.396s；物体中心 (0.45721, -0.00053, 0.30790) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 406, "support_height_m": 0.06530619375246854, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

511. 仿真 9.412s；物体中心 (0.45721, -0.00053, 0.30763) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 407, "support_height_m": 0.06530621240958925, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

512. 仿真 9.429s；物体中心 (0.45721, -0.00053, 0.30736) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 408, "support_height_m": 0.06530622194347288, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

513. 仿真 9.446s；物体中心 (0.45721, -0.00053, 0.30708) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 409, "support_height_m": 0.06530622703093324, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

514. 仿真 9.462s；物体中心 (0.45721, -0.00053, 0.30681) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 410, "support_height_m": 0.06530620232470419, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

515. 仿真 9.479s；物体中心 (0.45721, -0.00053, 0.30654) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 411, "support_height_m": 0.06530621713245129, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

516. 仿真 9.496s；物体中心 (0.45721, -0.00053, 0.30627) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 412, "support_height_m": 0.06530622454282024, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

517. 仿真 9.512s；物体中心 (0.45721, -0.00053, 0.30599) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 413, "support_height_m": 0.06530622840118555, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

518. 仿真 9.529s；物体中心 (0.45721, -0.00053, 0.30572) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 414, "support_height_m": 0.06530620711490294, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

519. 仿真 9.546s；物体中心 (0.45721, -0.00053, 0.30545) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 415, "support_height_m": 0.06530621932591098, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

520. 仿真 9.562s；物体中心 (0.45721, -0.00053, 0.30518) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 416, "support_height_m": 0.06530622546445904, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

521. 仿真 9.579s；物体中心 (0.45721, -0.00053, 0.30490) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 417, "support_height_m": 0.06530622866614344, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

522. 仿真 9.596s；物体中心 (0.45720, -0.00053, 0.30463) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 418, "support_height_m": 0.0653062070896565, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

523. 仿真 9.612s；物体中心 (0.45720, -0.00053, 0.30436) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 419, "support_height_m": 0.06530621906641948, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

524. 仿真 9.629s；物体中心 (0.45720, -0.00053, 0.30409) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 420, "support_height_m": 0.06530622266218103, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

525. 仿真 9.646s；物体中心 (0.45720, -0.00053, 0.30381) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 421, "support_height_m": 0.0653062242180028, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

526. 仿真 9.662s；物体中心 (0.45720, -0.00053, 0.30354) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 422, "support_height_m": 0.06530620162708554, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

527. 仿真 9.679s；物体中心 (0.45720, -0.00053, 0.30327) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 423, "support_height_m": 0.06530621286661152, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

528. 仿真 9.696s；物体中心 (0.45720, -0.00053, 0.30299) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 424, "support_height_m": 0.06530621839547002, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

529. 仿真 9.712s；物体中心 (0.45720, -0.00053, 0.30272) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 425, "support_height_m": 0.06530622121174363, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

530. 仿真 9.729s；物体中心 (0.45720, -0.00053, 0.30245) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 426, "support_height_m": 0.0653061995144657, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

531. 仿真 9.746s；物体中心 (0.45720, -0.00053, 0.30218) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 427, "support_height_m": 0.06530621126941988, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

532. 仿真 9.762s；物体中心 (0.45720, -0.00053, 0.30190) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 428, "support_height_m": 0.0653062171457734, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

533. 仿真 9.779s；物体中心 (0.45720, -0.00053, 0.30163) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 429, "support_height_m": 0.0653062201950752, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

534. 仿真 9.796s；物体中心 (0.45720, -0.00053, 0.30136) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 430, "support_height_m": 0.06530619871537229, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

535. 仿真 9.812s；物体中心 (0.45720, -0.00053, 0.30109) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 431, "support_height_m": 0.06530621054278722, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

536. 仿真 9.829s；物体中心 (0.45720, -0.00053, 0.30081) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 432, "support_height_m": 0.06530621647414085, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

537. 仿真 9.846s；物体中心 (0.45720, -0.00053, 0.30054) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 433, "support_height_m": 0.06530621956296999, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

538. 仿真 9.862s；物体中心 (0.45720, -0.00053, 0.30027) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 434, "support_height_m": 0.06530619817483811, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

539. 仿真 9.879s；物体中心 (0.45719, -0.00053, 0.29999) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 435, "support_height_m": 0.06530620999306516, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

540. 仿真 9.896s；物体中心 (0.45719, -0.00053, 0.29972) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 436, "support_height_m": 0.06530621592666619, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

541. 仿真 9.912s；物体中心 (0.45719, -0.00053, 0.29945) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 437, "support_height_m": 0.0653062190219482, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

542. 仿真 9.929s；物体中心 (0.45719, -0.00053, 0.29918) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 438, "support_height_m": 0.06530619769870193, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

543. 仿真 9.946s；物体中心 (0.45719, -0.00053, 0.29890) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 439, "support_height_m": 0.06530620949272678, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

544. 仿真 9.962s；物体中心 (0.45719, -0.00053, 0.29863) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 440, "support_height_m": 0.0653062154173101, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

545. 仿真 9.979s；物体中心 (0.45719, -0.00053, 0.29836) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 441, "support_height_m": 0.06530621851120665, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

546. 仿真 9.996s；物体中心 (0.45719, -0.00053, 0.29809) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 442, "support_height_m": 0.06530619725031837, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

547. 仿真 10.012s；物体中心 (0.45719, -0.00053, 0.29781) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 443, "support_height_m": 0.06530620901631153, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

548. 仿真 10.029s；物体中心 (0.45719, -0.00053, 0.29754) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 444, "support_height_m": 0.06530621493266196, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

549. 仿真 10.046s；物体中心 (0.45719, -0.00053, 0.29727) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 445, "support_height_m": 0.0653062180252502, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

550. 仿真 10.062s；物体中心 (0.45719, -0.00053, 0.29700) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 446, "support_height_m": 0.06530619682413037, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

551. 仿真 10.079s；物体中心 (0.45718, -0.00053, 0.29672) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 447, "support_height_m": 0.06530620856277693, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

552. 仿真 10.096s；物体中心 (0.45718, -0.00053, 0.29645) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 448, "support_height_m": 0.06530621446731362, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

553. 仿真 10.112s；物体中心 (0.45718, -0.00053, 0.29618) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 449, "support_height_m": 0.06530621538441779, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

554. 仿真 10.129s；物体中心 (0.45718, -0.00053, 0.29590) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 450, "support_height_m": 0.06530619282648926, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

555. 仿真 10.146s；物体中心 (0.45718, -0.00053, 0.29563) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 451, "support_height_m": 0.06530620360887694, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

556. 仿真 10.162s；物体中心 (0.45718, -0.00053, 0.29536) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 452, "support_height_m": 0.06530620889319963, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

557. 仿真 10.179s；物体中心 (0.45718, -0.00053, 0.29509) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 453, "support_height_m": 0.06530621157902058, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

558. 仿真 10.196s；物体中心 (0.45718, -0.00053, 0.29481) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 454, "support_height_m": 0.06530619022812788, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

559. 仿真 10.212s；物体中心 (0.45718, -0.00053, 0.29454) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 455, "support_height_m": 0.0653062017385234, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

560. 仿真 10.229s；物体中心 (0.45717, -0.00053, 0.29427) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 456, "support_height_m": 0.06530620750925896, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

561. 仿真 10.246s；物体中心 (0.45717, -0.00054, 0.29399) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 457, "support_height_m": 0.06530621051680492, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

562. 仿真 10.262s；物体中心 (0.45717, -0.00054, 0.29372) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 458, "support_height_m": 0.0653061894380521, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

563. 仿真 10.279s；物体中心 (0.45717, -0.00054, 0.29345) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 459, "support_height_m": 0.06530620106230167, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

564. 仿真 10.296s；物体中心 (0.45717, -0.00054, 0.29318) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 460, "support_height_m": 0.06530620691599957, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

565. 仿真 10.312s；物体中心 (0.45717, -0.00054, 0.29290) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 461, "support_height_m": 0.06530620998254537, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

566. 仿真 10.329s；物体中心 (0.45717, -0.00054, 0.29263) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 462, "support_height_m": 0.06530618899898115, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

567. 仿真 10.346s；物体中心 (0.45717, -0.00054, 0.29236) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 463, "support_height_m": 0.0653062006243195, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

568. 仿真 10.362s；物体中心 (0.45717, -0.00054, 0.29208) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 464, "support_height_m": 0.0653062064853243, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

569. 仿真 10.379s；物体中心 (0.45716, -0.00054, 0.29181) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 465, "support_height_m": 0.06530620956265852, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

570. 仿真 10.396s；物体中心 (0.45716, -0.00054, 0.29154) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 466, "support_height_m": 0.06530618471994397, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

571. 仿真 10.412s；物体中心 (0.45716, -0.00054, 0.29127) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 467, "support_height_m": 0.06530619833881782, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

572. 仿真 10.429s；物体中心 (0.45716, -0.00054, 0.29099) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 468, "support_height_m": 0.06530620512288562, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

573. 仿真 10.446s；物体中心 (0.45716, -0.00054, 0.29072) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 469, "support_height_m": 0.06530620864935249, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

574. 仿真 10.462s；物体中心 (0.45716, -0.00054, 0.29045) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 470, "support_height_m": 0.06530618410258346, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

575. 仿真 10.479s；物体中心 (0.45716, -0.00054, 0.29017) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 471, "support_height_m": 0.06530619585041623, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

576. 仿真 10.496s；物体中心 (0.45716, -0.00054, 0.28990) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 472, "support_height_m": 0.0653062014163676, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

577. 仿真 10.512s；物体中心 (0.45715, -0.00054, 0.28963) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 473, "support_height_m": 0.06530620413981443, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

578. 仿真 10.529s；物体中心 (0.45715, -0.00054, 0.28936) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 474, "support_height_m": 0.06530617912667096, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

579. 仿真 10.546s；物体中心 (0.45715, -0.00054, 0.28908) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 475, "support_height_m": 0.0653061924611029, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

580. 仿真 10.562s；物体中心 (0.45715, -0.00054, 0.28881) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 476, "support_height_m": 0.06530619906313682, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

581. 仿真 10.579s；物体中心 (0.45715, -0.00054, 0.28854) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 477, "support_height_m": 0.06530620247200121, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

582. 仿真 10.596s；物体中心 (0.45715, -0.00054, 0.28826) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 478, "support_height_m": 0.06530617332036355, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

583. 仿真 10.612s；物体中心 (0.45715, -0.00054, 0.28799) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 479, "support_height_m": 0.06530618931290728, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

584. 仿真 10.629s；物体中心 (0.45714, -0.00054, 0.28772) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 480, "support_height_m": 0.06530619721497034, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

585. 仿真 10.646s；物体中心 (0.45714, -0.00054, 0.28745) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 481, "support_height_m": 0.06530620128314202, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

586. 仿真 10.662s；物体中心 (0.45714, -0.00054, 0.28717) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 482, "support_height_m": 0.06530617255688104, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

587. 仿真 10.679s；物体中心 (0.45714, -0.00054, 0.28690) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 483, "support_height_m": 0.06530618870992791, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

588. 仿真 10.696s；物体中心 (0.45714, -0.00054, 0.28663) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 484, "support_height_m": 0.06530619671355412, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

589. 仿真 10.712s；物体中心 (0.45714, -0.00054, 0.28635) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 485, "support_height_m": 0.06530620084655613, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

590. 仿真 10.729s；物体中心 (0.45713, -0.00054, 0.28608) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 486, "support_height_m": 0.06530620305939472, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

591. 仿真 10.746s；物体中心 (0.45713, -0.00054, 0.28581) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 487, "support_height_m": 0.06530618100947637, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

592. 仿真 10.762s；物体中心 (0.45713, -0.00054, 0.28554) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 488, "support_height_m": 0.06530619252168293, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

593. 仿真 10.779s；物体中心 (0.45713, -0.00054, 0.28526) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 489, "support_height_m": 0.06530619661521878, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

594. 仿真 10.796s；物体中心 (0.45713, -0.00054, 0.28499) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 490, "support_height_m": 0.06530619858171194, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

595. 仿真 10.812s；物体中心 (0.45713, -0.00054, 0.28472) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 491, "support_height_m": 0.06530617728727191, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

596. 仿真 10.829s；物体中心 (0.45713, -0.00054, 0.28444) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 492, "support_height_m": 0.06530618826666504, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

597. 仿真 10.846s；物体中心 (0.45712, -0.00054, 0.28417) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 493, "support_height_m": 0.06530619375648375, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

598. 仿真 10.862s；物体中心 (0.45712, -0.00054, 0.28390) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 494, "support_height_m": 0.06530619661590524, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

599. 仿真 10.879s；物体中心 (0.45712, -0.00054, 0.28362) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 495, "support_height_m": 0.06530617595190442, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

600. 仿真 10.896s；物体中心 (0.45712, -0.00054, 0.28335) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 496, "support_height_m": 0.06530618728860446, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

601. 仿真 10.912s；物体中心 (0.45712, -0.00054, 0.28308) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 497, "support_height_m": 0.06530619301816679, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

602. 仿真 10.929s；物体中心 (0.45712, -0.00054, 0.28280) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 498, "support_height_m": 0.06530619603859346, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

603. 仿真 10.946s；物体中心 (0.45711, -0.00054, 0.28253) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 499, "support_height_m": 0.06530617169269887, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

604. 仿真 10.962s；物体中心 (0.45711, -0.00054, 0.28226) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 500, "support_height_m": 0.06530618504394392, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

605. 仿真 10.979s；物体中心 (0.45711, -0.00054, 0.28199) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 501, "support_height_m": 0.06530619172038492, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

606. 仿真 10.996s；物体中心 (0.45711, -0.00054, 0.28171) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 502, "support_height_m": 0.0653061952084856, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

607. 仿真 11.012s；物体中心 (0.45711, -0.00054, 0.28144) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 503, "support_height_m": 0.06530616658978831, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

608. 仿真 11.029s；物体中心 (0.45711, -0.00054, 0.28117) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 504, "support_height_m": 0.06530618239689613, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

609. 仿真 11.046s；物体中心 (0.45710, -0.00054, 0.28089) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 505, "support_height_m": 0.0653061886265189, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

610. 仿真 11.062s；物体中心 (0.45710, -0.00054, 0.28062) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 506, "support_height_m": 0.06530619163728633, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

611. 仿真 11.079s；物体中心 (0.45710, -0.00054, 0.28035) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 507, "support_height_m": 0.06530619312944944, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

612. 仿真 11.096s；物体中心 (0.45710, -0.00054, 0.28007) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 508, "support_height_m": 0.06530617088535988, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

613. 仿真 11.112s；物体中心 (0.45710, -0.00054, 0.27980) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 509, "support_height_m": 0.06530618196114577, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

614. 仿真 11.129s；物体中心 (0.45710, -0.00054, 0.27953) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 510, "support_height_m": 0.06530618757911537, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

615. 仿真 11.146s；物体中心 (0.45709, -0.00054, 0.27925) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 511, "support_height_m": 0.06530619055193328, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

616. 仿真 11.162s；物体中心 (0.45709, -0.00054, 0.27898) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 512, "support_height_m": 0.06530617018827797, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

617. 仿真 11.179s；物体中心 (0.45709, -0.00054, 0.27871) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 513, "support_height_m": 0.06530618148625532, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

618. 仿真 11.196s；物体中心 (0.45709, -0.00054, 0.27844) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 514, "support_height_m": 0.06530618721800051, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

619. 仿真 11.212s；物体中心 (0.45709, -0.00054, 0.27816) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 515, "support_height_m": 0.06530619025430999, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

620. 仿真 11.229s；物体中心 (0.45708, -0.00054, 0.27789) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 516, "support_height_m": 0.06530616617963825, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

621. 仿真 11.246s；物体中心 (0.45708, -0.00054, 0.27762) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 517, "support_height_m": 0.06530617942039611, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

622. 仿真 11.262s；物体中心 (0.45708, -0.00054, 0.27734) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 518, "support_height_m": 0.06530618605587961, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

623. 仿真 11.279s；物体中心 (0.45708, -0.00054, 0.27707) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 519, "support_height_m": 0.0653061895359572, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

624. 仿真 11.296s；物体中心 (0.45708, -0.00054, 0.27680) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 520, "support_height_m": 0.0653061612156314, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

625. 仿真 11.312s；物体中心 (0.45707, -0.00054, 0.27652) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 521, "support_height_m": 0.06530617541242233, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

626. 仿真 11.329s；物体中心 (0.45707, -0.00054, 0.27625) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 522, "support_height_m": 0.06530618224230293, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

627. 仿真 11.346s；物体中心 (0.45707, -0.00054, 0.27598) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 523, "support_height_m": 0.06530618565404331, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

628. 仿真 11.362s；物体中心 (0.45707, -0.00054, 0.27570) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 524, "support_height_m": 0.06530618742074705, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

629. 仿真 11.379s；物体中心 (0.45707, -0.00054, 0.27543) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 525, "support_height_m": 0.06530616652105019, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

630. 仿真 11.396s；物体中心 (0.45707, -0.00054, 0.27516) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 526, "support_height_m": 0.06530617732697305, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

631. 仿真 11.412s；物体中心 (0.45706, -0.00054, 0.27488) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 527, "support_height_m": 0.06530618277263718, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

632. 仿真 11.429s；物体中心 (0.45706, -0.00054, 0.27461) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 528, "support_height_m": 0.06530618563869701, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

633. 仿真 11.446s；物体中心 (0.45706, -0.00054, 0.27434) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 529, "support_height_m": 0.06530616164320785, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

634. 仿真 11.462s；物体中心 (0.45706, -0.00054, 0.27406) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 530, "support_height_m": 0.06530617472743903, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

635. 仿真 11.479s；物体中心 (0.45706, -0.00054, 0.27379) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 531, "support_height_m": 0.06530618128456651, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

636. 仿真 11.496s；物体中心 (0.45705, -0.00054, 0.27352) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 532, "support_height_m": 0.06530618472472852, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

637. 仿真 11.512s；物体中心 (0.45705, -0.00054, 0.27325) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 533, "support_height_m": 0.06530615660103366, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

638. 仿真 11.529s；物体中心 (0.45705, -0.00054, 0.27297) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 534, "support_height_m": 0.06530617213805193, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

639. 仿真 11.546s；物体中心 (0.45705, -0.00054, 0.27270) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 535, "support_height_m": 0.0653061798660977, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

640. 仿真 11.562s；物体中心 (0.45705, -0.00054, 0.27243) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 536, "support_height_m": 0.06530618255005974, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

641. 仿真 11.579s；物体中心 (0.45704, -0.00054, 0.27215) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 537, "support_height_m": 0.06530618385760341, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

642. 仿真 11.596s；物体中心 (0.45704, -0.00054, 0.27188) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 538, "support_height_m": 0.06530616280753092, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

643. 仿真 11.612s；物体中心 (0.45704, -0.00054, 0.27161) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 539, "support_height_m": 0.06530617334449057, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

644. 仿真 11.629s；物体中心 (0.45704, -0.00054, 0.27133) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 540, "support_height_m": 0.06530617863362012, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

645. 仿真 11.646s；物体中心 (0.45704, -0.00054, 0.27106) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 541, "support_height_m": 0.065306181406994, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

646. 仿真 11.662s；物体中心 (0.45703, -0.00054, 0.27079) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 542, "support_height_m": 0.06530615753006395, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

647. 仿真 11.679s；物体中心 (0.45703, -0.00054, 0.27051) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 543, "support_height_m": 0.06530617049039304, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

648. 仿真 11.696s；物体中心 (0.45703, -0.00054, 0.27024) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 544, "support_height_m": 0.06530617698775702, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

649. 仿真 11.712s；物体中心 (0.45703, -0.00054, 0.26997) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 545, "support_height_m": 0.0653061803996438, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

650. 仿真 11.729s；物体中心 (0.45703, -0.00054, 0.26969) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 546, "support_height_m": 0.0653061822579352, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

651. 仿真 11.746s；物体中心 (0.45702, -0.00054, 0.26942) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 547, "support_height_m": 0.06530616075691062, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

652. 仿真 11.762s；物体中心 (0.45702, -0.00054, 0.26915) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 548, "support_height_m": 0.06530617181856449, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

653. 仿真 11.779s；物体中心 (0.45702, -0.00054, 0.26887) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 549, "support_height_m": 0.06530617749072286, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

654. 仿真 11.796s；物体中心 (0.45702, -0.00054, 0.26860) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 550, "support_height_m": 0.06530617931808103, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

655. 仿真 11.812s；物体中心 (0.45702, -0.00054, 0.26833) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 551, "support_height_m": 0.06530615495288239, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

656. 仿真 11.829s；物体中心 (0.45701, -0.00054, 0.26805) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 552, "support_height_m": 0.06530616745849996, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

657. 仿真 11.846s；物体中心 (0.45701, -0.00054, 0.26778) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 553, "support_height_m": 0.06530617367295825, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

658. 仿真 11.862s；物体中心 (0.45701, -0.00054, 0.26751) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 554, "support_height_m": 0.06530617690591413, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

659. 仿真 11.879s；物体中心 (0.45701, -0.00054, 0.26723) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 555, "support_height_m": 0.06530617865378484, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

660. 仿真 11.896s；物体中心 (0.45701, -0.00054, 0.26696) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 556, "support_height_m": 0.06530615717827955, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

661. 仿真 11.912s；物体中心 (0.45700, -0.00054, 0.26669) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 557, "support_height_m": 0.0653061681432918, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

662. 仿真 11.929s；物体中心 (0.45700, -0.00054, 0.26641) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 558, "support_height_m": 0.06530617376308215, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

663. 仿真 11.946s；物体中心 (0.45700, -0.00054, 0.26614) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 559, "support_height_m": 0.06530617677887197, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

664. 仿真 11.962s；物体中心 (0.45700, -0.00054, 0.26587) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 560, "support_height_m": 0.06530615330607988, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

665. 仿真 11.979s；物体中心 (0.45699, -0.00054, 0.26559) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 561, "support_height_m": 0.06530616626406494, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

666. 仿真 11.996s；物体中心 (0.45699, -0.00054, 0.26532) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 562, "support_height_m": 0.06530617278822924, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

667. 仿真 12.012s；物体中心 (0.45699, -0.00054, 0.26505) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 563, "support_height_m": 0.06530617623305311, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

668. 仿真 12.029s；物体中心 (0.45699, -0.00054, 0.26477) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 564, "support_height_m": 0.06530617812595048, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

669. 仿真 12.046s；物体中心 (0.45699, -0.00054, 0.26450) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 565, "support_height_m": 0.06530615668178168, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

670. 仿真 12.062s；物体中心 (0.45698, -0.00054, 0.26423) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 566, "support_height_m": 0.06530616664651642, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

671. 仿真 12.079s；物体中心 (0.45698, -0.00054, 0.26395) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 567, "support_height_m": 0.06530617160160582, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

672. 仿真 12.096s；物体中心 (0.45698, -0.00054, 0.26368) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 568, "support_height_m": 0.06530617417666561, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

673. 仿真 12.112s；物体中心 (0.45698, -0.00054, 0.26341) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 569, "support_height_m": 0.0653061461325231, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

674. 仿真 12.129s；物体中心 (0.45698, -0.00054, 0.26313) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 570, "support_height_m": 0.06530616109488668, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

675. 仿真 12.146s；物体中心 (0.45697, -0.00054, 0.26286) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 571, "support_height_m": 0.06530616852403896, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

676. 仿真 12.162s；物体中心 (0.45697, -0.00054, 0.26259) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 572, "support_height_m": 0.06530617238538731, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

677. 仿真 12.179s；物体中心 (0.45697, -0.00054, 0.26231) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 573, "support_height_m": 0.0653061744767367, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

678. 仿真 12.196s；物体中心 (0.45697, -0.00054, 0.26204) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 574, "support_height_m": 0.06530615067079297, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

679. 仿真 12.212s；物体中心 (0.45696, -0.00054, 0.26177) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 575, "support_height_m": 0.06530616324270049, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

680. 仿真 12.229s；物体中心 (0.45696, -0.00054, 0.26149) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 576, "support_height_m": 0.06530616955459866, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

681. 仿真 12.246s；物体中心 (0.45696, -0.00054, 0.26122) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 577, "support_height_m": 0.06530617287788011, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

682. 仿真 12.262s；物体中心 (0.45696, -0.00054, 0.26095) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 578, "support_height_m": 0.06530617469834347, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

683. 仿真 12.279s；物体中心 (0.45696, -0.00054, 0.26067) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 579, "support_height_m": 0.06530615344621704, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

684. 仿真 12.296s；物体中心 (0.45695, -0.00054, 0.26040) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 580, "support_height_m": 0.0653061633726985, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

685. 仿真 12.312s；物体中心 (0.45695, -0.00054, 0.26013) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 581, "support_height_m": 0.06530616832104189, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

686. 仿真 12.329s；物体中心 (0.45695, -0.00054, 0.25985) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 582, "support_height_m": 0.06530617090126649, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

687. 仿真 12.346s；物体中心 (0.45695, -0.00054, 0.25958) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 583, "support_height_m": 0.06530617229890374, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

688. 仿真 12.362s；物体中心 (0.45694, -0.00054, 0.25931) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 584, "support_height_m": 0.06530615092311894, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

689. 仿真 12.379s；物体中心 (0.45694, -0.00054, 0.25903) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 585, "support_height_m": 0.06530616163178513, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

690. 仿真 12.396s；物体中心 (0.45694, -0.00054, 0.25876) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 586, "support_height_m": 0.06530616712086282, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

691. 仿真 12.412s；物体中心 (0.45694, -0.00054, 0.25849) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 587, "support_height_m": 0.06530617006904953, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

692. 仿真 12.429s；物体中心 (0.45694, -0.00054, 0.25821) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 588, "support_height_m": 0.06530614255986965, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

693. 仿真 12.446s；物体中心 (0.45693, -0.00054, 0.25794) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 589, "support_height_m": 0.06530615754973255, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

694. 仿真 12.462s；物体中心 (0.45693, -0.00054, 0.25766) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 590, "support_height_m": 0.06530616503415398, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

695. 仿真 12.479s；物体中心 (0.45693, -0.00054, 0.25739) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 591, "support_height_m": 0.06530616894904294, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

696. 仿真 12.496s；物体中心 (0.45693, -0.00054, 0.25712) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 592, "support_height_m": 0.06530617108672872, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

697. 仿真 12.512s；物体中心 (0.45692, -0.00054, 0.25684) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 593, "support_height_m": 0.06530614659891101, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

698. 仿真 12.529s；物体中心 (0.45692, -0.00054, 0.25657) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 594, "support_height_m": 0.0653061584667638, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

699. 仿真 12.546s；物体中心 (0.45692, -0.00054, 0.25630) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 595, "support_height_m": 0.0653061643433, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

700. 仿真 12.562s；物体中心 (0.45692, -0.00054, 0.25602) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 596, "support_height_m": 0.06530616739431912, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

701. 仿真 12.579s；物体中心 (0.45692, -0.00054, 0.25575) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 597, "support_height_m": 0.06530616904382239, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

702. 仿真 12.596s；物体中心 (0.45691, -0.00054, 0.25548) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 598, "support_height_m": 0.06530614527363779, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

703. 仿真 12.612s；物体中心 (0.45691, -0.00054, 0.25520) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 599, "support_height_m": 0.06530615754830675, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

704. 仿真 12.629s；物体中心 (0.45691, -0.00054, 0.25493) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 600, "support_height_m": 0.06530616370616475, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

705. 仿真 12.646s；物体中心 (0.45691, -0.00054, 0.25466) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 601, "support_height_m": 0.06530616694619892, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

706. 仿真 12.662s；物体中心 (0.45690, -0.00054, 0.25438) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 602, "support_height_m": 0.06530616872335344, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

707. 仿真 12.679s；物体中心 (0.45690, -0.00054, 0.25411) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 603, "support_height_m": 0.06530614510052266, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

708. 仿真 12.696s；物体中心 (0.45690, -0.00054, 0.25384) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 604, "support_height_m": 0.06530615740534991, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

709. 仿真 12.712s；物体中心 (0.45690, -0.00054, 0.25356) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 605, "support_height_m": 0.0653061635885234, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

710. 仿真 12.729s；物体中心 (0.45690, -0.00054, 0.25329) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 606, "support_height_m": 0.06530616685036587, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

711. 仿真 12.746s；物体中心 (0.45689, -0.00054, 0.25302) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 607, "support_height_m": 0.06530616864665409, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

712. 仿真 12.762s；物体中心 (0.45689, -0.00054, 0.25274) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 608, "support_height_m": 0.06530614421407574, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

713. 仿真 12.779s；物体中心 (0.45689, -0.00054, 0.25247) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 609, "support_height_m": 0.06530615592906815, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

714. 仿真 12.796s；物体中心 (0.45689, -0.00054, 0.25220) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 610, "support_height_m": 0.0653061617328554, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

715. 仿真 12.812s；物体中心 (0.45688, -0.00054, 0.25192) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 611, "support_height_m": 0.06530616474721683, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

716. 仿真 12.829s；物体中心 (0.45688, -0.00054, 0.25165) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 612, "support_height_m": 0.06530616637953479, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

717. 仿真 12.846s；物体中心 (0.45688, -0.00054, 0.25138) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 613, "support_height_m": 0.06530613848669004, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

718. 仿真 12.862s；物体中心 (0.45688, -0.00054, 0.25110) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 614, "support_height_m": 0.06530615286723228, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

719. 仿真 12.879s；物体中心 (0.45688, -0.00054, 0.25083) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 615, "support_height_m": 0.06530616001148681, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

720. 仿真 12.896s；物体中心 (0.45687, -0.00054, 0.25056) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 616, "support_height_m": 0.06530616373260244, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

721. 仿真 12.912s；物体中心 (0.45687, -0.00054, 0.25028) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 617, "support_height_m": 0.06530616575528962, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

722. 仿真 12.929s；物体中心 (0.45687, -0.00054, 0.25001) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 618, "support_height_m": 0.06530613815430089, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

723. 仿真 12.946s；物体中心 (0.45687, -0.00054, 0.24974) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 619, "support_height_m": 0.06530615263897432, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

724. 仿真 12.962s；物体中心 (0.45686, -0.00054, 0.24946) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 620, "support_height_m": 0.06530615985653088, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

725. 仿真 12.979s；物体中心 (0.45686, -0.00054, 0.24919) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 621, "support_height_m": 0.06530616362379907, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

726. 仿真 12.996s；物体中心 (0.45686, -0.00054, 0.24891) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 622, "support_height_m": 0.06530616486655696, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

727. 仿真 13.012s；物体中心 (0.45686, -0.00054, 0.24864) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 623, "support_height_m": 0.06530616550038998, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

728. 仿真 13.029s；物体中心 (0.45686, -0.00054, 0.24837) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 624, "support_height_m": 0.06530614500290564, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

729. 仿真 13.046s；物体中心 (0.45685, -0.00054, 0.24809) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 625, "support_height_m": 0.06530615494355112, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

730. 仿真 13.062s；物体中心 (0.45685, -0.00054, 0.24782) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 626, "support_height_m": 0.06530615996140707, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

731. 仿真 13.079s；物体中心 (0.45685, -0.00054, 0.24755) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 627, "support_height_m": 0.06530616262119397, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

732. 仿真 13.096s；物体中心 (0.45685, -0.00054, 0.24727) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 628, "support_height_m": 0.06530616408956981, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

733. 仿真 13.112s；物体中心 (0.45684, -0.00054, 0.24700) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 629, "support_height_m": 0.06530614058264177, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

734. 仿真 13.129s；物体中心 (0.45684, -0.00054, 0.24673) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 630, "support_height_m": 0.06530615263806945, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

735. 仿真 13.146s；物体中心 (0.45684, -0.00054, 0.24645) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 631, "support_height_m": 0.06530615869505993, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

736. 仿真 13.162s；物体中心 (0.45684, -0.00054, 0.24618) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 632, "support_height_m": 0.06530616189515247, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

737. 仿真 13.179s；物体中心 (0.45683, -0.00054, 0.24591) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 633, "support_height_m": 0.0653061636596525, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

738. 仿真 13.196s；物体中心 (0.45683, -0.00054, 0.24563) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 634, "support_height_m": 0.06530616466027545, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

739. 仿真 13.212s；物体中心 (0.45683, -0.00054, 0.24536) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 635, "support_height_m": 0.06530614357929125, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

740. 仿真 13.229s；物体中心 (0.45683, -0.00054, 0.24509) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 636, "support_height_m": 0.06530615394330695, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

741. 仿真 13.246s；物体中心 (0.45683, -0.00054, 0.24481) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 637, "support_height_m": 0.06530615851067248, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

742. 仿真 13.262s；物体中心 (0.45682, -0.00054, 0.24454) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 638, "support_height_m": 0.06530616089324096, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

743. 仿真 13.279s；物体中心 (0.45682, -0.00054, 0.24427) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 639, "support_height_m": 0.06530616218415129, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

744. 仿真 13.296s；物体中心 (0.45682, -0.00054, 0.24399) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 640, "support_height_m": 0.06530613868811658, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

745. 仿真 13.312s；物体中心 (0.45682, -0.00054, 0.24372) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 641, "support_height_m": 0.06530615060857187, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

746. 仿真 13.329s；物体中心 (0.45681, -0.00054, 0.24345) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 642, "support_height_m": 0.06530615659472197, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

747. 仿真 13.346s；物体中心 (0.45681, -0.00054, 0.24317) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 643, "support_height_m": 0.06530615974972644, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

748. 仿真 13.362s；物体中心 (0.45681, -0.00054, 0.24290) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 644, "support_height_m": 0.0653061614897096, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

749. 仿真 13.379s；物体中心 (0.45681, -0.00054, 0.24263) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 645, "support_height_m": 0.0653061624785998, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

750. 仿真 13.396s；物体中心 (0.45680, -0.00054, 0.24235) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 646, "support_height_m": 0.06530614242902691, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

751. 仿真 13.412s；物体中心 (0.45680, -0.00054, 0.24208) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 647, "support_height_m": 0.06530615244356347, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

752. 仿真 13.429s；物体中心 (0.45680, -0.00054, 0.24180) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 648, "support_height_m": 0.06530615753738124, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

753. 仿真 13.446s；物体中心 (0.45680, -0.00054, 0.24153) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 649, "support_height_m": 0.06530616025711292, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

754. 仿真 13.462s；物体中心 (0.45680, -0.00054, 0.24126) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 650, "support_height_m": 0.06530616177025099, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

755. 仿真 13.479s；物体中心 (0.45679, -0.00054, 0.24098) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 651, "support_height_m": 0.06530616263817754, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

756. 仿真 13.496s；物体中心 (0.45679, -0.00054, 0.24071) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 652, "support_height_m": 0.06530614186027456, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

757. 仿真 13.512s；物体中心 (0.45679, -0.00054, 0.24044) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 653, "support_height_m": 0.06530615134373953, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

758. 仿真 13.529s；物体中心 (0.45679, -0.00054, 0.24016) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 654, "support_height_m": 0.06530615609201067, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

759. 仿真 13.546s；物体中心 (0.45678, -0.00054, 0.23989) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 655, "support_height_m": 0.0653061585905902, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

760. 仿真 13.562s；物体中心 (0.45678, -0.00054, 0.23962) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 656, "support_height_m": 0.06530615996231519, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

761. 仿真 13.579s；物体中心 (0.45678, -0.00054, 0.23934) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 657, "support_height_m": 0.0653061607368773, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

762. 仿真 13.596s；物体中心 (0.45678, -0.00054, 0.23907) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 658, "support_height_m": 0.06530614066838043, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

763. 仿真 13.612s；物体中心 (0.45677, -0.00054, 0.23880) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 659, "support_height_m": 0.06530615054945065, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

764. 仿真 13.629s；物体中心 (0.45677, -0.00054, 0.23852) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 660, "support_height_m": 0.06530615556974, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

765. 仿真 13.646s；物体中心 (0.45677, -0.00054, 0.23825) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 661, "support_height_m": 0.06530615824655871, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

766. 仿真 13.662s；物体中心 (0.45677, -0.00054, 0.23798) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 662, "support_height_m": 0.06530615973818346, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

767. 仿真 13.679s；物体中心 (0.45677, -0.00054, 0.23770) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 663, "support_height_m": 0.06530616059200182, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

768. 仿真 13.696s；物体中心 (0.45676, -0.00054, 0.23743) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 664, "support_height_m": 0.0653061406344587, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

769. 仿真 13.712s；物体中心 (0.45676, -0.00054, 0.23716) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 665, "support_height_m": 0.0653061505241175, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

770. 仿真 13.729s；物体中心 (0.45676, -0.00054, 0.23688) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 666, "support_height_m": 0.06530615555735604, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

771. 仿真 13.746s；物体中心 (0.45676, -0.00054, 0.23661) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 667, "support_height_m": 0.06530615824766468, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

772. 仿真 13.762s；物体中心 (0.45675, -0.00054, 0.23634) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 668, "support_height_m": 0.06530615907167621, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

773. 仿真 13.779s；物体中心 (0.45675, -0.00054, 0.23606) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 669, "support_height_m": 0.06530615949465671, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

774. 仿真 13.796s；物体中心 (0.45675, -0.00054, 0.23579) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 670, "support_height_m": 0.06530613164422387, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

775. 仿真 13.812s；物体中心 (0.45675, -0.00054, 0.23552) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 671, "support_height_m": 0.0653061452322779, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

776. 仿真 13.829s；物体中心 (0.45674, -0.00054, 0.23524) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 672, "support_height_m": 0.065306151950335, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

777. 仿真 13.846s；物体中心 (0.45674, -0.00054, 0.23497) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 673, "support_height_m": 0.06530615543201189, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

778. 仿真 13.862s；物体中心 (0.45674, -0.00054, 0.23469) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 674, "support_height_m": 0.06530615732581978, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

779. 仿真 13.879s；物体中心 (0.45674, -0.00054, 0.23442) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 675, "support_height_m": 0.06530615839387348, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

780. 仿真 13.896s；物体中心 (0.45674, -0.00054, 0.23415) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 676, "support_height_m": 0.0653061590106669, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

781. 仿真 13.912s；物体中心 (0.45673, -0.00054, 0.23387) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 677, "support_height_m": 0.06530613903009337, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

782. 仿真 13.929s；物体中心 (0.45673, -0.00054, 0.23360) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 678, "support_height_m": 0.06530614877929183, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

783. 仿真 13.946s；物体中心 (0.45673, -0.00054, 0.23333) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 679, "support_height_m": 0.0653061537324149, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

784. 仿真 13.962s；物体中心 (0.45673, -0.00054, 0.23305) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 680, "support_height_m": 0.06530615637514511, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

785. 仿真 13.979s；物体中心 (0.45672, -0.00054, 0.23278) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 681, "support_height_m": 0.06530615785097707, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

786. 仿真 13.996s；物体中心 (0.45672, -0.00054, 0.23251) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 682, "support_height_m": 0.06530615870232805, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

787. 仿真 14.012s；物体中心 (0.45672, -0.00054, 0.23223) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 683, "support_height_m": 0.06530615855567033, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

788. 仿真 14.029s；物体中心 (0.45672, -0.00054, 0.23196) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 684, "support_height_m": 0.06530613815215919, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

789. 仿真 14.046s；物体中心 (0.45671, -0.00054, 0.23169) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 685, "support_height_m": 0.06530614755082458, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

790. 仿真 14.062s；物体中心 (0.45671, -0.00054, 0.23141) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 686, "support_height_m": 0.06530615228271132, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

791. 仿真 14.079s；物体中心 (0.45671, -0.00054, 0.23114) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 687, "support_height_m": 0.06530615478458653, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

792. 仿真 14.096s；物体中心 (0.45671, -0.00054, 0.23087) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 688, "support_height_m": 0.06530615616891719, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

793. 仿真 14.112s；物体中心 (0.45671, -0.00054, 0.23059) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 689, "support_height_m": 0.06530615695719202, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

794. 仿真 14.129s；物体中心 (0.45670, -0.00054, 0.23032) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 690, "support_height_m": 0.0653061574179397, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

795. 仿真 14.146s；物体中心 (0.45670, -0.00054, 0.23005) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 691, "support_height_m": 0.06530613401164596, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

796. 仿真 14.162s；物体中心 (0.45670, -0.00054, 0.22977) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 692, "support_height_m": 0.06530614540192169, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

797. 仿真 14.179s；物体中心 (0.45670, -0.00054, 0.22950) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 693, "support_height_m": 0.06530615110567603, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

798. 仿真 14.196s；物体中心 (0.45669, -0.00054, 0.22923) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 694, "support_height_m": 0.06530615411269013, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

799. 仿真 14.212s；物体中心 (0.45669, -0.00054, 0.22895) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 695, "support_height_m": 0.06530615577717001, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

800. 仿真 14.229s；物体中心 (0.45669, -0.00054, 0.22868) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 696, "support_height_m": 0.0653061567295464, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

801. 仿真 14.246s；物体中心 (0.45669, -0.00054, 0.22841) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 697, "support_height_m": 0.06530615728627479, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

802. 仿真 14.262s；物体中心 (0.45668, -0.00054, 0.22813) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 698, "support_height_m": 0.06530615761107164, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

803. 仿真 14.279s；物体中心 (0.45668, -0.00054, 0.22786) m；{"trial": "calibration", "kind": "ground_lowering_step", "index": 699, "support_height_m": 0.06530613671818579, "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}

804. 仿真 14.279s；物体中心 (0.45668, -0.00054, 0.22786) m；{"trial": "calibration", "kind": "trial_error", "error": "RuntimeError: ground lowering did not reach low-speed support", "物体抓持": true, "实际抬升": true, "事件": ["descending_object_caught_with_gated_fixed_constraint"]}


[2026-10-19T23:59:29+08:00] calibration 结束：{"label": "calibration", "parameters": {"target_x_m": 0.4, "target_z_m": 0.65, "release_min_vz_m_s": 1.06, "max_sweep_steps": 160, "catch_lead_s": 0.04}, "failure_mode": "none", "applied_skill_ids": ["grasp_without_lift_v1"], "lift_confirmed": true, "caught": true, "free_flight": true, "placement": {"passed": false}, "recovery_used": false, "max_sweep_vz_m_s": 1.0610871628118803, "release_height_m": 0.32622337170717197, "release_vz_m_s": 1.0610871628118803, "release_velocity_m_s": [0.05012743644590001, 0.0001101215396272239, 1.0610871628118803], "release_time_s": 1.9958333333333276, "rise_from_release_m": 0.054878205302841765, "catch_time_s": 2.1125, "catch_vz_m_s": -0.08748958365849183, "catch_distance_m": 0.05370682013285851, "catch_relative_speed_m_s": 0.14144620765016797, "apex_height_m": 0.38110157701001374, "had_apex": true, "flight_ticks": 28, "flight_contact_before_catch": false, "catch_hold_passed": true, "error": "RuntimeError: ground lowering did not reach low-speed support", "physics_samples": 3393, "max_joint_velocity_ratios": [0.016393830544591755, 1.0000091517096734, 1.000060881619031, 0.004212114253843383, 1.008908989008264, 0.020581870534083155], "passed": false}


[2026-10-20T00:00:22+08:00] 开始运行 6f73ea1170fc；输出目录 docs\throw_catch_005m_calibration_02。

1. 仿真 0.000s；物体中心 (—) m；{"kind": "source_verified", "source_path": "artifacts\\verification_20261019\\skills.json", "sha256": "1480ab7df263cab82d7df41eb84c92a961c2b70a2d8b7bb2cb8c02f94a1f7383", "target_rise_m": 0.05, "ground_z_m": 0}


[2026-10-20T00:00:22+08:00] 开始 calibration：参数 {"target_x_m": 0.4, "target_z_m": 0.65, "release_min_vz_m_s": 1.06, "max_sweep_steps": 160, "catch_lead_s": 0.04}；故障 none。
