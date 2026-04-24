# INTERRUPTION_HANDLING.md - 中断处理策略

## 目的
定义任务执行中被用户打断、改需求、插入新问题时的处理规则。

## 适用范围
所有任务执行中的中断场景。

## 中断类型

| 类型 | 说明 | 示例 | 处理方式 |
|------|------|------|----------|
| 用户打断 | 用户主动中断 | "等一下，先处理这个" | 暂停当前任务 |
| 需求变更 | 用户修改需求 | "不对，我要的是..." | 变更当前任务 |
| 插入问题 | 用户插入新问题 | "顺便问一下..." | 并行挂起 |
| 取消任务 | 用户取消任务 | "不用做了" | 取消旧任务 |
| 优先级调整 | 用户调整优先级 | "这个更紧急" | 重新排序 |

## 中断检测

### 检测规则
```yaml
detection_rules:
  user_interrupt:
    patterns:
      - "等一下"
      - "先处理"
      - "暂停"
      - "停一下"
    confidence: 0.9
    
  requirement_change:
    patterns:
      - "不对"
      - "我要的是"
      - "改一下"
      - "不是这个"
    confidence: 0.8
    
  inserted_question:
    patterns:
      - "顺便问"
      - "还有个问题"
      - "对了"
    confidence: 0.7
    
  task_cancellation:
    patterns:
      - "不用做了"
      - "取消"
      - "算了"
    confidence: 0.9
    
  priority_change:
    patterns:
      - "更紧急"
      - "优先"
      - "先做这个"
    confidence: 0.8
```

## 处理策略

### 1. 暂停当前任务
```yaml
pause_current:
  trigger: "user_interrupt"
  
  actions:
    - name: "保存状态"
      steps:
        - create_checkpoint
        - save_intermediate_results
        - record_progress
        
    - name: "通知用户"
      message: "已暂停当前任务，请处理新需求"
      
    - name: "等待指令"
      timeout: "30m"
      on_timeout: "ask_resume_or_cancel"
      
  resume_condition:
    - user_requests_resume
    - new_task_completed
```

### 2. 变更当前任务
```yaml
change_current:
  trigger: "requirement_change"
  
  actions:
    - name: "确认变更"
      steps:
        - clarify_new_requirement
        - confirm_change_scope
        - get_user_confirmation
        
    - name: "调整任务"
      steps:
        - update_task_definition
        - recalculate_plan
        - adjust_resources
        
    - name: "继续执行"
      steps:
        - apply_new_plan
        - continue_from_adjusted_point
        
  rollback:
    enabled: true
    checkpoint: "before_change"
```

### 3. 并行挂起
```yaml
parallel_suspend:
  trigger: "inserted_question"
  
  actions:
    - name: "评估插入问题"
      steps:
        - analyze_complexity
        - estimate_time
        - check_dependency
        
    - name: "决策处理方式"
      conditions:
        - if: "simple_question"
          action: "answer_immediately"
        - if: "complex_question"
          action: "create_parallel_task"
        - if: "related_to_current"
          action: "integrate_into_current"
          
    - name: "执行处理"
      steps:
        - handle_inserted_question
        - return_to_main_task
        
  context_isolation:
    enabled: true
    separate_context: true
```

### 4. 取消旧任务
```yaml
cancel_task:
  trigger: "task_cancellation"
  
  actions:
    - name: "确认取消"
      steps:
        - confirm_cancellation
        - record_reason
        
    - name: "清理资源"
      steps:
        - release_resources
        - archive_partial_results
        - update_statistics
        
    - name: "通知完成"
      message: "任务已取消"
```

### 5. 优先级调整
```yaml
priority_adjustment:
  trigger: "priority_change"
  
  actions:
    - name: "重新评估"
      steps:
        - analyze_new_priority
        - compare_with_existing_tasks
        - determine_order
        
    - name: "调整执行"
      steps:
        - pause_lower_priority
        - start_higher_priority
        - update_task_queue
```

## 状态一致性

### 一致性保证
```yaml
consistency_guarantee:
  checkpoint_before_interrupt:
    enabled: true
    content:
      - current_state
      - intermediate_results
      - context_data
      
  context_isolation:
    between_tasks: true
    prevent_cross_contamination: true
    
  state_validation:
    on_resume:
      - verify_checkpoint_integrity
      - check_context_validity
      - validate_dependencies
```

### 上下文隔离
```yaml
context_isolation:
  principles:
    - 每个任务独立上下文
    - 中断不污染主任务上下文
    - 恢复时完整还原上下文
    
  implementation:
    - separate_memory_scope
    - isolated_variable_space
    - clear_boundary_markers
```

## 中断恢复

### 恢复流程
```yaml
recovery_flow:
  steps:
    - name: "检测恢复条件"
      conditions:
        - interrupting_task_completed
        - user_requests_resume
        - timeout_reached
        
    - name: "验证状态"
      checks:
        - checkpoint_valid
        - context_available
        - dependencies_satisfied
        
    - name: "恢复执行"
      actions:
        - restore_state
        - reload_context
        - continue_execution
        
    - name: "通知用户"
      message: "已恢复原任务执行"
```

### 恢复确认
```yaml
resume_confirmation:
  required_when:
    - checkpoint_older_than: "1h"
    - context_changed_significantly
    - multiple_interrupts_occurred
    
  confirmation_message: |
    原任务「{task_name}」已暂停 {duration}。
    当前进度：{progress}%
    是否继续执行？
    1. 继续执行
    2. 重新开始
    3. 取消任务
```

## 多中断处理

### 中断队列
```yaml
interrupt_queue:
  max_concurrent: 3
  priority_order:
    - user_explicit_request
    - urgent_question
    - general_question
    
  handling:
    - process_in_order
    - prevent_cascade
    - limit_nesting
```

### 中断嵌套
```yaml
nested_interrupt:
  max_depth: 2
  warning_at_depth: 1
  
  actions:
    - warn_user_complexity
    - suggest_serial_processing
    - offer_task_queue_view
```

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 中断频率 | 中断次数/任务 | >5 |
| 恢复成功率 | 成功恢复/总中断 | <90% |
| 平均中断时长 | 中断持续时间 | >10m |
| 上下文丢失率 | 恢复时上下文丢失 | >0 |

## 维护方式
- 新增中断类型: 更新中断类型表
- 调整策略: 更新处理策略
- 优化恢复: 更新恢复流程

## 引用文件
- `state/STATE_MACHINE.md` - 状态机
- `state/RESUME_POLICY.md` - 恢复策略
- `state/CHECKPOINT_POLICY.md` - 检查点策略
