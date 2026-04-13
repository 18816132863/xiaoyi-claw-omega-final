"""
六层架构高速连接系统
V2.7.0 - 2026-04-10

提供层间零延迟调用、零拷贝传输、异步队列、多级缓存
"""

from .fast_bridge import (
    FastBridge, Layer, LayerCall,
    get_bridge, fast_call
)
from .zero_copy import (
    ZeroCopyManager, SharedData,
    get_zero_copy, share_data, get_shared
)
from .async_queue import (
    AsyncCallQueue, Priority, TaskItem,
    get_async_queue, async_call
)
from .layer_cache import (
    LayerCache, CacheEntry,
    get_layer_cache, cache_get, cache_set
)

__all__ = [
    # FastBridge
    'FastBridge', 'Layer', 'LayerCall', 'get_bridge', 'fast_call',
    # ZeroCopy
    'ZeroCopyManager', 'SharedData', 'get_zero_copy', 'share_data', 'get_shared',
    # AsyncQueue
    'AsyncCallQueue', 'Priority', 'TaskItem', 'get_async_queue', 'async_call',
    # LayerCache
    'LayerCache', 'CacheEntry', 'get_layer_cache', 'cache_get', 'cache_set',
]

__version__ = '2.7.0'
