# 任务生命周期文档

## once 任务生命周期

### 1. 创建
- 调用 `create_scheduled_message()`
- 状态: `persisted`
- `next_run_at` 设置为指定时间

### 2. 调度
- 调度器扫描到期任务
- 状态: `persisted -> queued`

### 3. 入队
- 任务写入 `task_queue.jsonl`
- 状态: `queued`

### 4. 执行
- 执行器拉取任务执行
- 状态: `queued -> running`
- 步骤执行成功后进入 `delivery_pending`

### 5. 送达确认
- 消息写入 `pending_sends.jsonl`
- `message_server` 真实送达
- 写入 `delivered_messages.jsonl`
- 状态: `delivery_pending -> succeeded`
- `next_run_at` 清空

## recurring 任务生命周期

### 1. 创建
- 调用 `create_recurring_message()`
- 状态: `persisted`
- `next_run_at` 设置为下次运行时间

### 2-5. 同 once 任务

### 6. 循环
- 送达确认后状态回到 `persisted`
- `next_run_at` 刷新为下次运行时间
- 等待下次调度

## 关键时间点

| 时间点 | 说明 |
|--------|------|
| created_at | 任务创建时间 |
| next_run_at | 下次运行时间 |
| last_run_at | 上次运行时间 |
| delivered_at | 真实送达时间 |
