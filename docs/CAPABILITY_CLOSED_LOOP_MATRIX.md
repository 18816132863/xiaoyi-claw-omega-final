# 能力闭环矩阵（完整版）

## 一、所有能力闭环状态

### 1. 短信 (MESSAGE_SENDING)

| 能力 | 文件 | 状态 |
|------|------|------|
| send_message | capabilities/send_message.py | ✅ 已有 |
| query_message_status | capabilities/query_message_status.py | ✅ 新增 |
| resend_message | capabilities/resend_message.py | ✅ 新增 |
| list_recent_messages | capabilities/list_recent_messages.py | ✅ 新增 |
| explain_message_result | capabilities/explain_message_result.py | ✅ 新增 |

---

### 2. 日历 (TASK_SCHEDULING)

| 能力 | 文件 | 状态 |
|------|------|------|
| schedule_task | capabilities/schedule_task.py | ✅ 已有 |
| query_calendar_event | capabilities/query_calendar_event.py | ✅ 新增 |
| update_calendar_event | capabilities/update_calendar_event.py | ✅ 新增 |
| delete_calendar_event | capabilities/delete_calendar_event.py | ✅ 新增 |
| list_calendar_events | capabilities/list_calendar_events.py | ✅ 新增 |
| check_calendar_conflicts | capabilities/check_calendar_conflicts.py | ✅ 新增 |

---

### 3. 备忘录 (STORAGE)

| 能力 | 文件 | 状态 |
|------|------|------|
| create_note | capabilities/create_note.py | ✅ 已有 |
| query_note | capabilities/query_note.py | ✅ 新增 |
| update_note | capabilities/update_note.py | ✅ 新增 |
| delete_note | capabilities/delete_note.py | ✅ 新增 |
| search_notes | capabilities/search_notes.py | ✅ 新增 |
| list_recent_notes | capabilities/list_recent_notes.py | ✅ 新增 |

---

### 4. 通知推送 (NOTIFICATION)

| 能力 | 文件 | 状态 |
|------|------|------|
| send_notification | capabilities/send_notification.py | ✅ 已有 |
| query_notification_status | capabilities/query_notification_status.py | ✅ 新增 |
| cancel_notification | capabilities/cancel_notification.py | ✅ 新增 |
| refresh_notification_auth | capabilities/refresh_notification_auth.py | ✅ 新增 |
| explain_notification_auth_state | capabilities/explain_notification_auth_state.py | ✅ 新增 |

---

### 5. 图库 (PHOTO)

| 能力 | 文件 | 状态 |
|------|------|------|
| query_photo | capabilities/query_photo.py | ✅ 新增 |
| list_photos | capabilities/query_photo.py | ✅ 新增 |
| search_photos | capabilities/query_photo.py | ✅ 新增 |
| delete_photo | capabilities/delete_photo.py | ✅ 新增 |
| create_album | capabilities/create_album.py | ✅ 新增 |

---

### 6. 联系人 (CONTACT)

| 能力 | 文件 | 状态 |
|------|------|------|
| query_contact | capabilities/query_contact.py | ✅ 新增 |
| list_contacts | capabilities/query_contact.py | ✅ 新增 |
| search_contacts | capabilities/query_contact.py | ✅ 新增 |
| create_contact | capabilities/create_contact.py | ✅ 新增 |
| update_contact | capabilities/update_contact.py | ✅ 新增 |
| delete_contact | capabilities/delete_contact.py | ✅ 新增 |

---

### 7. 文件管理 (FILE)

| 能力 | 文件 | 状态 |
|------|------|------|
| query_file | capabilities/query_file.py | ✅ 新增 |
| list_files | capabilities/query_file.py | ✅ 新增 |
| search_files | capabilities/query_file.py | ✅ 新增 |
| delete_file | capabilities/delete_file.py | ✅ 新增 |
| move_file | capabilities/manage_file.py | ✅ 新增 |
| copy_file | capabilities/manage_file.py | ✅ 新增 |
| rename_file | capabilities/manage_file.py | ✅ 新增 |

---

### 8. 闹钟 (ALARM)

| 能力 | 文件 | 状态 |
|------|------|------|
| query_alarm | capabilities/query_alarm.py | ✅ 新增 |
| list_alarms | capabilities/query_alarm.py | ✅ 新增 |
| create_alarm | capabilities/create_alarm.py | ✅ 新增 |
| update_alarm | capabilities/update_alarm.py | ✅ 新增 |
| delete_alarm | capabilities/delete_alarm.py | ✅ 新增 |

---

### 9. 电话 (PHONE)

| 能力 | 文件 | 状态 |
|------|------|------|
| make_call | capabilities/make_call.py | ✅ 新增 |
| end_call | capabilities/make_call.py | ✅ 新增 |
| get_call_history | capabilities/make_call.py | ✅ 新增 |

---

### 10. 定位服务 (LOCATION)

| 能力 | 文件 | 状态 |
|------|------|------|
| get_location | capabilities/get_location.py | ✅ 新增 |
| get_address_from_location | capabilities/get_location.py | ✅ 新增 |
| get_location_history | capabilities/get_location.py | ✅ 新增 |

---

### 11. 小艺帮记 (XIAOYI_NOTES)

| 能力 | 文件 | 状态 |
|------|------|------|
| query_xiaoyi_note | capabilities/query_xiaoyi_note.py | ✅ 新增 |
| list_xiaoyi_notes | capabilities/query_xiaoyi_note.py | ✅ 新增 |
| search_xiaoyi_notes | capabilities/query_xiaoyi_note.py | ✅ 新增 |
| delete_xiaoyi_note | capabilities/delete_xiaoyi_note.py | ✅ 新增 |

---

## 二、辅助能力

| 能力 | 文件 | 说明 |
|------|------|------|
| preview_side_effect | capabilities/preview_side_effect.py | 副作用预览 |
| approve_action | capabilities/approve_action.py | 审批动作 |
| confirm_invocation | capabilities/confirm_invocation.py | 确认调用记录 |

---

## 三、统计

| 类别 | 数量 |
|------|------|
| 能力类别 | 11 |
| 新增能力文件 | 32 |
| 辅助能力 | 3 |
| **总能力数** | **35** |

---

## 四、闭环特性

每个能力都支持：

| 特性 | 说明 |
|------|------|
| **查询** | 按ID/条件查询 |
| **列表** | 分页列出 |
| **搜索** | 关键词搜索 |
| **创建** | 新建记录 |
| **更新** | 修改记录 |
| **删除** | 删除记录 |
| **dry_run** | 预演模式 |
| **审计** | 操作记录 |
