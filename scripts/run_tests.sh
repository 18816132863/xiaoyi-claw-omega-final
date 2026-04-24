#!/bin/bash
# OpenClaw 统一测试入口 V3.0.0
# 自动检查并安装测试依赖，然后运行 pytest

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "  OpenClaw 统一测试入口 V3.0.0"
echo "============================================================"
echo ""

# 1. 检查并安装测试依赖
echo "[1/3] 检查测试依赖..."

# 依赖配置：(pip包名, import模块名, 版本要求, 是否强制版本)
DEPENDENCIES=(
    "croniter:croniter:>=2.0.0:false"
    "aiohttp:aiohttp:>=3.9.0:false"
    "pytest:pytest:>=8.0.0:false"
    "pytest-asyncio:pytest_asyncio:==0.23.6:true"
    "pydantic:pydantic:>=2.0.0:false"
)

for dep in "${DEPENDENCIES[@]}"; do
    IFS=':' read -r pip_pkg import_module version_req force_version <<< "$dep"
    
    # 检查模块是否存在
    if ! python3 -c "import $import_module" 2>/dev/null; then
        echo "  📦 安装 $pip_pkg ..."
        python3 -m pip install "$pip_pkg$version_req" -q
        echo "  ✅ $pip_pkg 安装完成"
        continue
    fi
    
    # 检查版本（如果需要强制版本）
    if [ "$force_version" = "true" ]; then
        current_version=$(python3 -c "import $import_module; print($import_module.__version__)" 2>/dev/null || echo "unknown")
        target_version=$(echo "$version_req" | sed 's/==//')
        
        if [ "$current_version" != "$target_version" ]; then
            echo "  ⚠️  $pip_pkg 版本不匹配 (当前: $current_version, 要求: $target_version)"
            echo "  📦 强制安装 $pip_pkg==$target_version ..."
            python3 -m pip install "$pip_pkg==$target_version" -q --force-reinstall
            echo "  ✅ $pip_pkg 已更新到 $target_version"
        else
            echo "  ✅ $pip_pkg 已安装 ($current_version)"
        fi
    else
        echo "  ✅ $pip_pkg 已安装"
    fi
done

echo ""

# 2. 运行 pytest
echo "[2/3] 运行 pytest..."
echo ""

python3 -m pytest tests/ -q "$@"

echo ""

# 3. 显示结果
echo "[3/3] 测试完成"
echo "============================================================"
