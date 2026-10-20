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
