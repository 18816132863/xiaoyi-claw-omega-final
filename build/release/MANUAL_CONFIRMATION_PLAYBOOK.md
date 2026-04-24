# 手动确认操作手册

## 版本
- V8.4.0 审计闭环版
- 日期: 2026-04-24

## 一、确认场景

### 1.1 何时需要手动确认

当平台调用返回 `timeout` 或 `result_uncertain` 时，系统无法确定操作是否已成功执行。此时需要人工介入确认实际结果。

### 1.2 确认状态

| 状态 | 说明 | 后续动作 |
|------|------|----------|
| confirmed_success | 确认操作已成功 | 无需额外动作 |
| confirmed_failed | 确认操作失败 | 可考虑手动重试 |
| confirmed_duplicate | 确认为重复操作 | 标记关联记录 |

## 二、确认流程

### 2.1 标准流程

```
1. 查询 uncertain 记录
   ↓
2. 检查实际结果
   ↓
3. 确认状态
   ↓
4. 记录备注
   ↓
5. 完成闭环
```

### 2.2 CLI 操作

```bash
# 1. 查询 uncertain 记录
python scripts/invocation_audit_cli.py query-uncertain --format table

# 2. 查看详情
python scripts/invocation_audit_cli.py query-uncertain --format json | jq '.[] | select(.id==123)'

# 3. 确认
python scripts/invocation_audit_cli.py confirm --id 123 --status confirmed_success --note "用户确认短信已收到"
```

### 2.3 程序化操作

```python
from capabilities.confirm_invocation import ConfirmInvocation

# 确认成功
ConfirmInvocation.confirm_success(
    record_id=123,
    note="用户确认短信已收到，时间 2026-04-24 14:00"
)

# 确认失败
ConfirmInvocation.confirm_failed(
    record_id=124,
    note="用户确认未收到短信，需要手动重发"
)

# 确认重复
ConfirmInvocation.confirm_duplicate(
    record_id=125,
    note="与记录 #120 重复，可能是网络延迟"
)
```

## 三、场景指南

### 3.1 短信发送超时

**场景**: 用户发送短信，系统返回超时

**确认步骤**:
1. 询问用户是否收到短信
2. 如果收到，确认 `confirmed_success`
3. 如果未收到，确认 `confirmed_failed`
4. 如果重复收到，确认 `confirmed_duplicate`

**示例对话**:
```
用户: 短信发出去了吗？
助手: 短信发送请求超时，当前无法确认是否已发送。请问您收到短信了吗？

用户: 收到了
助手: 好的，我记录一下确认结果。
[调用 confirm_success]

用户: 没收到
助手: 好的，我记录一下，稍后为您重发。
[调用 confirm_failed]
```

### 3.2 日程创建超时

**场景**: 创建日程，系统返回超时

**确认步骤**:
1. 请用户检查日历
2. 如果有该日程，确认 `confirmed_success`
3. 如果没有，确认 `confirmed_failed`
4. 如果有多个相同日程，确认 `confirmed_duplicate`

### 3.3 备忘录保存超时

**场景**: 保存备忘录，系统返回超时

**确认步骤**:
1. 请用户检查备忘录列表
2. 根据实际结果确认

### 3.4 通知推送超时

**场景**: 推送通知到负一屏，系统返回超时

**确认步骤**:
1. 请用户检查负一屏
2. 根据实际结果确认

## 四、确认统计

### 4.1 查看统计

```bash
python scripts/invocation_audit_cli.py stats
```

### 4.2 程序化获取

```python
from capabilities.confirm_invocation import ConfirmInvocation

stats = ConfirmInvocation.get_confirmation_stats()
print(f"确认率: {stats['confirmation_rate']:.1f}%")
print(f"待确认: {stats['unconfirmed_count']}")
```

## 五、最佳实践

### 5.1 及时确认

- 每日检查 uncertain 记录
- 及时跟进用户确认
- 保持确认率 > 80%

### 5.2 详细备注

确认时记录详细信息：
- 确认时间
- 确认人
- 确认依据
- 后续动作

**示例**:
```python
ConfirmInvocation.confirm_success(
    record_id=123,
    note="""
    确认时间: 2026-04-24 14:00
    确认人: 用户本人
    确认依据: 用户口头确认收到短信
    后续动作: 无
    """
)
```

### 5.3 关联记录

对于重复操作，记录关联的记录 ID：

```python
ConfirmInvocation.confirm_duplicate(
    record_id=125,
    note="与记录 #120 重复，可能是网络延迟导致的重复提交"
)
```

## 六、常见问题

### Q1: 如何批量确认？

```python
from capabilities.audit_queries import AuditQueries
from capabilities.confirm_invocation import ConfirmInvocation

# 获取未确认的 uncertain 记录
records = AuditQueries.get_unconfirmed_uncertain()

# 批量确认
for record in records:
    # 根据实际情况确认
    ConfirmInvocation.confirm_success(record["id"], "批量确认")
```

### Q2: 如何撤销确认？

目前不支持撤销确认。如需修改，请直接更新数据库。

### Q3: 确认后还能重试吗？

确认后不会自动重试。如需重试，请手动发起新请求。

## 七、监控告警

### 7.1 未确认记录过多

当未确认 uncertain 记录超过 10 条时，健康巡检会发出警告。

### 7.2 确认率过低

当确认率低于 80% 时，应加强确认流程。
