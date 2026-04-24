#!/bin/bash
# 停止定时任务 V1.0.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "========================================"
echo "  停止 OpenClaw 定时任务"
echo "========================================"
echo ""

# 检查是否在运行
if [ ! -f "$ROOT_DIR/logs/launcher.pid" ]; then
    echo "⚠️  定时任务未运行"
    exit 0
fi

PID=$(cat "$ROOT_DIR/logs/launcher.pid")

# 检查进程是否存在
if ! ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  进程不存在 (PID: $PID)"
    rm -f "$ROOT_DIR/logs/launcher.pid"
    exit 0
fi

# 停止进程
echo "🛑 停止定时任务 (PID: $PID)..."
kill $PID

# 等待停止
sleep 2

# 检查是否成功
if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  进程未响应，强制停止..."
    kill -9 $PID
    sleep 1
fi

# 清理
rm -f "$ROOT_DIR/logs/launcher.pid"

echo "✅ 定时任务已停止"
echo ""
