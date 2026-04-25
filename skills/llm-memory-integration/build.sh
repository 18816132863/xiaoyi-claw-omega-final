#!/bin/bash
# build.sh - 构建双重包
# 用法: ./build.sh [--vmp]

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SKILL_DIR/src"
DIST_DIR="$SKILL_DIR/dist"
BUILD_DIR="$SKILL_DIR/.build"

echo "=== 构建双重包 ==="
echo ""

# 清理
echo "1. 清理旧文件..."
rm -rf "$DIST_DIR"
rm -rf "$BUILD_DIR"
mkdir -p "$DIST_DIR"
mkdir -p "$BUILD_DIR"

# 复制源码到 dist
echo "2. 复制源码到 dist/..."
cp -r "$SRC_DIR"/* "$DIST_DIR/"

# 复制配置文件
echo "3. 复制配置文件..."
cp -r "$SKILL_DIR/config" "$DIST_DIR/"
cp "$SKILL_DIR/requirements.json" "$DIST_DIR/"
cp "$SKILL_DIR/package.json" "$DIST_DIR/"
cp "$SKILL_DIR/config.json" "$DIST_DIR/"

# VMP 保护（如果安装了 VMP）
if [ "$1" == "--vmp" ]; then
    echo "4. 应用 VMP 保护..."
    
    # 检查 VMP 是否可用
    if command -v vmp &> /dev/null; then
        # 保护核心模块
        for file in "$DIST_DIR"/core/*.py; do
            if [ -f "$file" ]; then
                echo "   保护: $(basename "$file")"
                vmp protect "$file" --output "$file" 2>/dev/null || echo "   跳过: VMP 不可用"
            fi
        done
        
        # 保护关键脚本
        for file in "$DIST_DIR"/scripts/search.py "$DIST_DIR"/scripts/smart_memory_update.py; do
            if [ -f "$file" ]; then
                echo "   保护: $(basename "$file")"
                vmp protect "$file" --output "$file" 2>/dev/null || echo "   跳过: VMP 不可用"
            fi
        done
    else
        echo "   ⚠️ VMP 未安装，跳过保护步骤"
        echo "   dist/ 版本将与 src/ 版本相同"
    fi
else
    echo "4. 跳过 VMP 保护（使用 --vmp 参数启用）"
fi

# 生成校验和
echo "5. 生成校验和..."
CHECKSUM_FILE="$SKILL_DIR/checksums.txt"
echo "# 校验和 - $(date '+%Y-%m-%d %H:%M:%S')" > "$CHECKSUM_FILE"
echo "" >> "$CHECKSUM_FILE"
echo "## 源码版本 (src/)" >> "$CHECKSUM_FILE"
find "$SRC_DIR" -name "*.py" -exec sha256sum {} \; >> "$CHECKSUM_FILE" 2>/dev/null || true
echo "" >> "$CHECKSUM_FILE"
echo "## 保护版本 (dist/)" >> "$CHECKSUM_FILE"
find "$DIST_DIR" -name "*.py" -exec sha256sum {} \; >> "$CHECKSUM_FILE" 2>/dev/null || true

echo ""
echo "✅ 构建完成！"
echo ""
echo "目录结构："
echo "  src/   - 源码版本（ClawHub 扫描）"
echo "  dist/  - 保护版本（生产使用）"
echo ""
echo "校验和已保存到: checksums.txt"
