# 可观测性文档

## 概述

OpenClaw 任务系统提供完整的可观测性支持，包括：
- 结构化日志
- 业务指标
- 健康检查

## 日志系统

### 日志字段

| 字段 | 说明 |
|------|------|
| timestamp | ISO 格式时间戳 |
| level | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| service | 服务名称 |
| component | 组件名称 |
| message | 日志消息 |
| task_id | 任务 ID |
| run_id | 运行 ID |
| event_type | 事件类型 |
| status | 状态 |
| tool_name | 工具名称 |
| schedule_mode | 调度模式 (once/cron/recurring) |
| delivery_status | 送达状态 |
| error_type | 错误类型 |
| error_message | 错误消息 |

### 日志级别

| 级别 | 说明 |
|------|------|
| DEBUG | 调试信息 |
| INFO | 正常流转 |
| WARNING | 可恢复异常 |
| ERROR | 失败但系统未崩 |
| CRITICAL | 服务不可用 |

### 日志位置

- 日志目录: `logs/`
- 格式: JSON Lines (`.jsonl`)

## 指标系统

### 核心指标

| 指标名 | 类型 | 说明 |
|--------|------|------|
| tasks_dispatched | counter | 任务投递总数 |
| tasks_executed | counter | 任务执行总数 |
| tasks_succeeded | counter | 任务成功总数 |
| tasks_failed | counter | 任务失败总数 |
| messages_delivered | counter | 消息送达总数 |
| deliveries_confirmed | counter | 送达确认总数 |
| message_send_failures | counter | 消息发送失败总数 |
| cycle_duration_seconds | histogram | 周期耗时 |

### 指标位置

- 指标目录: `reports/metrics/`
- 格式: JSON

## 健康检查

### 检查项

| 检查项 | 说明 |
|--------|------|
| daemon_running | 守护进程运行状态 |
| db_connection | 数据库连接 |
| queue_writable | 队列可写 |

### 健康状态

| 状态 | 说明 |
|------|------|
| healthy | 健康 |
| degraded | 降级 |
| unhealthy | 不健康 |

## 故障排查

### 任务执行失败

1. 查看 `logs/task_daemon_daemon.jsonl`
2. 搜索 `event_type=task_execution_failed`
3. 查看 `error_message` 字段

### 消息送达失败

1. 查看 `logs/task_daemon_daemon.jsonl`
2. 搜索 `event_type=message_send_error`
3. 检查 message_server 是否运行

### 任务卡在 delivery_pending

1. 查看 `reports/ops/delivered_messages.jsonl`
2. 检查是否有对应记录
3. 查看 daemon 日志中的 `delivery_confirmed` 事件
