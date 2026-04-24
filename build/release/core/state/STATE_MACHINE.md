# STATE_MACHINE.md - 系统级任务状态机

## 目的
定义系统级任务状态机，精确表达任务执行状态。

## 适用范围
所有任务的执行状态管理。

## 状态定义

```
idle → triaged → planned → executing → waiting_input → waiting_external → validating → completed → failed → aborted
```

## 状态说明

### 1. idle（空闲）
| 属性 | 说明 |
|------|------|
| 含义 | 任务尚未开始 |
| 触发 | 任务创建 |
| 允许操作 | 排队、取消 |
| 资源占用 | 无 |

### 2. triaged（已分流）
| 属性 | 说明 |
|------|------|
| 含义 | 任务已分类、优先级已确定 |
| 触发 | 任务分析完成 |
| 允许操作 | 规划、升级、降级 |
| 资源占用 | 分析资源 |

### 3. planned（已规划）
| 属性 | 说明 |
|------|------|
| 含义 | 执行计划已制定 |
| 触发 | 规划完成 |
| 允许操作 | 执行、调整计划 |
| 资源占用 | 规划资源 |

### 4. executing（执行中）
| 属性 | 说明 |
|------|------|
| 含义 | 正在执行任务 |
| 触发 | 开始执行 |
| 允许操作 | 暂停、中断、继续 |
| 资源占用 | 执行资源 |

### 5. waiting_input（等待输入）
| 属性 | 说明 |
|------|------|
| 含义 | 等待用户提供信息 |
| 触发 | 缺少必要输入 |
| 允许操作 | 接收输入、超时处理 |
| 资源占用 | 最小 |

### 6. waiting_external（等待外部）
| 属性 | 说明 |
|------|------|
| 含义 | 等待外部系统/条件 |
| 触发 | 依赖外部资源 |
| 允许操作 | 重试、超时处理、降级 |
| 资源占用 | 最小 |

### 7. validating（验证中）
| 属性 | 说明 |
|------|------|
| 含义 | 正在验证执行结果 |
| 触发 | 执行完成 |
| 允许操作 | 通过、失败、重试 |
| 资源占用 | 验证资源 |

### 8. completed（已完成）
| 属性 | 说明 |
|------|------|
| 含义 | 任务成功完成 |
| 触发 | 验证通过 |
| 允许操作 | 归档、复盘 |
| 资源占用 | 无（释放） |

### 9. failed（已失败）
| 属性 | 说明 |
|------|------|
| 含义 | 任务执行失败 |
| 触发 | 执行错误或验证失败 |
| 允许操作 | 重试、放弃、升级 |
| 资源占用 | 无（释放） |

### 10. aborted（已中止）
| 属性 | 说明 |
|------|------|
| 含义 | 任务被主动中止 |
| 触发 | 用户取消或系统终止 |
| 允许操作 | 记录原因、清理资源 |
| 资源占用 | 无（释放） |

## 状态转换图

```
                    ┌─────────────────────────────────────────┐
                    │                                         │
                    ▼                                         │
┌──────┐  分析  ┌─────────┐  规划  ┌─────────┐  执行  ┌───────────┐
│ idle │───────▶│ triaged │───────▶│ planned │───────▶│ executing │
└──────┘        └─────────┘        └─────────┘        └───────────┘
    │               │                   │                   │
    │ 取消          │ 升级/降级         │ 调整              │ 缺输入
    │               │                   │                   │
    ▼               ▼                   ▼                   ▼
┌─────────┐    ┌─────────┐        ┌─────────┐        ┌──────────────┐
│ aborted │    │(重新分流)│        │(重新规划)│        │waiting_input │
└─────────┘    └─────────┘        └─────────┘        └──────────────┘
                                                              │
                                                              │ 收到输入
                                                              ▼
                                                         ┌───────────┐
                                                         │ executing │
                                                         └───────────┘
                                                              │
                                                              │ 依赖外部
                                                              ▼
                                                        ┌───────────────┐
                                                        │waiting_external│
                                                        └───────────────┘
                                                              │
                                                              │ 完成
                                                              ▼
┌───────────┐  失败  ┌───────────┐  通过  ┌──────────┐
│  failed   │◀──────│ validating │───────▶│ completed │
└───────────┘       └───────────┘        └──────────┘
     │                                          ▲
     │ 重试                                     │
     └──────────────────────────────────────────┘
```

## 转换规则

### 转换条件
```yaml
transitions:
  idle_to_triaged:
    trigger: task_analyzed
    conditions:
      - task_type_identified
      - priority_assigned
    actions:
      - log_transition
      - notify_queue
      
  triaged_to_planned:
    trigger: planning_complete
    conditions:
      - execution_plan_created
      - resources_available
    actions:
      - create_checkpoint
      - allocate_resources
      
  planned_to_executing:
    trigger: execution_start
    conditions:
      - plan_approved
      - prerequisites_met
    actions:
      - start_execution
      - update_metrics
      
  executing_to_waiting_input:
    trigger: input_required
    conditions:
      - missing_input_identified
    actions:
      - save_state
      - request_input
      - start_timer
      
  waiting_input_to_executing:
    trigger: input_received
    conditions:
      - input_valid
    actions:
      - restore_state
      - continue_execution
      
  executing_to_waiting_external:
    trigger: external_dependency
    conditions:
      - external_call_made
    actions:
      - save_state
      - start_timeout_timer
      
  waiting_external_to_executing:
    trigger: external_complete
    conditions:
      - response_received
    actions:
      - restore_state
      - continue_execution
      
  executing_to_validating:
    trigger: execution_complete
    conditions:
      - output_generated
    actions:
      - start_validation
      - log_results
      
  validating_to_completed:
    trigger: validation_passed
    conditions:
      - quality_check_passed
      - output_valid
    actions:
      - finalize_output
      - release_resources
      - archive_task
      
  validating_to_failed:
    trigger: validation_failed
    conditions:
      - quality_check_failed
    actions:
      - record_failure
      - determine_retry
      
  failed_to_executing:
    trigger: retry_approved
    conditions:
      - retry_count < max
      - retry_possible
    actions:
      - reset_state
      - restart_execution
```

## 禁止转换

| 从状态 | 禁止转换到 | 原因 |
|--------|------------|------|
| completed | idle/triaged/planned | 已完成任务不可回退 |
| aborted | 任何状态 | 已中止任务不可恢复 |
| failed | completed | 失败任务不可直接完成 |

## 异常回退路径

### 执行异常
```yaml
execution_error:
  recoverable:
    - path: executing → failed → executing (重试)
    - path: executing → waiting_external (等待恢复)
  non_recoverable:
    - path: executing → failed → aborted (放弃)
```

### 超时处理
```yaml
timeout_handling:
  waiting_input:
    timeout: 30m
    action: escalate_to_user
    fallback: abort_if_critical
  waiting_external:
    timeout: 5m
    action: retry_or_fallback
    fallback: use_cached_or_fail
```

## 子状态支持

### 子状态定义
```yaml
substates:
  executing:
    - initializing
    - processing
    - finalizing
  validating:
    - checking_format
    - checking_quality
    - checking_constraints
```

## 状态监控

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 状态停留时间 | 在某状态时长 | 超预期 |
| 转换次数 | 状态转换频率 | 异常波动 |
| 失败率 | failed/total | >5% |
| 中止率 | aborted/total | >2% |

## 维护方式
- 新增状态: 更新状态定义和转换图
- 调整规则: 更新转换条件
- 新增子状态: 更新子状态定义

## 引用文件
- `state/TASK_STATE_SCHEMA.json` - 任务状态结构
- `state/BLOCKER_POLICY.md` - 阻塞策略
- `state/RESUME_POLICY.md` - 恢复策略
