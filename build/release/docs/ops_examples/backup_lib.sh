#!/bin/bash
# OpenClaw 备份通用函数库
# 可被其他脚本 source 引用

# 排除规则文件路径
BACKUP_EXCLUDE_FILE="${BACKUP_EXCLUDE_FILE:-$WORKSPACE/infrastructure/backup_excludes.txt}"

# 默认排除规则（当排除文件不存在时使用）
DEFAULT_EXCLUDES=(
    "--exclude=.openclaw/backup"
    "--exclude=.openclaw/browser"
    "--exclude=.openclaw/npm-cache"
    "--exclude=.openclaw/media/browser"
    "--exclude=*.jsonl.reset.*"
    "--exclude=*.jsonl.deleted.*"
    "--exclude=magika"
    "--exclude=git-lfs"
    "--exclude=*.tar.gz"
    "--exclude=*.zip"
)

# 创建优化备份
# 用法: create_backup <输出文件> [源目录...]
create_backup() {
    local output_file="$1"
    shift
    local sources=("$@")

    if [ ${#sources[@]} -eq 0 ]; then
        sources=(".openclaw" ".local/bin")
    fi

    local tar_args=(
        "-czvf" "$output_file"
        "-C" "$HOME"
    )

    if [ -f "$BACKUP_EXCLUDE_FILE" ]; then
        tar_args+=("--exclude-from=$BACKUP_EXCLUDE_FILE")
    else
        tar_args+=("${DEFAULT_EXCLUDES[@]}")
    fi

    tar_args+=("${sources[@]}")

    tar "${tar_args[@]}" 2>&1 | tail -5

    if [ -f "$output_file" ]; then
        echo "备份完成: $output_file ($(ls -lh "$output_file" | awk '{print $5}'))"
        return 0
    else
        echo "备份失败"
        return 1
    fi
}

# 获取排除规则说明
get_exclude_info() {
    cat << 'EOF'
排除内容:
  • 备份目录 (.openclaw/backup/)
  • 浏览器缓存 (.openclaw/browser/)
  • NPM 缓存 (.openclaw/npm-cache/)
  • 历史会话快照 (*.jsonl.reset.*, *.jsonl.deleted.*)
  • 大型工具 (magika 32MB, git-lfs 11MB)
  • 旧备份文件 (*.tar.gz, *.zip)
EOF
}

# 如果直接运行此脚本，执行默认备份
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT_FILE="$HOME/openclaw_backup_${TIMESTAMP}.tar.gz"

    echo "=== OpenClaw 优化备份 ==="
    get_exclude_info
    echo ""

    create_backup "$OUTPUT_FILE"
fi
