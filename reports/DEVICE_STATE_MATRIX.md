# Device State Matrix - 设备状态矩阵

## 状态维度

| 维度 | 可能状态 | 说明 |
|------|----------|------|
| session_connected | CONNECTED, DISCONNECTED, UNKNOWN | 会话连接状态 |
| runtime_bridge_ready | READY, ERROR, NOT_FOUND, UNKNOWN | 运行时桥接状态 |
| permissions | GRANTED, DENIED, PARTIAL, TIMEOUT, UNKNOWN | 权限状态（每个权限独立） |
| capabilities | READY, TIMEOUT, ERROR, NOT_AVAILABLE, UNKNOWN | 能力状态（每个能力独立） |
| action_ready | READY, PERMISSION_REQUIRED, SERVICE_DOWN, UNKNOWN | 动作就绪状态 |

## 小艺 Claw 连接端默认状态

```
is_xiaoyi_channel = True
session_connected = CONNECTED (默认)
runtime_bridge_ready = UNKNOWN (需检查)
permissions = {} (需检查每个权限)
capabilities = {} (需检查每个能力)
action_ready = UNKNOWN (综合判断)
```

## 状态判断规则

### 会话连接判断

| 条件 | 结果 |
|------|------|
| is_xiaoyi_channel = True | session_connected = CONNECTED |
| session heartbeat 失败 + runtime bridge 不存在 + 所有 probe 失败 | session_connected = DISCONNECTED |
| 其他情况 | session_connected = UNKNOWN |

### 能力超时判断

| 条件 | 结果 |
|------|------|
| 单个能力 timeout | capabilities[cap] = TIMEOUT, session 仍 CONNECTED |
| 多个能力 timeout | capabilities[cap] = TIMEOUT, session 仍 CONNECTED |
| 所有能力 timeout + bridge ERROR | 可能 session = DISCONNECTED |

### 动作就绪判断

| 条件 | 结果 |
|------|------|
| session = CONNECTED + 所有权限 GRANTED + 所有能力 READY | action_ready = READY |
| session = CONNECTED + 部分 权限 DENIED | action_ready = PERMISSION_REQUIRED |
| session = CONNECTED + 多个能力 TIMEOUT | action_ready = SERVICE_DOWN |

## 不再误报的场景

| 旧判断 | 新判断 |
|--------|--------|
| contact_service timeout → "no real device" | contact_service = TIMEOUT, session = CONNECTED, "partial" |
| calendar_service timeout → "device disconnected" | calendar_service = TIMEOUT, session = CONNECTED, "partial" |
| adapter_loaded = false → "device unreachable" | 检查具体原因，可能是服务问题而非设备问题 |

## 恢复策略矩阵

| 失败类型 | 第一步 | 第二步 | 第三步 | 第四步 | 第五步 |
|----------|--------|--------|--------|--------|--------|
| CONTACT_SERVICE_TIMEOUT | retry | limited_scope_probe | cache_fallback | permission_diagnosis | human_action_required |
| CALENDAR_SERVICE_TIMEOUT | retry | limited_scope_probe | pending_queue | permission_diagnosis | human_action_required |
| NOTE_SERVICE_TIMEOUT | retry | limited_scope_probe | cache_fallback | permission_diagnosis | human_action_required |
| LOCATION_SERVICE_TIMEOUT | retry | limited_scope_probe | cache_fallback | permission_diagnosis | human_action_required |
| PERMISSION_REQUIRED | permission_diagnosis | human_action_required | - | - | - |

## L0 降级链

```
normal_probe (成功率 < 80%)
    ↓
fast_probe (成功率 < 80%)
    ↓
limited_scope_probe (成功率 < 80%)
    ↓
cache_fallback (成功率 < 80%)
    ↓
permission_diagnosis (最终)
```

## 任务超时分级

| 时间 | 动作 | 说明 |
|------|------|------|
| 20s | heartbeat | 发送心跳，报告进度 |
| 60s | degrade | 降级探测模式 |
| 120s | stop_probe | 停止探测 |
| 180s | output_partial | 返回部分结果 |

## 权限检查清单

| 权限 | 用途 | 必需 |
|------|------|------|
| contact | 联系人查询 | 是 |
| calendar | 日历查询 | 是 |
| note | 备忘录查询 | 是 |
| location | 位置获取 | 是 |
| notification | 通知访问 | 是 |
| screenshot | 截图能力 | 是 |

## 能力检查清单

| 能力 | 依赖权限 | 必需 |
|------|----------|------|
| contact_service | contact | 是 |
| calendar_service | calendar | 是 |
| note_service | note | 是 |
| location_service | location | 是 |
| message_service | notification | 是 |
| phone_service | contact | 是 |
