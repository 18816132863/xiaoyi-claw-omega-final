# 能力矩阵

## 核心能力

| 能力 | 描述 | 默认模式 | 平台增强 | 自托管增强 |
|------|------|----------|----------|------------|
| send_message | 发送消息 | ✅ | ✅ | ✅ |
| schedule_task | 调度任务 | ✅ | ✅ | ✅ |
| retry_task | 重试任务 | ✅ | ✅ | ✅ |
| pause_task | 暂停任务 | ✅ | ✅ | ✅ |
| resume_task | 恢复任务 | ✅ | ✅ | ✅ |
| cancel_task | 取消任务 | ✅ | ✅ | ✅ |
| diagnostics | 系统诊断 | ✅ | ✅ | ✅ |
| export_history | 导出历史 | ✅ | ✅ | ✅ |
| replay_run | 回放运行 | ✅ | ✅ | ✅ |
| self_repair | 自修复 | ✅ | ✅ | ✅ |

## 增强能力

| 能力 | 描述 | 默认模式 | 平台增强 | 自托管增强 |
|------|------|----------|----------|------------|
| platform_scheduling | 平台调度 | ❌ | ✅ | ❌ |
| platform_messaging | 平台消息 | ❌ | ✅ | ❌ |
| distributed_execution | 分布式执行 | ❌ | ❌ | ✅ |
| advanced_retry | 高级重试 | ⚠️ | ⚠️ | ✅ |
| checkpoint_recovery | 检查点恢复 | ⚠️ | ⚠️ | ✅ |

图例：
- ✅ 完全支持
- ⚠️ 部分支持（有限制）
- ❌ 不支持

## 能力详情

### send_message

```python
params = {
    "channel": "default",  # 渠道
    "message": "Hello",    # 消息内容
    "metadata": {}         # 元数据
}

result = await capability_registry.execute("send_message", params)
```

### schedule_task

```python
params = {
    "task_type": "once",   # once / recurring
    "run_at": "2026-04-24T10:00:00",  # 执行时间
    "message": "Reminder", # 任务内容
    "cron_expr": "* * * * *"  # cron表达式（recurring）
}

result = await capability_registry.execute("schedule_task", params)
```

### retry_task

```python
params = {
    "task_id": "xxx-xxx-xxx"
}

result = await capability_registry.execute("retry_task", params)
```

### diagnostics

```python
result = await capability_registry.execute("diagnostics", {})
# 返回系统健康检查结果
```

## 能力注册

```python
from capabilities.registry import get_registry, register_capability

registry = get_registry()

# 查看所有能力
caps = registry.list_all()

# 查看可用能力
available = registry.list_available()

# 获取能力报告
report = registry.get_capabilities_report()
```
