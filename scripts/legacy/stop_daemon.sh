#!/bin/bash
# 停止定时任务守护进程 V2.0.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "========================================"
echo "  停止定时任务守护进程 V2.0.0"
echo "========================================"
echo ""

cd "$ROOT_DIR"
python3 scripts/scheduled_tasks_daemon.py stop

echo ""
