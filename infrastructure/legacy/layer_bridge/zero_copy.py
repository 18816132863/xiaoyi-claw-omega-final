#!/usr/bin/env python3
"""
零拷贝数据传输层
V2.7.0 - 2026-04-10
避免层间数据复制，使用引用传递
"""

import sys
from typing import Any, Dict, List, Optional
from weakref import WeakValueDictionary
from dataclasses import dataclass, field
from threading import RLock

@dataclass
class SharedData:
    """共享数据容器"""
    data_id: str
    data: Any
    ref_count: int = 0
    tags: List[str] = field(default_factory=list)

class ZeroCopyManager:
    """零拷贝数据管理器"""
    
    def __init__(self, max_size: int = 1000):
        self._shared_data: Dict[str, SharedData] = {}
        self._weak_refs = WeakValueDictionary()
        self._lock = RLock()
        self._max_size = max_size
        self._current_id = 0
    
    def _generate_id(self) -> str:
        """生成唯一ID"""
        self._current_id += 1
        return f"sd_{self._current_id}"
    
    def share(self, data: Any, tags: List[str] = None) -> str:
        """共享数据，返回引用ID"""
        with self._lock:
            # 检查是否已存在相同数据
            data_hash = hash(repr(data))
            for sd in self._shared_data.values():
                if hash(repr(sd.data)) == data_hash:
                    sd.ref_count += 1
                    return sd.data_id
            
            # 创建新的共享数据
            data_id = self._generate_id()
            self._shared_data[data_id] = SharedData(
                data_id=data_id,
                data=data,
                ref_count=1,
                tags=tags or []
            )
            
            # LRU 淘汰
            if len(self._shared_data) > self._max_size:
                self._evict()
            
            return data_id
    
    def get(self, data_id: str) -> Optional[Any]:
        """获取共享数据（不复制）"""
        with self._lock:
            sd = self._shared_data.get(data_id)
            if sd:
                return sd.data  # 直接返回引用，不复制
            return None
    
    def release(self, data_id: str):
        """释放数据引用"""
        with self._lock:
            sd = self._shared_data.get(data_id)
            if sd:
                sd.ref_count -= 1
                if sd.ref_count <= 0:
                    del self._shared_data[data_id]
    
    def _evict(self):
        """LRU 淘汰"""
        # 按引用计数排序，删除最少的
        sorted_items = sorted(
            self._shared_data.items(),
            key=lambda x: x[1].ref_count
        )
        
        # 删除10%
        to_remove = max(1, len(sorted_items) // 10)
        for data_id, _ in sorted_items[:to_remove]:
            del self._shared_data[data_id]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self._lock:
            total_refs = sum(sd.ref_count for sd in self._shared_data.values())
            return {
                "shared_count": len(self._shared_data),
                "total_refs": total_refs,
                "max_size": self._max_size
            }

# 全局单例
_zero_copy: Optional[ZeroCopyManager] = None

def get_zero_copy() -> ZeroCopyManager:
    """获取全局零拷贝管理器"""
    global _zero_copy
    if _zero_copy is None:
        _zero_copy = ZeroCopyManager()
    return _zero_copy

def share_data(data: Any, tags: List[str] = None) -> str:
    """共享数据（便捷函数）"""
    return get_zero_copy().share(data, tags)

def get_shared(data_id: str) -> Optional[Any]:
    """获取共享数据（便捷函数）"""
    return get_zero_copy().get(data_id)
