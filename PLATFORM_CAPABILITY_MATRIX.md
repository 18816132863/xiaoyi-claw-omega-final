# 平台能力接线矩阵

## 版本
- V8.3.0 小艺真实接线完成版
- 更新日期: 2026-04-24
- 最终验证版

## 口径定义

### 设备连接状态
- **device_connected = true（默认）**
- 当前运行环境是 OpenClaw / 小艺连接端环境
- 设备端默认视为已连接
- 不需要"先连接设备"的用户步骤

### 能力状态定义
- **connected**: 该能力在已连接设备环境中已真实可调用
- **probe_only**: 代码已实现，但能力未授权或未配置
- **mock**: 代码未实现

### 主要判定条件
1. capability 是否已接通
2. capability 是否已授权
3. 当前调用是否成功 / 超时 / 失败

## 矩阵总览

| 能力 | 代码实现 | 已授权 | 真实可调用 | 状态 |
|------|----------|--------|------------|------|
| MESSAGE_SENDING | ✅ | ✅ | ✅ | **connected** |
| TASK_SCHEDULING | ✅ | ✅ | ✅ | **connected** |
| STORAGE | ✅ | ✅ | ✅ | **connected** |
| NOTIFICATION | ✅ | ✅ | ✅ | **connected** |

## 各能力详情

### MESSAGE_SENDING ✅ connected

| 项目 | 状态 | 详情 |
|------|------|------|
| 代码实现 | ✅ | `_invoke_message_sending()` 已实现 |
| 已授权 | ✅ | 短信发送权限已授权 |
| 真实可调用 | ✅ | 调用返回成功 |
| 确认级别 | Level 2 | 短信发送是同步操作 |

**验证记录**:
```json
// 11:04
{"code":0,"result":{"message":"send success"}}

// 11:36
{"code":0,"result":{"message":"send success"}}
```

### TASK_SCHEDULING ✅ connected

| 项目 | 状态 | 详情 |
|------|------|------|
| 代码实现 | ✅ | `_invoke_task_scheduling()` 已实现 |
| 已授权 | ✅ | 日程创建权限已授权 |
| 真实可调用 | ✅ | 调用返回成功 |
| 确认级别 | Level 2 | 日程创建是同步操作 |

**验证记录**:
```json
// 11:04
{"code":0,"flags":0,"result":{"entityId":"1993"}}
```

### STORAGE ✅ connected

| 项目 | 状态 | 详情 |
|------|------|------|
| 代码实现 | ✅ | 可通过 call_device_tool 调用 create_note |
| 已授权 | ✅ | 备忘录创建权限已授权 |
| 真实可调用 | ✅ | 调用返回成功 |

**验证记录**:
```json
// 11:04
{"code":0,"flags":0,"result":{"entityId":"14abac0f$3887$4ddc$9b8c$58dc4f4f8800"}}
```

### NOTIFICATION ✅ connected

| 项目 | 状态 | 详情 |
|------|------|------|
| 代码实现 | ✅ | `_invoke_notification()` 脚本路径已实现 |
| 已授权 | ✅ | authCode 已配置 (8I5R***) |
| 真实可调用 | ✅ | 推送返回成功 |
| 确认级别 | Level 2 | 负一屏推送是同步操作 |

**验证记录**:
```json
// 12:05
{
  "code": "0000000000",
  "desc": "OK"
}
```

## 状态判定逻辑

### connected 判定

```python
connected = (
    code_implemented and      # 代码已实现
    capability_authorized and  # 能力已授权
    invocation_success         # 调用成功
)
```

### 当前状态

```python
{
    "device_connected": True,  # 默认 true
    
    "MESSAGE_SENDING": {
        "code_implemented": True,
        "capability_authorized": True,
        "invocation_success": True,
        "state": "connected"
    },
    "TASK_SCHEDULING": {
        "code_implemented": True,
        "capability_authorized": True,
        "invocation_success": True,
        "state": "connected"
    },
    "STORAGE": {
        "code_implemented": True,
        "capability_authorized": True,
        "invocation_success": True,
        "state": "connected"
    },
    "NOTIFICATION": {
        "code_implemented": True,
        "capability_authorized": True,
        "invocation_success": True,
        "state": "connected"
    }
}
```

## 验证记录汇总

| 能力 | 验证时间 | 调用结果 | 状态 |
|------|----------|----------|------|
| MESSAGE_SENDING | 11:04 | `{"code":0,"result":{"message":"send success"}}` | ✅ |
| MESSAGE_SENDING | 11:36 | `{"code":0,"result":{"message":"send success"}}` | ✅ |
| TASK_SCHEDULING | 11:04 | `{"code":0,"result":{"entityId":"1993"}}` | ✅ |
| STORAGE | 11:04 | `{"code":0,"result":{"entityId":"14abac0f..."}}` | ✅ |
| NOTIFICATION | 12:05 | `{"code":"0000000000","desc":"OK"}` | ✅ |

## 总结

| 项目 | 状态 |
|------|------|
| 设备连接 | ✅ 默认已连接 |
| MESSAGE_SENDING | ✅ connected |
| TASK_SCHEDULING | ✅ connected |
| STORAGE | ✅ connected |
| NOTIFICATION | ✅ connected |

**最终结论**: 4 个能力全部 connected ✅
