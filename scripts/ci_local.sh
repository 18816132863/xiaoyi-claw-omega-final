#!/bin/bash
# 本地 CI 脚本
# 顺序执行所有检查

set -e

WORKSPACE_DIR="/home/sandbox/.openclaw/workspace"

echo "========================================"
echo "🔄 本地 CI"
echo "========================================"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "工作目录: ${WORKSPACE_DIR}"
echo ""

# 1. Pytest
echo "========================================"
echo "步骤 1/3: Pytest 全量测试"
echo "========================================"
python -m pytest -q --tb=no
echo ""

# 2. Release Check
echo "========================================"
echo "步骤 2/3: 发布检查"
echo "========================================"
python "${WORKSPACE_DIR}/scripts/release_check.py"
echo ""

# 3. Skill Preflight Check
echo "========================================"
echo "步骤 3/3: 技能上传前检查"
echo "========================================"
python "${WORKSPACE_DIR}/scripts/skill_preflight_check.py"
echo ""

echo "========================================"
echo "✅ 本地 CI 完成"
echo "========================================"
