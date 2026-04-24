# 平台能力映射

## 映射表

| 技能能力 | 小艺平台 | 鸿蒙平台 | 降级方案 |
|----------|----------|----------|----------|
| send_message | 小艺消息API | 鸿蒙通知 | 本地记录 |
| schedule_task | 小艺任务调度 | 鸿蒙定时器 | 本地调度 |
| retry_task | 平台重试机制 | 平台重试 | 本地重试 |
| pause_task | 平台暂停 | 平台暂停 | 本地暂停 |
| resume_task | 平台恢复 | 平台恢复 | 本地恢复 |
| cancel_task | 平台取消 | 平台取消 | 本地取消 |
| diagnostics | 平台诊断 | 平台诊断 | 本地诊断 |
| export_history | 平台导出 | 平台导出 | 本地导出 |

## 能力探测

```python
from platform_adapter.base import PlatformCapability

# 检查特定能力
status = await adapter.get_capability(PlatformCapability.TASK_SCHEDULING)
if status.available:
    # 使用平台能力
    result = await adapter.invoke(PlatformCapability.TASK_SCHEDULING, params)
else:
    # 使用降级方案
    result = await local_scheduler.schedule(params)
```

## 平台能力详情

### 小艺平台

| 能力 | API | 状态 |
|------|-----|------|
| 任务调度 | xiaoyi.schedule | 待对接 |
| 消息发送 | xiaoyi.message | 待对接 |
| 通知 | xiaoyi.notify | 待对接 |

### 鸿蒙平台

| 能力 | API | 状态 |
|------|-----|------|
| 任务调度 | ohos.scheduler | 待对接 |
| 消息发送 | ohos.notification | 待对接 |
| 后台任务 | ohos.backgroundTask | 待对接 |

## 降级行为

当平台能力不可用时：

1. **记录降级事件** - 写入 task_events
2. **使用本地实现** - 保证功能可用
3. **通知用户** - 返回降级说明

```json
{
  "success": true,
  "degraded": true,
  "message": "Using local implementation (platform unavailable)",
  "original_capability": "platform_scheduling",
  "fallback_used": "local_scheduling"
}
```
