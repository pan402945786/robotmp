# 50 mm 方块长距离抛出接回：2026-10-21

[观看最新一次验证视频](long_distance_catch_video_20261021/index.html) · [MP4](long_distance_catch_video_20261021/latest_experiment.mp4) · [数据来源与校验](long_distance_catch_video_20261021/manifest.json)

本轮在短距离竖直抛接成功 skill 的基础上，加入了有界水平抛出轨迹，并使用本次飞行的时间戳位置观测和关节编码器做在线接回。发射阶段由 xArm6 的 IK 轨迹产生速度，没有注入方块位置或速度；接回阶段没有创建方块固定约束。

最终验证目录为 [`long_distance_throw_catch_20261021_clean_validation`](long_distance_throw_catch_20261021_clean_validation/)，三次独立干净仿真全部通过：

| 指标 | 结果 |
|---|---:|
| 物体 | 50 mm 方块，100 g |
| 水平释放到下降段最近接近距离 | 0.1174 m |
| 相对短竖直抛接的水平位移 | 约 11.7 cm |
| 实测上抛增高 | 0.0505 m |
| 连续双指保持 | 1.0042 s |
| 保持结束物体速度 | 0.00152 m/s |
| 在线位置观测 | 79 帧 |
| 在线规划调用 | 1 次，因果输入 |
| 运动限制检查 | 通过 |
| 完整成功 | 3 / 3 |

验证后的 skill 已写入 [`long_distance_throw_catch_50mm.json`](../assets/skills/long_distance_throw_catch_50mm.json)，状态为 `verified`。它显式依赖 [`short_vertical_throw_catch_50mm_v1`](../assets/skills/short_vertical_throw_catch_50mm.json)，适用条件限定为 PyBullet xArm6、50 mm 方块和至少 0.10 m 的水平范围。

## 失败反思

- 直接把短抛的静止接回逻辑用于横向运动时，手会在碰撞恢复前追随物体，产生单指接触或错过物体。
- 仅按 15 mm 几何净空恢复碰撞，在移动接回中可能太晚；长距离策略改为观测到下降、飞行至少 0.18 s 且预测距离不超过 0.25 m 后恢复碰撞。
- 下降段接触后必须切换到接触制动并保持实测指角；连续全闭合会把方块挤出。
- 噪声 2 mm、33.3 ms 延迟和 10% 漏帧的探索试验中，第一档参数 2/3 通过，1 次因接回时机失配失败，因此验证 skill 没有宣称对最差传感条件鲁棒。记录保存在 `long_distance_throw_catch_20261021_final2`。
- 将目标端点继续推到 15 cm、降低横向速度以保留接触裕量时，单次试验仍接回成功，但实际释放到最近下降接近点为 12.6 cm；因此当前 skill 把 11.7 cm 作为三次验证的保守范围，15 cm 目标仍是待继续优化的候选。
- 审计中“碰撞恢复时间与首次接触时间相差一帧”的边界已修正为带容差的非严格比较，避免把真实分离误判为失败。

## 复现

```powershell
# 三次独立干净验证
.\\run.cmd -m robotmp.long_distance_throw_catch `
  --output docs\\long_distance_throw_catch_20261021_clean_validation `
  --trials-per-config 3 --clean

# 含噪声、延迟和漏帧的探索与反思
.\\run.cmd -m robotmp.long_distance_throw_catch `
  --output docs\\long_distance_throw_catch_20261021_final2 `
  --trials-per-config 3
```

这是仿真范围内的长距离接回 skill；尚未证明真实相机、真实 xArm6 或更大方块尺寸下的性能。
