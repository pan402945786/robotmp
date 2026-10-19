# 大模型诊断接入说明

更新时间：2026 年 10 月 19 日（Asia/Shanghai）

## 已实现

`robotmp.diagnosis.OpenAICompatibleDiagnoser` 通过标准库 `urllib` 调用 OpenAI-compatible API，支持两种协议：

- `responses`：`POST {base_url}/responses`，适配 CC Switch 的 Codex Responses 入口；
- `chat`：`POST {base_url}/chat/completions`，适配常见 Chat Completions 服务。

模型配置不写死在代码中。配置优先级是 CLI 参数覆盖环境变量，未覆盖项使用默认值。默认仍是规则诊断，只有 `--diagnoser llm` 或 `ROBOTMP_LLM_ENABLED=1` 配合 `--diagnoser auto` 才会调用模型。

## 本机验证

本机 CC Switch 监听：

```text
http://127.0.0.1:15723
```

探测到：

- `GET /health` 正常；
- `GET /v1/models` 正常；
- 当前可调用的 Codex 路径为 `POST /v1/responses`；
- `gpt-6.1-sol` 实际调用成功；
- `gpt-5.4-mini` 由当前 provider 返回模型不可用，因此不能作为默认模型。

如果 PowerShell 禁止运行 `.ps1`，请把下面命令中的 `run.ps1` 换成 `run.cmd`；`run.cmd` 直接调用项目 `.venv`，不需要修改系统执行策略。

实际物理运行命令：

```powershell
.\run.cmd -m robotmp.sim_cli `
  --mode skills `
  --failure-mode low_grip_force `
  --arm xarm6 `
  --diagnoser llm `
  --llm-base-url http://127.0.0.1:15723/v1 `
  --llm-model gpt-6.1-sol `
  --llm-wire-api responses `
  --store artifacts/llm_verification/skills.json `
  --trace artifacts/llm_verification/xarm6_llm_trace.json
```

结果：

```text
status: recovered
诊断来源: OpenAICompatibleDiagnoser
Skill 名称: candidate_grasp_without_lift_recovery
```

模型输出包括观察事实、失败假设、预测修正和恢复意图。客户端自动补齐两个安全不变量：

```text
do_not_enter_transport_phase
require_lift_evidence_before_transport
```

然后继续使用项目现有的 `refresh_object_pose → retry_grasp → lift → move_to_target → release` 恢复流程。

## 模型诊断视频

物理视频入口也支持模型参数。它会实际调用模型生成诊断，再录制同一 episode 的 PyBullet 相机画面，并在右侧显示 `LLM / OpenAI` 诊断器标签：

```powershell
.\run.cmd -m robotmp.sim_video `
  --failure-mode low_grip_force `
  --output artifacts/llm_video `
  --diagnoser llm `
  --llm-base-url http://127.0.0.1:15723/v1 `
  --llm-model gpt-6.1-sol `
  --llm-wire-api responses
```

本机已生成一版视频：`artifacts/llm_video_20261019_v2/robotmp_simulation.mp4`。视频中可以看到首次低力度抓取未抬升，随后重新定位和重抓，最后物体进入搬运阶段并完成释放；`trace.json` 中记录了 `OpenAICompatibleDiagnoser` 且没有发生规则回退。

## 安全与回退

模型输出不会直接成为执行器命令。诊断器只生成 `Skill`，而实际动作集合仍由本地 runner 和环境实现控制。输出中出现关节、马达、力矩、轨迹、位置控制或速度命令等底层控制内容时，客户端拒绝该 Skill；网络错误、HTTP 错误、JSON 错误和结构校验错误会记录 `diagnosis_fallback` 并回退确定性规则诊断。

这使得关闭 CC Switch、切换主机、模型暂时不可用或 provider 返回错误时，规则闭环仍然可运行。通过 `observer` 产生的遥测可以审计模型是否真正参与了诊断。

## 尚未完成

当前接入完成的是“模型生成结构化失败经验”，还有几项后续工作：

1. 为不同失败类型建立不同的 Skill schema 和安全校验，而不是共用 `grasp_without_lift_v1`；
2. 让模型根据历史验证指标参与 Skill 版本决策，同时保留本地晋级门槛；
3. 记录调用延迟、token、模型 ID 和请求失败原因；
4. 将恢复意图映射到经过验证的动作模板，而不是只使用固定恢复序列；
5. 在多个随机物体位置、故障强度和遮挡时长下比较规则诊断与模型诊断；
6. 接入真实视觉估计和 ROS2 前继续保持模型只能输出高层结构化诊断。
