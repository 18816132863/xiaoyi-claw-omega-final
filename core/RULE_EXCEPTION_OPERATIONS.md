# 规则例外操作策略 V1.0.0

## 概述

本文档定义规则例外的操作策略，包括谁可以创建、续期、撤销例外，以及相关流程。

---

## 一、操作权限

### 1. 创建例外 (create)

**权限要求：**
- 必须有明确的审批人 (`approved_by`)
- 必须有明确的负责人 (`owner`)
- 必须有关联工单 (`ticket_ref`) - 推荐但非强制

**适用场景：**
- 临时绕过某条规则
- 技术债务的临时豁免
- 紧急发布的例外

**不适用场景：**
- 永久绕过规则（应修改规则本身）
- 无明确期限的例外

### 2. 续期例外 (renew)

**权限要求：**
- 必须有审批人 (`approved_by`)
- 续期次数不能超过 `max_renewals`

**限制条件：**
- 默认最大续期次数：2 次
- 达到最大续期次数后，必须：
  - 撤销例外并修复问题，或
  - 修改规则本身

**续期流程：**
1. 检查当前续期次数
2. 如果 `renewal_count >= max_renewals`，拒绝续期
3. 如果允许续期，更新 `expires_at` 和 `renewal_count`
4. 记录操作历史

### 3. 撤销例外 (revoke)

**权限要求：**
- 必须有审批人 (`approved_by`)
- 必须有撤销原因 (`reason`)

**适用场景：**
- 问题已修复，不再需要例外
- 例外被滥用
- 例外的风险超过收益

**撤销后：**
- 例外状态变为 `revoked`
- 不可恢复（如需恢复，需重新创建）

### 4. 自动过期 (expire-check)

**执行时机：**
- 每次 CI 运行前
- 每日定时任务

**处理逻辑：**
1. 扫描所有 `status = active` 的例外
2. 如果 `expires_at < now`，自动改为 `expired`
3. 记录操作历史

---

## 二、例外生命周期

```
创建 (create)
    │
    ▼
  active ──────────────────┐
    │                      │
    ├── 续期 (renew) ──────┤
    │                      │
    ├── 撤销 (revoke) ──► revoked
    │
    └── 过期 (expire) ──► expired
```

---

## 三、字段说明

### 必填字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `rule_id` | 关联的规则ID | R001 |
| `reason` | 例外原因 | 临时绕过检查 |
| `owner` | 负责人 | alice |
| `approved_by` | 审批人 | bob |
| `status` | 状态 | active/expired/revoked |
| `created_at` | 创建时间 | 2026-04-14T10:00:00 |
| `expires_at` | 过期时间 | 2026-05-14T10:00:00 |

### 可选字段

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `duration_days` | 有效期(天) | 30 |
| `max_renewals` | 最大续期次数 | 2 |
| `renewal_count` | 已续期次数 | 0 |
| `ticket_ref` | 关联工单 | - |
| `last_renewed_at` | 最后续期时间 | - |
| `last_renewed_by` | 最后续期人 | - |
| `revoked_at` | 撤销时间 | - |
| `revoked_by` | 撤销人 | - |
| `revoke_reason` | 撤销原因 | - |

---

## 四、操作入口

**唯一入口：** `scripts/exception_manager.py`

**禁止操作：**
- ❌ 直接修改 `core/RULE_EXCEPTIONS.json`
- ❌ 通过其他脚本修改例外

**正确操作：**
```bash
# 创建例外
python scripts/exception_manager.py create \
    --rule-id R001 \
    --reason "临时绕过" \
    --owner alice \
    --approved-by bob

# 续期例外
python scripts/exception_manager.py renew \
    --exception-id EXC-R001-20260414-abc123 \
    --approved-by bob

# 撤销例外
python scripts/exception_manager.py revoke \
    --exception-id EXC-R001-20260414-abc123 \
    --approved-by bob \
    --reason "问题已修复"

# 自动过期检查
python scripts/exception_manager.py expire-check
```

---

## 五、历史记录

所有操作记录在 `reports/ops/rule_exception_history.json`

**记录字段：**
- `event_id`: 事件ID
- `exception_id`: 例外ID
- `action`: 操作类型 (create/renew/revoke/expire)
- `rule_id`: 规则ID
- `approved_by`: 审批人
- `owner`: 负责人
- `old_status`: 旧状态
- `new_status`: 新状态
- `old_expires_at`: 旧过期时间
- `new_expires_at`: 新过期时间
- `reason`: 原因
- `timestamp`: 时间戳

---

## 六、何时必须 revoke 而非 renew

以下情况必须撤销例外：

1. **问题已修复** - 不再需要例外
2. **达到最大续期次数** - 不能无限续期
3. **例外被滥用** - 风险超过收益
4. **规则已修改** - 例外不再适用
5. **安全审计要求** - 必须修复问题

---

## 七、ticket_ref 的作用

`ticket_ref` 用于关联工单系统：

- 追踪例外的来源
- 关联修复任务
- 审计时提供上下文

**推荐格式：** `JIRA-12345` 或 `GH-123`

---

## 八、审批流程

### 创建例外
1. 提交例外请求（包含 reason, owner, ticket_ref）
2. 审批人审核
3. 审批通过后执行 create

### 续期例外
1. 检查续期次数
2. 审批人审核
3. 审批通过后执行 renew

### 撤销例外
1. 提交撤销请求（包含 reason）
2. 审批人审核
3. 审批通过后执行 revoke

---

## 九、监控与告警

### Stale Exceptions
- 状态为 active 但超过 30 天未更新
- 建议审查是否仍需要

### Overused Exceptions
- 续期次数接近 max_renewals
- 建议修复问题而非继续续期

### High Debt Exceptions
- 例外关联的规则影响范围大
- 建议优先修复

---

## 十、文件位置

| 文件 | 说明 |
|------|------|
| `core/RULE_EXCEPTIONS.json` | 例外真源（只读） |
| `reports/ops/rule_exception_history.json` | 操作历史 |
| `scripts/exception_manager.py` | 操作入口 |
| `core/RULE_EXCEPTION_OPERATIONS.md` | 本文档 |
