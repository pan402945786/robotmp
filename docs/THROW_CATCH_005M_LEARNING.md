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
