#!/bin/bash
# OpenClaw 服务状态检查 V1.0.0

echo "OpenClaw 服务状态"
echo "=================="

# 消息服务
if curl -s http://localhost:18790/health > /dev/null 2>&1; then
    echo "✅ 消息服务: 运行中 (端口 18790)"
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

# 定时消息统计
echo ""
echo "定时任务统计"
echo "------------"
python3 -c "
import sqlite3
conn = sqlite3.connect('data/tasks.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM tasks')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = \"succeeded\"')
succeeded = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = \"failed\"')
failed = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM tasks WHERE status IN (\"persisted\", \"queued\")')
pending = cursor.fetchone()[0]

print(f'总任务: {total}')
print(f'成功: {succeeded}')
print(f'失败: {failed}')
print(f'待执行: {pending}')

conn.close()
" 2>/dev/null || echo "数据库未初始化"

# 待发送消息
echo ""
echo "待发送消息"
echo "----------"
if [ -f "reports/ops/pending_sends.jsonl" ]; then
    COUNT=$(wc -l < reports/ops/pending_sends.jsonl)
    echo "待发送: $COUNT 条"
else
    echo "待发送: 0 条"
fi
