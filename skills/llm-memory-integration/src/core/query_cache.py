#!/usr/bin/env python3
"""
查询缓存模块 (v4.2)
LRU 缓存热门查询，相似查询匹配
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Callable
from collections import OrderedDict
import time
import hashlib


class QueryCache:
    """
    查询缓存
    LRU 策略 + 相似查询匹配
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        similarity_threshold: float = 0.99,
        ttl_seconds: int = 3600
    ):
        """
        初始化查询缓存
        
        Args:
            max_size: 最大缓存数量
            similarity_threshold: 相似查询阈值
            ttl_seconds: 缓存过期时间（秒）
        """
        self.max_size = max_size
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        
        # LRU 缓存
        self.cache = OrderedDict()
        
        # 统计
        self.stats = {
            'hits': 0,
            'misses': 0,
            'similar_hits': 0,
            'evictions': 0
        }
        
        print(f"查询缓存初始化:")
        print(f"  最大数量: {max_size}")
        print(f"  相似阈值: {similarity_threshold}")
        print(f"  过期时间: {ttl_seconds}s")
    
    def _hash_query(self, query: np.ndarray) -> str:
        """
        计算查询哈希
        
        Args:
            query: 查询向量
        
        Returns:
            str: 哈希值
        """
        return hashlib.sha256(query.tobytes()).hexdigest()[:16]
    
    def _is_similar(self, query1: np.ndarray, query2: np.ndarray) -> bool:
        """
        判断两个查询是否相似
        
        Args:
            query1: 查询向量1
            query2: 查询向量2
        
        Returns:
            bool: 是否相似
        """
        # 归一化
        q1_norm = query1 / (np.linalg.norm(query1) + 1e-10)
        q2_norm = query2 / (np.linalg.norm(query2) + 1e-10)
        
        # 计算相似度
        similarity = np.dot(q1_norm, q2_norm)
        
        return similarity >= self.similarity_threshold
    
    def get(self, query: np.ndarray) -> Optional[List[Tuple[str, float]]]:
        """
        从缓存获取结果
        
        Args:
            query: 查询向量
        
        Returns:
            Optional[List[Tuple[str, float]]]: 缓存结果
        """
        query_hash = self._hash_query(query)
        
        # 精确匹配
        if query_hash in self.cache:
            entry = self.cache[query_hash]
            
            # 检查是否过期
            if time.time() - entry['timestamp'] > self.ttl_seconds:
                del self.cache[query_hash]
                self.stats['misses'] += 1
                return None
            
            # 移到末尾（LRU）
            self.cache.move_to_end(query_hash)
            self.stats['hits'] += 1
            return entry['results']
        
        # 相似查询匹配
        for cached_hash, entry in self.cache.items():
            if time.time() - entry['timestamp'] > self.ttl_seconds:
                continue
            
            if self._is_similar(query, entry['query']):
                self.stats['similar_hits'] += 1
                self.stats['hits'] += 1
                return entry['results']
        
        self.stats['misses'] += 1
        return None
    
    def put(
        self,
        query: np.ndarray,
        results: List[Tuple[str, float]]
    ):
        """
        将结果存入缓存
        
        Args:
            query: 查询向量
            results: 搜索结果
        """
        query_hash = self._hash_query(query)
        
        # 检查是否已存在
        if query_hash in self.cache:
            self.cache.move_to_end(query_hash)
            return
        
        # 检查是否需要淘汰
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
            self.stats['evictions'] += 1
        
        # 添加到缓存
        self.cache[query_hash] = {
            'query': query,
            'results': results,
            'timestamp': time.time()
        }
    
    def get_or_compute(
        self,
        query: np.ndarray,
        compute_func: Callable[[], List[Tuple[str, float]]]
    ) -> List[Tuple[str, float]]:
        """
        获取或计算结果
        
        Args:
            query: 查询向量
            compute_func: 计算函数
        
        Returns:
            List[Tuple[str, float]]: 结果
        """
        # 尝试从缓存获取
        cached = self.get(query)
        if cached is not None:
            return cached
        
        # 计算
        results = compute_func()
        
        # 存入缓存
        self.put(query, results)
        
        return results
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
        print("✅ 缓存已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'similar_hits': self.stats['similar_hits'],
            'evictions': self.stats['evictions'],
            'hit_rate': hit_rate
        }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        print(f"\n缓存统计:")
        print(f"  大小: {stats['size']}/{stats['max_size']}")
        print(f"  命中: {stats['hits']}")
        print(f"  未命中: {stats['misses']}")
        print(f"  相似命中: {stats['similar_hits']}")
        print(f"  淘汰: {stats['evictions']}")
        print(f"  命中率: {stats['hit_rate']:.2%}")


class QueryResultCache:
    """
    查询结果缓存
    支持批量操作
    """
    
    def __init__(self, cache: QueryCache):
        """
        初始化结果缓存
        
        Args:
            cache: 查询缓存实例
        """
        self.cache = cache
    
    def batch_get(
        self,
        queries: np.ndarray
    ) -> Tuple[List[Optional[List]], List[int]]:
        """
        批量获取缓存
        
        Args:
            queries: 查询向量矩阵
        
        Returns:
            Tuple[List[Optional[List]], List[int]]: (结果列表, 未命中索引)
        """
        results = []
        miss_indices = []
        
        for i, query in enumerate(queries):
            cached = self.cache.get(query)
            if cached is not None:
                results.append(cached)
            else:
                results.append(None)
                miss_indices.append(i)
        
        return results, miss_indices
    
    def batch_put(
        self,
        queries: np.ndarray,
        results_list: List[List[Tuple[str, float]]]
    ):
        """
        批量存入缓存
        
        Args:
            queries: 查询向量矩阵
            results_list: 结果列表
        """
        for query, results in zip(queries, results_list):
            self.cache.put(query, results)


if __name__ == "__main__":
    # 测试
    print("=== 查询缓存测试 ===")
    
    cache = QueryCache(max_size=100, similarity_threshold=0.99)
    
    # 创建测试数据
    dim = 4096
    query1 = np.random.randn(dim).astype(np.float32)
    query2 = query1 + np.random.randn(dim).astype(np.float32) * 0.01  # 相似查询
    query3 = np.random.randn(dim).astype(np.float32)  # 不同查询
    
    results = [('id1', 0.9), ('id2', 0.8)]
    
    # 测试缓存
    cache.put(query1, results)
    
    # 精确匹配
    cached = cache.get(query1)
    print(f"精确匹配: {'✅' if cached is not None else '❌'}")
    
    # 相似匹配
    cached = cache.get(query2)
    print(f"相似匹配: {'✅' if cached is not None else '❌'}")
    
    # 未命中
    cached = cache.get(query3)
    print(f"未命中: {'✅' if cached is None else '❌'}")
    
    # 统计
    cache.print_stats()
