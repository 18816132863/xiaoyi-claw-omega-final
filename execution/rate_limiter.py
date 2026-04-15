#!/usr/bin/env python3
"""
速率限制器 - V1.0.0

限制操作频率，防止过载。
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass
from collections import defaultdict
import threading


@dataclass
class RateLimit:
    """速率限制配置"""
    max_calls: int
    period_seconds: int
    current_count: int = 0
    reset_time: float = 0


class RateLimiter:
    """速率限制器"""
    
    def __init__(self):
        self._limits: Dict[str, RateLimit] = {}
        self._lock = threading.Lock()
        
        # 默认限制
        self._default_limits = {
            "default": RateLimit(max_calls=100, period_seconds=60),
            "tool_call": RateLimit(max_calls=50, period_seconds=60),
            "skill_call": RateLimit(max_calls=30, period_seconds=60),
            "file_write": RateLimit(max_calls=20, period_seconds=60),
            "network": RateLimit(max_calls=30, period_seconds=60),
        }
    
    def configure(self, name: str, max_calls: int, period_seconds: int):
        """配置限制"""
        with self._lock:
            self._limits[name] = RateLimit(
                max_calls=max_calls,
                period_seconds=period_seconds
            )
    
    def _get_limit(self, name: str) -> RateLimit:
        """获取限制配置"""
        if name in self._limits:
            return self._limits[name]
        return self._default_limits.get(name, self._default_limits["default"])
    
    def check(self, name: str = "default") -> bool:
        """检查是否允许操作"""
        with self._lock:
            limit = self._get_limit(name)
            current_time = time.time()
            
            # 检查是否需要重置
            if current_time >= limit.reset_time:
                limit.current_count = 0
                limit.reset_time = current_time + limit.period_seconds
            
            # 检查是否超过限制
            if limit.current_count >= limit.max_calls:
                return False
            
            # 增加计数
            limit.current_count += 1
            return True
    
    def wait_time(self, name: str = "default") -> float:
        """获取需要等待的时间"""
        with self._lock:
            limit = self._get_limit(name)
            
            if limit.current_count < limit.max_calls:
                return 0
            
            return limit.reset_time - time.time()
    
    def acquire(self, name: str = "default", timeout: float = None) -> bool:
        """获取许可，如果需要则等待"""
        start_time = time.time()
        
        while True:
            if self.check(name):
                return True
            
            wait = self.wait_time(name)
            if wait <= 0:
                continue
            
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False
                wait = min(wait, timeout - elapsed)
            
            time.sleep(wait)
    
    def reset(self, name: str = None):
        """重置计数"""
        with self._lock:
            if name:
                if name in self._limits:
                    self._limits[name].current_count = 0
            else:
                for limit in self._limits.values():
                    limit.current_count = 0
    
    def status(self, name: str = "default") -> Dict:
        """获取状态"""
        with self._lock:
            limit = self._get_limit(name)
            return {
                "name": name,
                "current_count": limit.current_count,
                "max_calls": limit.max_calls,
                "period_seconds": limit.period_seconds,
                "remaining": limit.max_calls - limit.current_count,
                "reset_in": max(0, limit.reset_time - time.time())
            }


# 全局速率限制器
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """获取全局速率限制器"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
