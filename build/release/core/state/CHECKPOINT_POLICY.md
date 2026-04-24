# CHECKPOINT_POLICY.md - 检查点策略

## 目的
定义关键检查点规则，实现长流程可回退、可恢复、可复盘。

## 适用范围
所有需要检查点保护的长流程操作。

## 检查点类型

| 类型 | 触发时机 | 保留策略 | 用途 |
|------|----------|----------|------|
| 自动检查点 | 定时/状态变更 | 最近10个 | 自动恢复 |
| 关键检查点 | 关键节点 | 永久保留 | 回退和复盘 |
| 用户检查点 | 用户请求 | 用户指定 | 用户控制 |
| 强制检查点 | 高风险操作前 | 永久保留 | 安全回退 |

## 强制检查点节点

### 必须落检查点的场景
```yaml
mandatory_checkpoints:
  - name: "规划完成"
    trigger: "planning_phase_complete"
    content:
      - execution_plan
      - resource_allocation
      - risk_assessment
      
  - name: "检索完成"
    trigger: "retrieval_phase_complete"
    content:
      - retrieved_documents
      - relevance_scores
      - source_metadata
      
  - name: "文档草稿完成"
    trigger: "draft_complete"
    content:
      - draft_content
      - structure_outline
      - pending_validations
      
  - name: "最终输出前"
    trigger: "before_final_output"
    content:
      - final_content
      - quality_checks
      - citations
      
  - name: "高风险操作前"
    trigger: "before_high_risk_action"
    risk_conditions:
      - data_modification
      - external_api_call
      - irreversible_operation
    content:
      - operation_details
      - rollback_info
      - verification_data
```

## 检查点内容

### 标准内容
```yaml
checkpoint_content:
  metadata:
    - checkpoint_id
    - task_id
    - checkpoint_type
    - created_at
    - created_by
    
  state:
    - current_state
    - substate
    - progress_percentage
    - execution_context
    
  results:
    - intermediate_outputs
    - partial_artifacts
    - cached_data
    
  risk_info:
    - identified_risks
    - mitigation_actions
    - rollback_instructions
    
  rollback_point:
    - previous_checkpoint_id
    - rollback_data
    - rollback_steps
```

### 检查点结构
```json
{
  "checkpoint_id": "CP-TASK001-005",
  "task_id": "TASK-001",
  "checkpoint_type": "key",
  "name": "检索完成",
  "created_at": "2024-01-15T10:30:00Z",
  
  "state": {
    "current_state": "executing",
    "substate": "retrieval_complete",
    "progress": 40
  },
  
  "data": {
    "retrieved_docs": [...],
    "relevance_scores": {...},
    "query_history": [...]
  },
  
  "risk_info": {
    "risks": [],
    "mitigations": []
  },
  
  "rollback": {
    "previous_checkpoint": "CP-TASK001-004",
    "rollback_possible": true,
    "rollback_steps": ["restore_state", "clear_cache"]
  },
  
  "can_rollback": true,
  "retention": "permanent"
}
```

## 检查点创建

### 创建流程
```yaml
creation_flow:
  trigger_detection:
    - monitor_trigger_conditions
    - evaluate_checkpoint_necessity
    
  content_collection:
    - collect_current_state
    - gather_intermediate_results
    - prepare_rollback_data
    
  validation:
    - verify_content_integrity
    - check_storage_available
    
  storage:
    - save_to_primary_storage
    - replicate_to_backup
    - update_checkpoint_index
```

### 创建规则
```yaml
creation_rules:
  automatic:
    interval: "5m"
    on_state_change: true
    max_per_task: 10
    
  key_checkpoint:
    on_trigger: true
    permanent: true
    require_validation: true
    
  user_requested:
    on_user_command: true
    custom_retention: true
```

## 检查点恢复

### 恢复流程
```yaml
recovery_flow:
  selection:
    - list_available_checkpoints
    - show_checkpoint_summary
    - user_selects_or_auto_select
    
  validation:
    - verify_checkpoint_integrity
    - check_compatibility
    - validate_dependencies
    
  restoration:
    - restore_state
    - reload_context
    - recover_intermediate_results
    
  continuation:
    - determine_resume_point
    - notify_user
    - continue_execution
```

### 恢复验证
```yaml
recovery_validation:
  integrity_check:
    - checksum_verification
    - schema_validation
    - data_completeness
    
  compatibility_check:
    - version_compatibility
    - state_compatibility
    - resource_availability
    
  dependency_check:
    - external_dependencies_valid
    - internal_dependencies_satisfied
```

## 检查点回退

### 回退条件
```yaml
rollback_conditions:
  user_requested:
    - user_explicitly_requests
    - user_confirms_risk
    
  automatic:
    - error_detected
    - quality_check_failed
    - constraint_violated
    
  forced:
    - critical_error
    - data_corruption_detected
    - security_violation
```

### 回退流程
```yaml
rollback_flow:
  steps:
    - name: "评估回退影响"
      actions:
        - analyze_rollback_scope
        - identify_affected_data
        - estimate_recovery_time
        
    - name: "准备回退"
      actions:
        - save_current_state
        - prepare_rollback_data
        - notify_stakeholders
        
    - name: "执行回退"
      actions:
        - restore_checkpoint_state
        - clear_post_checkpoint_data
        - verify_restoration
        
    - name: "确认回退"
      actions:
        - validate_state
        - notify_user
        - log_rollback
```

## 检查点存储

### 存储策略
```yaml
storage_strategy:
  primary:
    type: "database"
    table: "task_checkpoints"
    indexing:
      - task_id
      - checkpoint_type
      - created_at
      
  backup:
    type: "file"
    path: "checkpoints/"
    format: "json"
    compression: true
    
  retention:
    automatic: "10 per task"
    key_checkpoint: "permanent"
    user_checkpoint: "user_defined"
    expired_cleanup: "daily"
```

### 存储优化
```yaml
storage_optimization:
  compression:
    enabled: true
    algorithm: "gzip"
    threshold: "1KB"
    
  deduplication:
    enabled: true
    scope: "same_task"
    
  incremental:
    enabled: true
    base: "previous_checkpoint"
    delta_only: true
```

## 检查点清理

### 清理规则
```yaml
cleanup_rules:
  expired_checkpoints:
    condition: "age > retention_period"
    action: "archive_or_delete"
    
  excess_checkpoints:
    condition: "count > max_per_task"
    action: "delete_oldest_non_key"
    
  completed_task_checkpoints:
    condition: "task_status == 'completed'"
    action: "archive_after_7d"
    
  failed_task_checkpoints:
    condition: "task_status == 'failed'"
    action: "retain_for_analysis"
```

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 检查点创建成功率 | 成功/总创建 | <99% |
| 检查点恢复成功率 | 成功/总恢复 | <95% |
| 检查点存储使用 | 存储空间占用 | >80% |
| 检查点创建延迟 | 创建耗时 | >5s |

## 维护方式
- 新增检查点类型: 更新检查点类型表
- 调整触发条件: 更新强制检查点配置
- 调整保留策略: 更新存储策略

## 引用文件
- `state/RESUME_POLICY.md` - 恢复策略
- `state/TASK_STATE_SCHEMA.json` - 任务状态结构
- `state/INTERRUPTION_HANDLING.md` - 中断处理
