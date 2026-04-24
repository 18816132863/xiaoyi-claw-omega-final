# Result Uncertain 处理机制

## 版本
- V8.4.0 平台稳定性硬化版
- 日期: 2026-04-24

## 一、什么是 Result Uncertain

**定义**: 当平台调用超时或返回未知格式时，系统无法确定操作是否已成功执行。

**关键原则**: 
- **不自动重试** - 避免产生重复副作用
- **需要人工确认** - 由用户或管理员确认实际结果
- **记录审计轨迹** - 完整记录调用过程和确认结果

## 二、触发条件

### 2.1 超时触发

```python
# 当调用超过 timeout_seconds 时
result = await guarded_platform_call(
    capability="MESSAGE_SENDING",
    op_name="send_message",
    call_coro=_call(),
    timeout_seconds=60,  # 超过 60 秒
)
# result.normalized_status = "timeout"
# result.result_uncertain = True
```

### 2.2 未知格式触发

```python
# 当平台返回无法识别的格式时
raw_result = "unknown response"
normalized = normalize_result(raw_result, "TEST", "test")
# normalized.status = "result_uncertain"
# normalized.result_uncertain = True
```

## 三、处理流程

### 3.1 自动处理

```
平台调用
    ↓
超时/未知格式
    ↓
标记 result_uncertain = True
    ↓
记录审计台账
    ↓
返回用户消息: "结果未知，为避免重复操作，系统未自动重试，请人工确认"
    ↓
不自动重试
```

### 3.2 人工确认流程

```
查询 uncertain 记录
    ↓
人工核实实际结果
    ↓
调用 confirm_invocation()
    ↓
记录确认状态和备注
    ↓
完成闭环
```

## 四、确认状态

| 状态 | 说明 | 后续动作 |
|------|------|----------|
| confirmed_success | 确认操作已成功 | 无需额外动作 |
| confirmed_failed | 确认操作失败 | 可考虑手动重试 |
| confirmed_duplicate | 确认为重复操作 | 标记关联记录 |

## 五、代码示例

### 5.1 查询 uncertain 记录

```python
from platform_adapter.invocation_ledger import export_uncertain_report

# 获取所有 uncertain 记录
uncertain_records = export_uncertain_report(limit=100)

for record in uncertain_records:
    print(f"ID: {record['id']}")
    print(f"能力: {record['capability']}")
    print(f"操作: {record['platform_op']}")
    print(f"时间: {record['created_at']}")
    print(f"请求: {record['request_json']}")
    print("---")
```

### 5.2 确认记录

```python
from platform_adapter.invocation_ledger import confirm_invocation

# 确认成功（用户确认短信已收到）
confirm_invocation(
    record_id=123,
    confirmed_status="confirmed_success",
    confirm_note="用户确认短信已收到，时间 2026-04-24 14:00"
)

# 确认失败（用户确认未收到）
confirm_invocation(
    record_id=124,
    confirmed_status="confirmed_failed",
    confirm_note="用户确认未收到短信，需要手动重发"
)

# 确认重复（与另一条记录重复）
confirm_invocation(
    record_id=125,
    confirmed_status="confirmed_duplicate",
    confirm_note="与记录 #120 重复，可能是网络延迟导致的重复提交"
)
```

### 5.3 检查是否已确认

```python
from platform_adapter.invocation_ledger import get_invocation_by_id

record = get_invocation_by_id(123)

if record.get("confirmed_status"):
    print(f"已确认: {record['confirmed_status']}")
    print(f"确认时间: {record['confirmed_at']}")
    print(f"确认备注: {record['confirm_note']}")
else:
    print("尚未确认")
```

## 六、用户沟通

### 6.1 用户消息

当发生 uncertain 时，用户看到的消息：

> "结果未知，为避免重复操作，系统未自动重试，请人工确认"

### 6.2 后续沟通

**场景 1: 短信发送超时**

用户: "短信发出去了吗？"

助手: "短信发送请求超时，当前无法确认是否已发送。为避免重复发送，系统未自动重试。请您检查是否收到短信，如果未收到，我可以手动重发。"

**场景 2: 日程创建超时**

用户: "日程创建成功了吗？"

助手: "日程创建请求超时，当前无法确认是否已创建。为避免重复创建，系统未自动重试。请您检查日历，如果没有该日程，我可以重新创建。"

## 七、统计与分析

### 7.1 Uncertain 统计

```python
from platform_adapter.invocation_ledger import get_statistics

stats = get_statistics()
print(f"Uncertain 记录数: {stats['uncertain_count']}")
print(f"已确认数: {stats['confirmed_count']}")
print(f"待确认数: {stats['uncertain_count'] - stats['confirmed_count']}")
```

### 7.2 确认率分析

```
Uncertain 记录: 100
已确认: 80
  - confirmed_success: 60 (75%)
  - confirmed_failed: 15 (19%)
  - confirmed_duplicate: 5 (6%)
待确认: 20
```

## 八、最佳实践

### 8.1 开发者

1. 所有副作用操作必须设置 `side_effecting=True`
2. 超时后不要自动重试
3. 记录完整的请求和响应
4. 提供清晰的用户消息

### 8.2 运维人员

1. 每日检查 uncertain 记录
2. 及时跟进用户确认
3. 分析 uncertain 原因
4. 优化超时时间配置

### 8.3 用户

1. 收到 uncertain 消息后检查实际结果
2. 告知助手实际结果
3. 不要重复提交相同请求
