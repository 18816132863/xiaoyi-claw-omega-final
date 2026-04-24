# 送达确认策略

## 版本
- V8.3.0 路径统一版
- 更新日期: 2026-04-24

## 平台确认能力分级

### Level 1: 完整确认 (Full Confirmation)
- 平台支持回调/Webhook
- 可获取最终送达状态
- 状态流转: `delivery_pending` → `delivery_confirmed` → `succeeded`

### Level 2: 投递确认 (Delivery Confirmation)
- 平台确认已投递到网关
- 无法确认用户是否收到
- 状态流转: `delivery_pending` → `delivered_to_gateway`

### Level 3: 无确认 (No Confirmation)
- 平台不支持任何确认
- 只能假设成功
- 状态流转: `delivery_pending` (停留)

## 当前平台状态

| 平台 | 确认级别 | 策略 |
|------|----------|------|
| xiaoyi (connected) | 待定 | 待API对接后确定 |
| xiaoyi (probe_only) | Level 3 | 无确认，记录 pending |
| fallback | Level 3 | 无确认，写入队列 |

## 降级策略详情

### 当平台不支持确认时

```python
{
    "status": "delivery_pending",
    "confirmation_available": false,
    "confirmation_level": "none",
    "user_message": "已提交，等待处理",
    "internal_note": "平台不支持送达确认，无法确定最终状态"
}
```

### 不允许的行为

❌ 把 `queued_for_delivery` 说成 `succeeded`
❌ 假设消息已送达
❌ 隐瞒确认不可用的事实

### 必须的行为

✅ 明确告知用户当前状态
✅ 区分"已提交"和"已完成"
✅ 记录确认不可用的原因

## 确认事件定义

### delivery_confirmed
```python
{
    "event_type": "delivery_confirmed",
    "task_id": "xxx",
    "run_id": "xxx",
    "confirmed_at": "2026-04-24T10:00:00",
    "confirmation_source": "platform_callback"  # 或 "manual" 或 "assumed"
}
```

### external_completed
```python
{
    "event_type": "external_completed",
    "task_id": "xxx",
    "external_system": "xiaoyi",
    "completed_at": "2026-04-24T10:00:00",
    "details": {...}
}
```

## 超时处理

当 `delivery_pending` 超过阈值时：

| 超时时间 | 处理 |
|----------|------|
| < 5分钟 | 等待 |
| 5-30分钟 | 标记 `confirmation_timeout_warning` |
| > 30分钟 | 标记 `confirmation_timeout`，人工介入 |

## 用户可见文案

| 状态 | 用户可见 |
|------|----------|
| `queued` | "任务已排队" |
| `running` | "正在执行..." |
| `delivery_pending` | "已提交，等待送达确认" |
| `delivery_confirmed` | "已完成" |
| `succeeded` | "成功完成" |

## 测试覆盖

| 测试 | 文件 |
|------|------|
| 确认语义 | tests/test_delivery_confirmation_semantics.py |
| 降级行为 | tests/test_delivery_confirmation_semantics.py |
