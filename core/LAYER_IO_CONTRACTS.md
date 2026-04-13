# 层间 IO 契约清单 V2.0.0

> **唯一真源** - 定义核心对象的输入输出契约

---

## 一、Registry Contract（技能注册表契约）

**文件真源**: `infrastructure/inventory/skill_registry.json`

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 技能名称 |
| display_name | string | 显示名称 |
| category | string | 类别 |
| path | string | 路径 |
| entry_point | string | 入口文件 |
| executor_type | string | 执行类型 |
| registered | boolean | 是否已注册 |
| routable | boolean | 是否可路由 |
| status | string | 状态 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| description | string | 描述 |
| priority | string | 优先级 |
| dependencies | array | 依赖列表 |
| timeout | number | 超时时间 |

### 关联 ID

- `skill_id`: 技能唯一标识（等于 name）

---

## 二、Execution Result Contract（执行结果契约）

**文件真源**: `execution/skill_adapter_gateway.py` 返回

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| data | object | 返回数据 |
| error | object | 错误信息 |
| error.code | string | 错误码 |
| error.message | string | 错误信息 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| execution_time | number | 执行时间(ms) |
| skill_id | string | 技能 ID |
| timestamp | string | 时间戳 |

### 关联 ID

- `execution_id`: 执行唯一标识
- `skill_id`: 技能 ID

---

## 三、Gate Report Contract（门禁报告契约）

**文件真源**: `reports/quality_gate.json`, `reports/release_gate.json`

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| profile | string | 门禁类型 (premerge/nightly/release) |
| overall_passed | boolean | 是否通过 |
| p0_count | number | P0 问题数 |
| local_status | string | 本地测试状态 |
| integration_status | string | 集成测试状态 |
| external_status | string | 外部测试状态 |
| verified_at | string | 验证时间 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total_checks | number | 总检查数 |
| passed_checks | number | 通过数 |
| failed_checks | number | 失败数 |
| errors | array | 错误列表 |
| warnings | array | 警告列表 |

### 关联 ID

- `gate_id`: 门禁唯一标识
- `run_id`: 运行唯一标识

---

## 四、Alert Contract（告警契约）

**文件真源**: `reports/alerts/latest_alerts.json`

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| alert_type | string | 告警类型 |
| severity | string | 严重程度 (critical/high/medium/low) |
| source_workflow | string | 来源 workflow |
| triggered_at | string | 触发时间 |
| blocked_reasons | array | 阻塞原因 |
| recommended_actions | array | 建议操作 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| alert_id | string | 告警 ID |
| status | string | 状态 |
| acknowledged_at | string | 确认时间 |
| resolved_at | string | 解决时间 |

### 关联 ID

- `alert_id`: 告警唯一标识
- `incident_id`: 关联的 Incident ID

---

## 五、Incident Contract（事件契约）

**文件真源**: `governance/ops/incident_tracker.json`

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| incident_id | string | 事件 ID |
| alert_type | string | 告警类型 |
| status | string | 状态 (open/investigating/mitigated/resolved/closed) |
| opened_at | string | 开启时间 |
| owner | string | 负责人 |
| resolution_note | string | 解决说明 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| description | string | 描述 |
| severity | string | 严重程度 |
| alerts | array | 关联告警 |
| timeline | array | 时间线 |

### 关联 ID

- `incident_id`: 事件唯一标识
- `alert_ids`: 关联的告警 ID 列表
- `remediation_id`: 关联的处置 ID

---

## 六、Remediation Contract（处置契约）

**文件真源**: `reports/remediation/latest_remediation.json`

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| action_id | string | 动作 ID |
| action_type | string | 动作类型 (safe_auto/semi_auto/forbidden_auto) |
| mode | string | 模式 |
| triggered_by | string | 触发者 |
| started_at | string | 开始时间 |
| finished_at | string | 结束时间 |
| success | boolean | 是否成功 |
| changed_files | array | 变更文件 |
| requires_approval | boolean | 是否需要审批 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| result | object | 结果 |
| error | string | 错误信息 |
| approval_id | string | 审批 ID |

### 关联 ID

- `action_id`: 处置唯一标识
- `incident_id`: 关联的事件 ID
- `approval_id`: 关联的审批 ID

---

## 七、Approval Contract（审批契约）

**文件真源**: `reports/remediation/approval_history.json`

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| approval_id | string | 审批 ID |
| action_type | string | 动作类型 |
| status | string | 状态 (pending/approved/executed/denied) |
| final_status | string | 最终状态 |
| created_at | string | 创建时间 |
| approved_by | string | 审批人 |
| approved_at | string | 审批时间 |
| executed_at | string | 执行时间 |
| execute_record_id | string | 执行记录 ID |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| action_params | object | 动作参数 |
| denial_reason | string | 拒绝原因 |
| notes | string | 备注 |

### 关联 ID

- `approval_id`: 审批唯一标识
- `execute_record_id`: 执行记录 ID（必须对应真实 remediation 记录）

---

## 八、Control Plane State Contract（控制平面状态契约）

**文件真源**: `reports/ops/control_plane_state.json`

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| overview | object | 概览 |
| gates | object | 门禁状态 |
| alerts | object | 告警状态 |
| incidents | object | 事件状态 |
| remediation | object | 处置状态 |
| approvals | object | 审批摘要 |
| dashboard | object | Dashboard 状态 |
| audit | object | 审计状态 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| notifications | object | 通知状态 |
| trends | object | 趋势状态 |
| timestamp | string | 时间戳 |

### 关联 ID

- `control_plane_id`: 控制平面唯一标识

---

## 九、Control Plane Audit Contract（控制平面审计契约）

**文件真源**: `reports/ops/control_plane_audit.json`

### 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| nightly_runs | array | Nightly 运行记录 |
| release_runs | array | Release 运行记录 |
| blocking_alerts | array | 阻塞告警 |
| incident_events | array | 事件记录 |
| remediation_events | array | 处置记录 |
| approvals | array | 审批记录 |

### 可选字段

| 字段 | 类型 | 说明 |
|------|------|------|
| timeline | array | 时间线 |
| timestamp | string | 时间戳 |

---

## 十、版本历史

- V2.0.0: 规则硬化版，明确必填字段和关联 ID
- V1.0.0: 初始版本

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-13
