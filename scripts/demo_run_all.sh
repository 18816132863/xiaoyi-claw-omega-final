#!/bin/bash
# 一键演示脚本
# 顺序运行所有演示命令

set -e

WORKSPACE_DIR="/home/sandbox/.openclaw/workspace"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${WORKSPACE_DIR}/demo_outputs"

# 创建输出目录
mkdir -p "${OUTPUT_DIR}"

echo "========================================"
echo "🚀 一键演示脚本"
echo "========================================"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "输出目录: ${OUTPUT_DIR}"
echo ""

# 1. 初始化演示环境
echo "========================================"
echo "步骤 1/5: 初始化演示环境"
echo "========================================"
python "${WORKSPACE_DIR}/scripts/demo_bootstrap.py" 2>&1 | tee "${OUTPUT_DIR}/01_bootstrap_${TIMESTAMP}.txt"

# 2. 审计统计
echo ""
echo "========================================"
echo "步骤 2/5: 审计统计"
echo "========================================"
python "${WORKSPACE_DIR}/scripts/invocation_audit_cli.py" stats 2>&1 | tee "${OUTPUT_DIR}/02_stats_${TIMESTAMP}.txt"

# 3. 健康巡检
echo ""
echo "========================================"
echo "步骤 3/5: 健康巡检"
echo "========================================"
python "${WORKSPACE_DIR}/scripts/platform_health_check.py" 2>&1 | tee "${OUTPUT_DIR}/03_health_check_${TIMESTAMP}.txt"

# 4. 日报导出
echo ""
echo "========================================"
echo "步骤 4/5: 日报导出"
echo "========================================"
python "${WORKSPACE_DIR}/scripts/export_daily_platform_report.py" --format json --output "${OUTPUT_DIR}/04_daily_report_${TIMESTAMP}.json"
python "${WORKSPACE_DIR}/scripts/export_daily_platform_report.py" --format csv --output "${OUTPUT_DIR}/04_daily_report_${TIMESTAMP}.csv"
cat "${OUTPUT_DIR}/04_daily_report_${TIMESTAMP}.json"

# 5. 周报导出
echo ""
echo "========================================"
echo "步骤 5/5: 周报导出"
echo "========================================"
python "${WORKSPACE_DIR}/scripts/export_weekly_platform_report.py" --format json --output "${OUTPUT_DIR}/05_weekly_report_${TIMESTAMP}.json"
python "${WORKSPACE_DIR}/scripts/export_weekly_platform_report.py" --format csv --output "${OUTPUT_DIR}/05_weekly_report_${TIMESTAMP}.csv"
cat "${OUTPUT_DIR}/05_weekly_report_${TIMESTAMP}.json"

# 完成
echo ""
echo "========================================"
echo "✅ 一键演示完成!"
echo "========================================"
echo ""
echo "输出文件:"
ls -la "${OUTPUT_DIR}"/*${TIMESTAMP}*
echo ""
