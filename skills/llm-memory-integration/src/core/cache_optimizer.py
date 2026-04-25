#!/usr/bin/env python3
"""
缓存优化模块 (v4.0)
针对你的设备缓存配置优化

设备缓存配置：
- L1: 80KB (48KB 数据 + 32KB 指令)
- L2: 1.3MB
- L3: 57MB

优化策略：
1. 缓存阻塞（Cache Blocking）
2. 数据预取
3. 内存对齐
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
import os


class CacheOptimizer:
    """
    缓存优化器
    
    根据你的设备缓存配置自动优化数据访问模式
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化缓存优化器
        
        Args:
            config: 缓存配置
        """
        self.config = config or {}
        
        # 缓存大小（字节）
        self.l1_size = self.config.get('l1_size', 80 * 1024)  # 80KB
        self.l2_size = self.config.get('l2_size', 1.3 * 1024 * 1024)  # 1.3MB
        self.l3_size = self.config.get('l3_size', 57 * 1024 * 1024)  # 57MB
        
        # 向量维度
        self.vector_dim = self.config.get('vector_dim', 4096)
        
        # 计算最优块大小
        self.l1_block_size = self._calculate_block_size(self.l1_size * 0.5)
        self.l2_block_size = self._calculate_block_size(self.l2_size * 0.5)
        self.l3_block_size = self._calculate_block_size(self.l3_size * 0.3)
        
        print(f"缓存优化器初始化:")
        print(f"  L1 块大小: {self.l1_block_size}")
        print(f"  L2 块大小: {self.l2_block_size}")
        print(f"  L3 块大小: {self.l3_block_size}")
    
    def _calculate_block_size(self, cache_size: int) -> int:
        """
        计算最优块大小
        
        Args:
            cache_size: 可用缓存大小（字节）
        
        Returns:
            int: 块大小（向量数量）
        """
        # 每个向量的字节数（float32）
        bytes_per_vector = self.vector_dim * 4
        
        # 计算块大小
        block_size = int(cache_size / bytes_per_vector)
        
        # 限制在合理范围
        return max(8, min(block_size, 1024))
    
    def search_with_cache_blocking(
        self,
        query: np.ndarray,
        vectors: np.ndarray,
        top_k: int = 10,
        use_l2: bool = True
    ) -> List[Tuple[int, float]]:
        """
        使用缓存阻塞优化的向量搜索
        
        Args:
            query: 查询向量
            vectors: 向量矩阵
            top_k: 返回数量
            use_l2: 是否使用 L2 缓存优化
        
        Returns:
            List[Tuple[int, float]]: [(索引, 得分), ...]
        """
        n_vectors = len(vectors)
        block_size = self.l2_block_size if use_l2 else self.l1_block_size
        
        all_scores = []
        
        # 分块处理
        for i in range(0, n_vectors, block_size):
            end_idx = min(i + block_size, n_vectors)
            block = vectors[i:end_idx]
            
            # 这个 block 的数据会在缓存中
            scores = self._compute_block_scores(query, block)
            
            # 收集结果
            for j, score in enumerate(scores):
                all_scores.append((i + j, float(score)))
        
        # 排序返回 top_k
        all_scores.sort(key=lambda x: x[1], reverse=True)
        return all_scores[:top_k]
    
    def _compute_block_scores(
        self,
        query: np.ndarray,
        block: np.ndarray
    ) -> np.ndarray:
        """
        计算块内得分（数据在缓存中）
        
        Args:
            query: 查询向量
            block: 向量块
        
        Returns:
            np.ndarray: 得分数组
        """
        # 归一化
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        block_norm = block / (np.linalg.norm(block, axis=1, keepdims=True) + 1e-10)
        
        # 点积
        return np.dot(block_norm, query_norm)
    
    def batch_search_with_cache(
        self,
        queries: np.ndarray,
        vectors: np.ndarray,
        top_k: int = 10
    ) -> List[List[Tuple[int, float]]]:
        """
        批量搜索（优化缓存利用率）
        
        Args:
            queries: 查询向量矩阵 (n_queries, dim)
            vectors: 向量矩阵 (n_vectors, dim)
            top_k: 每个查询返回的数量
        
        Returns:
            List[List[Tuple[int, float]]]: 每个查询的结果
        """
        n_queries = len(queries)
        n_vectors = len(vectors)
        
        # 预归一化所有向量（一次性完成，利用 L3 缓存）
        vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        
        results = []
        
        # 批量处理查询
        for i in range(0, n_queries, self.l2_block_size):
            end_idx = min(i + self.l2_block_size, n_queries)
            query_block = queries[i:end_idx]
            
            # 归一化查询块
            query_block_norm = query_block / (np.linalg.norm(query_block, axis=1, keepdims=True) + 1e-10)
            
            # 批量计算相似度
            scores_block = np.dot(query_block_norm, vectors_norm.T)
            
            # 获取每个查询的 top_k
            for j, scores in enumerate(scores_block):
                top_indices = np.argsort(scores)[::-1][:top_k]
                result = [(int(idx), float(scores[idx])) for idx in top_indices]
                results.append(result)
        
        return results
    
    def optimize_memory_layout(self, vectors: np.ndarray) -> np.ndarray:
        """
        优化内存布局以提高缓存命中率
        
        Args:
            vectors: 原始向量矩阵
        
        Returns:
            np.ndarray: 优化后的向量矩阵
        """
        # 确保是 C 连续布局（行优先）
        if not vectors.flags['C_CONTIGUOUS']:
            vectors = np.ascontiguousarray(vectors)
        
        # 确保数据类型是 float32
        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)
        
        return vectors
    
    def get_cache_stats(self) -> Dict:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 缓存统计
        """
        return {
            'l1_size_kb': self.l1_size / 1024,
            'l2_size_mb': self.l2_size / (1024 * 1024),
            'l3_size_mb': self.l3_size / (1024 * 1024),
            'l1_block_size': self.l1_block_size,
            'l2_block_size': self.l2_block_size,
            'l3_block_size': self.l3_block_size,
            'vector_dim': self.vector_dim,
            'bytes_per_vector': self.vector_dim * 4
        }


class MemoryPool:
    """
    内存池，避免频繁分配
    
    预分配内存，复用缓冲区
    """
    
    def __init__(self, max_vectors: int = 10000, dim: int = 4096):
        """
        初始化内存池
        
        Args:
            max_vectors: 最大向量数
            dim: 向量维度
        """
        self.max_vectors = max_vectors
        self.dim = dim
        
        # 预分配内存
        self.vector_pool = np.zeros((max_vectors, dim), dtype=np.float32)
        self.score_pool = np.zeros(max_vectors, dtype=np.float32)
        self.index_pool = np.zeros(max_vectors, dtype=np.int64)
        
        self.current_index = 0
    
    def get_vector_slice(self, n: int) -> np.ndarray:
        """
        获取向量切片
        
        Args:
            n: 需要的向量数
        
        Returns:
            np.ndarray: 向量切片
        """
        if self.current_index + n > self.max_vectors:
            self.reset()
        
        start = self.current_index
        end = start + n
        self.current_index = end
        
        return self.vector_pool[start:end]
    
    def get_score_slice(self, n: int) -> np.ndarray:
        """
        获取得分切片
        
        Args:
            n: 需要的得分数
        
        Returns:
            np.ndarray: 得分切片
        """
        return self.score_pool[:n]
    
    def get_index_slice(self, n: int) -> np.ndarray:
        """
        获取索引切片
        
        Args:
            n: 需要的索引数
        
        Returns:
            np.ndarray: 索引切片
        """
        return self.index_pool[:n]
    
    def reset(self):
        """重置内存池"""
        self.current_index = 0
    
    def get_stats(self) -> Dict:
        """
        获取内存池统计
        
        Returns:
            Dict: 统计信息
        """
        return {
            'max_vectors': self.max_vectors,
            'dim': self.dim,
            'current_index': self.current_index,
            'memory_mb': (self.max_vectors * self.dim * 4) / (1024 * 1024)
        }


# 便捷函数
def get_cache_optimizer(config: Optional[Dict] = None) -> CacheOptimizer:
    """获取缓存优化器实例"""
    return CacheOptimizer(config)


def get_memory_pool(max_vectors: int = 10000, dim: int = 4096) -> MemoryPool:
    """获取内存池实例"""
    return MemoryPool(max_vectors, dim)
