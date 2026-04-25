# 平台调用审计记录保留策略

## 版本
- V8.4.0 平台稳定性硬化版
- 日期: 2026-04-24

## 一、保留策略总览

| 状态 | 保留期限 | 说明 |
|------|----------|------|
| completed | 30 天 | 成功记录，用于短期审计 |
| failed | 90 天 | 失败记录，用于问题分析 |
| timeout | 90 天 | 超时记录，用于性能分析 |
| result_uncertain | 永久 | 不确定记录，需要人工确认 |
| confirmed_* | 永久 | 已确认记录，用于审计追溯 |

## 二、分层保留详解

### 2.1 Completed 记录

**保留期限**: 30 天

**理由**:
- 成功记录主要用于短期审计
- 数量大，长期保留占用存储
- 30 天足够覆盖月度报表需求

**清理条件**:
```python
# 清理 30 天前的 completed 记录
cleanup_old_records(
    days_to_keep=30,
    keep_failed=True,
    keep_uncertain=True,
)
```

### 2.2 Failed 记录

**保留期限**: 90 天

**理由**:
- 失败记录用于问题分析
- 可能需要追溯历史问题
- 90 天覆盖季度分析需求

**清理条件**:
```python
# Failed 记录不会被自动清理
# 需要单独清理时使用
cleanup_old_records(
    days_to_keep=90,
    keep_failed=False,  # 允许清理 failed
    keep_uncertain=True,
)
```

### 2.3 Timeout 记录

**保留期限**: 90 天

**理由**:
- 超时记录用于性能分析
- 可能指示平台问题
- 与 failed 同等重要性

### 2.4 Result Uncertain 记录

**保留期限**: 永久

**理由**:
- 需要人工确认
- 可能涉及用户投诉
- 审计追溯的重要依据

**例外**: 确认后可按 confirmed_* 策略处理

### 2.5 Confirmed 记录

**保留期限**: 永久

**理由**:
- 已人工确认的结果
- 审计追溯的重要依据
- 数量相对较少

## 三、清理机制

### 3.1 自动清理

**频率**: 每日凌晨 2:00

**脚本**: `scripts/cleanup_invocations.py`

```python
#!/usr/bin/env python
"""清理旧的审计记录"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from platform_adapter.invocation_ledger import cleanup_old_records

if __name__ == "__main__":
    # 清理 30 天前的 completed 记录
    deleted = cleanup_old_records(
        days_to_keep=30,
        keep_failed=True,
        keep_uncertain=True,
    )
    print(f"[{datetime.now()}] 已清理 {deleted} 条记录")
```

### 3.2 手动清理

**命令**:
```bash
# 清理 30 天前的记录（保留 failed 和 uncertain）
python scripts/cleanup_invocations.py

# 清理 90 天前的所有记录（包括 failed）
python -c "
from platform_adapter.invocation_ledger import cleanup_old_records
deleted = cleanup_old_records(days_to_keep=90, keep_failed=False, keep_uncertain=True)
print(f'已清理 {deleted} 条记录')
"
```

### 3.3 清理前备份

**建议**: 清理前导出重要记录

```python
from platform_adapter.invocation_ledger import export_recent, export_failed_report
import json

# 导出最近 1000 条记录
records = export_recent(1000)
with open("invocations_backup.json", "w") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
```

## 四、存储估算

### 4.1 单条记录大小

- 平均大小: ~1 KB
- 包含 request_json 和 raw_result_json

### 4.2 存储增长

假设每日调用 1000 次：

| 状态 | 每日新增 | 保留天数 | 稳定存储 |
|------|----------|----------|----------|
| completed | 900 | 30 | 27 MB |
| failed | 50 | 90 | 4.5 MB |
| timeout | 50 | 90 | 4.5 MB |
| uncertain | 10 | 永久 | 持续增长 |

**总计**: ~36 MB + uncertain 增长

### 4.3 存储优化

1. 定期清理 completed 记录
2. 压缩旧记录
3. 归档到冷存储

## 五、合规要求

### 5.1 审计要求

- 保留至少 90 天的操作记录
- 失败和异常记录保留更长时间
- 支持按需导出

### 5.2 隐私要求

- 清理时同步清理敏感信息
- 导出时脱敏处理
- 符合数据保留政策

## 六、监控告警

### 6.1 存储告警

```python
# 当 uncertain 记录超过 10000 条时告警
stats = get_statistics()
if stats["uncertain_count"] > 10000:
    print("WARNING: uncertain 记录过多，请及时确认")
```

### 6.2 清理告警

```python
# 当清理失败时告警
try:
    deleted = cleanup_old_records(days_to_keep=30)
except Exception as e:
    print(f"ERROR: 清理失败 - {e}")
```

## 七、最佳实践

### 7.1 定期检查

- 每周检查 uncertain 记录数量
- 每月检查存储使用情况
- 每季度评估保留策略

### 7.2 及时确认

- 每日处理 uncertain 记录
- 及时更新确认状态
- 保持确认率 > 80%

### 7.3 备份策略

- 清理前备份重要记录
- 定期导出统计报告
- 保留年度汇总数据
