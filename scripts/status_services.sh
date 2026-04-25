#!/bin/bash
# OpenClaw 服务状态脚本 V4.0.0

# 自动解析项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=============================================="
echo "  OpenClaw 服务状态"
echo "=============================================="

# 消息服务
if pgrep -f "message_server.py" > /dev/null; then
    PID=$(pgrep -f "message_server.py")
    if curl -s http://localhost:18790/health > /dev/null 2>&1; then
        echo "✅ 消息服务: 运行中 (PID: $PID, 端口 18790)"
    else
        echo "⚠️ 消息服务: 进程存在但未响应 (PID: $PID)"
    fi
else
    echo "❌ 消息服务: 未运行"
fi

# 任务守护进程
if pgrep -f "task_daemon.py" > /dev/null; then
    PID=$(pgrep -f "task_daemon.py")
    echo "✅ 任务守护进程: 运行中 (PID: $PID)"
else
    echo "❌ 任务守护进程: 未运行"
fi

# 数据库
if [ -f "data/tasks.db" ]; then
    TASK_COUNT=$(python3 -c "import sqlite3; conn = sqlite3.connect('data/tasks.db'); print(conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0])" 2>/dev/null || echo "?")
    PENDING=$(python3 -c "import sqlite3; conn = sqlite3.connect('data/tasks.db'); print(conn.execute(\"SELECT COUNT(*) FROM tasks WHERE status='persisted'\").fetchone()[0])" 2>/dev/null || echo "?")
    echo "✅ 数据库: $TASK_COUNT 个任务 ($PENDING 待执行)"
else
    echo "❌ 数据库: 不存在"
fi

# 待发送消息
if [ -f "reports/ops/pending_sends.jsonl" ]; then
    PENDING_SENDS=$(wc -l < reports/ops/pending_sends.jsonl 2>/dev/null || echo "0")
    echo "📧 待发送消息: $PENDING_SENDS 条"
fi

echo ""
echo "=============================================="
