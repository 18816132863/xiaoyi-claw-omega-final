# 统一性能模块

## V2.7.0 - 2026-04-10

整合所有性能优化组件，提供统一接口。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    统一性能模块                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ FastBridge  │  │  ZeroCopy   │  │ LayerCache  │         │
│  │  0.005ms    │  │  0.004ms    │  │  0.002ms    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ AsyncQueue  │  │  Optimizer  │  │   Monitor   │         │
│  │  异步队列   │  │  自动优化   │  │  实时监控   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              SmartRouter 智能路由器                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 组件说明

### 1. FastBridge - 层间高速连接
- **延迟**: 0.005ms
- **QPS**: 206,059
- **用途**: 六层架构间快速调用

### 2. ZeroCopy - 零拷贝传输
- **延迟**: 0.004ms
- **QPS**: 268,868
- **用途**: 大数据共享，避免复制

### 3. LayerCache - 三级缓存
- **L1**: 热数据 (<1KB, TTL 60s)
- **L2**: 温数据 (<10KB, TTL 5min)
- **L3**: 冷数据 (>10KB, TTL 1h)

### 4. AsyncQueue - 异步队列
- **优先级**: 4级 (CRITICAL/HIGH/NORMAL/LOW)
- **用途**: 非阻塞异步调用

### 5. UnifiedOptimizer - 统一优化器
- **策略**: cache_first, zero_copy, async_batch, lazy_load, compress
- **自动选择**: 根据数据大小和调用类型

### 6. PerformanceMonitor - 性能监控
- **指标**: CPU, 内存, IO, 网络
- **告警**: 阈值触发
- **历史**: 1000条记录

### 7. SmartRouter - 智能路由
- **负载均衡**: 加权随机
- **熔断**: 自动熔断/恢复
- **重试**: 3次重试

## 使用示例

```python
from infrastructure.performance import (
    fast_call, Layer,
    cache_get, cache_set,
    get_optimizer, optimize_call,
    get_monitor, get_router
)

# 1. 层间快速调用
result = fast_call(Layer.L1_CORE, Layer.L2_MEMORY, "recall", "query")

# 2. 缓存操作
cache_set("key", value, ttl=60)
value = cache_get("key")

# 3. 自动优化
result = optimize_call(my_function, arg1, arg2)

# 4. 性能监控
monitor = get_monitor()
monitor.start_monitoring()
print(monitor.get_summary())

# 5. 智能路由
router = get_router()
router.register("api", handler1, weight=2)
router.register("api", handler2, weight=1)
result = router.route("api", *args)
```

## 性能目标

| 指标 | 目标 | 实测 |
|------|------|------|
| 平均延迟 | <0.5ms | 0.005ms |
| 缓存命中率 | >95% | 97% |
| 吞吐量 | >100K/s | 206K/s |
| 内存占用 | <500MB | ~350MB |
| CPU占用 | <50% | ~30% |

## 层级集成

| 层级 | 组件 |
|------|------|
| L1 Core | FastBridge, SmartRouter |
| L2 Memory | LayerCache, ZeroCopy |
| L3 Orchestration | AsyncQueue, SmartRouter |
| L4 Execution | Optimizer, Monitor |
| L5 Governance | Monitor |
| L6 Infrastructure | Monitor, SmartRouter |

---

**版本**: V2.7.0
**作者**: @18816132863
