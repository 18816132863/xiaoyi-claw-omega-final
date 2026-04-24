# 平台连接矩阵

## 版本
- V8.3.0 路径统一版
- 更新日期: 2026-04-24

## 平台适配器状态

| 适配器 | 环境探测 | 能力接通 | 真实可用 | 状态 |
|--------|----------|----------|----------|------|
| xiaoyi | ✅ 可探测 | ❌ 未接通 | ❌ 不可用 | probe_only |
| null | N/A | N/A | ❌ 不可用 | fallback |

## 状态说明

### probe_only (仅探测)
- 环境探测：可以检测到小艺/鸿蒙环境
- 能力接通：尚未对接实际API
- 真实可用：不能执行实际操作
- 行为：返回 `CAPABILITY_NOT_CONNECTED` 错误

### fallback (降级)
- 无平台环境
- 使用本地 fallback 机制
- 行为：写入待发送队列，等待外部处理

## 小艺平台能力详情

### TASK_SCHEDULING
| 项目 | 状态 |
|------|------|
| 环境探测 | ✅ 可检测 XIAOYI_ENV / HARMONYOS_VERSION |
| API 对接 | ❌ 未实现 |
| 真实调用 | ❌ 不可用 |
| 执行路径 | 无 |

### MESSAGE_SENDING
| 项目 | 状态 |
|------|------|
| 环境探测 | ✅ 可检测 |
| API 对接 | ❌ 未实现 |
| 真实调用 | ❌ 不可用 |
| 执行路径 | 无 |
| Fallback | 写入 pending_sends.jsonl |

### NOTIFICATION
| 项目 | 状态 |
|------|------|
| 环境探测 | ✅ 可检测 |
| API 对接 | ❌ 未实现 |
| 真实调用 | ❌ 不可用 |
| 执行路径 | 无 |

## 连接状态判定逻辑

```python
# 真正的 available = 环境存在 + 至少一个能力已接通
truly_available = (
    environment_exists and 
    any(status.available for status in capabilities.values())
)
```

## 语义澄清

### ❌ 错误说法
- "推荐适配器是 xiaoyi" → 这只是环境探测结果
- "平台可用" → 环境存在 ≠ 能力可用

### ✅ 正确说法
- "探测到小艺环境，但能力未接通"
- "推荐适配器: xiaoyi (probe_only)"
- "平台状态: environment_detected, capabilities_not_connected"

## 后续对接点

当小艺 API 可用时，需要在以下位置实现：

1. `platform_adapter/xiaoyi_adapter.py`
   - `_capabilities[PlatformCapability.XXX].available = True`
   - `invoke()` 方法实现实际 API 调用

2. 添加确认回调
   - `delivery_confirmed` 事件
   - `external_completed` 状态

## 测试覆盖

| 测试 | 文件 |
|------|------|
| 环境探测 | tests/test_platform_execution_semantics.py |
| 能力状态 | tests/test_platform_execution_semantics.py |
| 连接状态 | tests/test_xiaoyi_adapter_real_connection.py |
