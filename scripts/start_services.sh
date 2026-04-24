#!/bin/bash
# OpenClaw 启动服务脚本 V7.0.0
# 从环境变量读取配置，支持 local/test/prod 三套环境

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 默认配置（可被环境变量覆盖）
MESSAGE_SERVER_PORT="${MESSAGE_SERVER_PORT:-18790}"
DAEMON_CHECK_INTERVAL="${DAEMON_CHECK_INTERVAL:-5.0}"
OPENCLAW_ENV="${OPENCLAW_ENV:-local}"

mkdir -p logs data reports/ops reports/metrics

echo "=============================================="
echo "  OpenClaw 服务启动 V7.0.0"
echo "=============================================="
echo "  项目根目录: $PROJECT_ROOT"
echo "  环境: $OPENCLAW_ENV"
echo "  消息服务端口: $MESSAGE_SERVER_PORT"
echo "  守护进程间隔: $DAEMON_CHECK_INTERVAL 秒"
echo "=============================================="

# 1. 检查依赖
echo ""
echo "[1/4] 检查依赖..."
python3 -c "import croniter; print('  ✅ croniter')" 2>/dev/null || pip install croniter -q
python3 -c "import aiohttp; print('  ✅ aiohttp')" 2>/dev/null || pip install aiohttp -q
python3 -c "import pydantic; print('  ✅ pydantic')" 2>/dev/null || pip install pydantic -q

# 2. 启动消息服务
echo ""
echo "[2/4] 启动消息服务..."
if ! pgrep -f "message_server.py" > /dev/null; then
    nohup python3 scripts/message_server.py --port $MESSAGE_SERVER_PORT > logs/message_server.log 2>&1 &
    MSG_PID=$!

    MSG_OK=0
    for i in $(seq 1 10); do
        if curl -sf http://localhost:$MESSAGE_SERVER_PORT/health > /dev/null 2>&1; then
            MSG_OK=1
            break
        fi
        sleep 1
    done

    if [ "$MSG_OK" -eq 1 ]; then
        echo "  ✅ 消息服务已启动 (PID: $MSG_PID, 端口: $MESSAGE_SERVER_PORT)"
    else
        echo "  ❌ 消息服务启动失败，请查看 logs/message_server.log"
        exit 1
    fi
else
    echo "  ✅ 消息服务已在运行"
fi

# 3. 启动任务守护进程
echo ""
echo "[3/4] 启动任务守护进程..."
if ! pgrep -f "task_daemon.py" > /dev/null; then
    nohup python3 scripts/task_daemon.py --interval $DAEMON_CHECK_INTERVAL > logs/task_daemon.log 2>&1 &
    DAEMON_PID=$!
    sleep 2
    
    if pgrep -f "task_daemon.py" > /dev/null; then
        echo "  ✅ 任务守护进程已启动 (PID: $DAEMON_PID, 间隔: ${DAEMON_CHECK_INTERVAL}s)"
    else
        echo "  ❌ 任务守护进程启动失败，请查看 logs/task_daemon.log"
        exit 1
    fi
else
    echo "  ✅ 任务守护进程已在运行"
fi

# 4. 检查状态
echo ""
echo "[4/4] 检查服务状态..."
curl -s http://localhost:$MESSAGE_SERVER_PORT/health > /dev/null 2>&1 && echo "  ✅ 消息服务: 健康" || echo "  ⚠️ 消息服务: 未响应"
pgrep -f "task_daemon.py" > /dev/null && echo "  ✅ 守护进程: 运行中" || echo "  ❌ 守护进程: 未运行"

echo ""
echo "=============================================="
echo "  启动完成"
echo "=============================================="
echo ""
echo "配置说明:"
echo "  - MESSAGE_SERVER_PORT: 消息服务端口 (默认: 18790)"
echo "  - DAEMON_CHECK_INTERVAL: 守护进程检查间隔 (默认: 5.0)"
echo "  - OPENCLAW_ENV: 运行环境 (默认: local)"
echo ""
echo "示例:"
echo "  MESSAGE_SERVER_PORT=8080 DAEMON_CHECK_INTERVAL=10 bash scripts/start_services.sh"
