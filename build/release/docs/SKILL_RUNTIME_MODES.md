# 技能运行模式

## 三种运行模式

### 1. Skill Default 模式（默认）

**适用场景**：
- 技能市场分享
- 用户零配置使用
- 平台受限环境

**特征**：
- SQLite 持久化
- 单进程执行
- Request-driven 触发
- 无外部依赖

**能力**：
| 能力 | 状态 |
|------|------|
| 任务创建 | ✅ |
| 任务执行 | ✅ |
| 任务调度 | ✅ |
| 失败重试 | ✅ |
| 暂停/恢复 | ✅ |
| 取消任务 | ✅ |
| 诊断 | ✅ |
| 导出 | ✅ |
| 回放 | ✅ |

### 2. Platform Enhanced 模式

**适用场景**：
- 小艺平台
- HarmonyOS 设备
- 有平台调度能力

**特征**：
- 借用平台调度
- 借用平台消息
- 自动降级到 Default

**额外能力**：
| 能力 | 状态 |
|------|------|
| 平台调度 | ✅ |
| 平台消息 | ✅ |
| 平台通知 | ✅ |

### 3. Self-hosted Enhanced 模式

**适用场景**：
- 自托管部署
- 需要完整功能
- 有 PostgreSQL/Redis

**特征**：
- PostgreSQL 存储
- Redis 缓存
- 分布式执行

**额外能力**：
| 能力 | 状态 |
|------|------|
| 分布式执行 | ✅ |
| 高级重试 | ✅ |
| 检查点恢复 | ✅ |

## 模式切换

```python
from platform_adapter.runtime_probe import RuntimeProbe

# 自动检测
env = RuntimeProbe.detect_environment()
print(f"当前模式: {env['runtime_mode']}")
```

## 降级策略

当高级模式不可用时，自动降级：

```
Platform Enhanced → Skill Default
Self-hosted Enhanced → Skill Default
```

降级不会导致功能完全不可用，只是性能/特性受限。
