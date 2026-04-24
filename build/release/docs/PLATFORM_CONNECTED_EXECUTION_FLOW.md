# 平台连接执行流程

## 版本
- V8.3.0 平台执行语义版
- 更新日期: 2026-04-24

## 一、执行流程总览

```
用户请求
    │
    ▼
PlatformAdapter.invoke()
    │
    ├── 检查能力是否可用
    │   └── 不可用 → 返回 CAPABILITY_NOT_CONNECTED
    │
    ▼
调用具体能力实现
    │
    ├── MESSAGE_SENDING → _invoke_message_sending()
    │   ├── call_device_tool("send_message")
    │   │   ├── 成功 → {status: "success"}
    │   │   └── 失败 → {status: "failed"}
    │   └── Fallback → MessageAdapter (queued_for_delivery)
    │
    ├── TASK_SCHEDULING → _invoke_task_scheduling()
    │   └── call_device_tool("create_calendar_event")
    │
    └── NOTIFICATION → _invoke_notification()
        └── today-task 技能
```

## 二、MESSAGE_SENDING 执行流程

### 2.1 正常流程 (connected)

```
invoke(MESSAGE_SENDING, {phone_number, message})
    │
    ▼
_invoke_message_sending()
    │
    ▼
call_device_tool("send_message", {phoneNumber, content})
    │
    ├── 成功
    │   └── 返回 {success: true, status: "success"}
    │       → completed
    │
    └── 失败
        └── 返回 {success: false, status: "failed", error: "..."}
            → failed
```

### 2.2 Fallback 流程 (probe_only / mock)

```
invoke(MESSAGE_SENDING, {phone_number, message})
    │
    ▼
_invoke_message_sending()
    │
    ▼
call_device_tool 不可用 (ImportError)
    │
    ▼
_fallback_message_sending()
    │
    ▼
MessageAdapter.send_message()
    │
    └── 返回 {success: true, status: "queued_for_delivery"}
        → queued (等待真实网关处理)
```

## 三、TASK_SCHEDULING 执行流程

### 3.1 正常流程 (connected)

```
invoke(TASK_SCHEDULING, {title, start_time, end_time})
    │
    ▼
_invoke_task_scheduling()
    │
    ▼
call_device_tool("create_calendar_event", {title, dtStart, dtEnd})
    │
    ├── 成功
    │   └── 返回 {success: true, status: "success"}
    │       → completed
    │
    └── 失败
        └── 返回 {success: false, status: "failed", error: "..."}
            → failed
```

## 四、NOTIFICATION 执行流程

### 4.1 正常流程 (connected)

```
invoke(NOTIFICATION, {title, content, result})
    │
    ▼
_invoke_notification()
    │
    ▼
today-task/scripts/task_push.py
    │
    ├── 成功
    │   └── 返回 {success: true, status: "success"}
    │       → completed
    │
    └── 失败
        └── 返回 {success: false, status: "failed", error: "..."}
            → failed
```

## 五、状态转换矩阵

| 平台状态 | 调用结果 | 返回状态 | 语义层级 |
|----------|----------|----------|----------|
| connected | 成功 | success | completed |
| connected | 失败 | failed | failed |
| probe_only | fallback | queued_for_delivery | queued |
| mock | fallback | queued_for_delivery | queued |

## 六、错误处理

### 6.1 错误码定义

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| UNKNOWN_CAPABILITY | 未知能力 | 返回错误 |
| CAPABILITY_NOT_CONNECTED | 能力未接通 | 返回错误 + fallback_available |
| TOOL_NOT_AVAILABLE | 工具不可用 | 使用 fallback |
| PLATFORM_ERROR | 平台错误 | 返回错误 |
| INVOKE_ERROR | 调用错误 | 返回错误 |
| SKILL_NOT_FOUND | 技能未找到 | 返回错误 |
| SKILL_ERROR | 技能执行错误 | 返回错误 |

### 6.2 错误处理流程

```
调用失败
    │
    ├── CAPABILITY_NOT_CONNECTED
    │   └── 检查 fallback_available
    │       ├── true → 使用 fallback
    │       └── false → 返回错误
    │
    ├── TOOL_NOT_AVAILABLE
    │   └── 使用 fallback
    │
    └── 其他错误
        └── 返回错误信息
```

## 七、确认级别

### 7.1 MESSAGE_SENDING

| 场景 | 确认级别 | 说明 |
|------|----------|------|
| call_device_tool 成功 | Level 2 | 短信已发送到运营商 |
| call_device_tool 失败 | - | 发送失败 |
| fallback | Level 3 | 已入队，无确认 |

### 7.2 TASK_SCHEDULING

| 场景 | 确认级别 | 说明 |
|------|----------|------|
| call_device_tool 成功 | Level 2 | 日程已创建 |
| call_device_tool 失败 | - | 创建失败 |

### 7.3 NOTIFICATION

| 场景 | 确认级别 | 说明 |
|------|----------|------|
| today-task 成功 | Level 3 | 已推送，无确认 |
| today-task 失败 | - | 推送失败 |

## 八、测试覆盖

| 测试 | 文件 |
|------|------|
| connected 路径 | test_xiaoyi_adapter_connected_path.py |
| MESSAGE_SENDING 真实调用 | test_message_sending_real_platform_path.py |
| Fallback 路径 | test_xiaoyi_adapter_connected_path.py |
