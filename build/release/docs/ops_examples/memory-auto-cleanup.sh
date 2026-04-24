#!/bin/bash

# 记忆系统自动清理和备份脚本 V2.0
# 执行时机：每次会话启动时

echo "=== 记忆系统自动清理 V2.0 ==="
echo "执行时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 删除7天前的日度记忆
echo "1. 清理日度记忆（保留7天）..."
deleted_daily=$(find ~/.openclaw/workspace/memory -name "????-??-??.md" -mtime +7 -delete -print 2>/dev/null | wc -l)
echo "   已删除 $deleted_daily 个日度记忆文件"

# 2. 删除3个月前的月度记忆
echo "2. 清理月度记忆（保留3个月）..."
deleted_monthly=$(find ~/.openclaw/workspace/memory -name "????-??.md" -mtime +90 -delete -print 2>/dev/null | wc -l)
echo "   已删除 $deleted_monthly 个月度记忆文件"

# 3. 压缩 MEMORY.md（超过200行）
echo "3. 压缩长期记忆（MEMORY.md）..."
memory_file="$HOME/.openclaw/workspace/MEMORY.md"
if [ -f "$memory_file" ]; then
    lines=$(wc -l < "$memory_file")
    if [ $lines -gt 200 ]; then
        echo "   当前行数: $lines，正在压缩..."
        # 保留标题和关键信息
        grep -E "^#|^##|用户信息|技能配置|关键经验" "$memory_file" > /tmp/memory_compressed.md
        mv /tmp/memory_compressed.md "$memory_file"
        new_lines=$(wc -l < "$memory_file")
        echo "   压缩后行数: $new_lines"
    else
        echo "   当前行数: $lines，无需压缩"
    fi
fi

# 4. 压缩月度记忆（超过500行）
echo "4. 压缩月度记忆..."
current_month=$(date +%Y-%m)
monthly_file="$HOME/.openclaw/workspace/memory/$current_month.md"
if [ -f "$monthly_file" ]; then
    lines=$(wc -l < "$monthly_file")
    if [ $lines -gt 500 ]; then
        echo "   $current_month.md 当前行数: $lines，正在压缩..."
        grep -E "^#|^##|^###" "$monthly_file" > /tmp/monthly_compressed.md
        mv /tmp/monthly_compressed.md "$monthly_file"
        new_lines=$(wc -l < "$monthly_file")
        echo "   压缩后行数: $new_lines"
    else
        echo "   $current_month.md 当前行数: $lines，无需压缩"
    fi
fi

# 5. 压缩日度记忆（超过100行）
echo "5. 压缩日度记忆..."
today=$(date +%Y-%m-%d)
daily_file="$HOME/.openclaw/workspace/memory/$today.md"
if [ -f "$daily_file" ]; then
    lines=$(wc -l < "$daily_file")
    if [ $lines -gt 100 ]; then
        echo "   $today.md 当前行数: $lines，正在压缩..."
        grep -E "^#|^##|^###" "$daily_file" > /tmp/daily_compressed.md
        mv /tmp/daily_compressed.md "$daily_file"
        new_lines=$(wc -l < "$daily_file")
        echo "   压缩后行数: $new_lines"
    else
        echo "   $today.md 当前行数: $lines，无需压缩"
    fi
fi

echo ""
echo "=== 清理完成 ==="
echo ""

# 6. 自动备份到 GitHub
echo "=== 自动备份到 GitHub ==="
cd ~/.openclaw/workspace

# 检查是否有改动
if [ -n "$(git status --porcelain)" ]; then
    echo "检测到文件改动，正在备份..."
    git add -A
    git commit -m "记忆系统自动备份: $(date '+%Y-%m-%d %H:%M:%S')"
    git push 2>&1 | tail -3
    echo "备份完成"
else
    echo "没有文件改动，无需备份"
fi

echo ""
echo "=== 全部完成 ==="
