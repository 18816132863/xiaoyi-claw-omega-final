# RESUME_POLICY.md - 任务恢复策略

## 目的
定义长任务或跨会话任务的恢复规则，确保中断后可继续执行。

## 适用范围
所有需要恢复能力的长时任务和跨会话任务。

## 恢复条件判断

### 可恢复条件
```yaml
resumable_conditions:
  required:
    - checkpoint_exists: true
    - state_valid: true
    - context_available: true
    
  optional:
    - user_present: false  # 用户在场非必需
    - resources_available: true
    - dependencies_satisfied: true
```

### 不可恢复条件
```yaml
non_resumable_conditions:
  - checkpoint_corrupted
  - state_expired  # 超过有效期
  - context_lost
  - dependencies_changed_significantly
  - user_cancelled
```

## 恢复内容加载

### 必须加载项
```yaml
required_load:
  - task_state:
      - task_id
      - current_state
      - substate
      - progress_percentage
      
  - project_context:
      - project_id
      - current_phase
      - active_milestones
      - key_decisions
      
  - hard_constraints:
      - time_constraints
      - budget_constraints
      - quality_constraints
      
  - pending_items:
      - incomplete_steps
      - pending_validations
      - waiting_inputs
```

### 可选加载项
```yaml
optional_load:
  - recent_decisions:
      - last_10_decisions
      - decision_context
      
  - failure_points:
      - last_failure
      - failure_reason
      - retry_count
      
  - intermediate_results:
      - cached_outputs
      - partial_artifacts
      
  - user_preferences:
      - communication_style
      - detail_level
```

## 恢复流程

### 标准恢复流程
```
恢复请求
    ↓
┌─────────────────────────────────────┐
│ 1. 验证恢复条件                      │
│    - 检查checkpoint存在              │
│    - 验证状态有效性                  │
│    - 确认资源可用                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 加载恢复内容                      │
│    - 加载任务状态                    │
│    - 加载项目上下文                  │
│    - 加载硬约束                      │
│    - 加载未完成项                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 状态一致性检查                    │
│    - 验证依赖状态                    │
│    - 检查外部条件                    │
│    - 确认无冲突                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 决定恢复方式                      │
│    - 安全续跑                        │
│    - 需要重新确认                    │
│    - 需要调整计划                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 5. 执行恢复                          │
│    - 恢复执行状态                    │
│    - 通知用户                        │
│    - 继续执行                        │
└─────────────────────────────────────┘
```

## 恢复方式

### 1. 安全续跑
```yaml
safe_resume:
  conditions:
    - all_dependencies_satisfied
    - no_significant_changes
    - checkpoint_recent  # 24小时内
    
  actions:
    - restore_state
    - continue_from_checkpoint
    - minimal_notification
    
  example: "任务在24小时内中断，直接继续"
```

### 2. 重新确认
```yaml
confirm_resume:
  conditions:
    - checkpoint_older_than: "24h"
    - external_changes_detected
    - user_preferences_unclear
    
  actions:
    - restore_state
    - present_summary
    - request_confirmation
    - adjust_if_needed
    
  example: "任务中断超过24小时，需要用户确认继续"
```

### 3. 调整计划
```yaml
adjusted_resume:
  conditions:
    - dependencies_changed
    - constraints_modified
    - resources_unavailable
    
  actions:
    - restore_state
    - analyze_changes
    - propose_adjustments
    - get_approval
    - execute_adjusted_plan
    
  example: "外部条件变化，需要调整执行计划"
```

### 4. 重新开始
```yaml
fresh_start:
  conditions:
    - checkpoint_invalid
    - context_lost
    - significant_time_passed  # 超过7天
    
  actions:
    - archive_old_state
    - create_new_task
    - start_fresh
    - reference_previous_attempt
    
  example: "任务状态已失效，重新开始"
```

## 恢复通知

### 通知内容
```yaml
notification_content:
  summary:
    - task_name
    - last_activity
    - time_elapsed
    - current_progress
    
  options:
    - continue_from_checkpoint
    - start_fresh
    - cancel
    
  context:
    - what_was_done
    - what_remains
    - any_issues
```

### 通知模板
```markdown
## 任务恢复提示

**任务**: ${task_name}
**中断时间**: ${elapsed_time}
**当前进度**: ${progress}%

### 已完成
${completed_items}

### 待完成
${pending_items}

### 请选择
1. 继续执行（从断点恢复）
2. 重新开始
3. 取消任务
```

## 检查点管理

### 检查点要求
```yaml
checkpoint_requirements:
  frequency:
    - on_state_change
    - on_major_step_complete
    - periodic: "5m"  # 长任务定期保存
    
  content:
    - current_state
    - intermediate_results
    - pending_actions
    - context_summary
    
  storage:
    - primary: database
    - backup: file
    - retention: "30d"
```

### 检查点验证
```yaml
checkpoint_validation:
  on_load:
    - verify_checksum
    - check_timestamp
    - validate_schema
    
  on_failure:
    - try_backup
    - reconstruct_from_logs
    - notify_admin
```

## 跨会话恢复

### 会话识别
```yaml
session_identification:
  methods:
    - user_id + project_id
    - task_id
    - session_token
    
  binding:
    - bind_task_to_user
    - track_session_changes
```

### 跨会话同步
```yaml
cross_session_sync:
  on_session_start:
    - check_pending_tasks
    - load_active_projects
    - restore_context
    
  on_session_end:
    - save_checkpoints
    - update_state
    - prepare_for_resume
```

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 恢复成功率 | 成功恢复/总恢复请求 | <90% |
| 恢复延迟 | 恢复操作耗时 | >10s |
| 检查点可用率 | 有效检查点/总检查点 | <95% |
| 数据丢失率 | 恢复时数据丢失 | >0 |

## 维护方式
- 调整恢复条件: 更新恢复条件配置
- 新增恢复方式: 创建恢复方式定义
- 调整通知: 更新通知模板

## 引用文件
- `state/CHECKPOINT_POLICY.md` - 检查点策略
- `state/TASK_STATE_SCHEMA.json` - 任务状态结构
- `projects/PROJECT_MEMORY_LINKING.md` - 项目记忆链接
