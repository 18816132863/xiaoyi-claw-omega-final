-- 统一表命名迁移脚本 V2.0.0
-- 所有表名使用 snake_case

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. 任务主表
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    goal TEXT NOT NULL,
    payload_json JSONB NOT NULL DEFAULT '{}',
    
    trigger_mode VARCHAR(50) NOT NULL DEFAULT 'immediate',
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    
    schedule_type VARCHAR(50),
    run_at TIMESTAMP WITH TIME ZONE,
    cron_expr VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    next_run_at TIMESTAMP WITH TIME ZONE,
    last_run_at TIMESTAMP WITH TIME ZONE,
    
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    retry_backoff_seconds INTEGER DEFAULT 60,
    
    timeout_seconds INTEGER DEFAULT 600,
    
    idempotency_key VARCHAR(255) UNIQUE,
    
    last_error TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 任务运行表
CREATE TABLE IF NOT EXISTS task_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    run_no INTEGER NOT NULL DEFAULT 1,
    
    workflow_thread_id VARCHAR(255),
    checkpoint_id VARCHAR(255),
    
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    error_text TEXT,
    retry_after TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 任务步骤表
CREATE TABLE IF NOT EXISTS task_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_run_id UUID NOT NULL REFERENCES task_runs(id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    
    tool_name VARCHAR(255),
    input_json JSONB DEFAULT '{}',
    output_json JSONB DEFAULT '{}',
    
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    
    error_text TEXT,
    
    idempotency_key VARCHAR(255) UNIQUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 任务事件表
CREATE TABLE IF NOT EXISTS task_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    task_run_id UUID REFERENCES task_runs(id) ON DELETE SET NULL,
    
    event_type VARCHAR(100) NOT NULL,
    event_payload JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 工具调用表
CREATE TABLE IF NOT EXISTS tool_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    task_run_id UUID REFERENCES task_runs(id) ON DELETE SET NULL,
    step_id UUID REFERENCES task_steps(id) ON DELETE SET NULL,
    
    tool_name VARCHAR(255) NOT NULL,
    request_json JSONB NOT NULL DEFAULT '{}',
    response_json JSONB DEFAULT '{}',
    
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    
    error_text TEXT,
    
    idempotency_key VARCHAR(255) UNIQUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. 工作流检查点表
CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    task_run_id UUID NOT NULL REFERENCES task_runs(id) ON DELETE CASCADE,
    
    thread_id VARCHAR(255) NOT NULL,
    checkpoint_id VARCHAR(255) NOT NULL,
    checkpoint_ns VARCHAR(255) DEFAULT '',
    
    snapshot_json JSONB NOT NULL DEFAULT '{}',
    metadata_json JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE (thread_id, checkpoint_id, checkpoint_ns)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_next_run_at ON tasks(next_run_at);
CREATE INDEX IF NOT EXISTS idx_tasks_idempotency_key ON tasks(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_task_runs_task_id ON task_runs(task_id);
CREATE INDEX IF NOT EXISTS idx_task_runs_status ON task_runs(status);
CREATE INDEX IF NOT EXISTS idx_task_steps_task_run_id ON task_steps(task_run_id);
CREATE INDEX IF NOT EXISTS idx_task_steps_idempotency_key ON task_steps(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_task_events_task_id ON task_events(task_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_task_id ON tool_calls(task_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_idempotency_key ON tool_calls(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_thread_id ON workflow_checkpoints(thread_id);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
