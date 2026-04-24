#!/bin/bash
# OpenClaw 停止服务脚本 V4.0.0

# 自动解析项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=============================================="
echo "  OpenClaw 停止服务"
echo "=============================================="

# 停止任务守护进程
pkill -f "task_daemon.py" 2>/dev/null && echo "✅ 任务守护进程已停止" || echo "⚠️ 任务守护进程未运行"

# 停止消息服务
pkill -f "message_server.py" 2>/dev/null && echo "✅ 消息服务已停止" || echo "⚠️ 消息服务未运行"

# 清理 PID 文件
rm -f "$PROJECT_ROOT/data/message_server.pid" 2>/dev/null
rm -f "$PROJECT_ROOT/data/task_daemon.pid" 2>/dev/null

echo ""
echo "=============================================="
echo "  所有服务已停止"
echo "=============================================="
