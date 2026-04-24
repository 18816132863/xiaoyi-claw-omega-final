#!/bin/bash
# OpenClaw 心跳守护进程管理脚本

WORKSPACE="$WORKSPACE"
PID_FILE="/tmp/openclaw_heartbeat.pid"
LOG_FILE="/tmp/openclaw_heartbeat.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "❌ 守护进程已在运行 (PID: $PID)"
                exit 1
            else
                rm -f "$PID_FILE"
            fi
        fi
        
        echo "🚀 启动心跳守护进程..."
        nohup "$WORKSPACE/infrastructure/heartbeat_daemon.sh" > /tmp/openclaw_daemon.log 2>&1 &
        sleep 2
        
        if [ -f "$PID_FILE" ]; then
            echo "✅ 守护进程已启动 (PID: $(cat $PID_FILE))"
        else
            echo "❌ 启动失败"
            exit 1
        fi
        ;;
    
    stop)
        if [ ! -f "$PID_FILE" ]; then
            echo "❌ 守护进程未运行"
            exit 1
        fi
        
        PID=$(cat "$PID_FILE")
        echo "🛑 停止守护进程 (PID: $PID)..."
        kill "$PID" 2>/dev/null
        sleep 2
        
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID" 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        echo "✅ 守护进程已停止"
        ;;
    
    status)
        if [ ! -f "$PID_FILE" ]; then
            echo "⏹️  守护进程未运行"
            exit 0
        fi
        
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ 守护进程运行中 (PID: $PID)"
            echo ""
            echo "📊 最近日志:"
            tail -10 "$LOG_FILE" 2>/dev/null || echo "无日志"
        else
            echo "❌ 守护进程已崩溃 (PID 文件存在但进程不存在)"
            rm -f "$PID_FILE"
        fi
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    logs)
        echo "📋 心跳日志 (最近 50 行):"
        echo "================================"
        tail -50 "$LOG_FILE" 2>/dev/null || echo "无日志"
        ;;
    
    *)
        echo "用法: $0 {start|stop|status|restart|logs}"
        echo ""
        echo "命令:"
        echo "  start   - 启动守护进程"
        echo "  stop    - 停止守护进程"
        echo "  status  - 查看状态"
        echo "  restart - 重启守护进程"
        echo "  logs    - 查看日志"
        exit 1
        ;;
esac
