# 安全控制

## 一、控制项列表

### 1.1 dry_run

**级别**: ENFORCE

**说明**: 副作用操作必须支持 dry_run 模式

**适用能力**:
- send_message
- schedule_task
- create_note
- send_notification
- update_calendar_event
- delete_calendar_event
- update_note
- delete_note
- cancel_notification

---

### 1.2 approval_required

**级别**: ENFORCE

**说明**: 批量操作需要审批

**触发条件**:

| 操作类型 | 阈值 | 说明 |
|----------|------|------|
| batch_sms | 5 条 | 批量短信超过 5 条需要审批 |
| batch_notification | 10 条 | 批量通知超过 10 条需要审批 |
| batch_calendar | 10 条 | 批量日程创建超过 10 条需要审批 |
| delete_all | 1 条 | 批量删除需要审批 |

---

### 1.3 max_batch_size

**级别**: ENFORCE

**阈值**: 20

**说明**: 批次大小不能超过 20

---

### 1.4 rate_limit

**级别**: ENFORCE

**限流配置**:

| 能力 | 每分钟限制 | 每小时限制 |
|------|-----------|-----------|
| send_message | 10 | 100 |
| send_notification | 20 | 200 |
| schedule_task | 30 | 300 |
| create_note | 30 | 300 |

---

### 1.5 safe_mode

**级别**: WARN

**说明**: 安全模式已启用

---

### 1.6 side_effect_preview

**级别**: ENFORCE

**说明**: 副作用操作必须可预览

---

### 1.7 idempotency_scope

**级别**: ENFORCE

**说明**: 幂等键必须在正确的作用域内

---

## 二、安全控制 API

### 2.1 检查审批需求

```python
from config.safety_controls import check_approval_required

result = check_approval_required("batch_sms", 10)
# {"approval_required": True, "threshold": 5, ...}
```

### 2.2 检查批次大小

```python
from config.safety_controls import check_batch_size

result = check_batch_size("batch_sms", 30)
# {"allowed": False, "max_batch_size": 20, ...}
```

### 2.3 检查限流

```python
from config.safety_controls import check_rate_limit

result = check_rate_limit("send_message", 15, "per_minute")
# {"allowed": False, "limit": 10, ...}
```

### 2.4 验证安全控制

```python
from config.safety_controls import validate_safety_controls

result = validate_safety_controls("send_message", {"to": "...", "message": "..."}, dry_run=False)
# {"valid": True, "violations": None, "warnings": [...]}
```

---

## 三、审批流程

### 3.1 请求审批

```python
from capabilities.approve_action import request_approval

result = request_approval(
    action_type="batch_sms",
    action_params={"count": 10},
    reason="批量发送短信"
)
# {"approval_id": "approval_xxx", "status": "pending", ...}
```

### 3.2 批准操作

```python
from capabilities.approve_action import approve_action

result = approve_action(
    approval_id="approval_xxx",
    approved_by="admin"
)
# {"status": "approved", ...}
```

### 3.3 拒绝操作

```python
from capabilities.approve_action import reject_action

result = reject_action(
    approval_id="approval_xxx",
    rejected_by="admin",
    reason="不允许批量发送"
)
# {"status": "rejected", ...}
```

---

## 四、副作用预览

### 4.1 单个预览

```python
from capabilities.preview_side_effect import preview_side_effect

result = preview_side_effect(
    capability="send_message",
    params={"to": "13800138000", "message": "测试"}
)
# {"is_side_effect": True, "estimated_effects": [...], "warnings": [...]}
```

### 4.2 批量预览

```python
from capabilities.preview_side_effect import batch_preview

result = batch_preview([
    {"capability": "send_message", "params": {...}},
    {"capability": "schedule_task", "params": {...}}
])
# {"total_actions": 2, "side_effect_count": 2, ...}
```

---

## 五、配置文件

**位置**: `config/safety_controls.py`

**可配置项**:
- DEFAULT_CONTROLS: 默认控制配置
- APPROVAL_REQUIRED_ACTIONS: 需要审批的操作
- RATE_LIMITS: 限流配置
