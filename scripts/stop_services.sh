#!/bin/bash
# OpenClaw 服务停止脚本 V1.0.0

echo "停止 OpenClaw 服务..."

# 停止消息服务
pkill -f "message_server.py" 2>/dev/null && echo "✅ 消息服务已停止" || echo "⚠️ 消息服务未运行"

# 停止任务守护进程
pkill -f "task_daemon.py" 2>/dev/null && echo "✅ 任务守护进程已停止" || echo "⚠️ 任务守护进程未运行"

# 清理 PID 文件
rm -f /home/sandbox/.openclaw/workspace/data/message_server.pid
rm -f /home/sandbox/.openclaw/workspace/data/task_daemon.pid

echo "完成！"
