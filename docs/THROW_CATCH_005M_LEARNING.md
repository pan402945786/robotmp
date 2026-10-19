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
