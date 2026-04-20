#!/bin/bash
# OpenClaw 服务启动脚本 V1.0.0
# 启动消息服务和任务守护进程

set -e

cd /home/sandbox/.openclaw/workspace

# 创建日志目录
mkdir -p logs data

# 启动消息服务
echo "启动消息服务..."
if ! pgrep -f "message_server.py" > /dev/null; then
    nohup /usr/local/bin/python3 scripts/message_server.py --port 18790 > logs/message_server.log 2>&1 &
    echo "  消息服务已启动 (PID: $!)"
else
    echo "  消息服务已在运行"
fi

# 启动任务守护进程
echo "启动任务守护进程..."
if ! pgrep -f "task_daemon.py" > /dev/null; then
    nohup /usr/local/bin/python3 scripts/task_daemon.py --interval 5 > logs/task_daemon.log 2>&1 &
    echo "  任务守护进程已启动 (PID: $!)"
else
    echo "  任务守护进程已在运行"
fi

# 等待服务启动
sleep 2

# 检查服务状态
echo ""
echo "服务状态:"
echo "=========="

if curl -s http://localhost:18790/health > /dev/null 2>&1; then
    echo "✅ 消息服务: 运行中"
else
    echo "❌ 消息服务: 未运行"
fi

if pgrep -f "task_daemon.py" > /dev/null; then
    echo "✅ 任务守护进程: 运行中"
else
    echo "❌ 任务守护进程: 未运行"
fi

echo ""
echo "完成！"
