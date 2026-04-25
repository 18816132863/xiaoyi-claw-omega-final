#!/bin/bash
# 启动定时任务守护进程 V2.0.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "========================================"
echo "  启动定时任务守护进程 V2.0.0"
echo "========================================"
echo ""

cd "$ROOT_DIR"
python3 scripts/scheduled_tasks_daemon.py start

echo ""
echo "📋 查看状态: python3 scripts/scheduled_tasks_daemon.py status"
echo "📋 查看日志: tail -f logs/daemon.log"
echo "🛑 停止方式: python3 scripts/scheduled_tasks_daemon.py stop"
echo ""
