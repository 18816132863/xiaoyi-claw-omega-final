#!/bin/bash
# 后台启动定时任务 V1.0.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "========================================"
echo "  启动 OpenClaw 定时任务"
echo "========================================"
echo ""

# 检查是否已经在运行
if [ -f "$ROOT_DIR/logs/launcher.pid" ]; then
    PID=$(cat "$ROOT_DIR/logs/launcher.pid")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  定时任务已在运行 (PID: $PID)"
        echo ""
        echo "停止方式: kill $PID"
        exit 0
    else
        echo "🧹 清理旧的 PID 文件"
        rm -f "$ROOT_DIR/logs/launcher.pid"
    fi
fi

# 创建日志目录
mkdir -p "$ROOT_DIR/logs"

# 后台启动
echo "🚀 启动定时任务..."
nohup python3 "$ROOT_DIR/scripts/scheduled_tasks_launcher.py" > "$ROOT_DIR/logs/launcher.log" 2>&1 &
PID=$!

# 等待启动
sleep 2

# 检查是否成功
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 定时任务已启动 (PID: $PID)"
    echo ""
    echo "📋 查看日志: tail -f $ROOT_DIR/logs/launcher.log"
    echo "🛑 停止方式: kill $PID"
    echo ""
else
    echo "❌ 启动失败"
    echo "查看日志: cat $ROOT_DIR/logs/launcher.log"
    exit 1
fi
