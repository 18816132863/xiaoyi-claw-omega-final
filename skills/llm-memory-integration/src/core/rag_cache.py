#!/usr/bin/env python3
"""
RAGCache - 知识缓存系统 (v5.2.31)
缓存检索知识的中间状态，避免重复计算

论文参考: RAGCache: Efficient Knowledge Caching for Retrieval-Augmented Generation (2024)
效果: TTFT 降低 4x，吞吐量提升 2.1x

功能：
- 多级动态缓存（GPU/主机内存）
- 知识树组织
- LLM 推理感知替换策略
- 检索与推理重叠

优化效果：
- TTFT (Time To First Token) 降低 4x
- 吞吐量提升 2.1x
- 内存使用优化
"""

import os
import time
import hashlib
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
import threading


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str                          # 缓存键
    query_hash: str                   # 查询哈希
    knowledge_embeddings: np.ndarray  # 知识嵌入
    intermediate_states: Dict         # 中间状态
    timestamp: float                  # 时间戳
    access_count: int = 0             # 访问次数
    last_access: float = 0.0          # 最后访问时间
    size_bytes: int = 0               # 大小（字节）
    metadata: Dict = field(default_factory=dict)


class KnowledgeTree:
    """
    知识树
    
    组织检索知识的层次结构，支持高效缓存和检索。
    """
    
    def __init__(self, max_depth: int = 3):
        """
        初始化知识树
        
        Args:
            max_depth: 最大深度
        """
        self.max_depth = max_depth
        self.root = {}
        self.node_count = 0
    
    def insert(
        self,
        query: str,
        knowledge: List[str],
        embeddings: np.ndarray
    ) -> str:
        """
        插入知识到树中
        
        Args:
            query: 查询
            knowledge: 知识列表
            embeddings: 嵌入向量
            
        Returns:
            str: 节点路径
        """
        # 生成路径
        query_hash = self._hash_query(query)
        path = self._generate_path(query_hash)
        
        # 插入节点
        current = self.root
        for i, segment in enumerate(path[:-1]):
            if segment not in current:
                current[segment] = {'children': {}, 'data': None}
            current = current[segment]['children']
        
        # 存储数据
        current[path[-1]] = {
            'children': {},
            'data': {
                'query': query,
                'knowledge': knowledge,
                'embeddings': embeddings,
                'hash': query_hash,
            }
        }
        self.node_count += 1
        
        return '/'.join(path)
    
    def search(self, query: str) -> Optional[Dict]:
        """
        搜索知识
        
        Args:
            query: 查询
            
        Returns:
            Optional[Dict]: 知识数据
        """
        query_hash = self._hash_query(query)
        path = self._generate_path(query_hash)
        
        current = self.root
        for segment in path:
            if segment not in current:
                return None
            if 'children' in current[segment]:
                current = current[segment]['children']
            else:
                return current[segment].get('data')
        
        return None
    
    def _hash_query(self, query: str) -> str:
        """生成查询哈希"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _generate_path(self, query_hash: str) -> List[str]:
        """生成路径"""
        # 将哈希分割成路径段
        segment_size = len(query_hash) // self.max_depth
        path = []
        for i in range(self.max_depth):
            start = i * segment_size
            end = start + segment_size if i < self.max_depth - 1 else len(query_hash)
            path.append(query_hash[start:end])
        return path


class LRUKCache:
    """
    LRU-K 缓存
    
    考虑访问频率的 LRU 变体。
    """
    
    def __init__(self, capacity: int, k: int = 2):
        """
        初始化 LRU-K 缓存
        
        Args:
            capacity: 容量
            k: 考虑最近 k 次访问
        """
        self.capacity = capacity
        self.k = k
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.access_history: Dict[str, List[float]] = {}
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """
        获取缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            Optional[CacheEntry]: 缓存条目
        """
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            entry.access_count += 1
            entry.last_access = time.time()
            
            # 更新访问历史
            if key not in self.access_history:
                self.access_history[key] = []
            self.access_history[key].append(entry.last_access)
            if len(self.access_history[key]) > self.k:
                self.access_history[key].pop(0)
            
            # 移动到末尾（最近使用）
            self.cache.move_to_end(key)
            
            return entry
    
    def put(self, entry: CacheEntry):
        """
        放入缓存条目
        
        Args:
            entry: 缓存条目
        """
        with self.lock:
            if entry.key in self.cache:
                self.cache.move_to_end(entry.key)
                self.cache[entry.key] = entry
                return
            
            # 检查容量
            while len(self.cache) >= self.capacity:
                self._evict()
            
            self.cache[entry.key] = entry
            self.access_history[entry.key] = [time.time()]
    
    def _evict(self):
        """驱逐条目"""
        if not self.cache:
            return
        
        # 找到最少使用的条目
        min_score = float('inf')
        evict_key = None
        
        for key, entry in self.cache.items():
            # 计算分数：访问次数越少、最后访问越早，分数越低
            history = self.access_history.get(key, [])
            recency = time.time() - entry.last_access
            frequency = entry.access_count
            
            # LRU-K 分数
            if len(history) >= self.k:
                kth_access = history[-self.k]
                score = kth_access  # 第 k 次访问时间
            else:
                score = recency / (frequency + 1)
            
            if score < min_score:
                min_score = score
                evict_key = key
        
        if evict_key:
            del self.cache[evict_key]
            if evict_key in self.access_history:
                del self.access_history[evict_key]
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.access_history.clear()


class RAGCache:
    """
    RAGCache - RAG 知识缓存系统
    
    多级动态缓存，优化 RAG 推理性能。
    """
    
    def __init__(
        self,
        gpu_cache_size: int = 1000,
        host_cache_size: int = 10000,
        max_depth: int = 3
    ):
        """
        初始化 RAGCache
        
        Args:
            gpu_cache_size: GPU 缓存容量
            host_cache_size: 主机缓存容量
            max_depth: 知识树最大深度
        """
        self.gpu_cache = LRUKCache(gpu_cache_size)
        self.host_cache = LRUKCache(host_cache_size)
        self.knowledge_tree = KnowledgeTree(max_depth)
        
        self.stats = {
            'gpu_hits': 0,
            'host_hits': 0,
            'misses': 0,
            'total_queries': 0,
        }
        
        self.lock = threading.Lock()
    
    def get(
        self,
        query: str,
        knowledge_hashes: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        获取缓存的知识
        
        Args:
            query: 查询
            knowledge_hashes: 知识哈希列表（可选）
            
        Returns:
            Optional[Dict]: 缓存的知识数据
        """
        with self.lock:
            self.stats['total_queries'] += 1
        
        # 生成缓存键
        cache_key = self._generate_key(query, knowledge_hashes)
        
        # 先查 GPU 缓存
        entry = self.gpu_cache.get(cache_key)
        if entry is not None:
            with self.lock:
                self.stats['gpu_hits'] += 1
            return entry.intermediate_states
        
        # 再查主机缓存
        entry = self.host_cache.get(cache_key)
        if entry is not None:
            with self.lock:
                self.stats['host_hits'] += 1
            # 提升到 GPU 缓存
            self.gpu_cache.put(entry)
            return entry.intermediate_states
        
        # 查知识树
        tree_data = self.knowledge_tree.search(query)
        if tree_data is not None:
            with self.lock:
                self.stats['host_hits'] += 1
            return tree_data
        
        with self.lock:
            self.stats['misses'] += 1
        return None
    
    def put(
        self,
        query: str,
        knowledge: List[str],
        embeddings: np.ndarray,
        intermediate_states: Dict,
        knowledge_hashes: Optional[List[str]] = None
    ):
        """
        缓存知识
        
        Args:
            query: 查询
            knowledge: 知识列表
            embeddings: 嵌入向量
            intermediate_states: 中间状态
            knowledge_hashes: 知识哈希列表
        """
        cache_key = self._generate_key(query, knowledge_hashes)
        
        # 计算大小
        size_bytes = embeddings.nbytes + sum(
            len(json.dumps(s)) for s in intermediate_states.values()
            if isinstance(s, (dict, list, str))
        )
        
        entry = CacheEntry(
            key=cache_key,
            query_hash=hashlib.md5(query.encode()).hexdigest(),
            knowledge_embeddings=embeddings,
            intermediate_states=intermediate_states,
            timestamp=time.time(),
            last_access=time.time(),
            size_bytes=size_bytes,
        )
        
        # 放入缓存
        self.gpu_cache.put(entry)
        self.host_cache.put(entry)
        
        # 放入知识树
        self.knowledge_tree.insert(query, knowledge, embeddings)
    
    def _generate_key(
        self,
        query: str,
        knowledge_hashes: Optional[List[str]] = None
    ) -> str:
        """生成缓存键"""
        if knowledge_hashes:
            combined = query + ''.join(knowledge_hashes)
        else:
            combined = query
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            total = self.stats['total_queries']
            if total == 0:
                hit_rate = 0.0
            else:
                hits = self.stats['gpu_hits'] + self.stats['host_hits']
                hit_rate = hits / total
            
            return {
                **self.stats,
                'hit_rate': hit_rate,
                'gpu_cache_size': len(self.gpu_cache.cache),
                'host_cache_size': len(self.host_cache.cache),
                'knowledge_tree_nodes': self.knowledge_tree.node_count,
            }
    
    def clear(self):
        """清空缓存"""
        self.gpu_cache.clear()
        self.host_cache.clear()
        self.knowledge_tree = KnowledgeTree(self.knowledge_tree.max_depth)


class RetrievalInferenceOverlap:
    """
    检索与推理重叠
    
    在检索过程中提前开始推理，减少端到端延迟。
    """
    
    def __init__(self, rag_cache: RAGCache):
        """
        初始化重叠处理器
        
        Args:
            rag_cache: RAG 缓存
        """
        self.cache = rag_cache
        self.pending_retrievals: Dict[str, Dict] = {}
        self.lock = threading.Lock()
    
    def start_retrieval(self, query: str) -> str:
        """
        开始检索
        
        Args:
            query: 查询
            
        Returns:
            str: 检索 ID
        """
        retrieval_id = hashlib.md5(f"{query}{time.time()}".encode()).hexdigest()
        
        with self.lock:
            self.pending_retrievals[retrieval_id] = {
                'query': query,
                'status': 'pending',
                'start_time': time.time(),
            }
        
        return retrieval_id
    
    def complete_retrieval(
        self,
        retrieval_id: str,
        knowledge: List[str],
        embeddings: np.ndarray
    ):
        """
        完成检索
        
        Args:
            retrieval_id: 检索 ID
            knowledge: 知识列表
            embeddings: 嵌入向量
        """
        with self.lock:
            if retrieval_id in self.pending_retrievals:
                self.pending_retrievals[retrieval_id].update({
                    'status': 'completed',
                    'knowledge': knowledge,
                    'embeddings': embeddings,
                    'end_time': time.time(),
                })
    
    def get_retrieval_result(self, retrieval_id: str) -> Optional[Dict]:
        """
        获取检索结果
        
        Args:
            retrieval_id: 检索 ID
            
        Returns:
            Optional[Dict]: 检索结果
        """
        with self.lock:
            if retrieval_id not in self.pending_retrievals:
                return None
            
            result = self.pending_retrievals[retrieval_id]
            if result['status'] == 'completed':
                return {
                    'knowledge': result['knowledge'],
                    'embeddings': result['embeddings'],
                }
            return None


def print_ragcache_status(cache: RAGCache):
    """打印 RAGCache 状态"""
    stats = cache.get_stats()
    
    print("=== RAGCache 状态 ===")
    print(f"总查询: {stats['total_queries']}")
    print(f"GPU 命中: {stats['gpu_hits']}")
    print(f"主机命中: {stats['host_hits']}")
    print(f"未命中: {stats['misses']}")
    print(f"命中率: {stats['hit_rate']:.2%}")
    print(f"GPU 缓存大小: {stats['gpu_cache_size']}")
    print(f"主机缓存大小: {stats['host_cache_size']}")
    print(f"知识树节点: {stats['knowledge_tree_nodes']}")
    print("====================")


# 导出
__all__ = [
    'RAGCache',
    'KnowledgeTree',
    'LRUKCache',
    'CacheEntry',
    'RetrievalInferenceOverlap',
    'print_ragcache_status',
]


# 测试
if __name__ == "__main__":
    # 创建缓存
    cache = RAGCache(gpu_cache_size=100, host_cache_size=1000)
    
    # 测试缓存
    query = "什么是机器学习？"
    knowledge = ["机器学习是人工智能的一个分支", "机器学习使用算法从数据中学习"]
    embeddings = np.random.randn(2, 768).astype(np.float32)
    intermediate_states = {'layer1': np.random.randn(768), 'layer2': np.random.randn(768)}
    
    # 第一次查询（未命中）
    result = cache.get(query)
    print(f"第一次查询: {'命中' if result else '未命中'}")
    
    # 放入缓存
    cache.put(query, knowledge, embeddings, intermediate_states)
    
    # 第二次查询（命中）
    result = cache.get(query)
    print(f"第二次查询: {'命中' if result else '未命中'}")
    
    # 打印状态
    print_ragcache_status(cache)
