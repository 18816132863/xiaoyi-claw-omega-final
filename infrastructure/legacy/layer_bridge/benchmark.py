#!/usr/bin/env python3
"""
层间连接性能测试
V2.7.0 - 2026-04-10
"""

import time
import sys
from infrastructure.path_resolver import get_project_root
sys.path.insert(0, str(get_project_root()))

from core.layer_bridge import (
    get_bridge, fast_call, Layer,
    get_zero_copy, share_data, get_shared,
    get_layer_cache, cache_get, cache_set,
    get_async_queue, Priority
)

def benchmark_bridge():
    """测试桥接器性能"""
    bridge = get_bridge()
    
    # 注册测试处理器
    bridge.register_handler(Layer.L2_MEMORY, "recall", lambda x: f"recalled: {x}")
    bridge.register_handler(Layer.L3_ORCHESTRATION, "route", lambda x: f"routed: {x}")
    
    # 测试调用
    iterations = 10000
    start = time.perf_counter()
    
    for i in range(iterations):
        fast_call(Layer.L1_CORE, Layer.L2_MEMORY, "recall", f"test_{i}")
    
    elapsed = time.perf_counter() - start
    avg_latency = (elapsed / iterations) * 1000  # ms
    
    print(f"=== Bridge 性能测试 ===")
    print(f"迭代次数: {iterations}")
    print(f"总耗时: {elapsed:.3f}s")
    print(f"平均延迟: {avg_latency:.4f}ms")
    print(f"QPS: {iterations / elapsed:.0f}")
    print(f"统计: {bridge.get_stats()}")
    print()

def benchmark_zero_copy():
    """测试零拷贝性能"""
    zm = get_zero_copy()
    
    # 测试数据共享
    test_data = {"key": "value" * 100}
    
    iterations = 10000
    start = time.perf_counter()
    
    for i in range(iterations):
        data_id = share_data(test_data)
        result = get_shared(data_id)
    
    elapsed = time.perf_counter() - start
    avg_latency = (elapsed / iterations) * 1000
    
    print(f"=== ZeroCopy 性能测试 ===")
    print(f"迭代次数: {iterations}")
    print(f"总耗时: {elapsed:.3f}s")
    print(f"平均延迟: {avg_latency:.4f}ms")
    print(f"QPS: {iterations / elapsed:.0f}")
    print(f"统计: {zm.get_stats()}")
    print()

def benchmark_cache():
    """测试缓存性能"""
    cache = get_layer_cache()
    
    iterations = 10000
    
    # 写入测试
    start = time.perf_counter()
    for i in range(iterations):
        cache_set(f"key_{i}", f"value_{i}")
    write_time = time.perf_counter() - start
    
    # 读取测试
    start = time.perf_counter()
    for i in range(iterations):
        cache_get(f"key_{i}")
    read_time = time.perf_counter() - start
    
    print(f"=== Cache 性能测试 ===")
    print(f"迭代次数: {iterations}")
    print(f"写入耗时: {write_time:.3f}s ({write_time/iterations*1000:.4f}ms/op)")
    print(f"读取耗时: {read_time:.3f}s ({read_time/iterations*1000:.4f}ms/op)")
    print(f"写入QPS: {iterations / write_time:.0f}")
    print(f"读取QPS: {iterations / read_time:.0f}")
    print(f"统计: {cache.get_stats()}")
    print()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("六层架构高速连接性能测试")
    print("="*50 + "\n")
    
    benchmark_bridge()
    benchmark_zero_copy()
    benchmark_cache()
    
    print("="*50)
    print("测试完成")
    print("="*50)
