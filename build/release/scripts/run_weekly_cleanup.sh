#!/bin/bash
# 每周清理脚本
# 清理旧的 platform_invocations 记录

set -e

# 配置
WORKSPACE_DIR="/home/sandbox/.openclaw/workspace"
BACKUP_DIR="${WORKSPACE_DIR}/backups/platform_invocations"
DATE=$(date +%Y%m%d)

# 清理配置
COMPLETED_DAYS=30      # completed 记录保留 30 天
FAILED_DAYS=90         # failed 记录保留 90 天
TIMEOUT_DAYS=90        # timeout 记录保留 90 天
UNCERTAIN_KEEP=true    # uncertain 记录永久保留

echo "========================================"
echo "每周平台调用清理"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 清理前先备份
echo "清理前备份..."
mkdir -p "${BACKUP_DIR}"
python "${WORKSPACE_DIR}/scripts/invocation_audit_cli.py" export \
    --type recent \
    --format json \
    --limit 10000 \
    --output "${BACKUP_DIR}/pre_cleanup_${DATE}.json"

echo ""

# 清理 completed 记录
echo "清理 ${COMPLETED_DAYS} 天前的 completed 记录..."
python "${WORKSPACE_DIR}/scripts/invocation_audit_cli.py" cleanup \
    --days ${COMPLETED_DAYS} \
    --keep-failed true \
    --keep-uncertain true

echo ""
echo "✅ 清理完成!"
echo ""
echo "保留策略:"
echo "   completed: ${COMPLETED_DAYS} 天"
echo "   failed: ${FAILED_DAYS} 天"
echo "   timeout: ${TIMEOUT_DAYS} 天"
echo "   uncertain: 永久保留"
echo ""
echo "备份文件: ${BACKUP_DIR}/pre_cleanup_${DATE}.json"
echo "========================================"
