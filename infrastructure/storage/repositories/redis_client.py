"""

PROJECT_ROOT = Path(__file__).resolve().parents[3]
Redis 客户端 V1.0.0

职责：
- 消息队列
- 分布式锁
- 缓存
"""

import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

try:
    import redis.asyncio as aioredis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


class RedisClient:
    """Redis 客户端"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or "redis://localhost:6379"
        self.client = None
        self._available = False
    
    async def connect(self):
        """连接 Redis"""
        if not HAS_REDIS:
            print("[Redis] aioredis 未安装，使用文件 fallback")
            return False
        
        try:
            self.client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.client.ping()
            self._available = True
            print("[Redis] 连接成功")
            return True
        except Exception as e:
            print(f"[Redis] 连接失败: {e}，使用文件 fallback")
            self._available = False
            return False
    
    async def close(self):
        """关闭连接"""
        if self.client:
            await self.client.close()
    
    # ==================== 队列操作 ====================
    
    async def enqueue(self, queue_name: str, data: Dict[str, Any]) -> bool:
        """入队"""
        if self._available and self.client:
            try:
                await self.client.lpush(queue_name, json.dumps(data, ensure_ascii=False))
                return True
            except:
                pass
        
        # Fallback: 写入文件
        root = Path(str(PROJECT_ROOT))
        queue_file = root / "data" / f"{queue_name}.jsonl"
        queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        return True
    
    async def dequeue(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """出队"""
        if self._available and self.client:
            try:
                data = await self.client.rpop(queue_name)
                if data:
                    return json.loads(data)
            except:
                pass
        
        # Fallback: 从文件读取
        root = Path(str(PROJECT_ROOT))
        queue_file = root / "data" / f"{queue_name}.jsonl"
        
        if not queue_file.exists():
            return None
        
        with open(queue_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return None
        
        # 取第一条
        first = lines.pop(0)
        
        # 写回剩余的
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return json.loads(first.strip())
    
    async def queue_length(self, queue_name: str) -> int:
        """队列长度"""
        if self._available and self.client:
            try:
                return await self.client.llen(queue_name)
            except:
                pass
        
        # Fallback: 统计文件行数
        root = Path(str(PROJECT_ROOT))
        queue_file = root / "data" / f"{queue_name}.jsonl"
        
        if not queue_file.exists():
            return 0
        
        with open(queue_file, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    
    # ==================== 分布式锁 ====================
    
    async def acquire_lock(self, lock_name: str, ttl: int = 60) -> bool:
        """获取锁"""
        if self._available and self.client:
            try:
                result = await self.client.set(lock_name, "1", ex=ttl, nx=True)
                return result is not None
            except:
                pass
        
        # Fallback: 文件锁
        import fcntl
        import os
        
        lock_file = f"/tmp/{lock_name}.lock"
        try:
            fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except:
            return False
    
    async def release_lock(self, lock_name: str) -> bool:
        """释放锁"""
        if self._available and self.client:
            try:
                await self.client.delete(lock_name)
                return True
            except:
                pass
        
        # Fallback: 删除文件锁
        import os
        
        lock_file = f"/tmp/{lock_name}.lock"
        try:
            os.remove(lock_file)
            return True
        except:
            return False
    
    # ==================== 缓存 ====================
    
    async def set_cache(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存"""
        if self._available and self.client:
            try:
                await self.client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
                return True
            except:
                pass
        
        return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if self._available and self.client:
            try:
                value = await self.client.get(key)
                if value:
                    return json.loads(value)
            except:
                pass
        
        return None


# 全局实例
_redis_client: Optional[RedisClient] = None


async def get_redis() -> RedisClient:
    """获取 Redis 客户端"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client
