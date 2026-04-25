#!/usr/bin/env python3
"""
cache - V4.3.2 融合版

融合自:
- infrastructure/shared/cache.py
- memory_context/cache/cache.py
- memory_context/vector/cache.py

此模块为统一实现，其他位置通过兼容层引用
"""

from typing import Any, Optional
from datetime import datetime, timedelta
import threading

class CacheEntry:
    """缓存条目"""
    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

class UnifiedCache:
    """统一缓存管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._cache = {}
                    cls._instance._cache_lock = threading.Lock()
        return cls._instance
    
    def get(self, key: str) -> Optional[Any]:
        with self._cache_lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                return entry.value
            elif entry:
                del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        with self._cache_lock:
            self._cache[key] = CacheEntry(value, ttl_seconds)
    
    def delete(self, key: str):
        with self._cache_lock:
            self._cache.pop(key, None)
    
    def clear(self):
        with self._cache_lock:
            self._cache.clear()

# 全局实例
_cache: Optional[UnifiedCache] = None

def get_cache() -> UnifiedCache:
    global _cache
    if _cache is None:
        _cache = UnifiedCache()
    return _cache
