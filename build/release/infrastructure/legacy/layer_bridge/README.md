# 六层架构高速连接系统

## V2.7.0 - 2026-04-10

实现层间零延迟调用，确保架构间最快速度连接。

## 性能指标

| 组件 | 平均延迟 | QPS |
|------|----------|-----|
| FastBridge | 0.005ms | 206,059 |
| ZeroCopy | 0.004ms | 268,868 |
| Cache读取 | 0.002ms | 688,599 |
| Cache写入 | 0.226ms | 4,426 |

## 组件说明

### 1. FastBridge - 高速层间连接器

```python
from core.layer_bridge import fast_call, Layer

# 快速调用
result = fast_call(
    from_layer=Layer.L1_CORE,
    to_layer=Layer.L2_MEMORY,
    action="recall",
    data="query"
)
```

**特性**:
- 直连路由表
- LRU缓存
- 调用统计

### 2. ZeroCopy - 零拷贝数据传输

```python
from core.layer_bridge import share_data, get_shared

# 共享数据
data_id = share_data(large_data)

# 获取数据（不复制）
data = get_shared(data_id)
```

**特性**:
- 引用传递
- 自动引用计数
- LRU淘汰

### 3. LayerCache - 多级缓存

```python
from core.layer_bridge import cache_get, cache_set

# 设置缓存
cache_set("key", value, ttl=60)

# 获取缓存
value = cache_get("key")
```

**特性**:
- L1/L2/L3 三级缓存
- 自动升级/降级
- TTL过期

### 4. AsyncQueue - 异步调用队列

```python
from core.layer_bridge import async_call, Priority

# 提交异步任务
task_id = async_call(
    coroutine=my_async_function(),
    priority=Priority.HIGH
)
```

**特性**:
- 优先级队列
- 异步非阻塞
- 回调支持

## 层间路由

```
L1 (Core) ──┬──> L2 (Memory)
            ├──> L3 (Orchestration)
            └──> L4 (Execution)

L2 (Memory) ──┬──> L1 (Core)
              └──> L3 (Orchestration)

L3 (Orchestration) ──┬──> L2 (Memory)
                     └──> L4 (Execution)

L4 (Execution) ──┬──> L5 (Governance)
                 └──> L6 (Infrastructure)

L5 (Governance) ────> L6 (Infrastructure)

L6 (Infrastructure) ────> L1 (Core)
```

## 配置

见 `LAYER_BRIDGE_CONFIG.json`

## 使用建议

1. **热数据**: 使用 L1 缓存，TTL 60秒
2. **温数据**: 使用 L2 缓存，TTL 5分钟
3. **冷数据**: 使用 L3 缓存，TTL 1小时
4. **大对象**: 使用 ZeroCopy 共享
5. **耗时操作**: 使用 AsyncQueue 异步

---

**版本**: V2.7.0
**作者**: @18816132863
