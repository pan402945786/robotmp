# 本地物理仿真运行结果

运行日期：2026-10-19（Asia/Shanghai）
代码基线：`af1bd3b6ff429c057be456c9ccc50cb348dfef05`

## 运行环境

项目目录内的 `.venv` 已建立，可通过 `run.ps1` 调用，无需系统 PATH 中的 `python`、Conda 激活或本机 C++ 编译器。

- Python：3.11.17，64 位 Windows。
- conda-forge 包：`pybullet=3.25`；对应 Python 包元数据版本：`3.2.5`。
- PyBullet API 版本：`202010061`。
- NumPy：2.4.6；Pillow：12.3.0；imageio-ffmpeg：0.6.0。
- xArm6：`pybullet_data/xarm/xarm6_with_gripper.urdf`。
- 已验证 `DIRECT` 无窗口物理仿真，以及 GUI 实时仿真；视频由 PyBullet 相机渲染。
- 项目已通过 editable 方式安装到 `.venv`，`pip check` 通过。

此环境使用 conda-forge 的 Windows 预编译包，没有把它记作 PyPI `pybullet==3.2.7`。可用仓库根目录的 `environment.yml` 重新创建；下载工具位于忽略目录 `artifacts/tools/`，micromamba 包缓存位于 `C:/Users/haina/.cache/rmp`，以避免 Windows 路径过长。

## 实测结果

`./run.ps1 -m unittest discover -s tests -v`：11 项全部通过，0 失败、0 跳过。其中 6 项为规则测试，5 项为物理后端测试。

| 物理场景 | 运行结果 | 最终证据 |
|---|---|---|
| xArm6 正常抓取 | `success` | 比较器 `match`，抬升后释放，最终阶段 `finished` |
| xArm6 低抓取力度 | `recovered` | 首次抬升偏差触发诊断，刷新位置、重试、抬升并释放，最终 `finished` |
| xArm6 抓取点偏移 | `recovered` | 首次失败后恢复，最终 `finished` |
| xArm6 遮挡 | `uncertain` | 低置信度触发 `stop`，事件包含 `safety_stop` |
| xArm6 Skill 物理验证 | `verified` | 20 次验证，恢复成功率 100%，误判成功率 0% |
| 验证后的 Skill 复用 | `recovered` | `applied_skill_ids=["grasp_without_lift_v1"]` |
| GUI 实时窗口 | `recovered` | Intel UHD Graphics / OpenGL 4.6，窗口启动、实时执行和退出均成功 |
| 物理相机视频 | 生成成功 | 1280 × 720，24 FPS，203 帧，约 8.46 秒；全片解码检查通过 |

低力度物理 episode 的实际高度（米）：

```text
首次闭合：0.750103
首次抬升：0.748714 → 未抬升
比较结果：deviation
错误：expected_lift_but_not_detected
      missing_event:object_lift_detected
      object_displaced_before_grasp
重新抓取后抬升：0.876287
释放后：0.767427，phase=finished
```

Skill 应用前，预测为 `expected_phase=transport, confidence=0.75`；应用后为 `expected_phase=lift, confidence=0.90`，并记录 `grasp_without_lift_v1`。

## 物理 A/B/C 对比

使用同一 xArm6 物理后端，在固定 `low_grip_force` 故障下，每组运行 20 次。

| 模式 | 次数 | 成功率 | 误判成功率 | 恢复率 | Skill 应用率 |
|---|---:|---:|---:|---:|---:|
| baseline | 20 | 0% | 100% | 0% | 0% |
| feedback | 20 | 100% | 0% | 100% | 0% |
| skills | 20 | 100% | 0% | 100% | 100% |

当前实验中 B、C 两组成功率相同，不能据此声称 C 优于 B。实验验证了 Skill 的生成、持久化、验证和复用；尚未证明它能提前消除首次抓取失败或减少重试。

## 对照总体架构图

原始架构见 `predictive_robotics_failure_skills.md` 第 3 节。

| 架构节点 | 本次物理运行对应内容 | 覆盖程度 |
|---|---|---|
| 用户目标 / 自然语言指令 | CLI 选择任务模式、故障、机械臂 | 固定抓取任务；无自然语言解析 |
| 大模型任务规划器 | `run_episode` 固定动作流程、`make_prediction` 规则预测 | 固定任务仍是规则；诊断节点已支持可配置模型 |
| 未来状态 / 预期事件 | `Prediction` 指定抬升标记、预期事件、阶段、置信度 | 已运行；没有完整未来轨迹预测 |
| 机器人技能与底层控制器 | xArm6 URDF、IK、关节 `POSITION_CONTROL` | 已运行；包含关节状态重置和固定抓取约束等简化 |
| 环境动作执行 | PyBullet 桌面、立方体、机械臂、碰撞和释放 | 已运行；没有连接真实机器人 |
| 多模态传感器反馈 | PyBullet 状态、关节状态、相机帧 | 已运行仿真反馈；没有真实传感器输入 |
| 状态估计 / 事件提取 | `observe` 输出 `SceneState`、物体位姿、抬升状态和事件 | 已运行；直接读取仿真真值 |
| 预测与实际比较 | `compare_prediction` 的 `match/deviation/uncertain` | 三个分支均已触发 |
| 偏差诊断 | `RuleBasedDiagnoser` 或 `OpenAICompatibleDiagnoser` | 规则和本机 CC Switch 大模型均已运行 |
| 候选 Skill 生成 | 首次失败生成 `grasp_without_lift_v1` 并保存 JSON | 已运行 |
| 仿真 / 安全测试 / 验证 | 20 次物理 feedback episode 后写入验证指标 | 验证流程已运行；晋级逻辑没有完整阈值及多场景安全门槛 |
| Skill 经验库更新 | `SkillStore` 持久化 `verified` 及指标 | 已运行 |
| 下一次预测前检索 | 后续 `skills` episode 检索已验证 Skill | 已运行 |
| 修正预测与策略 | 预期阶段、置信度改变；通用恢复流程执行 | 已运行预测修正；尚未学习新的力矩、姿态或轨迹 |

完整执行链：

```text
reset → retrieve（skills 模式）
→ approach_object → close_gripper → prediction → lift_object
→ comparison → diagnosis → candidate（skills 模式）
→ refresh_object_pose → retry_grasp → close_gripper → lift_object
→ move_to_target → release_object → result
→ 20 次验证 → verified → 后续任务检索与预测修正
```

任务成功沿用现有代码的指标：抬升和流程完成。释放结束有桌面附近高度检查，尚无精确目标位置误差、姿态误差或稳定性标准。恢复动作会清除注入故障；以上比例描述固定场景，不能外推为真实机器人成功率。

## 再次运行

在仓库根目录执行：

```powershell
.\run.ps1 -m unittest discover -s tests -v
.\run.ps1 -m robotmp.sim_cli --mode feedback --failure-mode low_grip_force --arm xarm6 --trace artifacts/xarm6_recovery.json
.\run.ps1 -m robotmp.sim_cli --validate-skill --trials 20 --failure-mode low_grip_force --arm xarm6 --store artifacts/xarm6_skills.json --trace artifacts/xarm6_skill_validation.json
.\run.ps1 -m robotmp.sim_video --failure-mode low_grip_force --output artifacts/simulation_video_xarm6
```

打开可交互仿真窗口：

```powershell
.\run.ps1 -m robotmp.sim_cli --mode feedback --failure-mode low_grip_force --arm xarm6 --gui --realtime --hold 5
```

上述 GUI 命令也已实测成功：窗口正常启动，低力度抓取恢复后保留 5 秒，随后正常退出；遥测保存在 `xarm6_gui.json`，启动及 OpenGL 日志保存在 `gui.log`。

## 本次产物

文件均位于 `artifacts/physical_verification/`：

- `tests.log`：11 项测试结果。
- `xarm6_normal.json`：正常任务的状态、预测、比较和动作遥测。
- `xarm6_recovery.json`：低力度失败恢复遥测。
- `xarm6_skills.json`：20 次物理验证后的 Skill。
- `xarm6_skill_validation.json`：首次学习及验证后复用遥测；原 CLI 不保存中间每次验证的逐步轨迹。
- `matrix_*_trace.json`：四种故障条件的物理遥测。
- `physical_experiment_summary.json`：物理 A/B/C 实验指标及四种故障的最终状态。
- `simulation_video/robotmp_simulation.mp4`：PyBullet 相机视频。
- `simulation_video/trace.json`：视频运行遥测。
- `simulation_video/preview.png`：视频预览帧。

这些输出和 `.venv` 均被 Git 忽略；环境文件、启动脚本和本文档保留在工作区供复用。


## 大模型诊断实测

2026 年 10 月 19 日，本机通过 CC Switch 的 `127.0.0.1:15723` 访问 OpenAI-compatible Responses API，指定 `gpt-6.1-sol`。xArm6 低抓取力度任务返回 `recovered`，遥测的诊断来源为 `OpenAICompatibleDiagnoser`，模型生成的候选 Skill 名称为 `candidate_grasp_without_lift_recovery`。客户端保留本地安全不变量并继续使用固定恢复动作。

本次还验证了两个边界：当前 provider 对 `gpt-5.4-mini` 返回模型不可用；服务端要求 JSON 输出请求的输入中明确出现 `JSON`，因此 Responses 请求会在输入前加入 JSON 输出约束。模型请求失败时，runner 会回退到规则诊断并记录 `diagnosis_fallback`。

真实调用产物位于 `artifacts/llm_verification/`：`run2.log`、`skills.json`、`xarm6_llm_trace.json`、`validated.log`、`validated_skills.json` 和 `validated_trace.json`。5 次模型诊断验证中，模型调用 5 次、回退 0 次，最终 Skill 验证成功率 100%、误判率 0%。这些文件被 Git 忽略，不包含在提交中。
