# 用户结果消息矩阵

## 版本
- V8.4.0 平台稳定性硬化版
- 日期: 2026-04-24

## 一、消息矩阵总览

| 状态 | 用户消息 | 是否成功 | 是否可重试 | 需要确认 |
|------|----------|----------|------------|----------|
| completed | 已完成 | ✅ | ❌ | ❌ |
| queued_for_delivery | 已提交，等待平台处理 | ⏳ | ❌ | ❌ |
| timeout | 请求超时，当前无法确认是否已执行，请稍后检查结果 | ❓ | ❌ | ✅ |
| result_uncertain | 结果未知，为避免重复操作，系统未自动重试，请人工确认 | ❓ | ❌ | ✅ |
| auth_required | 该能力未授权，请先完成授权后再试 | ❌ | ❌ | ❌ |
| fallback_used | 平台能力当前不可直接调用，已转入待处理队列 | ⏳ | ❌ | ❌ |
| failed | 操作失败，请稍后重试 | ❌ | ✅ | ❌ |

## 二、状态详解

### 2.1 completed

**含义**: 操作已成功完成

**用户消息**: "已完成"

**示例场景**:
- 短信发送成功
- 日程创建成功
- 备忘录保存成功
- 通知推送成功

**用户感知**:
```
助手: 短信发送: 已完成
```

### 2.2 queued_for_delivery

**含义**: 请求已提交，等待平台处理

**用户消息**: "已提交，等待平台处理"

**示例场景**:
- 平台能力暂时不可用，使用 fallback
- 请求已进入队列

**用户感知**:
```
助手: 短信发送: 已提交，等待平台处理
```

### 2.3 timeout

**含义**: 请求超时，无法确认结果

**用户消息**: "请求超时，当前无法确认是否已执行，请稍后检查结果"

**示例场景**:
- 网络延迟
- 平台响应慢
- 设备离线

**用户感知**:
```
助手: 短信发送: 请求超时，当前无法确认是否已执行，请稍后检查结果
```

**后续动作**:
- 用户检查实际结果
- 告知助手实际情况
- 助手记录确认状态

### 2.4 result_uncertain

**含义**: 结果未知，需要人工确认

**用户消息**: "结果未知，为避免重复操作，系统未自动重试，请人工确认"

**示例场景**:
- 平台返回未知格式
- 调用过程中断
- 无法解析响应

**用户感知**:
```
助手: 短信发送: 结果未知，为避免重复操作，系统未自动重试，请人工确认
```

**后续动作**:
- 用户检查实际结果
- 告知助手实际情况
- 助手记录确认状态

### 2.5 auth_required

**含义**: 能力未授权

**用户消息**: "该能力未授权，请先完成授权后再试"

**示例场景**:
- authCode 无效
- 权限未开启
- 授权过期

**用户感知**:
```
助手: 通知推送: 该能力未授权，请先完成授权后再试
```

**后续动作**:
- 用户完成授权
- 重新尝试操作

### 2.6 fallback_used

**含义**: 使用了备用通道

**用户消息**: "平台能力当前不可直接调用，已转入待处理队列"

**示例场景**:
- call_device_tool 不可用
- 平台维护中
- 能力暂时不可用

**用户感知**:
```
助手: 短信发送: 平台能力当前不可直接调用，已转入待处理队列
```

### 2.7 failed

**含义**: 操作失败

**用户消息**: "操作失败，请稍后重试"

**示例场景**:
- 参数错误
- 平台错误
- 权限拒绝

**用户感知**:
```
助手: 短信发送: 操作失败，请稍后重试
```

**后续动作**:
- 用户可选择重试
- 助手分析失败原因

## 三、能力特定消息

### 3.1 MESSAGE_SENDING

| 状态 | 消息 |
|------|------|
| completed | 短信发送: 已完成 |
| timeout | 短信发送: 请求超时，当前无法确认是否已发送，请检查是否收到短信 |
| failed | 短信发送: 发送失败，请稍后重试 |

### 3.2 TASK_SCHEDULING

| 状态 | 消息 |
|------|------|
| completed | 日程创建: 已完成 |
| timeout | 日程创建: 请求超时，当前无法确认是否已创建，请检查日历 |
| failed | 日程创建: 创建失败，请稍后重试 |

### 3.3 STORAGE

| 状态 | 消息 |
|------|------|
| completed | 备忘录: 已保存 |
| timeout | 备忘录: 请求超时，当前无法确认是否已保存，请检查备忘录列表 |
| failed | 备忘录: 保存失败，请稍后重试 |

### 3.4 NOTIFICATION

| 状态 | 消息 |
|------|------|
| completed | 通知推送: 已完成 |
| auth_required | 通知推送: 该能力未授权，请先完成授权后再试 |
| failed | 通知推送: 推送失败，请稍后重试 |

## 四、消息生成代码

```python
from platform_adapter.user_messages import format_user_result

# 生成用户消息
message = format_user_result(
    capability="MESSAGE_SENDING",
    status="timeout",
    error_code="PLATFORM_TIMEOUT",
)

print(message)
# 输出: "短信发送: 请求超时，当前无法确认是否已执行，请稍后检查结果"
```

## 五、消息设计原则

### 5.1 清晰性

- 使用简单易懂的语言
- 避免技术术语
- 明确告知用户当前状态

### 5.2 可操作性

- 告诉用户下一步该做什么
- 提供明确的行动指引
- 避免模糊表述

### 5.3 一致性

- 同一状态始终使用相同消息
- 不同能力使用一致的格式
- 保持品牌语气统一

### 5.4 安全性

- 不暴露敏感信息
- 不泄露系统细节
- 不误导用户

## 六、消息测试用例

### 6.1 completed 消息

```python
def test_completed_message():
    msg = get_user_message("completed")
    assert "完成" in msg
    assert "失败" not in msg
    assert "超时" not in msg
```

### 6.2 timeout 消息

```python
def test_timeout_message():
    msg = get_user_message("timeout", "PLATFORM_TIMEOUT")
    assert "超时" in msg or "确认" in msg
    assert "重试" not in msg  # 不建议自动重试
```

### 6.3 auth_required 消息

```python
def test_auth_required_message():
    msg = get_user_message("auth_required", "PLATFORM_AUTH_REQUIRED")
    assert "授权" in msg
```

## 七、国际化支持（预留）

当前仅支持中文，未来可扩展：

```python
MESSAGES = {
    "zh_CN": {
        "completed": "已完成",
        "timeout": "请求超时，当前无法确认是否已执行，请稍后检查结果",
        # ...
    },
    "en_US": {
        "completed": "Completed",
        "timeout": "Request timed out. Unable to confirm if executed. Please check the result later.",
        # ...
    }
}
```
