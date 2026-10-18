# robotmp

`robotmp` 是一个按照《基于预测误差与失败经验 Skill 的具身智能系统》方案实现的最小可行版本。它用一个轻量级抓取环境验证下面的闭环：

```text
预测未来 → 执行动作 → 观察实际 → 比较偏差 → 诊断失败
→ 生成候选 Skill → 验证 Skill → 检索并修正下一次预测
```

当前 MVP 只实现“夹爪闭合但物体没有抬升”这一失败模式。运行时不需要机器人硬件、仿真器或模型 API；规则诊断器作为大模型诊断接口的本地替身，便于先验证系统闭环。

## 快速开始

需要 Python 3.10 或更高版本。

```powershell
python -m unittest discover -s tests -v
python -m robotmp.cli demo --mode baseline --failure-mode low_grip_force
python -m robotmp.cli demo --mode feedback --failure-mode low_grip_force
python -m robotmp.cli demo --mode skills --failure-mode low_grip_force
python -m robotmp.cli validate --trials 20
python -m robotmp.cli experiment --trials 20 --failure-mode low_grip_force
```

运行后，Skill 会保存到 `artifacts/skills.json`。验证后的 Skill 状态为 `verified`，之后 `--mode skills` 会在任务开始时检索它。

## 运行可视化视频

```powershell
python -m pip install -e ".[video]"
python -m robotmp.video --trials 20 --fps 24
Start-Process artifacts/visualization/index.html
```

生成约 67 秒、1600 × 900 的中文 MP4，包含基线误判、反馈恢复、Skill 验证与复用、遮挡安全停止，以及每组 20 次的对比结果。参数面板显示实际模型时间、夹爪力度、物体高度、预测与观测置信度和首次抬升比较结果；下方显示高度曲线及执行记录。视频无音轨。

输出默认保存在 `artifacts/visualization/`：

- `robotmp_run.mp4`：可直接播放的视频。
- `index.html`：带章节跳转、实验结果和数据链接的本地播放页。
- `run_data.json`：从 `run_episode(observer=...)` 记录的原始状态、预测、比较、诊断和结果，以及验证后的 Skill 与统计。
- `video_info.json`：视频规格和章节起始时间。
- `01_overview.png` 至 `07_summary.png`：各章节预览。

可用 `--output 路径` 指定输出位置，用 `--font 字体路径` 指定中文字体。默认寻找 Windows 微软雅黑或 Linux Noto Sans CJK。生成过程使用临时独立经验库，不改变现有 `artifacts/skills.json`。

视频是当前确定性规则环境的状态示意，不是硬件录像或物理仿真。夹爪力度没有标定物理单位；运动插值只用于播放。`retry_grasp` 通过清除故障注入完成恢复，释放后模型仍保留物体高度和抬升标记。已验证 Skill 会改变预测置信度和预期阶段，当前尚未减少此场景中的重试次数。比较面板保留首次抬升比较结果，恢复后原流程不会再次调用比较器。实验比例仅描述固定故障下的闭环行为。

## 当前模块

- `robotmp/environment.py`：轻量级抓取环境和失败注入。
- `robotmp/models.py`：结构化状态、预测结果和 Skill 数据结构。
- `robotmp/predictor.py`：MVP 规则预测器。
- `robotmp/monitor.py`：预测与观测比较器。
- `robotmp/diagnosis.py`：本地规则诊断器，后续可替换为大模型适配器。
- `robotmp/skills.py`：JSON-backed Skill 经验库。
- `robotmp/runner.py`：任务执行、恢复、Skill 验证和 A/B/C 实验。
- `robotmp/cli.py`：本地演示命令。
- `robotmp/sim_environment.py`：PyBullet 物理后端。
- `robotmp/sim_cli.py`：仿真运行入口。

## 与设计文档的对应关系

| 设计概念 | MVP 实现 |
|---|---|
| 结构化状态 | `SceneState`、`ObjectState`、`RobotState` |
| 未来状态预测 | `Prediction` 和 `make_prediction` |
| 预测残差/事件偏差 | `compare_prediction` |
| 候选失败 Skill | `RuleBasedDiagnoser` |
| Skill 经验库 | `SkillStore` |
| Skill 验证 | `validate_skill` |
| 后续任务检索 | `SkillStore.retrieve` |
| 多时间尺度安全边界 | 有限动作集合和 `stop` 动作 |

详细设计及实现状态见 [`docs/predictive_robotics_failure_skills.md`](docs/predictive_robotics_failure_skills.md)。

## 后续迭代

1. 将轻量环境替换为 PyBullet 或 MuJoCo 适配器。
2. 把规则诊断器替换为结构化输出的大模型适配器。
3. 将 JSON Skill 库迁移为 SQLite，并保存预测、观测和执行证据。
4. 增加物体位置过时、视觉遮挡和物体滑落等失败模式。
5. 实现 A/B/C 批量实验和指标报表。
6. 经过仿真和安全测试后，再接入 ROS2 或真实机器人。

## 进入 PyBullet 仿真阶段

当前规则环境仍保留为回归基线；仿真环境通过同一组 `reset / observe / execute` 动作接口接入。项目机器已有 Conda `py311` 环境，建议把 PyBullet 安装在那里，避免 Python 3.14 没有匹配的二进制包：

```powershell
conda run -n py311 python -m pip install pybullet==3.2.7
conda run -n py311 python -m robotmp.sim_cli --mode feedback --failure-mode low_grip_force --arm xarm6 --gui --realtime --hold 5 --trace artifacts/sim_xarm6.json
```

不需要窗口时去掉 `--gui`；无窗口运行适合批量实验。`--realtime` 按仿真时间推进，`--hold` 在 episode 结束后保留窗口。默认 `--arm xarm6` 使用 PyBullet 数据包中的 UFactory xArm6 URDF，6 个 revolute 关节的上下限、最大力矩和速度从 URDF 的 `getJointInfo` 读取，再通过末端逆运动学和 `POSITION_CONTROL` 移动；`--arm arm6dof` 保留项目自制模型，`--arm none` 可回退到原来的运动学腕部。xArm6 自带 URDF 夹爪传动；回退模式可用 `--gripper urdf` 或 `--gripper procedural`。低力度首次抓取会推动物体，恢复动作会读取新物体位置后重新规划末端。`--trace` 保存与现有 `run_episode(observer=...)` 相同结构的遥测。

对 xArm6 做物理 Skill 验证：

```powershell
conda run -n py311 python -m robotmp.sim_cli --validate-skill --trials 20 --failure-mode low_grip_force --arm xarm6 --store artifacts/xarm6_skills.json --trace artifacts/xarm6_skill_validation.json
```

流程会先用一次 `skills` episode 生成候选 Skill，再用 xArm6 物理环境重复验证，最后再次运行 `skills` episode。最后一次运行的遥测中应看到 `applied_skill_ids: ["grasp_without_lift_v1"]`。当前 Skill 学到的是“夹爪闭合不代表抬升成功”和“恢复前重新读取物体位置”；它不会训练神经网络，也不会自动更新电机参数。

仿真还会记录 `object_displaced_before_grasp`：如果闭合动作使物体位移超过 1 cm，会把它作为抓取前碰撞异常保存在事件历史中。xArm6 默认把物体生成在 `x=0.45 m`，避开 URDF 初始姿态，并在放置阶段下降到桌面高度后再释放，因此正常抓取会以 `finished` 结束，低力度场景则先经历推开、检测、重新定位和恢复。

代码位置：`robotmp/sim_environment.py` 是 PyBullet 后端，`robotmp/sim_cli.py` 是入口，`tests/test_simulation.py` 是仿真冒烟测试。xArm6 的关节动力学、限制和夹爪来自 `pybullet_data/xarm/xarm6_with_gripper.urdf`；预测、监控、诊断、Skill 和视频数据格式继续复用。

导出实际仿真画面：

```powershell
conda run -n py311 python -m pip install Pillow imageio-ffmpeg
conda run -n py311 python -m robotmp.sim_video --failure-mode low_grip_force
```

视频默认输出到 `artifacts/simulation_video/robotmp_simulation.mp4`，右侧参数栏来自 PyBullet 的实际状态和相机帧，原始事件保存在同目录 `trace.json`。

