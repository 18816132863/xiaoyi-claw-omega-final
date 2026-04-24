#!/bin/bash
# 每小时健康巡检脚本
# 检查平台调用健康状况

set -e

# 配置
WORKSPACE_DIR="/home/sandbox/.openclaw/workspace"
LOG_DIR="${WORKSPACE_DIR}/logs"
LOG_FILE="${LOG_DIR}/health_check.log"
ALERT_THRESHOLD_FAILED=10    # 失败率 > 10% 告警
ALERT_THRESHOLD_TIMEOUT=10   # 超时率 > 10% 告警

# 创建日志目录
mkdir -p "${LOG_DIR}"

echo "========================================"
echo "每小时平台健康巡检"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 运行健康检查
REPORT=$(python "${WORKSPACE_DIR}/scripts/platform_health_check.py" 2>&1)
EXIT_CODE=$?

# 记录日志
echo "${REPORT}" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"

# 检查是否需要告警
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    echo "⚠️ 健康检查发现问题!"
    echo ""
    echo "${REPORT}"
    echo ""
    echo "请检查以下问题:"
    echo "  - 失败率是否过高 (> ${ALERT_THRESHOLD_FAILED}%)"
    echo "  - 超时率是否过高 (> ${ALERT_THRESHOLD_TIMEOUT}%)"
    echo "  - NOTIFICATION 授权是否有效"
else
    echo ""
    echo "✅ 健康检查通过"
fi

echo ""
echo "日志文件: ${LOG_FILE}"
echo "========================================"

exit $EXIT_CODE
