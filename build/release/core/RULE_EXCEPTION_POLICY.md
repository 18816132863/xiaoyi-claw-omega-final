# 规则例外策略 V1.0.0

> 定义规则例外的申请、审批、生效和过期机制

---

## 一、例外适用范围

### 允许例外的规则

| 规则 ID | 规则名称 | 允许例外原因 |
|---------|----------|--------------|
| R004 | 变更影响规则 | 特定变更可能需要临时豁免 |
| R006 | 仓库完整性规则 | 新增测试文件可能需要临时豁免 |
| R007 | 技能安全规则 | 实验阶段规则允许豁免 |

### 禁止例外的规则

| 规则 ID | 规则名称 | 禁止例外原因 |
|---------|----------|--------------|
| R001 | 层间依赖规则 | 架构核心规则，不可豁免 |
| R002 | JSON 契约规则 | 契约核心规则，不可豁免 |
| R003 | 唯一真源规则 | 真源核心规则，不可豁免 |
| R005 | 规则自测规则 | 治理核心规则，不可豁免 |

---

## 二、例外审批人

| 规则 Owner | 审批权限 |
|------------|----------|
| architecture | 可审批 R001-R003 的例外申请（但禁止例外） |
| governance | 可审批 R004, R005, R007 的例外申请 |
| infrastructure | 可审批 R006, R008 的例外申请 |

---

## 三、例外最长时长

| Scope | 最长时长 |
|-------|----------|
| global | 30 天 |
| profile | 14 天 |
| file | 7 天 |

---

## 四、例外状态流转

### 1. 申请例外

- 提交 exception 申请
- 指定 rule_id, scope, reason, expires_at
- 等待审批

### 2. 审批通过

- `status: active`
- 记录 `approved_by`
- 记录 `created_at`

### 3. 过期

- 当 `now > expires_at`
- `status: expired`
- 例外不再生效

### 4. 撤销

- 审批人可随时撤销
- `status: revoked`
- 例外不再生效

---

## 五、过期后恢复阻断

当例外过期后：
1. 规则引擎自动恢复阻断行为
2. 在 `rule_exceptions_snapshot.json` 中记录过期例外
3. 在 summary 中显示 `Expired Exceptions`

---

## 六、例外生效条件

例外生效需同时满足：
1. `status = active`
2. `now <= expires_at`
3. 当前 profile 在 `applies_to.profiles` 中（或 profiles 为空）
4. 当前文件/路径在 `applies_to` 中（或 applies_to 为空）

---

## 七、例外记录要求

每次规则引擎运行时：
1. 记录所有 active exceptions
2. 记录所有 expired exceptions
3. 记录所有 revoked exceptions
4. 记录哪些规则被 waived

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-14
