# CI/发布策略 V1.0.0

## 概述

本文档定义 OpenClaw 项目的 CI 门禁策略和发布流程。

## Workflow 说明

### 1. Premerge Gate (`.github/workflows/premerge.yml`)

**触发条件：**
- Pull Request 到 main/master/develop 分支
- Push 到 main/master 分支
- 手动触发 (workflow_dispatch)

**执行内容：**
- 运行 `make verify-premerge`
- 检查 P0 硬编码路径 = 0
- 检查 Local 层通过
- Integration/External 不阻塞

**Artifacts 保留：** 7 天

### 2. Nightly Audit (`.github/workflows/nightly.yml`)

**触发条件：**
- 定时触发：每天 2:00 UTC
- 手动触发 (workflow_dispatch)

**执行内容：**
- 运行 `python scripts/run_nightly_audit.py`
- 比较 runtime/quality/release 三类报告
- 检测强回归/弱回归
- 生成趋势数据

**Artifacts 保留：** 30 天

### 3. Release Gate (`.github/workflows/release-gate.yml`)

**触发条件：**
- 手动触发 (workflow_dispatch)
- Tag push (v*)
- Release 发布

**执行内容：**
- 运行 `make verify-release`
- 检查 P0 = 0
- 检查 Local/Integration 通过
- 检查 External 无 error
- 检查 Quality Gate 通过
- 检查 can_release = true

**Artifacts 保留：** 90 天

## 回归规则

### 强回归（阻塞发布）

| 规则 | 说明 |
|------|------|
| P0 上升 | 主链硬编码路径增加 |
| local pass → fail | 本地技能测试失败 |
| integration pass → fail | 集成技能测试失败 |
| quality pass → fail | 质量检查退化 |
| can_release true → false | 发布门禁退化 |

### 弱回归（警告）

| 规则 | 说明 |
|------|------|
| P1/P2 上升 | 工具链/历史遗留增加 |
| skipped reason 变化 | 外部技能跳过原因变化 |
| skill 总数异常 | 技能数量大幅波动 |
| 元数据缺失 | 新技能缺 test_mode 等 |

## Skipped External 口径

External 技能因缺少环境变量而 skipped 是**正常状态**，不阻塞发布。

**当前 External 技能：**
- find-skills (需要 SKILLHUB_TOKEN)
- huawei-drive (需要 HUAWEI_DRIVE_TOKEN)
- xiaoyi-image-understanding (需要 XIAOYI_TOKEN)

**处理方式：**
- skipped → 正常，不阻塞
- fail/error → 需要调查，阻塞 release

## Blocked Reasons 处理

当门禁被阻塞时：

1. **查看 Summary** - GitHub Step Summary 显示具体原因
2. **下载 Artifacts** - 查看完整报告
3. **修复问题** - 根据原因修复
4. **重新触发** - 修复后重新运行 workflow

## Artifact 保留策略

| Workflow | 保留时间 | 原因 |
|----------|----------|------|
| premerge | 7 天 | PR 生命周期短 |
| nightly | 30 天 | 趋势分析需要 |
| release | 90 天 | 发布追溯需要 |

## 本地测试

在提交 PR 前，建议本地测试：

```bash
# 测试 premerge
make verify-premerge

# 测试 nightly
python scripts/run_nightly_audit.py

# 测试 release
make verify-release
```

## 更新记录

- 2026-04-12: V1.0.0 初始版本

---

## 告警与值守策略

### 告警事件分类

| 事件类型 | 严重级别 | 触发条件 |
|----------|----------|----------|
| P0_BLOCKED | 阻塞级 | p0_count > 0 |
| STRONG_REGRESSION | 阻塞级 | strong_regressions 非空 |
| RELEASE_BLOCKED | 阻塞级 | can_release = false |
| WEAK_REGRESSION | 警告级 | weak_regressions 非空 |

### 告警输出

每次运行告警生成后，输出：
- `reports/alerts/latest_alerts.json` - 最新告警
- `reports/alerts/history/{timestamp}_alerts.json` - 历史快照
- `governance/ops/incident_tracker.json` - Incident 闭环记录

### 值守流程

1. **发现阻塞级告警**
   - 查看 `latest_alerts.json` 确认告警类型
   - 查看 `blocked_reasons` 了解具体原因
   - 查看 `recommended_actions` 获取处理建议

2. **处理告警**
   - 修复问题代码
   - 重新运行门禁验证
   - 告警消失后 incident 自动关闭

3. **Incident 闭环**
   - 阻塞级告警自动创建 open incident
   - 告警恢复后自动标记为 resolved
   - 可手动添加 `resolution_note`

### 通知渠道

当前支持：
- GitHub Actions Summary（自动）
- Generic Webhook（可选，配置 `ALERT_WEBHOOK_URL` 环境变量）

**注意**：Webhook 未配置时，告警仅保存本地，不影响门禁结果。
