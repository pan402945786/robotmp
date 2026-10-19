# robotmp 开发进展

更新时间：2026 年 10 月 18 日

## 当前目标

robotmp 用“预测未来 → 执行动作 → 观察实际 → 比较偏差 → 诊断失败 → 生成并验证 Skill → 检索 Skill 修正下一次预测”的闭环验证具身机器人失败经验机制。

当前系统同时保留两种环境：

- `PickPlaceEnv`：Python 规则环境，用于快速回归和确定性单元测试。
- `PyBulletPickPlaceEnv`：物理环境，用于碰撞、物体位姿、夹爪约束、关节控制和相机画面验证。

## 已完成

### 规则 MVP

- 实现结构化 `SceneState`、`ObjectState`、`RobotState`、`Prediction` 和 `Skill`。
- 支持 `baseline`、`feedback`、`skills` 三种执行模式。
- 支持 `low_grip_force`、`misaligned_grasp`、`occluded` 和 `none` 故障模式。
- 监控器会检查物体是否抬升、是否出现预期事件、观测置信度是否足够。
- 规则诊断器生成 `grasp_without_lift_v1` 候选 Skill。
- Skill 经过重复验证后写入 JSON 并标记为 `verified`。

### 物理仿真

- 接入 PyBullet，运行环境为 Conda `py311`，PyBullet 版本为 `3.2.7`。
- 增加动态立方体、桌面、夹爪接触、抬升、搬运和释放。
- 增加项目自制简化 6DOF 模型 `assets/arm6dof_gripper.urdf`，保留为回退模型。
- 默认工业模型改为 PyBullet 数据包中的 UFactory xArm6：
  `pybullet_data/xarm/xarm6_with_gripper.urdf`。
- xArm6 使用 6 个 revolute 关节，关节上下限、最大力矩和速度从 URDF 的 `getJointInfo` 读取。
- 末端控制使用 `calculateInverseKinematics` 生成目标，再通过 `POSITION_CONTROL` 驱动关节。
- 使用 xArm6 URDF 自带夹爪传动；夹爪和机械臂状态会进入 `SceneState`。

### 失败处理

- xArm6 的物体默认生成在 `x=0.45 m`，机械臂基座位置由 `SimConfig.arm_base_x` 配置，默认与抓取目标对齐。
- xArm6 接近动作会等待位置控制器完成仿真步进，避免接近、闭合和抬升之间发生关节瞬移。
- 抓取约束按实际末端和物体相对位姿创建；高层 MVP 会屏蔽不可控的刚体推挤，由抓取策略显式决定失败注入或建立约束。
- 低力度场景中，物体可能被推开而不产生抬升；反馈模式会停止继续搬运，刷新物体位置，重新用 IK 规划并重试。
- 搬运到目标时会下降到桌面高度，再移除抓取约束并释放，正常任务以 `finished` 结束。

### Skill 物理验证

`sim_cli.py` 支持直接在 xArm6 物理环境中验证 Skill：

```powershell
conda run -n py311 python -m robotmp.sim_cli `
  --validate-skill `
  --trials 20 `
  --failure-mode low_grip_force `
  --arm xarm6 `
  --store artifacts/xarm6_skills.json `
  --trace artifacts/xarm6_skill_validation.json
```

验证顺序为：

1. 运行一次 `skills` episode，生成候选 Skill。
2. 使用 xArm6 物理环境重复运行 `feedback` episode。
3. 根据恢复成功率和误判成功率将 Skill 标记为 `verified`。
4. 再运行一次 `skills` episode，确认 Skill 被检索并应用。

最近一次 5 次物理验证结果：

| 指标 | 结果 |
|---|---:|
| 验证次数 | 5 |
| 恢复成功率 | 100% |
| 误判成功率 | 0% |
| 最后一次 Skill 应用 | `grasp_without_lift_v1` |
| Skill 应用后预测置信度 | 0.90 |

当前 Skill 是符号化失败经验，不是神经网络训练。它改变预测阶段和恢复决策，但还不会自动学习新的抓取姿态、夹爪力矩、速度或轨迹。

## 运行入口

规则环境：

```powershell
python -m unittest discover -s tests -v
python -m robotmp.cli demo --mode feedback --failure-mode low_grip_force
```

xArm6 GUI：

```powershell
conda run -n py311 python -m robotmp.sim_cli `
  --mode feedback `
  --failure-mode low_grip_force `
  --arm xarm6 `
  --gui `
  --realtime `
  --hold 5 `
  --trace artifacts/sim_xarm6.json
```

实际 PyBullet 相机视频：

```powershell
conda run -n py311 python -m robotmp.sim_video `
  --failure-mode low_grip_force `
  --output artifacts/simulation_video_xarm6
```

输出包含 MP4、事件遥测和视频参数。视频右侧显示仿真时间、物体高度、夹爪力度、观测置信度、阶段、抬升状态和事件。

## 测试状态

在 Conda `py311` 仿真环境中，当前共 11 项测试全部通过，覆盖：

- 规则环境的成功、失败、误判、遮挡和 Skill 验证；
- PyBullet 实际物体高度变化；
- 简化 6DOF IK 与关节状态；
- xArm6 URDF 关节限制和执行器参数；
- xArm6 初始无碰撞、正常抓取和桌面放置；
- xArm6 低力度失败恢复。

Python 3.14 主环境可以运行规则测试；由于 PyBullet 安装在 `py311` 环境，仿真测试在主环境中会按条件跳过。

## 当前边界

- xArm6 使用 PyBullet 数据包中的 URDF，不是厂商控制器或真实机器人连接。
- 控制器是 PyBullet 位置控制器，尚未接入 `ros2_control`、速度控制或力矩控制。
- 夹爪力度仍是模型标量，尚未对应真实电机电流或接触力传感器。
- 低力度和抓取点偏移仍是确定性失败注入；当前恢复会刷新物体位姿并重新执行抓取，Skill 尚未主动学习新的抓取姿态。
- 视觉观测目前使用仿真状态和 PyBullet 相机画面，没有视觉检测模型、深度估计或遮挡推理。
- 释放成功目前表示物体回到桌面附近并完成流程，不包含精确放置误差、姿态误差或稳定性评估。

## 下一步

1. 将抓取前的末端规划拆成预抓取位姿、闭合位姿和抬升位姿，加入碰撞距离检查。
2. 让 Skill 记录抓取前位移、末端位姿、关节目标和恢复后的成功证据。
3. 使用这些证据选择下一次抓取偏移、夹爪闭合速度和抬升高度。
4. 加入物体滑落、目标位置误差和释放后稳定性检查。
5. 接入真实相机观测和 `ros2_control` 前，继续在多个随机物体位置和随机故障强度下验证。


## 大模型诊断接入

`robotmp.diagnosis.OpenAICompatibleDiagnoser` 支持通过环境变量或 CLI 参数接入不同主机上的 OpenAI-compatible 服务。默认仍使用规则诊断；使用 `--diagnoser llm` 才会调用模型。当前本机 CC Switch 使用 `http://127.0.0.1:15723/v1`、`responses` 协议和 `gpt-6.1-sol` 已实际返回结构化候选 Skill。模型不可用或输出不安全时，runner 会记录 `diagnosis_fallback` 并回退规则诊断。详细配置和边界见 [`docs/LLM_INTEGRATION.md`](LLM_INTEGRATION.md)。模型请求和响应默认写入 `artifacts/llm_diagnosis.jsonl`，用于复现诊断问题。
