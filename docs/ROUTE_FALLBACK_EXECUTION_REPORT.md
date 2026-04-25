# ROUTE FALLBACK EXECUTION REPORT

## Fallback 测试结果

### 测试时间
2026-04-25 08:35

### 测试模式
- Dry-run: True
- Fake-device: True

## Fallback 执行详情

### 1. route.delete_note
- **Primary Route**: route.delete_note
- **Fallback Routes**: 
  - route.query_note
- **Fallback Tested**: ✅
- **Fallback Result**: Success

### 2. route.send_message
- **Primary Route**: route.send_message
- **Fallback Routes**:
  - route.query_message_status
  - route.list_recent_messages
- **Fallback Tested**: ✅
- **Fallback Result**: Success

### 3. route.create_alarm
- **Primary Route**: route.create_alarm
- **Fallback Routes**:
  - route.query_alarm
- **Fallback Tested**: ✅
- **Fallback Result**: Success

### 4. route.delete_alarm
- **Primary Route**: route.delete_alarm
- **Fallback Routes**:
  - route.query_alarm
- **Fallback Tested**: ✅
- **Fallback Result**: Success

### 5. route.make_call
- **Primary Route**: route.make_call
- **Fallback Routes**:
  - route.query_contact
- **Fallback Tested**: ✅
- **Fallback Result**: Success

## Fallback 映射表

| Primary Route | Fallback Routes | Error Type |
|---------------|-----------------|------------|
| route.delete_note | query_note | STORAGE_FAILED |
| route.send_message | query_message_status, list_recent_messages | MESSAGE_SENDING_FAILED |
| route.create_alarm | query_alarm | TASK_SCHEDULING_FAILED |
| route.delete_alarm | query_alarm | STORAGE_FAILED |
| route.make_call | query_contact, send_message | CALL_FAILED |

## 统计

- **Total Fallback Tests**: 5
- **Passed**: 5
- **Failed**: 0
- **Audit Written**: 5

## 结论

✅ Fallback 机制正常工作，所有 fallback route 都能正确执行并写入 audit。
