#!/bin/bash
# 自动备份到 GitHub
# 每次有改动时自动提交并推送

WORKSPACE_DIR="$HOME/.openclaw/workspace"
LOG_FILE="$WORKSPACE_DIR/.auto-backup.log"

cd "$WORKSPACE_DIR" || exit 1

# 检查是否有改动
CHANGES=$(git status --porcelain)

if [ -z "$CHANGES" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 无改动，跳过" >> "$LOG_FILE"
    exit 0
fi

# 记录改动数量
CHANGE_COUNT=$(echo "$CHANGES" | wc -l)
echo "$(date '+%Y-%m-%d %H:%M:%S') - 发现 $CHANGE_COUNT 个改动" >> "$LOG_FILE"

# 添加所有改动
git add -A

# 生成提交信息
COMMIT_MSG="自动备份: $(date '+%Y-%m-%d %H:%M:%S')
改动文件: $CHANGE_COUNT 个"

# 提交
git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1

# 推送
git push origin master >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 推送成功" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 推送失败" >> "$LOG_FILE"
fi
