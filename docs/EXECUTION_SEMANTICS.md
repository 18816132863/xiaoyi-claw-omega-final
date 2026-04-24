# 执行语义说明

## 版本
- V8.3.0 路径统一版
- 更新日期: 2026-04-24

## 核心语义区分

### 三层执行状态

| 状态 | 含义 | 说明 |
|------|------|------|
| `accepted` | 已接受 | 任务已被系统接受，准备执行 |
| `queued_for_delivery` | 已入队 | 已生成执行请求，等待真实投递 |
| `completed` / `confirmed` | 已完成 | 真实执行完成，已获确认 |

## 任务状态 (TaskStatus)

| 状态 | 语义层级 | 说明 |
|------|----------|------|
| `draft` | - | 草稿，未提交 |
| `validated` | accepted | 已校验，准备执行 |
| `persisted` | accepted | 已持久化，等待调度 |
| `queued` | accepted | 已入队，等待执行 |
| `running` | - | 执行中 |
| `delivery_pending` | queued_for_delivery | 已执行，等待真实送达确认 |
| `succeeded` | completed | 成功完成 |
| `failed` | - | 失败 |
| `cancelled` | - | 已取消 |

## 步骤状态 (StepStatus)

| 状态 | 语义层级 | 说明 |
|------|----------|------|
| `pending` | accepted | 待执行 |
| `running` | - | 执行中 |
| `succeeded` | completed | 成功完成 |
| `failed` | - | 失败 |
| `skipped` | - | 已跳过 |

## 事件类型 (EventType)

| 事件 | 语义层级 | 说明 |
|------|----------|------|
| `created` | - | 任务创建 |
| `validated` | accepted | 校验通过 |
| `persisted` | accepted | 持久化完成 |
| `queued` | accepted | 入队完成 |
| `started` | - | 开始执行 |
| `step_started` | - | 步骤开始 |
| `step_completed` | completed | 步骤完成 |
| `step_failed` | - | 步骤失败 |
| `delivery_pending` | queued_for_delivery | 等待送达确认 |
| `delivery_confirmed` | completed | 送达已确认 |
| `succeeded` | completed | 任务成功 |
| `failed` | - | 任务失败 |

## 消息发送状态 (MessageSendResult)

| 状态 | 语义层级 | 说明 |
|------|----------|------|
| `success` | completed | 真实送达用户 |
| `queued_for_delivery` | queued | 已生成发送请求，等待处理 |
| `failed` | - | 发送失败 |

## 状态流转图

```
draft → validated → persisted → queued → running
                                              ↓
                                       delivery_pending
                                              ↓
                                       delivery_confirmed
                                              ↓
                                          succeeded
```

## 关键区分

### ❌ 错误理解
- "任务状态是 succeeded" 但实际只是 "已入队"
- "消息已发送" 但实际只是 "已写入队列"

### ✅ 正确理解
- `delivery_pending` = "已执行，等待真实送达确认"
- `queued_for_delivery` = "已生成请求，等待网关处理"
- `succeeded` = "真实完成，已获确认"

## 平台能力与执行语义

| 平台状态 | 执行结果 | 最终状态 |
|----------|----------|----------|
| connected | success | succeeded |
| connected | queued | delivery_pending → delivery_confirmed |
| probe_only | queued | delivery_pending (无确认) |
| fallback | queued | delivery_pending (无确认) |

## 降级策略

当平台不支持确认时：

1. 记录 `delivery_pending` 状态
2. 标记 `confirmation_unavailable: true`
3. 不声称 `succeeded`
4. 用户可见："已提交，等待处理"

## 测试覆盖

| 测试 | 文件 |
|------|------|
| 状态语义 | tests/test_platform_execution_semantics.py |
| 状态流转 | tests/test_delivery_confirmation_semantics.py |
