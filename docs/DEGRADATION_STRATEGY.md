# 降级策略

## 降级原则

1. **永不失败** - 平台不可用不等于技能不可用
2. **透明降级** - 用户知道发生了什么
3. **记录追踪** - 所有降级都有日志
4. **自动恢复** - 平台恢复后自动升级

## 降级规则

### 规则1: 平台能力降级

```
平台能力不可用 → 使用本地实现
```

示例：
```python
# 尝试使用平台调度
result = await platform_adapter.invoke("schedule", params)

if not result["success"]:
    # 降级到本地调度
    result = await local_scheduler.schedule(params)
    result["degraded"] = True
    result["degradation_reason"] = "Platform scheduling unavailable"
```

### 规则2: 存储降级

```
PostgreSQL 不可用 → SQLite
Redis 不可用 → 内存缓存
```

### 规则3: 调度降级

```
常驻进程不可用 → Request-driven 执行
高级调度不可用 → 基础 once/recurring
```

### 规则4: 功能降级

```
某功能超出限制 → 返回明确说明
```

## 降级事件记录

所有降级都会记录到 task_events：

```json
{
  "event_type": "degradation",
  "capability": "platform_scheduling",
  "reason": "Platform adapter returned unavailable",
  "fallback_used": "local_scheduling",
  "timestamp": "2026-04-23T22:00:00Z"
}
```

## 降级通知

返回给用户的响应包含降级信息：

```json
{
  "success": true,
  "degraded": true,
  "message": "Task scheduled successfully (using local scheduler)",
  "degradation_info": {
    "original_method": "platform_scheduling",
    "actual_method": "local_scheduling",
    "reason": "Platform unavailable"
  }
}
```

## 自动恢复

当平台能力恢复时：

1. 探测器检测到平台可用
2. 更新能力状态
3. 后续请求使用平台能力
4. 记录恢复事件
