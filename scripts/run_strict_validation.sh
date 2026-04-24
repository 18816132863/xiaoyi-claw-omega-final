#!/bin/bash
# 严格验收脚本 V3.0.0

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "  严格验收测试 V3.0.0"
echo "============================================================"
echo ""

# 0. 检查并安装测试依赖
echo "[0/10] 检查测试依赖..."

REQUIRED_PACKAGES=("croniter" "aiohttp" "pytest" "pytest-asyncio" "pydantic")

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "  ✅ $pkg 已安装"
    else
        echo "  📦 安装 $pkg ..."
        pip install $pkg -q
        echo "  ✅ $pkg 安装完成"
    fi
done

echo ""

# 1. 创建必要目录
echo "[1/10] 创建必要目录..."
mkdir -p logs data reports/ops reports/metrics
echo "  ✅ 目录已创建"

# 2. 清理环境
echo ""
echo "[2/10] 清理环境..."
rm -f data/tasks.db data/task_queue.jsonl
rm -f reports/ops/pending_sends.jsonl reports/ops/delivered_messages.jsonl
rm -f data/message_server.pid data/task_daemon.pid
pkill -f message_server.py 2>/dev/null || true
pkill -f task_daemon.py 2>/dev/null || true
sleep 2
echo "  ✅ 环境已清理"

# 3. 运行单元测试
echo ""
echo "[3/10] 运行单元测试..."
python3 -m pytest tests/ -q --tb=short 2>&1 | tail -5
TEST_RESULT=${PIPESTATUS[0]}
if [ $TEST_RESULT -ne 0 ]; then
    echo "  ❌ 单元测试失败"
    exit 1
fi
echo "  ✅ 单元测试通过"

# 4. 启动消息服务
echo ""
echo "[4/10] 启动消息服务..."
nohup python3 scripts/message_server.py --port 18790 > logs/message_server.log 2>&1 &
MSG_PID=$!
echo "  PID: $MSG_PID"

# 等待并检查健康
MSG_OK=0
for i in $(seq 1 10); do
    if curl -sf http://localhost:18790/health > /dev/null 2>&1; then
        MSG_OK=1
        break
    fi
    sleep 1
done

if [ "$MSG_OK" -eq 1 ]; then
    echo "  ✅ 消息服务健康"
else
    echo "  ❌ 消息服务启动失败"
    cat logs/message_server.log
    exit 1
fi

# 5. 启动任务守护进程
echo ""
echo "[5/10] 启动任务守护进程..."
nohup python3 scripts/task_daemon.py --interval 2 > logs/task_daemon.log 2>&1 &
DAEMON_PID=$!
echo "  PID: $DAEMON_PID"

# 等待并检查
sleep 3
if pgrep -f "task_daemon.py" > /dev/null; then
    echo "  ✅ 守护进程运行中"
else
    echo "  ❌ 守护进程启动失败"
    cat logs/task_daemon.log
    exit 1
fi

# 6. 测试 once 任务完整流程
echo ""
echo "[6/10] 测试 once 任务完整流程..."
python3 << 'PYEOF'
import asyncio
import sys
import time
sys.path.insert(0, '.')

from infrastructure.task_manager import get_task_manager
from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
from domain.tasks import TaskStatus
from datetime import datetime, timedelta

async def test_once_full():
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 创建任务（过去时间，立即执行）
    run_at = (datetime.now() - timedelta(seconds=10)).isoformat()
    result = await tm.create_scheduled_message(
        user_id="strict_validation",
        message="once-full-test",
        run_at=run_at
    )
    
    if not result.get("success"):
        print(f"  ❌ 创建失败: {result.get('error')}")
        return False
    
    task_id = result["task_id"]
    print(f"  任务ID: {task_id[:16]}...")
    
    # 等待执行
    for i in range(30):
        task = await repo.get(task_id)
        if task.status in (TaskStatus.SUCCEEDED, TaskStatus.DELIVERY_PENDING):
            print(f"  ✅ 任务状态: {task.status.value}")
            return True
        time.sleep(1)
    
    print(f"  ❌ 任务超时，当前状态: {task.status.value}")
    return False

success = asyncio.run(test_once_full())
sys.exit(0 if success else 1)
PYEOF

if [ $? -ne 0 ]; then
    echo "  ❌ once 任务测试失败"
    exit 1
fi

# 7. 测试 recurring 任务
echo ""
echo "[7/10] 测试 recurring 任务..."
python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '.')

from infrastructure.task_manager import get_task_manager
from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
from domain.tasks import TaskStatus

async def test_recurring():
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    result = await tm.create_recurring_message(
        user_id="strict_validation",
        message="recurring-test",
        cron_expr="*/1 * * * *"
    )
    
    if not result.get("success"):
        print(f"  ❌ 创建失败: {result.get('error')}")
        return False
    
    task_id = result["task_id"]
    print(f"  任务ID: {task_id[:16]}...")
    
    task = await repo.get(task_id)
    if task.status == TaskStatus.PERSISTED and task.schedule:
        print(f"  ✅ recurring 任务创建成功")
        print(f"  下次运行: {task.schedule.next_run_at}")
        return True
    
    return False

success = asyncio.run(test_recurring())
sys.exit(0 if success else 1)
PYEOF

if [ $? -ne 0 ]; then
    echo "  ❌ recurring 任务测试失败"
    exit 1
fi

# 8. 健康检查接口
echo ""
echo "[8/10] 健康检查接口..."
echo "  /health:"
curl -s http://localhost:18790/health | python3 -m json.tool 2>/dev/null | head -5

echo ""
echo "  /ready:"
curl -s http://localhost:18790/ready | python3 -m json.tool 2>/dev/null | head -5

echo ""
echo "  /metrics:"
curl -s http://localhost:18790/metrics | python3 -m json.tool 2>/dev/null | head -10

# 9. 检查日志和指标
echo ""
echo "[9/10] 检查日志和指标..."
if [ -f "logs/task_daemon_daemon.jsonl" ]; then
    echo "  ✅ 守护进程日志存在"
    wc -l logs/task_daemon_daemon.jsonl
else
    echo "  ⚠️ 守护进程日志不存在"
fi

if [ -f "reports/metrics/metrics.json" ]; then
    echo "  ✅ 指标文件存在"
else
    echo "  ⚠️ 指标文件不存在"
fi

# 10. 清理
echo ""
echo "[10/10] 清理服务..."
pkill -f message_server.py 2>/dev/null || true
pkill -f task_daemon.py 2>/dev/null || true
echo "  ✅ 服务已停止"

echo ""
echo "============================================================"
echo "  验收完成"
echo "============================================================"
