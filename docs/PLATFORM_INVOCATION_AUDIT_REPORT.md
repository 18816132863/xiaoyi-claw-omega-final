# 平台调用审计报告

## 版本
- V8.4.0 平台稳定性硬化版
- 日期: 2026-04-24

## 一、审计台账概述

### 1.1 数据库表

**表名**: `platform_invocations`

**用途**: 记录所有平台调用的详细信息，支持审计、追溯、统计分析

### 1.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| task_id | TEXT | 任务 ID |
| task_run_id | TEXT | 任务运行 ID |
| task_step_id | TEXT | 任务步骤 ID |
| capability | TEXT | 能力名称 |
| platform_op | TEXT | 平台操作 |
| idempotency_key | TEXT | 幂等键（唯一） |
| side_effecting | INTEGER | 是否有副作用 |
| request_json | TEXT | 请求参数 JSON |
| raw_result_json | TEXT | 原始结果 JSON |
| normalized_status | TEXT | 归一化状态 |
| error_code | TEXT | 错误码 |
| user_message | TEXT | 用户消息 |
| result_uncertain | INTEGER | 结果是否不确定 |
| fallback_used | INTEGER | 是否使用了 fallback |
| elapsed_ms | INTEGER | 耗时（毫秒） |
| created_at | TEXT | 创建时间 |
| completed_at | TEXT | 完成时间 |
| confirmed_status | TEXT | 人工确认状态 |
| confirm_note | TEXT | 确认备注 |
| confirmed_at | TEXT | 确认时间 |

## 二、查询接口

### 2.1 基础查询

```python
from platform_adapter.invocation_ledger import (
    query_by_task_id,
    query_by_capability,
    query_by_status,
    get_invocation_by_id,
    get_invocation_by_idempotency_key,
)
```

**按 task_id 查询**:
```python
records = query_by_task_id("task_123")
```

**按 capability 查询**:
```python
records = query_by_capability("MESSAGE_SENDING")
```

**按状态查询**:
```python
records = query_by_status("timeout")
```

**按 ID 查询**:
```python
record = get_invocation_by_id(1)
```

**按幂等键查询**:
```python
record = get_invocation_by_idempotency_key("MESSAGE_SENDING:abc123...")
```

### 2.2 导出接口

```python
from platform_adapter.invocation_ledger import (
    export_recent,
    export_failed_report,
    export_timeout_report,
    export_uncertain_report,
)
```

**导出最近 N 条**:
```python
records = export_recent(100)
```

**导出 failed 报告**:
```python
records = export_failed_report(100)
```

**导出 timeout 报告**:
```python
records = export_timeout_report(100)
```

**导出 uncertain 报告**:
```python
records = export_uncertain_report(100)
```

### 2.3 统计接口

```python
from platform_adapter.invocation_ledger import get_statistics

stats = get_statistics()
# {
#     "total": 1000,
#     "by_status": {"completed": 900, "failed": 50, "timeout": 50},
#     "uncertain_count": 50,
#     "confirmed_count": 30,
# }
```

## 三、人工确认机制

### 3.1 确认状态

| 状态 | 说明 |
|------|------|
| confirmed_success | 确认成功 |
| confirmed_failed | 确认失败 |
| confirmed_duplicate | 确认为重复 |

### 3.2 确认接口

```python
from platform_adapter.invocation_ledger import confirm_invocation

# 确认成功
confirm_invocation(
    record_id=1,
    confirmed_status="confirmed_success",
    confirm_note="用户确认短信已收到"
)

# 确认失败
confirm_invocation(
    record_id=2,
    confirmed_status="confirmed_failed",
    confirm_note="用户确认未收到短信"
)

# 确认为重复
confirm_invocation(
    record_id=3,
    confirmed_status="confirmed_duplicate",
    confirm_note="与记录 #1 重复"
)
```

### 3.3 确认流程

1. 查询 result_uncertain=1 的记录
2. 人工核实实际结果
3. 调用 confirm_invocation() 记录确认结果
4. 系统不再自动重试

## 四、清理策略

### 4.1 保留策略

| 状态 | 保留天数 | 说明 |
|------|----------|------|
| completed | 30 天 | 成功记录保留 30 天 |
| failed | 90 天 | 失败记录保留 90 天 |
| timeout | 90 天 | 超时记录保留 90 天 |
| result_uncertain | 永久 | 不确定记录永久保留 |

### 4.2 清理接口

```python
from platform_adapter.invocation_ledger import cleanup_old_records

# 清理 30 天前的记录（保留 failed 和 uncertain）
deleted = cleanup_old_records(
    days_to_keep=30,
    keep_failed=True,
    keep_uncertain=True,
)
```

### 4.3 清理脚本

**位置**: `scripts/cleanup_invocations.py`

```python
#!/usr/bin/env python
"""清理旧的审计记录"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from platform_adapter.invocation_ledger import cleanup_old_records

if __name__ == "__main__":
    deleted = cleanup_old_records(
        days_to_keep=30,
        keep_failed=True,
        keep_uncertain=True,
    )
    print(f"已清理 {deleted} 条记录")
```

## 五、审计报告示例

### 5.1 每日统计

```
日期: 2026-04-24
总调用: 1000
成功: 900 (90%)
失败: 50 (5%)
超时: 50 (5%)
不确定: 50 (5%)
已确认: 30 (60%)
```

### 5.2 按 capability 统计

```
MESSAGE_SENDING: 500 次
  - 成功: 450 (90%)
  - 失败: 25 (5%)
  - 超时: 25 (5%)

TASK_SCHEDULING: 300 次
  - 成功: 280 (93%)
  - 失败: 10 (3%)
  - 超时: 10 (3%)

NOTIFICATION: 200 次
  - 成功: 170 (85%)
  - 失败: 15 (7%)
  - 超时: 15 (7%)
```

## 六、最佳实践

### 6.1 查询最佳实践

1. 使用 task_id 追踪单个任务的完整调用链
2. 使用 capability 分析特定能力的稳定性
3. 使用 normalized_status 筛选异常情况
4. 使用 idempotency_key 检查重复调用

### 6.2 确认最佳实践

1. 每日检查 uncertain 记录
2. 及时确认并记录结果
3. 对于重复调用，标记为 confirmed_duplicate
4. 对于失败调用，记录失败原因

### 6.3 清理最佳实践

1. 定期执行清理脚本
2. 保留 failed 和 uncertain 记录用于分析
3. 导出重要记录后再清理
