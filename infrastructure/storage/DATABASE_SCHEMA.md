# 任务系统数据库表结构 V1.0.0

## 概述

本文档定义任务系统的核心数据库表结构，支持：
- 任务持久化
- 状态机管理
- 调度管理
- 执行追踪
- 幂等控制
- 检查点恢复

## 表结构

### 1. tasks（任务主表）

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    goal TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}',
    
    -- 触发模式
    trigger_mode VARCHAR(50) NOT NULL DEFAULT 'immediate',
    -- immediate | scheduled | event_driven
    
    -- 状态
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    -- draft | validated | persisted | queued | running | waiting_retry | waiting_human | paused | resumed | succeeded | failed | cancelled
    
    -- 调度配置
    schedule_type VARCHAR(50),
    -- once | delay | cron | recurring | null
    run_at TIMESTAMP WITH TIME ZONE,
    cron_expr VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    next_run_at TIMESTAMP WITH TIME ZONE,
    last_run_at TIMESTAMP WITH TIME ZONE,
    
    -- 重试配置
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    retry_backoff_seconds INTEGER DEFAULT 60,
    
    -- 超时配置
    timeout_seconds INTEGER DEFAULT 600,
    
    -- 幂等控制
    idempotency_key VARCHAR(255) UNIQUE,
    
    -- 错误信息
    last_error TEXT,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 索引
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_next_run_at (next_run_at),
    INDEX idx_tasks_idempotency_key (idempotency_key),
    INDEX idx_tasks_task_type (task_type)
);
```

### 2. task_runs（任务运行表）

```sql
CREATE TABLE task_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id),
    run_no INTEGER NOT NULL DEFAULT 1,
    
    -- 工作流关联
    workflow_thread_id VARCHAR(255),
    checkpoint_id VARCHAR(255),
    
    -- 当前步骤
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    
    -- 状态
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending | running | succeeded | failed | waiting_retry | waiting_human | paused
    
    -- 时间
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    -- 错误
    error_text TEXT,
    
    -- 重试
    retry_after TIMESTAMP WITH TIME ZONE,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 索引
    INDEX idx_task_runs_task_id (task_id),
    INDEX idx_task_runs_status (status),
    INDEX idx_task_runs_workflow_thread_id (workflow_thread_id)
);
```

### 3. task_steps（任务步骤表）

```sql
CREATE TABLE task_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_run_id UUID NOT NULL REFERENCES task_runs(id),
    step_index INTEGER NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    
    -- 工具调用
    tool_name VARCHAR(255),
    input_json JSONB DEFAULT '{}',
    output_json JSONB DEFAULT '{}',
    
    -- 状态
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending | running | succeeded | failed | skipped
    
    -- 时间
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    -- 错误
    error_text TEXT,
    
    -- 幂等控制
    idempotency_key VARCHAR(255) UNIQUE,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 索引
    INDEX idx_task_steps_task_run_id (task_run_id),
    INDEX idx_task_steps_status (status),
    INDEX idx_task_steps_idempotency_key (idempotency_key)
);
```

### 4. task_events（任务事件表）

```sql
CREATE TABLE task_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id),
    task_run_id UUID REFERENCES task_runs(id),
    
    -- 事件类型
    event_type VARCHAR(100) NOT NULL,
    -- created | validated | persisted | queued | started | step_started | step_completed | step_failed | retrying | waiting_human | resumed | paused | cancelled | succeeded | failed
    
    -- 事件详情
    event_payload JSONB DEFAULT '{}',
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 索引
    INDEX idx_task_events_task_id (task_id),
    INDEX idx_task_events_event_type (event_type),
    INDEX idx_task_events_created_at (created_at)
);
```

### 5. tool_calls（工具调用表）

```sql
CREATE TABLE tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id),
    task_run_id UUID REFERENCES task_runs(id),
    step_id UUID REFERENCES task_steps(id),
    
    -- 工具信息
    tool_name VARCHAR(255) NOT NULL,
    request_json JSONB NOT NULL DEFAULT '{}',
    response_json JSONB DEFAULT '{}',
    
    -- 状态
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending | running | succeeded | failed
    
    -- 错误
    error_text TEXT,
    
    -- 幂等控制
    idempotency_key VARCHAR(255) UNIQUE,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 索引
    INDEX idx_tool_calls_task_id (task_id),
    INDEX idx_tool_calls_tool_name (tool_name),
    INDEX idx_tool_calls_status (status),
    INDEX idx_tool_calls_idempotency_key (idempotency_key)
);
```

### 6. workflow_checkpoints（工作流检查点表）

```sql
CREATE TABLE workflow_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id),
    task_run_id UUID NOT NULL REFERENCES task_runs(id),
    
    -- LangGraph 检查点
    thread_id VARCHAR(255) NOT NULL,
    checkpoint_id VARCHAR(255) NOT NULL,
    checkpoint_ns VARCHAR(255) DEFAULT '',
    
    -- 快照
    snapshot_json JSONB NOT NULL DEFAULT '{}',
    
    -- 元数据
    metadata_json JSONB DEFAULT '{}',
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 索引
    INDEX idx_workflow_checkpoints_task_id (task_id),
    INDEX idx_workflow_checkpoints_thread_id (thread_id),
    INDEX idx_workflow_checkpoints_checkpoint_id (checkpoint_id),
    UNIQUE (thread_id, checkpoint_id, checkpoint_ns)
);
```

### 7. scheduled_jobs（调度作业表）

```sql
CREATE TABLE scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id),
    
    -- 调度类型
    schedule_type VARCHAR(50) NOT NULL,
    -- once | delay | cron | recurring
    
    -- 调度配置
    run_at TIMESTAMP WITH TIME ZONE,
    cron_expr VARCHAR(100),
    interval_seconds INTEGER,
    
    -- 状态
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- pending | queued | running | completed | failed | cancelled
    
    -- 执行追踪
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    run_count INTEGER DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 索引
    INDEX idx_scheduled_jobs_task_id (task_id),
    INDEX idx_scheduled_jobs_status (status),
    INDEX idx_scheduled_jobs_next_run_at (next_run_at)
);
```

## 迁移脚本

见 `infrastructure/storage/migrations/001_task_system.sql`

## 使用说明

1. 所有任务必须先入库，再执行
2. 状态流转必须通过事件记录
3. 幂等键必须唯一，重复请求返回历史结果
4. 检查点用于中断恢复
5. 调度作业由 Celery Beat 管理
