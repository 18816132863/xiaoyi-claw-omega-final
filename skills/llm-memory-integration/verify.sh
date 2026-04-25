#!/bin/bash
# verify.sh - 验证双重包一致性
# 用法: ./verify.sh

set -e

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SKILL_DIR/src"
DIST_DIR="$SKILL_DIR/dist"

echo "=== 验证双重包 ==="
echo ""

# 检查目录存在
if [ ! -d "$SRC_DIR" ]; then
    echo "❌ src/ 目录不存在"
    exit 1
fi

if [ ! -d "$DIST_DIR" ]; then
    echo "❌ dist/ 目录不存在，请先运行 ./build.sh"
    exit 1
fi

# 检查文件结构一致性
echo "1. 检查文件结构..."
SRC_FILES=$(find "$SRC_DIR" -type f -name "*.py" | wc -l)
DIST_FILES=$(find "$DIST_DIR" -type f -name "*.py" | wc -l)

echo "   src/ 文件数: $SRC_FILES"
echo "   dist/ 文件数: $DIST_FILES"

if [ "$SRC_FILES" -eq "$DIST_FILES" ]; then
    echo "   ✅ 文件数量一致"
else
    echo "   ⚠️ 文件数量不一致"
fi

# 检查配置文件
echo ""
echo "2. 检查配置文件..."
for file in config.json requirements.json package.json; do
    if [ -f "$SKILL_DIR/$file" ] && [ -f "$DIST_DIR/$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ⚠️ $file 缺失"
    fi
done

# 检查敏感操作声明
echo ""
echo "3. 检查敏感操作声明..."
for pattern in subprocess os.system eval exec compile __import__; do
    SRC_COUNT=$(grep -r "$pattern" "$SRC_DIR" --include="*.py" 2>/dev/null | wc -l || echo "0")
    echo "   '$pattern': $SRC_COUNT 处使用"
done

# 检查硬编码密钥
echo ""
echo "4. 检查硬编码密钥..."

# 只检查 JSON 配置文件中的实际密钥值
FOUND_KEYS=0
for json_file in $(find "$SRC_DIR" "$DIST_DIR" -name "*.json" 2>/dev/null); do
    # 查找 api_key 字段值
    while IFS= read -r line; do
        # 提取值部分
        value=$(echo "$line" | sed -n 's/.*"api_key"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
        if [ -n "$value" ]; then
            # 检查是否是占位符
            case "$value" in
                YOUR_*|placeholder|example|"")
                    # 安全的占位符
                    ;;
                *)
                    # 检查长度是否超过20字符（可能是真实密钥）
                    if [ ${#value} -gt 20 ]; then
                        echo "   ⚠️ 发现可能的硬编码密钥: $json_file"
                        FOUND_KEYS=1
                    fi
                    ;;
            esac
        fi
    done < <(grep '"api_key"' "$json_file" 2>/dev/null || true)
done

if [ "$FOUND_KEYS" -eq 0 ]; then
    echo "   ✅ 未发现硬编码密钥"
fi

# 显示校验和
echo ""
echo "5. 校验和摘要..."
if [ -f "$SKILL_DIR/checksums.txt" ]; then
    echo "   校验和文件: checksums.txt"
    echo "   最后更新: $(head -1 "$SKILL_DIR/checksums.txt")"
else
    echo "   ⚠️ 校验和文件不存在，请运行 ./build.sh"
fi

echo ""
echo "✅ 验证完成！"
