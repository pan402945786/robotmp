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
python -m robotmp.cli validate --trials 20\npython -m robotmp.cli experiment --trials 20 --failure-mode low_grip_force
```

运行后，Skill 会保存到 `artifacts/skills.json`。验证后的 Skill 状态为 `verified`，之后 `--mode skills` 会在任务开始时检索它。

## 当前模块

- `robotmp/environment.py`：轻量级抓取环境和失败注入。
- `robotmp/models.py`：结构化状态、预测结果和 Skill 数据结构。
- `robotmp/predictor.py`：MVP 规则预测器。
- `robotmp/monitor.py`：预测与观测比较器。
- `robotmp/diagnosis.py`：本地规则诊断器，后续可替换为大模型适配器。
- `robotmp/skills.py`：JSON-backed Skill 经验库。
- `robotmp/runner.py`：任务执行、恢复、Skill 验证和 A/B/C 实验。
- `robotmp/cli.py`：本地演示命令。

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

