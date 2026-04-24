# 任务状态机文档

## 全部状态

| 状态 | 说明 |
|------|------|
| draft | 草稿 |
| validated | 已校验 |
| persisted | 已持久化 |
| queued | 已入队 |
| running | 运行中 |
| delivery_pending | 已执行，等待真实送达确认 |
| waiting_retry | 等待重试 |
| waiting_human | 等待人工 |
| paused | 已暂停 |
| resumed | 已恢复 |
| succeeded | 成功 |
| failed | 失败 |
| cancelled | 已取消 |

## 关键流转

### once 任务
```
persisted -> queued -> running -> delivery_pending -> succeeded
```

### recurring 任务
```
persisted -> queued -> running -> delivery_pending -> persisted
```

### 失败重试
```
running -> waiting_retry -> queued -> running
```

## 状态转移规则

| 当前状态 | 事件 | 目标状态 |
|----------|------|----------|
| running | await_delivery | delivery_pending |
| delivery_pending | delivery_ok | succeeded |
| delivery_pending | delivery_reschedule | persisted |
| delivery_pending | delivery_retry | waiting_retry |
| delivery_pending | delivery_give_up | failed |
