-- 平台调用审计台账
-- 记录所有平台调用的详细信息

CREATE TABLE IF NOT EXISTS platform_invocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    task_run_id TEXT,
    task_step_id TEXT,
    capability TEXT NOT NULL,
    platform_op TEXT NOT NULL,
    idempotency_key TEXT UNIQUE,
    side_effecting INTEGER DEFAULT 0,
    request_json TEXT,
    raw_result_json TEXT,
    normalized_status TEXT NOT NULL,
    error_code TEXT,
    user_message TEXT,
    result_uncertain INTEGER DEFAULT 0,
    fallback_used INTEGER DEFAULT 0,
    elapsed_ms INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    -- 人工确认字段
    confirmed_status TEXT,
    confirm_note TEXT,
    confirmed_at TEXT
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_platform_invocations_task_id ON platform_invocations(task_id);
CREATE INDEX IF NOT EXISTS idx_platform_invocations_capability ON platform_invocations(capability);
CREATE INDEX IF NOT EXISTS idx_platform_invocations_status ON platform_invocations(normalized_status);
CREATE INDEX IF NOT EXISTS idx_platform_invocations_idempotency ON platform_invocations(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_platform_invocations_created_at ON platform_invocations(created_at);
CREATE INDEX IF NOT EXISTS idx_platform_invocations_confirmed ON platform_invocations(confirmed_status);
