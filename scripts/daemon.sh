#!/bin/bash
# OpenClaw 守护进程启动脚本 V7.2.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "========================================"
echo "  OpenClaw 守护进程管理器 V7.2.0"
echo "========================================"
echo ""

case "$1" in
    start)
        echo "启动守护进程..."
        cd "$ROOT_DIR"
        python3 infrastructure/daemon_manager.py start &
        echo $! > infrastructure/daemon_manager.pid
        echo "✅ 守护进程已启动 (PID: $(cat infrastructure/daemon_manager.pid))"
        ;;
    
    stop)
        echo "停止守护进程..."
        if [ -f infrastructure/daemon_manager.pid ]; then
            PID=$(cat infrastructure/daemon_manager.pid)
            kill $PID 2>/dev/null
            rm infrastructure/daemon_manager.pid
            echo "✅ 守护进程已停止"
        else
            echo "⚠️  守护进程未运行"
        fi
        ;;
    
    status)
        python3 infrastructure/daemon_manager.py status
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    install-systemd)
        echo "安装 systemd 服务..."
        sudo cp infrastructure/openclaw-daemon.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable openclaw-daemon
        echo "✅ systemd 服务已安装"
        echo "   启动: sudo systemctl start openclaw-daemon"
        echo "   状态: sudo systemctl status openclaw-daemon"
        ;;
    
    *)
        echo "用法: $0 {start|stop|status|restart|install-systemd}"
        echo ""
        echo "命令说明:"
        echo "  start           - 启动守护进程"
        echo "  stop            - 停止守护进程"
        echo "  status          - 查看状态"
        echo "  restart         - 重启守护进程"
        echo "  install-systemd - 安装为 systemd 服务（开机自启）"
        exit 1
        ;;
esac
