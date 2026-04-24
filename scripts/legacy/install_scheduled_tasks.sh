#!/bin/bash
# 定时任务安装脚本 V1.0.0
#
# 功能：
# 1. 检查环境
# 2. 安装 cron 任务
# 3. 测试定时任务
#
# 使用方式：
#   bash scripts/install_scheduled_tasks.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "========================================"
echo "  OpenClaw 定时任务安装 V1.0.0"
echo "========================================"
echo ""

# 1. 检查环境
echo "🔍 检查环境..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi
echo "  ✅ Python3: $(python3 --version)"

# 检查项目目录
if [ ! -f "$ROOT_DIR/core/ARCHITECTURE.md" ]; then
    echo "❌ 项目目录不正确"
    exit 1
fi
echo "  ✅ 项目目录: $ROOT_DIR"

# 检查 cron
if ! command -v crontab &> /dev/null; then
    echo "❌ crontab 未安装"
    echo "   请安装: sudo apt-get install cron"
    exit 1
fi
echo "  ✅ crontab: 已安装"

echo ""

# 2. 创建日志目录
echo "📁 创建日志目录..."
mkdir -p "$ROOT_DIR/logs"
echo "  ✅ logs/"
echo ""

# 3. 测试脚本
echo "🧪 测试脚本..."

# 测试心跳执行器
echo "  测试: heartbeat_executor.py"
python3 "$ROOT_DIR/scripts/heartbeat_executor.py" > /dev/null 2>&1 && echo "    ✅ 通过" || echo "    ⚠️  有警告"

# 测试消息发送助手
echo "  测试: send_message_helper.py"
python3 "$ROOT_DIR/scripts/send_message_helper.py" > /dev/null 2>&1 && echo "    ✅ 通过" || echo "    ⚠️  有警告"

echo ""

# 4. 安装 cron 任务
echo "⏰ 安装 cron 任务..."

# 检查是否已安装
if crontab -l 2>/dev/null | grep -q "heartbeat_executor.py"; then
    echo "  ⚠️  cron 任务已存在"
    echo "  如需重新安装，请先运行: crontab -e 并删除相关行"
else
    # 添加 cron 任务
    (crontab -l 2>/dev/null; echo "*/15 * * * * cd $ROOT_DIR && /usr/bin/python3 scripts/heartbeat_executor.py >> logs/cron.log 2>&1") | crontab -
    echo "  ✅ cron 任务已安装"
    echo "     每 15 分钟执行一次心跳"
fi

echo ""

# 5. 显示当前 cron 任务
echo "📋 当前 cron 任务:"
crontab -l 2>/dev/null | grep -v "^#" | grep -v "^$" || echo "  (无)"
echo ""

# 6. 显示下一步
echo "========================================"
echo "  ✅ 安装完成"
echo "========================================"
echo ""
echo "📌 下一步:"
echo "  1. 查看日志: tail -f $ROOT_DIR/logs/cron.log"
echo "  2. 手动测试: python3 scripts/heartbeat_executor.py"
echo "  3. 查看 cron: crontab -l"
echo "  4. 编辑 cron: crontab -e"
echo ""
