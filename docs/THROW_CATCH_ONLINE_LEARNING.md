# 基于在线观测的接回实验

旧的完整飞行离线选点只保留为历史诊断，不能作为本轮控制输入或成功证据。

传感输入为仿真器采样的位置观测，可带噪声、延迟和漏帧；不是摄像头检测。控制器没有动态世界句柄，只接收已送达的位置观测和关节编码器状态。独立运动学模型允许求解未来动作，不读取未来物体状态。

## online_001：skill v1 → v2

```json
{
  "label": "online_001",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 77,
  "planner_calls": 10,
  "planner_deadline_misses": 5,
  "max_planner_wall_s": 0.2291817999794148,
  "forecast_100ms_rmse_m": 0.06046805568000734,
  "estimated_drag": 0.0,
  "motion_checks_passed": false,
  "error": null,
  "closest_distance_m": 0.1475220045155627
}
```

本次反思：position_history_requires_online_drag_estimation；slow_kinematic_search_must_not_be_treated_as_instantaneous；position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## online_002：skill v2 → v3

```json
{
  "label": "online_002",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 83,
  "planner_calls": 14,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.07545769997523166,
  "forecast_100ms_rmse_m": 0.06241967901651536,
  "estimated_drag": 0.03121578708113678,
  "motion_checks_passed": false,
  "error": null,
  "closest_distance_m": 0.08032649267565876
}
```

本次反思：position_history_requires_online_drag_estimation；position_velocity_approach_is_not_bilateral_contact_capture；reject_infeasible_complete_paths_and_recheck_after_planning_delay；reserve_joint_travel_for_followthrough_and_braking。完整接稳未通过时保持 candidate，不记成功。

## online_003：skill v3 → v4

```json
{
  "label": "online_003",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 0,
  "planner_calls": 0,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.0,
  "forecast_100ms_rmse_m": null,
  "estimated_drag": 0.0,
  "motion_checks_passed": false,
  "error": null,
  "closest_distance_m": null
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture；reject_infeasible_complete_paths_and_recheck_after_planning_delay；reserve_joint_travel_for_followthrough_and_braking。完整接稳未通过时保持 candidate，不记成功。

## online_004：skill v4 → v5

```json
{
  "label": "online_004",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 0,
  "planner_calls": 0,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.0,
  "forecast_100ms_rmse_m": null,
  "estimated_drag": 0.0,
  "motion_checks_passed": false,
  "error": null,
  "closest_distance_m": null
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture；reject_infeasible_complete_paths_and_recheck_after_planning_delay；reserve_joint_travel_for_followthrough_and_braking。完整接稳未通过时保持 candidate，不记成功。

## online_005：skill v5 → v6

```json
{
  "label": "online_005",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 79,
  "planner_calls": 13,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.052914600004442036,
  "forecast_100ms_rmse_m": 0.05900143213886379,
  "estimated_drag": 0.03204540910385401,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.0791793532214195
}
```

本次反思：position_history_requires_online_drag_estimation；position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## online_006：skill v6 → v7

```json
{
  "label": "online_006",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": false,
  "position_observations": 112,
  "planner_calls": 20,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.05609250001725741,
  "forecast_100ms_rmse_m": 0.08918331201195863,
  "estimated_drag": 0.14650289399415484,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.08493263254239354
}
```

本次反思：position_history_requires_online_drag_estimation；position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## online_007：skill v7 → v8

```json
{
  "label": "online_007",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": false,
  "position_observations": 70,
  "planner_calls": 13,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.05005849999724887,
  "forecast_100ms_rmse_m": 0.11152911883878104,
  "estimated_drag": 0.03720717029520632,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.0935437618572167
}
```

本次反思：position_history_requires_online_drag_estimation；position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## online_008：skill v8 → v9

```json
{
  "label": "online_008",
  "released": false,
  "caught": null,
  "physical_capture": null,
  "causality_passed": null,
  "position_observations": null,
  "planner_calls": null,
  "planner_deadline_misses": null,
  "max_planner_wall_s": null,
  "forecast_100ms_rmse_m": null,
  "estimated_drag": null,
  "motion_checks_passed": null,
  "error": null,
  "closest_distance_m": null
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## online_009：skill v9 → v10

```json
{
  "label": "online_009",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 79,
  "planner_calls": 13,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.05266409998876043,
  "forecast_100ms_rmse_m": 0.05918408016588154,
  "estimated_drag": 0.032307620335623316,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.08131230683100125
}
```

本次反思：position_history_requires_online_drag_estimation；position_velocity_approach_is_not_bilateral_contact_capture；one_sided_finger_impact_does_not_establish_capture；ballistic_prediction_error_after_contact_is_not_free_flight_model_error。完整接稳未通过时保持 candidate，不记成功。

## online_010：skill v10 → v11

```json
{
  "label": "online_010",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 78,
  "planner_calls": 14,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.04335329998866655,
  "forecast_100ms_rmse_m": 0.09008839751863103,
  "estimated_drag": 0.05107571025032176,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.07300223880667327
}
```

本次反思：position_history_requires_online_drag_estimation；position_velocity_approach_is_not_bilateral_contact_capture；one_sided_finger_impact_does_not_establish_capture；ballistic_prediction_error_after_contact_is_not_free_flight_model_error。完整接稳未通过时保持 candidate，不记成功。

## online_011：skill v11 → v12

```json
{
  "label": "online_011",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 69,
  "planner_calls": 13,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.04397880000760779,
  "forecast_100ms_rmse_m": 0.11234924051620769,
  "estimated_drag": 0.040247223492792264,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.060332754916487465
}
```

本次反思：position_history_requires_online_drag_estimation；position_velocity_approach_is_not_bilateral_contact_capture；one_sided_finger_impact_does_not_establish_capture；ballistic_prediction_error_after_contact_is_not_free_flight_model_error。完整接稳未通过时保持 candidate，不记成功。

## online_012：skill v12 → v13

```json
{
  "label": "online_012",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 79,
  "planner_calls": 13,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.043074099987279624,
  "forecast_100ms_rmse_m": 0.054806796046500274,
  "estimated_drag": 0.03989421435242954,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.07982009645603767
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture；one_sided_finger_impact_does_not_establish_capture；ballistic_prediction_error_after_contact_is_not_free_flight_model_error。完整接稳未通过时保持 candidate，不记成功。

## online_013：skill v13 → v14

```json
{
  "label": "online_013",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 76,
  "planner_calls": 13,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.047864099993603304,
  "forecast_100ms_rmse_m": 0.07790655104632978,
  "estimated_drag": 0.056127428142794936,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.07483562332114216
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture；one_sided_finger_impact_does_not_establish_capture；ballistic_prediction_error_after_contact_is_not_free_flight_model_error。完整接稳未通过时保持 candidate，不记成功。

## online_014：skill v14 → v15

```json
{
  "label": "online_014",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 105,
  "planner_calls": 19,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.04125670000212267,
  "forecast_100ms_rmse_m": 0.12924407135306634,
  "estimated_drag": 0.04591561325012504,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.0638100734216059
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture；one_sided_finger_impact_does_not_establish_capture；ballistic_prediction_error_after_contact_is_not_free_flight_model_error。完整接稳未通过时保持 candidate，不记成功。

## online_015：skill v16 → v17

```json
{
  "label": "online_015",
  "released": false,
  "caught": false,
  "physical_capture": false,
  "causality_passed": null,
  "position_observations": 0,
  "planner_calls": 0,
  "planner_deadline_misses": null,
  "max_planner_wall_s": null,
  "forecast_100ms_rmse_m": null,
  "estimated_drag": null,
  "motion_checks_passed": null,
  "error": null,
  "closest_distance_m": null
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## ????????????skill v19

?? online_015???? 15 ??????13 ????11 ???????????????9 ?????????????? 0 ??online_015 ?????????????????????

???????????????????????????????????????????? 1e-15 ??????????????????????????????????????????? audit.json?

??????????? 86.93 mm???????? 92.27 mm????????? 100 mm ??????????????80 mm ?????????????????????????????????????????????????????????????

??????????????????????????????????????????????????????????????????? online_012?014?100 ms ?????? RMSE ? 1.05?7.59?13.08 mm?????????????????

?????? candidate??????? 0?52 ?????????????????????????????????????????????????????????? THROW_CATCH_ONLINE_RESULTS.md?

## online_016：skill v19 → v20

```json
{
  "label": "online_016",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 70,
  "planner_calls": 12,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.011596199998166412,
  "forecast_100ms_rmse_m": 0.0008823454000979809,
  "estimated_drag": 0.0398464378744699,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.7983026846123443
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## online_017：skill v20 → v21

```json
{
  "label": "online_017",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 64,
  "planner_calls": 11,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.008377299993298948,
  "forecast_100ms_rmse_m": 0.00684427257002545,
  "estimated_drag": 0.05971410628721805,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.7823845598407032
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## online_018：skill v21 → v22

```json
{
  "label": "online_018",
  "released": true,
  "caught": false,
  "physical_capture": false,
  "causality_passed": true,
  "position_observations": 62,
  "planner_calls": 11,
  "planner_deadline_misses": 0,
  "max_planner_wall_s": 0.008719500008737668,
  "forecast_100ms_rmse_m": 0.012508321021176909,
  "estimated_drag": 0.031248642828455325,
  "motion_checks_passed": true,
  "error": null,
  "closest_distance_m": 0.8531884444162613
}
```

本次反思：position_velocity_approach_is_not_bilateral_contact_capture。完整接稳未通过时保持 candidate，不记成功。

## 2026-10-20：按用户要求改为 50 mm，集中调参与复测

质量仍为 100 g；本轮 61 次尝试（含 online_016–018，不重复计数）、58 次释放、53 次因果及运动检查通过、13 次出现双指接触。最长连续双指接触 0.1167 s，0.5 s 保持未通过；接稳数仍为 0。另有 1 次不释放的发射测量，不计接回尝试。

改进：尺寸贯通碰撞、外观和惯量；几何检查读本轮尺寸；取消恢复碰撞的任意 20 cm 中心距离门槛，保留实际表面间隙检查；双指触觉接触后保持闭合并制动。测试了释放门槛、向内释放、挥臂比例、闭合提前量、制动时长、姿态及夹持深度。

下一轮候选：无底座预转，挥臂比例 0.8，向内释放，1.5 m/s 门槛，180 ms 闭合提前量及接触制动。实际释放竖直速度约 4.57 m/s。三个新种子的复测均未接稳。集中复核后更新候选 skill 为 v23；手工搜索保存实际参数，不声称逐轮自动反思或逐轮 Git 提交。

完整证据见 [50 mm 结果](THROW_CATCH_50MM_RESULTS.md) 和 [独立审计](throw_catch_50mm_20261020_final/audit.json)。
