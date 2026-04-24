# 小艺 API 接线点

## 版本
- V8.3.0 平台执行语义版
- 更新日期: 2026-04-24

## 一、API 接线点总览

| API 名称 | 接入方式 | 工具名称 | 能力类型 |
|----------|----------|----------|----------|
| 发送短信 | call_device_tool | send_message | MESSAGE_SENDING |
| 创建日程 | call_device_tool | create_calendar_event | TASK_SCHEDULING |
| 创建备忘录 | call_device_tool | create_note | STORAGE |
| 拨打电话 | call_device_tool | call_phone | COMMUNICATION |
| 负一屏推送 | HTTP API | today-task | NOTIFICATION |

## 二、MESSAGE_SENDING 接线点

### 2.1 工具定义

```json
{
  "name": "send_message",
  "description": "通过手机发送短信",
  "parameters": {
    "phoneNumber": "接收方手机号码（会自动添加+86前缀）",
    "content": "短信内容"
  },
  "required": ["phoneNumber", "content"]
}
```

### 2.2 调用方式

```python
# 在 xiaoyi_adapter.py 中
from tools import call_device_tool

async def _invoke_message_sending(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """调用短信发送"""
    result = await call_device_tool(
        toolName="send_message",
        arguments={
            "phoneNumber": params.get("phone_number"),
            "content": params.get("message")
        }
    )
    return result
```

### 2.3 返回结果

| 场景 | 返回值 | 语义 |
|------|--------|------|
| 成功 | `{success: true}` | completed |
| 权限不足 | `{error: "没有授权"}` | failed |
| 参数错误 | `{error: "参数缺失"}` | failed |
| 超时 | `{error: "timeout"}` | failed |

### 2.4 对接文件位置

```
platform_adapter/xiaoyi_adapter.py
  └── invoke() 方法
       └── case MESSAGE_SENDING:
            └── _invoke_message_sending()
                 └── call_device_tool("send_message", ...)
```

## 三、TASK_SCHEDULING 接线点

### 3.1 工具定义

```json
{
  "name": "create_calendar_event",
  "description": "在用户设备上创建日程",
  "parameters": {
    "title": "日程标题",
    "dtStart": "开始时间 (yyyy-mm-dd hh:mm:ss)",
    "dtEnd": "结束时间 (yyyy-mm-dd hh:mm:ss)"
  },
  "required": ["title", "dtStart", "dtEnd"]
}
```

### 3.2 调用方式

```python
async def _invoke_task_scheduling(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """调用日程创建"""
    result = await call_device_tool(
        toolName="create_calendar_event",
        arguments={
            "title": params.get("title"),
            "dtStart": params.get("start_time"),
            "dtEnd": params.get("end_time")
        }
    )
    return result
```

### 3.3 对接文件位置

```
platform_adapter/xiaoyi_adapter.py
  └── invoke() 方法
       └── case TASK_SCHEDULING:
            └── _invoke_task_scheduling()
                 └── call_device_tool("create_calendar_event", ...)
```

## 四、NOTIFICATION 接线点

### 4.1 API 定义

```json
{
  "endpoint": "hiboard_url",
  "method": "POST",
  "headers": {
    "Authorization": "auth_code"
  },
  "body": {
    "taskId": "任务ID",
    "taskName": "任务名称",
    "taskContent": "任务内容",
    "taskResult": "任务结果"
  }
}
```

### 4.2 调用方式

```python
# 使用 today-task 技能
import subprocess

async def _invoke_notification(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """调用负一屏推送"""
    # 创建任务 JSON
    task_data = {
        "task_name": params.get("title"),
        "task_content": params.get("content"),
        "task_result": params.get("result", "已完成")
    }
    
    # 调用 today-task 技能
    result = subprocess.run([
        "python",
        "skills/today-task/scripts/task_push.py",
        "--data", json.dumps(task_data)
    ], capture_output=True, text=True)
    
    return {"success": result.returncode == 0}
```

### 4.3 对接文件位置

```
platform_adapter/xiaoyi_adapter.py
  └── invoke() 方法
       └── case NOTIFICATION:
            └── _invoke_notification()
                 └── skills/today-task/scripts/task_push.py
```

## 五、STORAGE 接线点

### 5.1 工具定义

```json
{
  "name": "create_note",
  "description": "在用户设备上创建备忘录",
  "parameters": {
    "title": "备忘录标题",
    "content": "备忘录内容"
  },
  "required": ["title", "content"]
}
```

### 5.2 对接文件位置

```
platform_adapter/xiaoyi_adapter.py
  └── invoke() 方法
       └── case STORAGE:
            └── _invoke_storage()
                 └── call_device_tool("create_note", ...)
```

## 六、接线状态跟踪

| API | 定义 | 实现 | 测试 | 状态 |
|-----|------|------|------|------|
| send_message | ✅ | 待实现 | 待测试 | probe_only |
| create_calendar_event | ✅ | 待实现 | 待测试 | probe_only |
| create_note | ✅ | 待实现 | 待测试 | probe_only |
| call_phone | ✅ | 待实现 | 待测试 | probe_only |
| today-task | ✅ | ✅ | ✅ | connected |

## 七、下一步行动

1. 实现 `_invoke_message_sending()` 方法
2. 设置 `MESSAGE_SENDING.available = True`
3. 编写 connected 路径测试
4. 验证真实调用
