"""缓存管理器 - V4.3.1

兼容层：引用 infrastructure/shared/cache.py
"""

from infrastructure.shared.cache import UnifiedCache, CacheEntry, get_cache

CacheManager = UnifiedCache

__all__ = ['UnifiedCache', 'CacheEntry', 'get_cache', 'CacheManager']
