# 规则例外门禁强制策略 V1.0.0

## 概述

本文档定义规则例外在 CI/CD 门禁中的强制行为，包括 premerge、nightly、release 三个阶段对例外的处理方式。

---

## 一、门禁前置步骤：expire-check

### 执行时机

所有门禁（premerge / nightly / release）开始前，必须先执行：

```bash
python scripts/exception_manager.py expire-check
```

### 目的

- 把已过期但仍是 `active` 的例外，自动转成 `expired`
- 让 `expired` 成为真源状态，而不是运行时推断
- 确保后续检查基于最新的例外状态

### 执行逻辑

1. 扫描 `RULE_EXCEPTIONS.json` 中所有 `status = active` 的例外
2. 如果 `expires_at < now`，自动改为 `expired`
3. 写入 `rule_exception_history.json`

---

## 二、例外状态快照

### 文件位置

`reports/ops/rule_exception_status.json`

### 内容

| 字段 | 说明 |
|------|------|
| `active_count` | 活跃例外数量 |
| `soon_expiring_count` | 即将过期数量（≤7天） |
| `stale_count` | 陈旧例外数量（>30天未更新） |
| `overused_count` | 超续期例外数量 |
| `expired_count` | 已过期例外数量 |
| `revoked_count` | 已撤销例外数量 |
| `high_debt_count` | 高债务例外数量 |
| `by_owner` | 按负责人分组统计 |
| `generated_at` | 生成时间 |

### 刷新时机

每次 `create / renew / revoke / expire-check` 后自动刷新。

---

## 三、门禁行为

### premerge

| 例外类型 | 行为 |
|----------|------|
| expired | 不再生效，跳过 |
| stale | ⚠️ warning，不阻断 |
| overused | ⚠️ warning，不阻断 |
| high debt | ⚠️ warning，不阻断 |

### nightly

| 例外类型 | 行为 |
|----------|------|
| expired | 不再生效，跳过 |
| stale | ⚠️ warning，不阻断 |
| overused | ⚠️ warning，不阻断 |
| high debt | ⚠️ warning，不阻断 |

### release

| 例外类型 | 行为 |
|----------|------|
| expired | 不再生效，跳过 |
| stale | ⚠️ warning，不阻断 |
| overused | ⚠️ warning，不阻断 |
| **high debt + overused + blocking rule** | ❌ **阻断** |

---

## 四、高风险例外阻断规则

### 阻断条件（必须同时满足）

1. `debt_level = high`
2. `renewal_count >= max_renewals`
3. 对应 rule 的 `enforcement = blocking`

### 阻断原因

- 高债务：例外影响范围大
- 超续期：已多次续期，问题仍未修复
- blocking rule：规则本身是阻断级别

### 解决方式

1. 修复问题，撤销例外
2. 修改规则本身（如果规则不再适用）
3. 降低债务级别（如果影响范围已缩小）

---

## 五、为什么 expire-check 要前置执行

### 问题

如果只在 rule engine 运行时判断过期：
- `expired` 只是运行时推断
- 真源状态仍是 `active`
- 无法追溯何时过期
- 无法在历史记录中看到过期事件

### 解决

前置执行 `expire-check`：
- `expired` 成为真源状态
- 写入历史记录
- 后续检查基于最新状态
- 可追溯过期时间

---

## 六、Summary 显示

### Exception Status

```
Exception Status
- Active Exceptions: <active_count>
- Soon Expiring Exceptions: <soon_expiring_count>
- Expired Exceptions: <expired_count>
- Revoked Exceptions: <revoked_count>
```

### Recent Exception Actions

```
Recent Exception Actions (24h)
- create: <count>
- renew: <count>
- revoke: <count>
- expire: <count>
```

---

## 七、文件位置

| 文件 | 说明 |
|------|------|
| `scripts/exception_manager.py` | 例外管理器 |
| `scripts/run_release_gate.py` | 门禁入口 |
| `core/RULE_EXCEPTIONS.json` | 例外真源 |
| `reports/ops/rule_exception_status.json` | 状态快照 |
| `reports/ops/rule_exception_history.json` | 操作历史 |
| `core/RULE_EXCEPTION_ENFORCEMENT_POLICY.md` | 本文档 |

---

## 八、示例

### expire-check 自动转 expired

```bash
$ python scripts/exception_manager.py expire-check
{
  "status": "success",
  "expired_count": 2,
  "expired": ["EX001", "EX003"],
  "message": "已处理 2 个过期例外"
}
```

### release 被高风险例外阻断

```bash
$ python scripts/run_release_gate.py release

==================================================
【Exception Constraint Violation】
==================================================
  Reason: 存在高风险例外：high debt + overused + blocking rule
  - EX005: R004
    debt_level: high, renewals: 2/2
==================================================
❌ Release blocked by high-risk exceptions
```

---

## 九、版本

- V1.0.0 - 2026-04-15 - 初始版本
