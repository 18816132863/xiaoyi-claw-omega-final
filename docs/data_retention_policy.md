# 数据保留策略

## 概述

本文档定义 OpenClaw 任务系统的数据保留和清理策略。

## 数据分类

### 短期数据 (保留 7 天)

| 数据类型 | 位置 | 清理方式 |
|----------|------|----------|
| 任务队列 | data/task_queue.jsonl | 自动清理已完成任务 |
| 待发送消息 | reports/ops/pending_sends.jsonl | 发送后清理 |
| 临时日志 | logs/*.log | 日志轮转 |

### 中期数据 (保留 30 天)

| 数据类型 | 位置 | 清理方式 |
|----------|------|----------|
| 已送达消息 | reports/ops/delivered_messages.jsonl | 归档后清理 |
| 任务事件 | 数据库 task_events 表 | 归档后清理 |
| 指标数据 | reports/metrics/ | 压缩归档 |

### 长期数据 (保留 365 天)

| 数据类型 | 位置 | 清理方式 |
|----------|------|----------|
| 任务定义 | 数据库 tasks 表 | 归档后清理 |
| 检查点 | 数据库 checkpoints 表 | 任务完成后清理 |

## 清理脚本

### 每日清理

```bash
# 清理 7 天前的临时数据
python scripts/cleanup_temp_data.py --days 7
```

### 每周归档

```bash
# 归档 30 天前的数据
python scripts/archive_old_data.py --days 30
```

### 每月清理

```bash
# 清理 365 天前的归档数据
python scripts/cleanup_archives.py --days 365
```

## 日志轮转

### 配置

日志文件按大小轮转：
- 最大大小: 100MB
- 保留文件数: 10
- 压缩旧文件: 是

### 手动轮转

```bash
# 强制轮转日志
python scripts/rotate_logs.py
```

## 数据库清理

### 任务事件清理

```sql
-- 删除 30 天前的事件
DELETE FROM task_events 
WHERE created_at < NOW() - INTERVAL '30 days';
```

### 已完成任务清理

```sql
-- 归档 90 天前完成的任务
INSERT INTO tasks_archive 
SELECT * FROM tasks 
WHERE status IN ('succeeded', 'failed', 'cancelled')
AND last_run_at < NOW() - INTERVAL '90 days';

DELETE FROM tasks 
WHERE status IN ('succeeded', 'failed', 'cancelled')
AND last_run_at < NOW() - INTERVAL '90 days';
```

## 监控

### 存储使用

```bash
# 检查数据目录大小
du -sh data/ reports/ logs/

# 检查数据库大小
psql -c "SELECT pg_size_pretty(pg_database_size('openclaw'));"
```

### 清理统计

```bash
# 查看清理统计
python scripts/cleanup_stats.py
```
