#!/bin/bash
# 每日备份脚本
# 备份 platform_invocations 到 JSON 文件

set -e

# 配置
WORKSPACE_DIR="/home/sandbox/.openclaw/workspace"
BACKUP_DIR="${WORKSPACE_DIR}/backups/platform_invocations"
DATE=$(date +%Y%m%d)
RETENTION_DAYS=7

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

echo "========================================"
echo "每日平台调用备份"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 导出所有记录
echo "导出所有记录..."
python "${WORKSPACE_DIR}/scripts/invocation_audit_cli.py" export \
    --type recent \
    --format json \
    --limit 10000 \
    --output "${BACKUP_DIR}/invocations_${DATE}.json"

# 导出 uncertain 记录
echo "导出 uncertain 记录..."
python "${WORKSPACE_DIR}/scripts/invocation_audit_cli.py" export \
    --type uncertain \
    --format json \
    --limit 1000 \
    --output "${BACKUP_DIR}/uncertain_${DATE}.json"

# 导出 failed 记录
echo "导出 failed 记录..."
python "${WORKSPACE_DIR}/scripts/invocation_audit_cli.py" export \
    --type failed \
    --format json \
    --limit 1000 \
    --output "${BACKUP_DIR}/failed_${DATE}.json"

# 导出 timeout 记录
echo "导出 timeout 记录..."
python "${WORKSPACE_DIR}/scripts/invocation_audit_cli.py" export \
    --type timeout \
    --format json \
    --limit 1000 \
    --output "${BACKUP_DIR}/timeout_${DATE}.json"

# 清理旧备份
echo "清理 ${RETENTION_DAYS} 天前的备份..."
find "${BACKUP_DIR}" -name "*.json" -mtime +${RETENTION_DAYS} -delete

# 统计
TOTAL_FILES=$(ls -1 "${BACKUP_DIR}"/*.json 2>/dev/null | wc -l || echo 0)
TOTAL_SIZE=$(du -sh "${BACKUP_DIR}" 2>/dev/null | cut -f1 || echo "0")

echo ""
echo "✅ 备份完成!"
echo "   备份目录: ${BACKUP_DIR}"
echo "   今日文件: 4 个"
echo "   总文件数: ${TOTAL_FILES}"
echo "   总大小: ${TOTAL_SIZE}"
echo "========================================"
