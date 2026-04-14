# 规则例外债务策略 V1.0.0

> 定义例外债务的识别、治理和升级机制

---

## 一、例外状态定义

### 1. healthy_exception（健康例外）

**条件**：
- 未过期
- 未超续期次数
- 未到 escalation 阈值

**行为**：正常豁免，不产生告警

### 2. stale_exception（陈旧例外）

**条件**（满足任一）：
- 距离 `expires_at` 少于 `warning_days` 天
- 已超过 `escalation_after_days` 天

**行为**：
- 进入 warning_rules
- 在 summary 中显示
- 不立即阻断

### 3. overused_exception（滥用例外）

**条件**：
- `renewal_count >= max_renewals`

**行为**：
- 进入 warning_rules
- 如果 `debt_level=high` 且规则 `blocking=true`，进入 blocking_failures
- 需要升级处理

### 4. expired_exception（过期例外）

**条件**：
- `now > expires_at`

**行为**：
- 不再生效
- 原规则恢复原始行为
- 在 summary 中显示

---

## 二、债务等级定义

| 等级 | warning_days | max_renewals | 说明 |
|------|--------------|--------------|------|
| low | 7 | 3 | 低风险，可多次续期 |
| medium | 5 | 2 | 中风险，限制续期 |
| high | 3 | 1 | 高风险，严格限制 |

---

## 三、续期规则

### 允许续期的例外

- `debt_level=low` 且 `renewal_count < max_renewals`
- `debt_level=medium` 且有 ticket_ref
- 必须有 owner 确认

### 不允许续期的例外

- `debt_level=high` 且 `renewal_count >= max_renewals`
- 禁止例外的规则（R001, R002, R003, R005）
- 无 owner 的例外

---

## 四、升级处理

### 自动升级条件

- `overused_exception` 且 `debt_level=high`
- `stale_exception` 持续超过 7 天

### 升级流程

1. 生成告警
2. 通知 owner
3. 记录到 `rule_exception_debt.json`
4. 如果 3 天内未处理，自动失效

---

## 五、例外债务快照

**路径**: `reports/ops/rule_exception_debt.json`

**内容**：
- active_count
- stale_count
- overused_count
- expired_count
- high_debt_count
- exceptions_by_owner
- exceptions_by_rule
- generated_at

---

## 六、例外不是永久通行证

**核心原则**：
- 例外是临时豁免，不是永久权利
- 超期和滥用要开始有成本
- 债务积累到阈值必须处理

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-14
