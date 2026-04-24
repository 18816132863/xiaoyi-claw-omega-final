#!/bin/bash
# OpenClaw 心跳守护脚本
# 每 15 分钟自动执行心跳任务

WORKSPACE="$WORKSPACE"
LOG_FILE="/tmp/openclaw_heartbeat.log"
PID_FILE="/tmp/openclaw_heartbeat.pid"
INTERVAL=900  # 15 分钟 = 900 秒

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "守护进程已在运行 (PID: $PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# 写入 PID
echo $$ > "$PID_FILE"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 清理函数
cleanup() {
    log "守护进程停止"
    rm -f "$PID_FILE"
    exit 0
}

# 信号处理
trap cleanup SIGTERM SIGINT

# 主循环
log "守护进程启动 (间隔: ${INTERVAL}秒)"

while true; do
    log "执行心跳任务..."
    cd "$WORKSPACE"
    /usr/bin/python3 scripts/heartbeat_executor.py >> "$LOG_FILE" 2>&1
    
    log "等待 ${INTERVAL} 秒..."
    sleep "$INTERVAL"
done
