"""资源池管理器 - V1.0.0"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import threading

@dataclass
class Resource:
    """资源"""
    id: str
    type: str
    data: Any
    created_at: datetime
    last_used: datetime
    use_count: int
    size_bytes: int

class ResourcePool:
    """资源池管理器 - 管理共享资源"""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size = max_size_mb * 1024 * 1024
        self.resources: Dict[str, Resource] = {}
        self.lock = threading.Lock()
        self.current_size = 0
    
    def put(self, resource_id: str, data: Any, resource_type: str = "generic") -> bool:
        """添加资源"""
        with self.lock:
            # 估算大小
            size = len(str(data)) if isinstance(data, str) else len(str(data))
            
            # 检查是否需要淘汰
            while self.current_size + size > self.max_size and self.resources:
                self._evict_lru()
            
            now = datetime.now()
            self.resources[resource_id] = Resource(
                id=resource_id,
                type=resource_type,
                data=data,
                created_at=now,
                last_used=now,
                use_count=0,
                size_bytes=size
            )
            self.current_size += size
            return True
    
    def get(self, resource_id: str) -> Optional[Any]:
        """获取资源"""
        with self.lock:
            if resource_id not in self.resources:
                return None
            
            resource = self.resources[resource_id]
            resource.last_used = datetime.now()
            resource.use_count += 1
            return resource.data
    
    def _evict_lru(self):
        """淘汰最少使用的资源"""
        if not self.resources:
            return
        
        # 找到 LRU
        lru_id = min(self.resources.keys(), key=lambda k: self.resources[k].last_used)
        resource = self.resources.pop(lru_id)
        self.current_size -= resource.size_bytes
    
    def clear(self):
        """清空资源池"""
        with self.lock:
            self.resources.clear()
            self.current_size = 0
    
    def get_stats(self) -> Dict:
        """获取统计"""
        with self.lock:
            return {
                "resource_count": len(self.resources),
                "current_size_mb": self.current_size / (1024 * 1024),
                "max_size_mb": self.max_size / (1024 * 1024),
                "usage_rate": self.current_size / self.max_size,
                "total_use_count": sum(r.use_count for r in self.resources.values())
            }
