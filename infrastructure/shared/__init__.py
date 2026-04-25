"""共享层 - V4.3.2

所有共享模块的唯一实现。
"""

from .router import UnifiedRouter, get_router, route

# 可选导入 - 模块可能不存在某些类
try:
    from .weights import normalize_weights, weighted_score
except ImportError:
    pass

try:
    from .cache import UnifiedCache, get_cache
except ImportError:
    pass

try:
    from .dedup import deduplicate, deduplicate_dicts
except ImportError:
    pass

try:
    from .config import UnifiedConfig, get_config
except ImportError:
    pass

__all__ = [
    'UnifiedRouter', 'get_router', 'route',
]
