# 自愈审计策略

## 概述

本文档定义自愈（self-healing）动作的审计要求，确保每次自动处置都有完整记录。

## 审计对象

### 1. 自动执行审计
**文件**: `reports/remediation/auto_execute_audit.json`

**记录内容**:
| 字段 | 说明 |
|------|------|
| workflow | 来源 workflow (nightly/release-gate) |
| profile | 执行策略 (nightly_auto/release_auto/manual_only) |
| auto_execute_enabled | 是否开启自动执行 |
| action_considered | 考虑执行的动作列表 |
| action_executed | 实际执行的动作列表 |
| action_denied | 被拒绝的动作列表 |
| deny_reasons | 拒绝原因映射 |
| preflight_result | 前置检查结果 |
| cooldown_hit | 是否命中冷却 |
| circuit_open | 熔断器是否开启 |
| remediation_record_id | 关联的处置记录 ID |
| timestamp | 审计时间戳 |

### 2. 熔断状态审计
**文件**: `reports/remediation/remediation_guard.json`

**记录内容**:
| 字段 | 说明 |
|------|------|
| action_type | 动作类型 |
| root_cause_key | 根因标识 |
| retry_count | 重试次数 |
| last_attempt_at | 最后尝试时间 |
| last_success_at | 最后成功时间 |
| circuit_open | 熔断器是否开启 |
| circuit_reason | 熔断原因 |
| circuit_opened_at | 熔断开启时间 |

### 3. 处置历史审计
**文件**: `reports/remediation/history/*.json`

**记录内容**:
| 字段 | 说明 |
|------|------|
| action_id | 动作 ID |
| action_type | 动作类型 |
| mode | 执行模式 (plan/dry-run/execute/auto-execute) |
| triggered_by | 触发来源 (manual/workflow) |
| source_alert | 来源告警 |
| source_incident | 来源 incident |
| started_at | 开始时间 |
| finished_at | 结束时间 |
| success | 是否成功 |
| changed_files | 修改的文件 |
| error | 错误信息 |
| requires_approval | 是否需要审批 |

## 审计查询

### 查看最近自动执行审计
```bash
python scripts/remediation_center.py audit --last 10
```

### 查看被拒绝的动作
```bash
python scripts/remediation_center.py audit --denied
```

### 查看特定 workflow 的审计
```bash
python scripts/remediation_center.py audit --workflow nightly
```

### 查看熔断状态
```bash
python scripts/remediation_center.py guard
```

## 审计保留

| 类型 | 保留时间 |
|------|----------|
| auto_execute_audit.json | 30 天 |
| remediation_guard.json | 永久 |
| history/*.json | 90 天 |

## 审计报告

### Workflow Summary 集成
每次 workflow 运行后，summary 中显示：

```
## 🔧 Remediation Summary
- Auto execute: enabled/disabled
- Profile: nightly_auto
- Executed: rebuild_dashboard, rebuild_ops_state
- Denied: retry_notifications (reason: cooldown)
- Circuit open: false
```

### 定期审计报告
建议每周生成审计报告，包含：

1. 自动执行次数统计
2. 成功/失败比例
3. 被拒绝的动作及原因
4. 熔断器触发次数
5. 需要人工介入的情况

## 合规要求

1. **完整性**: 每次自动执行必须有审计记录
2. **准确性**: 审计记录必须反映真实执行情况
3. **可追溯**: 审计记录必须能追溯到具体的 workflow run
4. **不可篡改**: 审计记录写入后不应被修改

## 异常处理

### 审计记录缺失
如果发现审计记录缺失：
1. 检查 remediation_center.py 是否正常执行
2. 检查文件系统权限
3. 手动补充记录（如有其他日志来源）

### 审计记录异常
如果发现审计记录异常：
1. 停止自动执行
2. 调查异常原因
3. 修复后恢复

---

**版本**: V1.0.0
**更新时间**: 2026-04-12
