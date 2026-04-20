from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
完整性能测试
V2.7.0 - 2026-04-10
"""

import time
import sys
sys.path.insert(0, str(get_project_root()))

from infrastructure.performance import (
    get_bridge, fast_call, Layer,
    get_zero_copy, share_data, get_shared,
    get_layer_cache, cache_get, cache_set,
    get_optimizer, optimize_call,
    get_monitor,
    get_router
)

def test_bridge():
    """测试桥接器"""
    bridge = get_bridge()
    bridge.register_handler(Layer.L2_MEMORY, "recall", lambda x: f"recalled: {x}")
    
    iterations = 10000
    start = time.perf_counter()
    for i in range(iterations):
        fast_call(Layer.L1_CORE, Layer.L2_MEMORY, "recall", f"test_{i}")
    elapsed = time.perf_counter() - start
    
    return {
        "name": "FastBridge",
        "iterations": iterations,
        "total_time_s": round(elapsed, 3),
        "avg_latency_ms": round(elapsed / iterations * 1000, 4),
        "qps": int(iterations / elapsed)
    }

def test_zero_copy():
    """测试零拷贝"""
    zm = get_zero_copy()
    test_data = {"key": "value" * 100}
    
    iterations = 10000
    start = time.perf_counter()
    for i in range(iterations):
        data_id = share_data(test_data)
        get_shared(data_id)
    elapsed = time.perf_counter() - start
    
    return {
        "name": "ZeroCopy",
        "iterations": iterations,
        "total_time_s": round(elapsed, 3),
        "avg_latency_ms": round(elapsed / iterations * 1000, 4),
        "qps": int(iterations / elapsed)
    }

def test_cache():
    """测试缓存"""
    cache = get_layer_cache()
    
    iterations = 10000
    
    # 写入
    start = time.perf_counter()
    for i in range(iterations):
        cache_set(f"key_{i}", f"value_{i}")
    write_time = time.perf_counter() - start
    
    # 读取
    start = time.perf_counter()
    for i in range(iterations):
        cache_get(f"key_{i}")
    read_time = time.perf_counter() - start
    
    return {
        "name": "LayerCache",
        "iterations": iterations,
        "write_time_s": round(write_time, 3),
        "read_time_s": round(read_time, 3),
        "write_latency_ms": round(write_time / iterations * 1000, 4),
        "read_latency_ms": round(read_time / iterations * 1000, 4),
        "write_qps": int(iterations / write_time),
        "read_qps": int(iterations / read_time)
    }

def test_optimizer():
    """测试优化器"""
    optimizer = get_optimizer()
    
    def test_func(x):
        return x * 2
    
    iterations = 1000
    start = time.perf_counter()
    for i in range(iterations):
        optimize_call(test_func, i)
    elapsed = time.perf_counter() - start
    
    stats = optimizer.get_stats()
    
    return {
        "name": "UnifiedOptimizer",
        "iterations": iterations,
        "total_time_s": round(elapsed, 3),
        "avg_latency_ms": round(elapsed / iterations * 1000, 4),
        "qps": int(iterations / elapsed),
        "cache_hit_rate": round(stats.get("cache_hit_rate", 0), 3),
        "best_strategy": stats.get("best_strategy", "unknown")
    }

def test_router():
    """测试路由器"""
    router = get_router()
    
    def handler1(x):
        return x * 2
    
    def handler2(x):
        return x * 3
    
    router.register("test", handler1, weight=2)
    router.register("test", handler2, weight=1)
    
    iterations = 10000
    start = time.perf_counter()
    for i in range(iterations):
        router.route("test", i)
    elapsed = time.perf_counter() - start
    
    stats = router.get_stats()
    
    return {
        "name": "SmartRouter",
        "iterations": iterations,
        "total_time_s": round(elapsed, 3),
        "avg_latency_ms": round(elapsed / iterations * 1000, 4),
        "qps": int(iterations / elapsed),
        "cache_hit_rate": round(stats.get("cache_hit_rate", 0), 3)
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("统一性能模块 - 完整测试")
    print("="*60 + "\n")
    
    results = []
    
    print("测试 FastBridge...")
    results.append(test_bridge())
    
    print("测试 ZeroCopy...")
    results.append(test_zero_copy())
    
    print("测试 LayerCache...")
    results.append(test_cache())
    
    print("测试 UnifiedOptimizer...")
    results.append(test_optimizer())
    
    print("测试 SmartRouter...")
    results.append(test_router())
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60 + "\n")
    
    for r in results:
        print(f"【{r['name']}】")
        print(f"  迭代次数: {r['iterations']}")
        if 'avg_latency_ms' in r:
            print(f"  平均延迟: {r['avg_latency_ms']}ms")
        if 'qps' in r:
            print(f"  QPS: {r['qps']:,}")
        if 'read_latency_ms' in r:
            print(f"  读取延迟: {r['read_latency_ms']}ms")
            print(f"  写入延迟: {r['write_latency_ms']}ms")
            print(f"  读取QPS: {r['read_qps']:,}")
            print(f"  写入QPS: {r['write_qps']:,}")
        if 'cache_hit_rate' in r:
            print(f"  缓存命中率: {r['cache_hit_rate']}")
        print()
    
    print("="*60)
    print("所有测试完成")
    print("="*60)
