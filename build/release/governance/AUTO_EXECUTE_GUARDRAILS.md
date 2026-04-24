# 自动执行护栏

## 概述

本文档定义自动执行（auto-execute）的护栏规则，确保自动处置安全、可控、可审计。

## 执行模式

### 1. nightly_auto - Nightly 自动执行
**允许的动作**:
- rebuild_dashboard
- rebuild_ops_state
- rebuild_bundle
- retry_notifications

**前置条件**:
| 条件 | 说明 |
|------|------|
| must_be_safe_auto | 必须是 safe_auto 动作 |
| no_blocking_alerts | 无阻塞级告警 |
| no_strong_regressions | 无强回归 |
| no_release_blocked | 未被阻塞发布 |
| p0_must_be_zero | P0 数量为 0 |
| not_in_cooldown | 不在冷却期 |
| within_retry_limit | 未超过重试上限 |
| circuit_not_open | 熔断器未开启 |

**开启方式**: 设置 `ENABLE_SAFE_REMEDIATION=true`

### 2. release_auto - Release 自动执行（更严格）
**允许的动作**:
- retry_notifications（仅此一个）

**仅 dry-run 的动作**:
- rebuild_dashboard
- rebuild_ops_state
- rebuild_bundle

**额外前置条件**:
- release_gate_passed: Release gate 必须通过

### 3. manual_only - 人工模式（默认）
**允许的动作**: 无（只允许 plan/dry-run）

**执行方式**: 必须人工调用 `ops_center.py remediation execute ...`

## 冷却机制

| 动作 | 冷却时间 |
|------|----------|
| rebuild_dashboard | 10 分钟 |
| rebuild_ops_state | 5 分钟 |
| rebuild_bundle | 10 分钟 |
| retry_notifications | 3 分钟 |

**规则**: 同一动作在冷却期内不会重复执行。

## 重试机制

| 重试次数 | 退避时间 |
|----------|----------|
| 第 1 次 | 1 分钟 |
| 第 2 次 | 2 分钟 |
| 第 3 次 | 5 分钟 |

**上限**: 最多重试 3 次。

## 熔断机制

| 动作 | 失败阈值 | 重置时间 |
|------|----------|----------|
| rebuild_dashboard | 3 次 | 30 分钟 |
| rebuild_ops_state | 3 次 | 30 分钟 |
| rebuild_bundle | 3 次 | 30 分钟 |
| retry_notifications | 5 次 | 15 分钟 |

**规则**: 连续失败达到阈值后，熔断器开启，拒绝执行直到重置时间到达。

## 拒绝场景

以下场景必须拒绝自动执行：

| 场景 | 原因 |
|------|------|
| 非 safe_auto 动作 | 安全限制 |
| 存在 blocking alerts | 需人工处理 |
| 存在 strong regressions | 需人工分析 |
| release blocked | 需人工决策 |
| P0 > 0 | 严重问题 |
| 冷却期内 | 防止重复执行 |
| 超过重试上限 | 防止无限重试 |
| 熔断器开启 | 防止雪崩 |
| 未显式开启 | 默认关闭 |

## 审计记录

每次 auto-execute 尝试都会记录到 `auto_execute_audit.json`：

```json
{
  "workflow": "nightly",
  "profile": "nightly_auto",
  "auto_execute_enabled": true,
  "action_considered": ["rebuild_dashboard"],
  "action_executed": ["rebuild_dashboard"],
  "action_denied": [],
  "deny_reasons": {},
  "preflight_result": "passed",
  "cooldown_hit": false,
  "circuit_open": false,
  "remediation_record_id": "rem_xxx"
}
```

## 查看状态

```bash
# 查看熔断状态
python scripts/remediation_center.py guard

# 查看审计记录
python scripts/remediation_center.py audit

# 通过 ops_center
python scripts/ops_center.py remediation guard
python scripts/ops_center.py remediation audit
```

## 人工接管

当出现以下情况时，需要人工接管：

1. 熔断器开启
2. 连续失败超过阈值
3. 存在 blocking alerts / strong regressions
4. P0 > 0
5. release blocked

**接管方式**:
```bash
# 手动执行
python scripts/remediation_center.py execute <action>

# 重置熔断器
python scripts/remediation_center.py guard --reset <action>
```

---

**版本**: V1.0.0
**更新时间**: 2026-04-12
