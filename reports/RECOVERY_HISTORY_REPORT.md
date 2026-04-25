# Recovery History Report - 恢复历史报告

## 概述

本文档记录所有故障注入和自动恢复的历史。

## 统计

| 指标 | 值 |
|------|-----|
| 总故障注入 | 4 |
| 成功恢复 | 4 |
| 等待中 | 0 |
| 需人工干预 | 0 |
| 恢复率 | 100% |
| 总恢复尝试 | 8 |
| 总审计记录 | 4 |

## 故障注入详情

### 1. contact_service_timeout

| 字段 | 值 |
|------|-----|
| fault_id | fault_cf57bf38 |
| capability | query_contact |
| route_id | route.query_contact |
| final_result | recovered |
| human_action_required | False |
| executed_steps | 2 |

**恢复步骤**:
1. retry → 失败 (timeout)
2. limited_scope_probe → 成功

### 2. calendar_service_timeout

| 字段 | 值 |
|------|-----|
| fault_id | fault_be11ce93 |
| capability | query_calendar |
| route_id | route.query_calendar |
| final_result | recovered |
| human_action_required | False |
| executed_steps | 2 |

**恢复步骤**:
1. retry → 失败 (timeout)
2. limited_scope_probe → 成功

### 3. note_service_timeout

| 字段 | 值 |
|------|-----|
| fault_id | fault_5cee9e94 |
| capability | query_note |
| route_id | route.query_note |
| final_result | recovered |
| human_action_required | False |
| executed_steps | 2 |

**恢复步骤**:
1. retry → 失败 (timeout)
2. limited_scope_probe → 成功

### 4. location_service_timeout

| 字段 | 值 |
|------|-----|
| fault_id | fault_45895b23 |
| capability | get_location |
| route_id | route.get_location |
| final_result | recovered |
| human_action_required | False |
| executed_steps | 2 |

**恢复步骤**:
1. retry → 失败 (timeout)
2. limited_scope_probe → 成功

## L0 降级事件

### 降级链

| 序号 | before_mode | after_mode | success_rate | reason |
|------|-------------|------------|--------------|--------|
| 1 | normal_probe | fast_probe | 60.0% | success_rate < 80% |
| 2 | fast_probe | limited_scope_probe | 66.7% | success_rate < 80% |
| 3 | limited_scope_probe | cache_fallback | 71.4% | success_rate < 80% |
| 4 | cache_fallback | permission_diagnosis | 62.5% | success_rate < 80% |

### L0 Probe 结果

| route_id | mode | result | error |
|----------|------|--------|-------|
| route.query_note | normal_probe | ✓ | - |
| route.search_notes | normal_probe | ✓ | - |
| route.query_alarm | normal_probe | ✗ | timeout |
| route.query_contact | normal_probe | ✗ | timeout |
| route.get_location | normal_probe | ✓ | - |
| route.query_message_status | fast_probe | ✓ | - |
| route.list_recent_messages | limited_scope_probe | ✓ | - |
| route.check_calendar_conflicts | cache_fallback | ✗ | timeout |
| route.query_note | permission_diagnosis | ✓ | - |
| route.search_notes | permission_diagnosis | ✓ | - |

## 审计记录

| audit_id | event_type | failure_type | recovery_result | human_action_required |
|----------|------------|--------------|-----------------|----------------------|
| audit_f2e10b07 | fault_injection | contact_service_timeout | recovered | False |
| audit_be480a24 | fault_injection | calendar_service_timeout | recovered | False |
| audit_b77d6087 | fault_injection | note_service_timeout | recovered | False |
| audit_43084575 | fault_injection | location_service_timeout | recovered | False |

## 结论

1. **所有故障注入都成功恢复**，无需人工干预
2. **L0 降级链正确执行**，从 normal_probe 逐步降级到 permission_diagnosis
3. **恢复历史和审计记录完整**，可用于追溯和分析
