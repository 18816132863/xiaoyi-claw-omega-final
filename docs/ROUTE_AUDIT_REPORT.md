# ROUTE AUDIT REPORT

## 审计统计

### 总览
- **Total Records**: 20+
- **Time Range**: 2026-04-25 08:35

### 按状态分布

| Status | Count |
|--------|-------|
| dry_run | 19 |
| cancelled | 1 |

### 按风险等级分布

| Risk Level | Count |
|------------|-------|
| L0 | 10 |
| L2 | 2 |
| L3 | 6 |
| L4 | 2 |

### 按 Route 分布

| Route | Count |
|-------|-------|
| route.query_note | 1 |
| route.delete_note | 1 |
| route.send_message | 1 |
| route.create_alarm | 2 |
| route.query_alarm | 3 |
| route.delete_alarm | 2 |
| route.make_call | 2 |
| route.query_contact | 2 |
| route.get_location | 1 |
| route.query_message_status | 2 |
| route.list_recent_messages | 1 |
| route.bootstrap | 2 |

## 审计记录示例

### 成功执行 (L0)
```
audit_id: audit_a84346b8db89
route_id: route.query_message_status
capability: query_message_status
risk_level: L0
status: dry_run
duration_ms: 0
```

### 成功执行 (L3)
```
audit_id: audit_6e6bdcd3e3d1
route_id: route.delete_note
capability: delete_note
risk_level: L3
status: dry_run
duration_ms: 0
```

### L4 取消执行
```
audit_id: audit_d78efc00577b
route_id: route.bootstrap
capability: bootstrap
risk_level: L4
status: cancelled
error_code: strong_confirm_required
error_message: L4 route requires strong confirmation
```

## 审计字段说明

每条审计记录包含：
- `audit_id`: 唯一审计 ID
- `route_id`: 路由 ID
- `capability`: 能力名称
- `handler`: 处理器路径
- `risk_level`: 风险等级
- `policy`: 执行策略
- `params_redacted`: 脱敏后的参数
- `dry_run`: 是否 dry-run
- `status`: 执行状态
- `fallback_used`: 使用的 fallback route
- `started_at`: 开始时间
- `finished_at`: 结束时间
- `duration_ms`: 执行时长
- `error_code`: 错误码
- `error_message`: 错误信息

## 结论

✅ 审计系统正常工作，所有 route 执行都有完整的审计记录。
✅ L4 route 正确被取消，不会自动执行。
