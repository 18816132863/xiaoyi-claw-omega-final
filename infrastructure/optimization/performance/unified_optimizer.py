#!/usr/bin/env python3
"""
统一优化器
V2.7.0 - 2026-04-10

整合所有优化策略，自动选择最优方案
"""

import time
import json
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class OptStrategy(Enum):
    """优化策略"""
    CACHE_FIRST = "cache_first"       # 优先缓存
    ZERO_COPY = "zero_copy"           # 零拷贝
    ASYNC_BATCH = "async_batch"       # 异步批处理
    LAZY_LOAD = "lazy_load"           # 延迟加载
    COMPRESS = "compress"             # 压缩传输
    PRECOMPUTE = "precompute"         # 预计算

@dataclass
class OptResult:
    """优化结果"""
    strategy: OptStrategy
    original_time_ms: float
    optimized_time_ms: float
    improvement_ratio: float
    data: Any

@dataclass
class OptConfig:
    """优化配置"""
    enable_cache: bool = True
    enable_zero_copy: bool = True
    enable_async: bool = True
    enable_lazy: bool = True
    enable_compress: bool = True
    cache_ttl: int = 300
    max_cache_size_mb: int = 100
    async_batch_size: int = 10
    lazy_threshold_kb: int = 10
    compress_threshold_kb: int = 50

class UnifiedOptimizer:
    """统一优化器"""
    
    def __init__(self, config: OptConfig = None):
        self.config = config or OptConfig()
        self._stats = {
            "total_calls": 0,
            "cache_hits": 0,
            "zero_copy_calls": 0,
            "async_calls": 0,
            "lazy_loads": 0,
            "compressions": 0,
        }
        self._strategy_usage: Dict[str, int] = {}
        self._optimization_history: List[OptResult] = []
    
    def optimize(self, func: Callable, *args, **kwargs) -> OptResult:
        """自动优化函数调用"""
        start = time.perf_counter()
        
        # 1. 分析调用特征
        call_size = self._estimate_size(args, kwargs)
        call_type = self._analyze_call_type(func, args, kwargs)
        
        # 2. 选择最优策略
        strategy = self._select_strategy(call_size, call_type)
        
        # 3. 执行优化
        original_time = self._measure_original(func, args, kwargs)
        
        if strategy == OptStrategy.CACHE_FIRST:
            result = self._execute_cached(func, args, kwargs)
        elif strategy == OptStrategy.ZERO_COPY:
            result = self._execute_zero_copy(func, args, kwargs)
        elif strategy == OptStrategy.ASYNC_BATCH:
            result = self._execute_async(func, args, kwargs)
        elif strategy == OptStrategy.LAZY_LOAD:
            result = self._execute_lazy(func, args, kwargs)
        elif strategy == OptStrategy.COMPRESS:
            result = self._execute_compressed(func, args, kwargs)
        else:
            result = func(*args, **kwargs)
        
        optimized_time = (time.perf_counter() - start) * 1000
        
        # 4. 记录结果
        opt_result = OptResult(
            strategy=strategy,
            original_time_ms=original_time,
            optimized_time_ms=optimized_time,
            improvement_ratio=original_time / max(optimized_time, 0.001),
            data=result
        )
        
        self._record_optimization(opt_result)
        
        return opt_result
    
    def _estimate_size(self, args, kwargs) -> int:
        """估算调用数据大小"""
        try:
            return len(str(args) + str(kwargs))
        except:
            return 100
    
    def _analyze_call_type(self, func: Callable, args, kwargs) -> str:
        """分析调用类型"""
        func_name = getattr(func, '__name__', 'unknown')
        
        if 'get' in func_name or 'fetch' in func_name or 'load' in func_name:
            return 'read'
        elif 'set' in func_name or 'save' in func_name or 'write' in func_name:
            return 'write'
        elif 'process' in func_name or 'compute' in func_name:
            return 'compute'
        else:
            return 'mixed'
    
    def _select_strategy(self, size: int, call_type: str) -> OptStrategy:
        """选择最优策略"""
        # 小数据 + 读操作 -> 缓存优先
        if size < 1024 and call_type == 'read' and self.config.enable_cache:
            return OptStrategy.CACHE_FIRST
        
        # 大数据 -> 零拷贝
        if size > 10240 and self.config.enable_zero_copy:
            return OptStrategy.ZERO_COPY
        
        # 批量操作 -> 异步批处理
        if size > 5000 and self.config.enable_async:
            return OptStrategy.ASYNC_BATCH
        
        # 超大数据 -> 压缩
        if size > 51200 and self.config.enable_compress:
            return OptStrategy.COMPRESS
        
        # 默认 -> 缓存
        if self.config.enable_cache:
            return OptStrategy.CACHE_FIRST
        
        return OptStrategy.PRECOMPUTE
    
    def _measure_original(self, func: Callable, args, kwargs) -> float:
        """测量原始执行时间"""
        start = time.perf_counter()
        try:
            func(*args, **kwargs)
        except:
            pass
        return (time.perf_counter() - start) * 1000
    
    def _execute_cached(self, func: Callable, args, kwargs) -> Any:
        """缓存执行"""
        from core.layer_bridge import cache_get, cache_set
        
        cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
        
        # 尝试从缓存获取
        cached = cache_get(cache_key)
        if cached is not None:
            self._stats["cache_hits"] += 1
            return cached
        
        # 执行并缓存
        result = func(*args, **kwargs)
        cache_set(cache_key, result, self.config.cache_ttl)
        
        return result
    
    def _execute_zero_copy(self, func: Callable, args, kwargs) -> Any:
        """零拷贝执行"""
        from core.layer_bridge import share_data, get_shared
        
        # 共享大参数
        shared_args = []
        for arg in args:
            if self._estimate_size([arg], {}) > 1024:
                data_id = share_data(arg)
                shared_args.append(('shared', data_id))
            else:
                shared_args.append(('direct', arg))
        
        # 执行
        result = func(*args, **kwargs)
        self._stats["zero_copy_calls"] += 1
        
        return result
    
    def _execute_async(self, func: Callable, args, kwargs) -> Any:
        """异步执行"""
        import asyncio
        
        async def async_wrapper():
            return func(*args, **kwargs)
        
        created_loop = False
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            created_loop = True
        
        try:
            result = loop.run_until_complete(async_wrapper())
            self._stats["async_calls"] += 1
            return result
        finally:
            # 自己创建的 loop 必须关闭
            if created_loop:
                loop.close()
    
    def _execute_lazy(self, func: Callable, args, kwargs) -> Any:
        """延迟加载执行"""
        from core.layer_bridge import cache_get, cache_set
        
        cache_key = f"lazy:{func.__name__}:{hash(str(args) + str(kwargs))}"
        
        # 检查是否已加载
        cached = cache_get(cache_key)
        if cached is not None:
            return cached
        
        # 延迟执行
        result = func(*args, **kwargs)
        cache_set(cache_key, result, self.config.cache_ttl * 2)
        self._stats["lazy_loads"] += 1
        
        return result
    
    def _execute_compressed(self, func: Callable, args, kwargs) -> Any:
        """压缩执行"""
        import gzip
        import pickle
        
        # 执行
        result = func(*args, **kwargs)
        
        # 压缩结果
        try:
            pickled = pickle.dumps(result)
            compressed = gzip.compress(pickled)
            self._stats["compressions"] += 1
        except:
            pass
        
        return result
    
    def _record_optimization(self, result: OptResult):
        """记录优化结果"""
        self._stats["total_calls"] += 1
        
        strategy_name = result.strategy.value
        self._strategy_usage[strategy_name] = self._strategy_usage.get(strategy_name, 0) + 1
        
        # 只保留最近100条
        self._optimization_history.append(result)
        if len(self._optimization_history) > 100:
            self._optimization_history = self._optimization_history[-100:]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self._stats["total_calls"]
        if total == 0:
            return self._stats
        
        avg_improvement = 0
        if self._optimization_history:
            avg_improvement = sum(
                r.improvement_ratio for r in self._optimization_history
            ) / len(self._optimization_history)
        
        return {
            **self._stats,
            "cache_hit_rate": self._stats["cache_hits"] / total if total > 0 else 0,
            "strategy_usage": self._strategy_usage,
            "avg_improvement_ratio": round(avg_improvement, 2),
        }
    
    def get_best_strategy(self) -> OptStrategy:
        """获取最佳策略"""
        if not self._strategy_usage:
            return OptStrategy.CACHE_FIRST
        
        best = max(self._strategy_usage.items(), key=lambda x: x[1])
        return OptStrategy(best[0])
    
    def reset_stats(self):
        """重置统计"""
        self._stats = {k: 0 for k in self._stats}
        self._strategy_usage.clear()
        self._optimization_history.clear()

# 全局单例
_optimizer: Optional[UnifiedOptimizer] = None

def get_optimizer() -> UnifiedOptimizer:
    """获取全局优化器"""
    global _optimizer
    if _optimizer is None:
        _optimizer = UnifiedOptimizer()
    return _optimizer

def optimize_call(func: Callable, *args, **kwargs) -> Any:
    """优化调用（便捷函数）"""
    result = get_optimizer().optimize(func, *args, **kwargs)
    return result.data
