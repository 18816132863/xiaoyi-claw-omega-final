from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

"""
统一性能模块
V2.7.0 - 2026-04-10

整合所有性能优化组件
"""

import sys
sys.path.insert(0, str(get_project_root()))

# 从 layer_bridge 导入
from core.layer_bridge import (
    FastBridge, Layer, LayerCall, get_bridge, fast_call,
    ZeroCopyManager, SharedData, get_zero_copy, share_data, get_shared,
    AsyncCallQueue, Priority, TaskItem, get_async_queue, async_call,
    LayerCache, CacheEntry, get_layer_cache, cache_get, cache_set,
)

# 本地组件
from .unified_optimizer import UnifiedOptimizer, get_optimizer, optimize_call
from .performance_monitor import PerformanceMonitor, get_monitor
from .smart_router import SmartRouter, get_router

__all__ = [
    'FastBridge', 'Layer', 'LayerCall', 'get_bridge', 'fast_call',
    'ZeroCopyManager', 'SharedData', 'get_zero_copy', 'share_data', 'get_shared',
    'AsyncCallQueue', 'Priority', 'TaskItem', 'get_async_queue', 'async_call',
    'LayerCache', 'CacheEntry', 'get_layer_cache', 'cache_get', 'cache_set',
    'UnifiedOptimizer', 'get_optimizer', 'optimize_call',
    'PerformanceMonitor', 'get_monitor',
    'SmartRouter', 'get_router',
]

__version__ = '2.7.0'
