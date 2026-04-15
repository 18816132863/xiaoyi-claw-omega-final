---
name: backup-cleaner
description: backup-cleaner 技能模块
---

# backup-cleaner

自动清理 OpenClaw 工作空间中的老旧备份文件，释放磁盘空间。

## 功能

1. **清理备份目录** - `.openclaw/backup/` 中的旧备份
2. **清理工作空间备份** - `workspace/*.tar.gz`, `workspace/*.zip`
3. **清理会话快照** - `sessions/*.jsonl.reset.*`, `sessions/*.jsonl.deleted.*`
4. **清理浏览器缓存** - `.openclaw/browser/` (可选)
5. **清理 NPM 缓存** - `.openclaw/npm-cache/` (可选)

## 使用方法

```bash
# 查看可清理的空间（干运行）
python ~/.openclaw/workspace/skills/backup-cleaner/cleaner.py --dry-run

# 执行清理（保留最近 N 天）
python ~/.openclaw/workspace/skills/backup-cleaner/cleaner.py --keep-days 7

# 清理所有（包括浏览器缓存）
python ~/.openclaw/workspace/skills/backup-cleaner/cleaner.py --keep-days 7 --include-browser

# 激进清理（只保留最近 3 天）
python ~/.openclaw/workspace/skills/backup-cleaner/cleaner.py --keep-days 3 --aggressive
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--dry-run` | 只显示可清理空间，不实际删除 | False |
| `--keep-days` | 保留最近 N 天的文件 | 7 |
| `--include-browser` | 同时清理浏览器缓存 | False |
| `--include-npm` | 同时清理 NPM 缓存 | False |
| `--aggressive` | 激进模式，清理更多内容 | False |

## 定时任务

建议配置 cron 每周执行一次：

```bash
# 每周日凌晨 3 点清理
0 3 * * 0 python ~/.openclaw/workspace/skills/backup-cleaner/cleaner.py --keep-days 7
```

## 安全规则

- 不会删除当前活跃的会话文件
- 不会删除配置文件
- 不会删除技能文件
- 删除前会显示文件列表和大小
