#!/bin/bash
# OpenClaw 完整启动脚本 V3.0.0

set -e

cd /home/sandbox/.openclaw/workspace

echo "=============================================="
echo "  OpenClaw 任务系统启动"
echo "=============================================="

# 1. 检查依赖
echo ""
echo "[1/6] 检查依赖..."
python3 -c "import langgraph; print('  ✅ LangGraph')" 2>/dev/null || echo "  ❌ LangGraph 未安装"
python3 -c "import asyncpg; print('  ✅ asyncpg')" 2>/dev/null || echo "  ❌ asyncpg 未安装"
python3 -c "import redis; print('  ✅ redis')" 2>/dev/null || echo "  ❌ redis 未安装"
python3 -c "import celery; print('  ✅ celery')" 2>/dev/null || echo "  ❌ celery 未安装"

# 2. 启动 Docker 服务（如果可用）
echo ""
echo "[2/6] 启动 Docker 服务..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d 2>/dev/null || echo "  ⚠️ Docker 不可用，使用本地模式"
else
    echo "  ⚠️ Docker 不可用，使用本地模式"
fi

# 3. 初始化数据库
echo ""
echo "[3/6] 初始化数据库..."
mkdir -p data
python3 -c "
import sqlite3
conn = sqlite3.connect('data/tasks.db')
cursor = conn.cursor()

# 创建表
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    task_type TEXT NOT NULL,
    goal TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    trigger_mode TEXT NOT NULL DEFAULT 'immediate',
    status TEXT NOT NULL DEFAULT 'draft',
    schedule_type TEXT,
    run_at TEXT,
    cron_expr TEXT,
    timezone TEXT DEFAULT 'Asia/Shanghai',
    next_run_at TEXT,
    last_run_at TEXT,
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    retry_backoff_seconds INTEGER DEFAULT 60,
    timeout_seconds INTEGER DEFAULT 600,
    idempotency_key TEXT UNIQUE,
    last_error TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS task_runs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    run_no INTEGER NOT NULL DEFAULT 1,
    workflow_thread_id TEXT,
    checkpoint_id TEXT,
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT,
    ended_at TEXT,
    error_text TEXT,
    retry_after TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS task_steps (
    id TEXT PRIMARY KEY,
    task_run_id TEXT NOT NULL,
    step_index INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    tool_name TEXT,
    input_json TEXT DEFAULT '{}',
    output_json TEXT DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT,
    ended_at TEXT,
    error_text TEXT,
    idempotency_key TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS task_events (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    task_run_id TEXT,
    event_type TEXT NOT NULL,
    event_payload TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS tool_calls (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    task_run_id TEXT,
    step_id TEXT,
    tool_name TEXT NOT NULL,
    request_json TEXT NOT NULL DEFAULT '{}',
    response_json TEXT DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    error_text TEXT,
    idempotency_key TEXT UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    task_run_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    checkpoint_ns TEXT DEFAULT '',
    snapshot_json TEXT NOT NULL DEFAULT '{}',
    metadata_json TEXT DEFAULT '{}',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (thread_id, checkpoint_id, checkpoint_ns)
)
''')

conn.commit()
conn.close()
print('  ✅ 数据库初始化完成')
"

# 4. 启动消息服务
echo ""
echo "[4/6] 启动消息服务..."
if ! pgrep -f "message_server.py" > /dev/null; then
    nohup python3 scripts/message_server.py --port 18790 > logs/message_server.log 2>&1 &
    sleep 2
    echo "  ✅ 消息服务已启动 (PID: $!)"
else
    echo "  ✅ 消息服务已在运行"
fi

# 5. 启动任务守护进程
echo ""
echo "[5/6] 启动任务守护进程..."
if ! pgrep -f "task_daemon_v2.py" > /dev/null; then
    nohup python3 scripts/task_daemon_v2.py --interval 5 > logs/task_daemon.log 2>&1 &
    sleep 2
    echo "  ✅ 任务守护进程已启动 (PID: $!)"
else
    echo "  ✅ 任务守护进程已在运行"
fi

# 6. 检查服务状态
echo ""
echo "[6/6] 检查服务状态..."
echo ""

# 消息服务
if curl -s http://localhost:18790/health > /dev/null 2>&1; then
    echo "  ✅ 消息服务: 运行中 (端口 18790)"
else
    echo "  ❌ 消息服务: 未运行"
fi

# 任务守护进程
if pgrep -f "task_daemon_v2.py" > /dev/null; then
    PID=$(pgrep -f "task_daemon_v2.py")
    echo "  ✅ 任务守护进程: 运行中 (PID: $PID)"
else
    echo "  ❌ 任务守护进程: 未运行"
fi

# 数据库
if [ -f "data/tasks.db" ]; then
    TASK_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('data/tasks.db'); print(conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0])")
    echo "  ✅ 数据库: 已初始化 ($TASK_COUNT 个任务)"
else
    echo "  ❌ 数据库: 未初始化"
fi

echo ""
echo "=============================================="
echo "  启动完成！"
echo "=============================================="
echo ""
echo "管理命令:"
echo "  查看状态: ./scripts/status_services.sh"
echo "  停止服务: ./scripts/stop_services.sh"
echo "  创建任务: python scripts/quick_task.py '消息' '时间'"
echo ""
