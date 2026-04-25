#!/bin/bash
# OpenClaw 优化备份脚本
# 自动排除备份、缓存等不必要文件

set -e

# 配置
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
VERSION="v4.3.3"
OUTPUT_DIR="${1:-$HOME}"
OUTPUT_FILE="${OUTPUT_DIR}/openclaw_${VERSION}_${TIMESTAMP}.tar.gz"
BASE_DIR="$OPENCLAW_HOME"
EXCLUDE_FILE="$WORKSPACE/infrastructure/backup_excludes.txt"

echo "╔══════════════════════════════════════════════════╗"
echo "║        OpenClaw 优化备份 v${VERSION}               ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "输出: $OUTPUT_FILE"

# 检查排除文件
if [ ! -f "$EXCLUDE_FILE" ]; then
    echo "警告: 排除规则文件不存在，使用默认规则"
    EXCLUDE_FILE="/dev/null"
fi

# 计算源目录大小
echo ""
echo "源目录大小:"
du -sh "$BASE_DIR" 2>/dev/null || echo "无法计算"

# 显示排除规则
echo ""
echo "排除规则:"
echo "  ✓ 备份目录 (.openclaw/backup/)"
echo "  ✓ 浏览器缓存 (.openclaw/browser/)"
echo "  ✓ NPM 缓存 (.openclaw/npm-cache/)"
echo "  ✓ 历史会话快照 (*.jsonl.reset.*, *.jsonl.deleted.*)"
echo "  ✓ 大型工具 (magika, git-lfs)"
echo "  ✓ 旧备份文件 (*.tar.gz, *.zip)"
echo "  ✓ Python 库 (repo/lib/, repo/include/, repo/bin/)"
echo "  ✓ 向量索引 (memory_context/index/)"
echo "  ✓ Node modules (extensions/*/node_modules/)"

# 执行打包
echo ""
echo "开始打包..."

tar -czvf "$OUTPUT_FILE" \
    --exclude-from="$EXCLUDE_FILE" \
    -C $HOME \
    .openclaw \
    .local/bin \
    2>&1 | tail -5

# 验证结果
echo ""
echo "══════════════════════════════════════════════════"
echo "备份完成"
echo "══════════════════════════════════════════════════"
echo ""
ls -lh "$OUTPUT_FILE"
echo ""
echo "文件数: $(tar -tzf "$OUTPUT_FILE" | wc -l)"

# 显示压缩包内容分布
echo ""
echo "内容分布:"
tar -tzvf "$OUTPUT_FILE" 2>/dev/null | awk '
{
  size = $3
  path = $6
  if (path ~ /\/sessions\//) sessions += size
  else if (path ~ /\/skills\//) skills += size
  else if (path ~ /\.local\/bin\//) localbin += size
  else if (path ~ /\/workspace\//) workspace += size
  else if (path ~ /\/extensions\//) extensions += size
  else other += size
}
END {
  total = sessions + skills + localbin + workspace + extensions + other
  printf "  会话日志:   %6.2f MB (%.0f%%)\n", sessions/1048576, sessions/total*100
  printf "  技能文件:   %6.2f MB (%.0f%%)\n", skills/1048576, skills/total*100
  printf "  本地工具:   %6.2f MB (%.0f%%)\n", localbin/1048576, localbin/total*100
  printf "  工作空间:   %6.2f MB (%.0f%%)\n", workspace/1048576, workspace/total*100
  printf "  扩展:       %6.2f MB (%.0f%%)\n", extensions/1048576, extensions/total*100
  printf "  其他:       %6.2f MB (%.0f%%)\n", other/1048576, other/total*100
}'

echo ""
echo "输出文件: $OUTPUT_FILE"
