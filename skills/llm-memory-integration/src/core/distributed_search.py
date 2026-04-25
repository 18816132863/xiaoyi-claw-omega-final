#!/usr/bin/env python3
"""
分布式向量搜索模块 (v4.2)
向量分片索引、多节点并行搜索、分布式结果聚合
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Callable
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib

# 可选依赖：aiohttp
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    aiohttp = None
    HAS_AIOHTTP = False


class VectorSharder:
    """
    向量分片器
    将大规模向量数据分片存储
    """
    
    def __init__(self, n_shards: int = 4, hash_func: str = 'murmur'):
        """
        初始化分片器
        
        Args:
            n_shards: 分片数量
            hash_func: 哈希函数
        """
        self.n_shards = n_shards
        self.hash_func = hash_func
        self.shards = [[] for _ in range(n_shards)]
        self.shard_metadata = [{} for _ in range(n_shards)]
    
    def _hash(self, vector_id: str) -> int:
        """
        计算向量 ID 的哈希值
        
        Args:
            vector_id: 向量 ID
        
        Returns:
            int: 分片索引
        """
        if self.hash_func == 'murmur':
            # MurmurHash 简化实现
            h = int(hashlib.md5(vector_id.encode()).hexdigest(), 16)
            return h % self.n_shards
        else:
            return hash(vector_id) % self.n_shards
    
    def add_vector(self, vector_id: str, vector: np.ndarray, metadata: Optional[Dict] = None):
        """
        添加向量到分片
        
        Args:
            vector_id: 向量 ID
            vector: 向量数据
            metadata: 元数据
        """
        shard_idx = self._hash(vector_id)
        self.shards[shard_idx].append((vector_id, vector))
        if metadata:
            self.shard_metadata[shard_idx][vector_id] = metadata
    
    def get_shard(self, shard_idx: int) -> List[Tuple[str, np.ndarray]]:
        """
        获取分片数据
        
        Args:
            shard_idx: 分片索引
        
        Returns:
            List[Tuple[str, np.ndarray]]: 分片数据
        """
        return self.shards[shard_idx]
    
    def get_all_shards(self) -> List[List[Tuple[str, np.ndarray]]]:
        """
        获取所有分片
        
        Returns:
            List[List[Tuple[str, np.ndarray]]]: 所有分片数据
        """
        return self.shards


class DistributedSearcher:
    """
    分布式搜索器
    多节点并行搜索，结果聚合
    """
    
    def __init__(
        self,
        nodes: Optional[List[str]] = None,
        local_mode: bool = True,
        n_workers: int = 4
    ):
        """
        初始化分布式搜索器
        
        Args:
            nodes: 节点列表（URL）
            local_mode: 是否本地模式（模拟分布式）
            n_workers: 工作线程数
        """
        self.nodes = nodes or []
        self.local_mode = local_mode
        self.n_workers = n_workers
        self.executor = ThreadPoolExecutor(max_workers=n_workers)
        
        # 本地模式的分片数据
        self.local_shards = []
        
        print(f"分布式搜索器初始化:")
        print(f"  模式: {'本地' if local_mode else '远程'}")
        print(f"  节点数: {len(self.nodes) if not local_mode else n_workers}")
    
    def set_local_shards(self, shards: List[np.ndarray]):
        """
        设置本地分片数据
        
        Args:
            shards: 分片数据列表
        """
        self.local_shards = shards
    
    async def search(
        self,
        query: np.ndarray,
        top_k: int = 10,
        n_probe: int = 1
    ) -> List[Tuple[str, float]]:
        """
        分布式搜索
        
        Args:
            query: 查询向量
            top_k: 返回数量
            n_probe: 探测节点数
        
        Returns:
            List[Tuple[str, float]]: [(向量ID, 得分), ...]
        """
        if self.local_mode:
            return await self._local_search(query, top_k)
        else:
            return await self._remote_search(query, top_k, n_probe)
    
    async def _local_search(
        self,
        query: np.ndarray,
        top_k: int
    ) -> List[Tuple[str, float]]:
        """
        本地并行搜索
        
        Args:
            query: 查询向量
            top_k: 返回数量
        
        Returns:
            List[Tuple[str, float]]: 搜索结果
        """
        # 并行搜索所有分片
        loop = asyncio.get_event_loop()
        tasks = []
        
        for shard_idx, shard in enumerate(self.local_shards):
            task = loop.run_in_executor(
                self.executor,
                self._search_shard,
                query,
                shard,
                top_k,
                shard_idx
            )
            tasks.append(task)
        
        # 等待所有分片完成
        shard_results = await asyncio.gather(*tasks)
        
        # 聚合结果
        all_results = []
        for results in shard_results:
            all_results.extend(results)
        
        # 排序并返回 top_k
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:top_k]
    
    def _search_shard(
        self,
        query: np.ndarray,
        shard: np.ndarray,
        top_k: int,
        shard_idx: int
    ) -> List[Tuple[str, float]]:
        """
        搜索单个分片
        
        Args:
            query: 查询向量
            shard: 分片数据
            top_k: 返回数量
            shard_idx: 分片索引
        
        Returns:
            List[Tuple[str, float]]: 分片搜索结果
        """
        if len(shard) == 0:
            return []
        
        # 归一化
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        shard_norm = shard / (np.linalg.norm(shard, axis=1, keepdims=True) + 1e-10)
        
        # 计算相似度
        scores = np.dot(shard_norm, query_norm)
        
        # 获取 top_k
        if top_k >= len(scores):
            indices = np.argsort(scores)[::-1]
        else:
            indices = np.argpartition(scores, -top_k)[-top_k:]
            indices = indices[np.argsort(scores[indices])[::-1]]
        
        # 返回结果（带分片前缀）
        results = []
        for idx in indices:
            vector_id = f"shard{shard_idx}_{idx}"
            results.append((vector_id, float(scores[idx])))
        
        return results
    
    async def _remote_search(
        self,
        query: np.ndarray,
        top_k: int,
        n_probe: int
    ) -> List[Tuple[str, float]]:
        """
        远程分布式搜索
        
        Args:
            query: 查询向量
            top_k: 返回数量
            n_probe: 探测节点数
        
        Returns:
            List[Tuple[str, float]]: 搜索结果
        """
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp 未安装，请运行: pip install aiohttp")
        
        # 选择节点
        selected_nodes = self.nodes[:n_probe] if n_probe < len(self.nodes) else self.nodes
        
        # 并行请求
        async with aiohttp.ClientSession() as session:
            tasks = []
            for node in selected_nodes:
                task = self._search_node(session, node, query, top_k)
                tasks.append(task)
            
            node_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 聚合结果
        all_results = []
        for result in node_results:
            if isinstance(result, list):
                all_results.extend(result)
        
        # 排序并返回 top_k
        all_results.sort(key=lambda x: x[1], reverse=True)
        return all_results[:top_k]
    
    async def _search_node(
        self,
        session,
        node: str,
        query: np.ndarray,
        top_k: int
    ) -> List[Tuple[str, float]]:
        """
        搜索单个节点
        
        Args:
            session: HTTP 会话
            node: 节点 URL
            query: 查询向量
            top_k: 返回数量
        
        Returns:
            List[Tuple[str, float]]: 节点搜索结果
        """
        try:
            payload = {
                'query': query.tolist(),
                'top_k': top_k
            }
            
            async with session.post(
                f"{node}/search",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                result = await response.json()
                return [(r['id'], r['score']) for r in result['results']]
        except Exception as e:
            print(f"节点 {node} 搜索失败: {e}")
            return []
    
    def close(self):
        """关闭资源"""
        self.executor.shutdown(wait=True)


if __name__ == "__main__":
    # 测试
    async def test():
        print("=== 分布式搜索测试 ===")
        
        # 创建测试数据
        dim = 4096
        n_vectors = 10000
        n_shards = 4
        
        vectors = np.random.randn(n_vectors, dim).astype(np.float32)
        query = np.random.randn(dim).astype(np.float32)
        
        # 分片
        shard_size = n_vectors // n_shards
        shards = [vectors[i*shard_size:(i+1)*shard_size] for i in range(n_shards)]
        
        # 创建搜索器
        searcher = DistributedSearcher(local_mode=True, n_workers=n_shards)
        searcher.set_local_shards(shards)
        
        # 搜索
        import time
        start = time.time()
        results = await searcher.search(query, top_k=20)
        elapsed = time.time() - start
        
        print(f"搜索耗时: {elapsed*1000:.2f}ms")
        print(f"结果数量: {len(results)}")
        
        searcher.close()
    
    asyncio.run(test())
