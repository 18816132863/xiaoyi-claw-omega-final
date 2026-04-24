# BLOCKER_POLICY.md - 阻塞状态治理

## 目的
定义阻塞状态的识别、处理和恢复策略。

## 适用范围
所有任务执行中遇到的阻塞情况。

## 阻塞类型

| 类型 | 说明 | 示例 | 恢复方式 |
|------|------|------|----------|
| 用户未提供信息 | 缺少必要输入 | 用户未提供需求文档 | 等待用户输入 |
| 外部工具失败 | 外部服务不可用 | API调用失败 | 重试/降级 |
| 依赖未完成 | 前置任务未完成 | 依赖任务未完成 | 等待/调整 |
| 来源冲突 | 信息矛盾 | 多来源数据冲突 | 消歧/确认 |
| 权限不足 | 无操作权限 | 无数据库访问权限 | 申请权限 |
| 预算耗尽 | 资源不足 | API配额用尽 | 申请预算/降级 |

## 阻塞识别

### 识别规则
```yaml
identification_rules:
  user_input_missing:
    detection:
      - required_input_not_provided
      - input_validation_failed
    indicators:
      - waiting_for_input_timeout
      - user_prompt_unanswered
      
  external_tool_failed:
    detection:
      - api_error_response
      - timeout_error
      - service_unavailable
    indicators:
      - error_code_match
      - retry_count_exceeded
      
  dependency_incomplete:
    detection:
      - dependency_status_check
      - prerequisite_not_met
    indicators:
      - blocked_by_task
      - waiting_for_milestone
      
  source_conflict:
    detection:
      - contradictory_information
      - multiple_sources_disagree
    indicators:
      - conflict_score_above_threshold
      
  permission_denied:
    detection:
      - access_denied_response
      - authorization_failed
    indicators:
      - permission_check_failed
      
  budget_exhausted:
    detection:
      - quota_exceeded
      - resource_limit_reached
    indicators:
      - usage_above_limit
```

## 阻塞处理

### 处理策略矩阵
```yaml
strategy_matrix:
  user_input_missing:
    immediate_action: "request_input"
    timeout: "30m"
    timeout_action: "escalate"
    recovery: "on_input_received"
    
  external_tool_failed:
    immediate_action: "retry_with_backoff"
    max_retries: 3
    fallback: "use_cached_or_alternative"
    recovery: "on_service_restored"
    
  dependency_incomplete:
    immediate_action: "wait_with_periodic_check"
    check_interval: "5m"
    max_wait: "24h"
    fallback: "propose_alternative_path"
    recovery: "on_dependency_completed"
    
  source_conflict:
    immediate_action: "request_clarification"
    timeout: "1h"
    fallback: "use_highest_confidence"
    recovery: "on_conflict_resolved"
    
  permission_denied:
    immediate_action: "request_permission"
    timeout: "4h"
    fallback: "skip_if_non_critical"
    recovery: "on_permission_granted"
    
  budget_exhausted:
    immediate_action: "notify_budget_owner"
    timeout: "24h"
    fallback: "switch_to_low_cost_mode"
    recovery: "on_budget_replenished"
```

### 处理流程
```
阻塞检测
    ↓
┌─────────────────────────────────────┐
│ 1. 阻塞分类                          │
│    - 识别阻塞类型                    │
│    - 评估严重程度                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 策略选择                          │
│    - 匹配处理策略                    │
│    - 评估替代方案                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 执行处理                          │
│    - 执行立即动作                    │
│    - 设置超时监控                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 等待恢复                          │
│    - 监控恢复条件                    │
│    - 执行超时动作                    │
└─────────────────────────────────────┘
```

## 超时处理

### 超时配置
```yaml
timeout_config:
  by_blocker_type:
    user_input_missing:
      initial: "30m"
      escalation: "2h"
      final: "24h"
      
    external_tool_failed:
      initial: "5m"
      escalation: "30m"
      final: "2h"
      
    dependency_incomplete:
      initial: "1h"
      escalation: "6h"
      final: "24h"
      
    source_conflict:
      initial: "1h"
      escalation: "4h"
      final: "24h"
      
    permission_denied:
      initial: "4h"
      escalation: "24h"
      final: "72h"
      
    budget_exhausted:
      initial: "24h"
      escalation: "72h"
      final: "168h"
```

### 超时动作
```yaml
timeout_actions:
  initial_timeout:
    - notify_owner
    - log_timeout_event
    
  escalation_timeout:
    - escalate_to_higher
    - propose_alternatives
    - increase_priority
    
  final_timeout:
    - mark_task_failed
    - archive_partial_results
    - notify_all_stakeholders
```

## 升级策略

### 升级级别
```yaml
escalation_levels:
  level_0:
    handler: "auto_handling"
    timeout: "initial_timeout"
    
  level_1:
    handler: "task_owner"
    timeout: "escalation_timeout"
    notification: "immediate"
    
  level_2:
    handler: "project_owner"
    timeout: "final_timeout"
    notification: "immediate"
    
  level_3:
    handler: "admin"
    timeout: "manual_resolution"
    notification: "immediate"
```

### 升级触发
```yaml
escalation_triggers:
  - condition: "timeout_exceeded"
    from_level: 0
    to_level: 1
    
  - condition: "escalation_timeout_exceeded"
    from_level: 1
    to_level: 2
    
  - condition: "critical_blocker"
    from_level: 0
    to_level: 2
    immediate: true
    
  - condition: "manual_escalation_requested"
    to_level: 3
```

## 恢复机制

### 恢复检测
```yaml
recovery_detection:
  user_input_missing:
    trigger: "input_received"
    validation: "input_valid"
    
  external_tool_failed:
    trigger: "service_available"
    validation: "health_check_passed"
    
  dependency_incomplete:
    trigger: "dependency_completed"
    validation: "status_verified"
    
  source_conflict:
    trigger: "conflict_resolved"
    validation: "resolution_confirmed"
    
  permission_denied:
    trigger: "permission_granted"
    validation: "access_verified"
    
  budget_exhausted:
    trigger: "budget_replenished"
    validation: "quota_available"
```

### 恢复流程
```yaml
recovery_flow:
  steps:
    - name: "检测恢复"
      action: "check_recovery_condition"
      
    - name: "验证状态"
      action: "validate_recovery"
      
    - name: "恢复执行"
      action: "resume_task"
      
    - name: "更新状态"
      action: "clear_blocker"
      
    - name: "通知相关方"
      action: "notify_recovery"
```

## 阻塞统计

### 统计指标
```yaml
statistics:
  metrics:
    - blocker_count_by_type
    - blocker_count_by_task
    - average_blocker_duration
    - blocker_resolution_rate
    - escalation_rate
    
  reporting:
    frequency: "daily"
    aggregation: ["by_type", "by_project", "by_time"]
```

## 监控告警

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 阻塞任务数 | 当前阻塞任务数 | >10 |
| 平均阻塞时长 | 平均阻塞时间 | >4h |
| 升级率 | 需升级/总阻塞 | >20% |
| 恢复失败率 | 超时未恢复/总阻塞 | >10% |

## 维护方式
- 新增阻塞类型: 更新阻塞类型表
- 调整策略: 更新处理策略矩阵
- 调整超时: 更新超时配置

## 引用文件
- `state/STATE_MACHINE.md` - 状态机
- `state/TASK_STATE_SCHEMA.json` - 任务状态结构
- `projects/DEPENDENCY_RULES.md` - 依赖规则
