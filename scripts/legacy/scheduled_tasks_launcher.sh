#!/bin/bash
# 定时任务启动器 V1.0.0
#
# 功能：
# 1. 在前台持续运行
# 2. 每 15 分钟执行一次心跳
# 3. 适合在没有 crontab 权限的环境使用
#
# 使用方式：
#   nohup bash scripts/scheduled_tasks_launcher.sh > logs/launcher.log 2>&1 &
#   或
#   screen -dmS openclaw-scheduler bash scripts/scheduled_tasks_launcher.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "========================================"
echo "  OpenClaw 定时任务启动器 V1.0.0"
echo "========================================"
echo ""
echo "⏰ 心跳间隔: 15 分钟"
echo "📁 日志目录: $ROOT_DIR/logs"
echo "🛑 停止方式: kill \$$(cat $ROOT_DIR/logs/launcher.pid 2>/dev/null || echo 'PID')"
echo ""
echo "按 Ctrl+C 停止"
echo ""

# 创建日志目录
mkdir -p "$ROOT_DIR/logs"

# 保存 PID
echo $$ > "$ROOT_DIR/logs/launcher.pid"

# 捕获退出信号
trap 'echo ""; echo "🛑 收到停止信号"; rm -f "$ROOT_DIR/logs/launcher.pid"; exit 0' SIGINT SIGTERM

# 循环执行
while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] 🔧 执行心跳..."
    
    # 执行心跳
    cd "$ROOT_DIR"
    python3 scripts/heartbeat_executor.py >> logs/launcher.log 2>&1
    
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$TIMESTAMP] ✅ 心跳完成"
    else
        echo "[$TIMESTAMP] ⚠️  心跳异常 (exit code: $EXIT_CODE)"
    fi
    
    # 等待 15 分钟
    echo "[$TIMESTAMP] 😴 等待 15 分钟..."
    sleep 900
done
