# 小艺真实集成计划

## 版本
- V8.3.0 平台执行语义版
- 更新日期: 2026-04-24

## 一、小艺官方可用接入点

### 1.1 接入方式
**SDK / 系统接口 / 插件接口 / 技能能力接口**

小艺平台使用 **技能能力接口** 方式接入，通过 `call_device_tool` 调用设备端能力。

### 1.2 官方接入入口名称

| 入口 | 类型 | 说明 |
|------|------|------|
| `call_device_tool` | 工具调用 | 调用设备端能力的统一入口 |
| `get_contact_tool_schema` | Schema 获取 | 获取通讯录相关工具定义 |
| `get_note_tool_schema` | Schema 获取 | 获取备忘录相关工具定义 |
| `get_calendar_tool_schema` | Schema 获取 | 获取日程相关工具定义 |

### 1.3 当前项目对接文件位置

| 文件 | 职责 |
|------|------|
| `platform_adapter/xiaoyi_adapter.py` | 小艺平台适配器主文件 |
| `infrastructure/tool_adapters/message_adapter.py` | 消息发送适配器 |
| `skills/today-task/scripts/task_push.py` | 负一屏推送实现 |

## 二、真实能力链路规划

### 2.1 MESSAGE_SENDING (首选)

**接入点**: `call_device_tool` + `send_message`

**调用链路**:
```
xiaoyi_adapter.invoke(MESSAGE_SENDING)
  → call_device_tool("send_message", {phoneNumber, content})
    → 设备端短信发送
      → 返回结果
```

**预期结果**:
- 成功: `{success: true, status: "success"}`
- 失败: `{success: false, error: "..."}`

### 2.2 TASK_SCHEDULING

**接入点**: `call_device_tool` + `create_calendar_event`

**调用链路**:
```
xiaoyi_adapter.invoke(TASK_SCHEDULING)
  → call_device_tool("create_calendar_event", {title, dtStart, dtEnd})
    → 设备端日程创建
      → 返回结果
```

### 2.3 NOTIFICATION

**接入点**: `today-task` 技能 + 负一屏推送

**调用链路**:
```
xiaoyi_adapter.invoke(NOTIFICATION)
  → today-task/scripts/task_push.py
    → hiboard_url + auth_code
      → 负一屏推送
        → 返回结果
```

## 三、实现步骤

### 3.1 第一阶段：MESSAGE_SENDING 真实接线

1. 修改 `xiaoyi_adapter.py`
   - 导入 `call_device_tool`
   - 实现 `_invoke_message_sending()` 方法
   - 设置 `MESSAGE_SENDING.available = True`

2. 处理返回结果
   - 区分 accepted / queued_for_delivery / completed / failed
   - 短信发送通常是同步完成，返回 success 或 failed

3. 确认级别
   - 短信发送是同步操作
   - 返回 success = completed
   - 返回 failed = failed
   - 确认级别: Level 2 (投递确认)

### 3.2 第二阶段：TASK_SCHEDULING 真实接线

1. 实现 `_invoke_task_scheduling()` 方法
2. 设置 `TASK_SCHEDULING.available = True`
3. 日程创建是同步操作，确认级别: Level 2

### 3.3 第三阶段：NOTIFICATION 真实接线

1. 实现 `_invoke_notification()` 方法
2. 集成 `today-task` 技能
3. 负一屏推送可能有延迟，确认级别: Level 3

## 四、测试策略

### 4.1 真实环境测试
- 在有小艺环境的设备上运行
- 调用真实 API
- 验证返回结果

### 4.2 模拟环境测试
- 在无小艺环境的设备上运行
- 使用 mock 数据
- 验证代码路径

### 4.3 条件跳过
- connected 测试在无环境时跳过
- 但代码路径必须存在

## 五、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 设备端工具不可用 | 无法真实调用 | 返回 CAPABILITY_NOT_CONNECTED |
| 权限不足 | 调用失败 | 返回权限错误信息 |
| 网络问题 | 调用超时 | 设置超时，返回 TIMEOUT |

## 六、验收标准

| 标准 | 状态 |
|------|------|
| 至少 1 个 capability 进入 connected | 待验证 |
| 真实调用路径落地 | 待验证 |
| 返回结果语义正确 | 待验证 |
| 测试覆盖 | 待验证 |
