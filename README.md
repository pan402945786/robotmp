# robotmp

2026-10-20 抛前夹持修复与接回：修复联动关节和约束坐标框架，消除原 52.65 / 58.19 mm 夹持间隙；50 mm 方块约 10–11 cm 竖直小抛接回完成 20/20 独立审计，每次连续双指保持至少 1.004 秒，接回阶段无固定约束。通用失败经验已更新至 v25，限定短抛 skill 另存 verified。参见 [修复说明](docs/PRETHROW_GRASP_FIX.md)、[接回结果](docs/SHORT_VERTICAL_CATCH_RESULTS.md) 与 [实际视频](docs/short_vertical_catch_20261020_final/index.html)。

2026-10-20 50 mm 抛接更新：按用户要求缩小方块，质量仍为 100 g；完成 61 次尝试，出现受力双指接触，但最长连续接触约 0.117 s，尚未通过 0.5 s 保持。已修正小抛高时的碰撞恢复与双指接触制动。参见 [50 mm 实验结果](docs/THROW_CATCH_50MM_RESULTS.md) 和 [实际仿真视频](docs/throw_catch_50mm_20261020_final/index.html)。

2026-10-20 在线接回更新：新增只使用本次已送达位置观测和关节编码器的预测、重规划与接触检查；不读取旧完整飞行轨迹选点。14 次迭代尝试及几何检查尚未验证接稳，经验 skill 保持 candidate。当前模型的有效指间开口约 86.9 mm，小于 100 mm 方块，默认会在中心夹持适用条件检查时阻止发射。方法、失败反思、审计和运行命令见 [在线接回实验结果](docs/THROW_CATCH_ONLINE_RESULTS.md)。

2026-10-20 多圈实验：已实现多关节闭合轨迹逐圈加速；100 g 物体在 5 圈策略中，各圈竖直峰值依次约 2.17、3.10、3.81、4.47、4.66 m/s。底座预转后上挥最高 4.928 m/s，仍未达到两米释放门槛。实测圈数、限制、21 条轨迹审计及复现见 [多圈加速分析](docs/THROW_CATCH_SPIN_ANALYSIS.md)。

2026-10-20 联动实验：优化预摆姿态和肩肘腕启动时序后，100 g 物体峰值竖直速度达到 4.809 m/s，1 g 达到 4.972 m/s，仍未通过两米释放门槛。对照、限制和复现见 [多关节联动分析](docs/THROW_CATCH_COORDINATION_ANALYSIS.md)。

2026-10-20 减重实验：物体从 100 g 降至 0.1 g，当前轨迹峰值竖直速度仅从 2.027 增至 2.059 m/s，仍未达到两米任务要求。199 次对照/搜索/复验与复现命令见 [质量实验分析](docs/THROW_CATCH_MASS_ANALYSIS.md)。

`robotmp` 是一个按照《基于预测误差与失败经验 Skill 的具身智能系统》方案实现的最小可行版本。它用一个轻量级抓取环境验证下面的闭环：

```text
预测未来 → 执行动作 → 观察实际 → 比较偏差 → 诊断失败
→ 生成候选 Skill → 验证 Skill → 检索并修正下一次预测
```

当前 MVP 只实现“夹爪闭合但物体没有抬升”这一失败模式。项目既可以不依赖模型 API 运行规则闭环，也可以通过可配置的 OpenAI-compatible 接口调用大模型生成结构化诊断。

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

## Windows 项目独立仿真环境

Windows 可以使用 conda-forge 的预编译包创建项目内 `.venv`，无需本机 C++ 编译器。`run.cmd` 不依赖 PowerShell 执行策略；如果系统禁止运行 `.ps1`，优先使用它：


```powershell
conda env create --prefix .venv --file environment.yml
.\run.cmd -m unittest discover -s tests -v
.\run.cmd -m robotmp.sim_cli --mode feedback --failure-mode low_grip_force --arm xarm6 --trace artifacts/xarm6_recovery.json
.\run.cmd -m robotmp.sim_cli --validate-skill --trials 20 --failure-mode low_grip_force --arm xarm6 --store artifacts/xarm6_skills.json --trace artifacts/xarm6_skill_validation.json
.\run.cmd -m robotmp.sim_video --failure-mode low_grip_force --output artifacts/simulation_video_xarm6
```

也可用 `micromamba create --prefix .venv --file environment.yml` 创建同一环境。`run.cmd`（也可使用 `run.ps1`）会切换到仓库根目录，优先使用 `.venv/python.exe`，不存在时通过 `conda run -n py311` 使用已有仿真环境，并返回执行退出码。需要实时窗口时，在 `sim_cli` 命令后加上 `--gui --realtime --hold 5`。

`environment.yml` 使用 conda-forge 的 `pybullet=3.25` 包，其 Python 包元数据版本为 `3.2.5`；这与下文 PyPI 的 `pybullet==3.2.7` 是不同的发行版本。本机使用前者完成全部 11 项测试、20 次 xArm6 Skill 物理验证以及仿真视频生成。该环境的依赖由 conda-forge 管理，请按此节的环境文件创建。

本次物理运行结果和架构对应分析见 [`docs/LOCAL_RUN_RESULTS.md`](docs/LOCAL_RUN_RESULTS.md)。

## 可配置的大模型诊断

### 复用抓取 Skill，学习持物竖直画 8 字

通过本机 CC Switch（`127.0.0.1:15723`）调用大模型，提出高层运动参数，执行仿真、反馈实际结果并验证新 Skill：

```powershell
.\run.cmd -m robotmp.figure_eight --output artifacts/figure_eight_new_run
```

已验证的新 Skill 保存在 `assets/skills/vertical_figure_eight.json`。直接从文件加载并执行“抓起 → 在 Y–Z 竖直平面画完整 8 字 → 放下 → 稳定性检查”：

```powershell
.\run.cmd -m robotmp.figure_eight --replay-only --output artifacts/figure_eight_replay
```

加 `--gui` 可查看实时窗口；输出目录包含 `replay.mp4`、逐路点轨迹、JSONL 事件和完整模型日志。每一步同时追加到 [过程记录](docs/FIGURE_EIGHT_LEARNING.md)，每次模型调用的完整输入、原始输出和解析结果写入 [模型调用记录](docs/FIGURE_EIGHT_LLM_CALLS.md)。当前是预定义轨迹原语上的模型参数选择与 Skill 组合，使用固定抓取约束的 PyBullet 仿真。

偏差诊断支持规则实现和 OpenAI-compatible HTTP 大模型实现。默认使用规则诊断，不会自动访问网络或本机服务；需要接入模型时显式指定 `--diagnoser llm`。环境变量可以在不同主机上复用：

```powershell
$env:ROBOTMP_LLM_BASE_URL = "http://127.0.0.1:15723/v1"
$env:ROBOTMP_LLM_MODEL = "gpt-6.1-sol"
$env:ROBOTMP_LLM_WIRE_API = "responses"
$env:ROBOTMP_LLM_TIMEOUT = "90"

.\run.cmd -m robotmp.sim_cli `
  --mode skills `
  --failure-mode low_grip_force `
  --arm xarm6 `
  --diagnoser llm `
  --store artifacts/llm_skills.json `
  --trace artifacts/llm_trace.json
```

也可以不设置环境变量，直接传参数：

```powershell
.\run.cmd -m robotmp.sim_cli `
  --mode skills `
  --failure-mode low_grip_force `
  --arm xarm6 `
  --diagnoser llm `
  --llm-base-url http://127.0.0.1:15723/v1 `
  --llm-model gpt-6.1-sol `
  --llm-wire-api responses
```

视频入口也支持同样的模型参数：

```powershell
.\run.cmd -m robotmp.sim_video `
  --failure-mode low_grip_force `
  --output artifacts/llm_video `
  --diagnoser llm `
  --llm-base-url http://127.0.0.1:15723/v1 `
  --llm-model gpt-6.1-sol `
  --llm-wire-api responses
```

支持的配置变量：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `ROBOTMP_LLM_BASE_URL` | `http://127.0.0.1:15723/v1` | OpenAI-compatible API 的 base URL |
| `ROBOTMP_LLM_MODEL` | `gpt-6.1-sol` | 当前 provider 接受的模型 ID，应按主机配置修改 |
| `ROBOTMP_LLM_WIRE_API` | `responses` | `responses` 或 `chat` |
| `ROBOTMP_LLM_API_KEY` | 空 | 远程服务需要认证时设置；本机 CC Switch 通常不需要传入 |
| `ROBOTMP_LLM_TIMEOUT` | `90` | 单次诊断调用超时，单位秒 |
| `ROBOTMP_LLM_LOG` | `artifacts/llm_diagnosis.jsonl` | 请求、响应、解析结果和错误的 JSONL 日志路径 |
| `ROBOTMP_LLM_ENABLED` | `0` | `--diagnoser auto` 时设为 `1/true/yes/on` 才启用模型 |

模型只负责生成结构化失败诊断。客户端会：

- 只发送任务、预测、观测、比较结果和相关 Skill 上下文；
- 要求 JSON 输出，并把结果转换成项目的 `Skill` 数据结构；
- 强制保留“没有抬升证据就不能进入搬运阶段”的安全规则；
- 拒绝包含关节、马达、力矩、轨迹或底层控制器指令的模型输出；
- 模型服务不可用、输出格式错误或触发安全校验时回退到 `RuleBasedDiagnoser`；
- 在遥测中记录 `diagnosis` 的来源，回退时记录 `diagnosis_fallback`。

当前本机实测：CC Switch 的 `15723` 端口返回 OpenAI-compatible Responses API；`gpt-6.1-sol` 调用成功，`gpt-5.4-mini` 在当前 FennoAI 账号组返回模型不可用。因此模型 ID 必须配置，不能假设不同主机或 provider 使用同一名称。


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

## 夹取稳定性修复

PyBullet xArm6 环境已加入接近步进、可配置机械臂基座位置和基于实际接触位姿的抓取约束。xArm6 的高层 MVP 抓取会屏蔽不可控的刚体推挤，由本地策略判断抓取成功后建立固定约束，避免夹爪闭合瞬间把物体推离；20 次重复运行的正常抓取、低力度恢复和抓取点偏移恢复均保持稳定。

模型调用默认写入 `artifacts/llm_diagnosis.jsonl`，每次调用包含 `request`、`response`、`parsed_output` 或 `error` 记录；可用 `--llm-log` 或 `ROBOTMP_LLM_LOG` 指定路径。

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

当前实现进展、仿真入口、物理 Skill 验证结果、测试状态和边界见 [`docs/DEVELOPMENT_STATUS.md`](docs/DEVELOPMENT_STATUS.md)。

## 后续迭代

1. 扩展 PyBullet 或 MuJoCo 中的随机场景和故障强度。
2. 让大模型诊断参与多个失败类型、Skill 版本决策和动作模板选择。
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
