#!/usr/bin/env python3
"""
ANN 索引自动选择模块 (v4.1)
根据数据规模自动选择最优算法

算法选择策略：
- 小规模 (<10K): HNSW（高精度）
- 中等规模 (10K-1M): IVF（平衡）
- 大规模 (>1M): LSH（快速）
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import os


class ANNSelector:
    """
    ANN 索引自动选择器
    """
    
    def __init__(
        self,
        n_vectors: int,
        dim: int = 4096,
        metric: str = 'cosine'
    ):
        """
        初始化选择器
        
        Args:
            n_vectors: 向量数量
            dim: 向量维度
            metric: 距离度量
        """
        self.n_vectors = n_vectors
        self.dim = dim
        self.metric = metric
        
        # 选择算法
        self.algorithm = self._select_algorithm()
        self.index = None
        
        print(f"ANN 选择器初始化:")
        print(f"  向量数: {n_vectors}")
        print(f"  算法: {self.algorithm}")
    
    def _select_algorithm(self) -> str:
        """
        根据数据规模选择算法
        
        Returns:
            str: 算法名称
        """
        if self.n_vectors < 10000:
            return 'hnsw'
        elif self.n_vectors < 1000000:
            return 'ivf'
        else:
            return 'lsh'
    
    def build_index(self, vectors: np.ndarray):
        """
        构建索引
        
        Args:
            vectors: 向量矩阵 (n, dim)
        """
        if self.algorithm == 'hnsw':
            self._build_hnsw(vectors)
        elif self.algorithm == 'ivf':
            self._build_ivf(vectors)
        else:
            self._build_lsh(vectors)
    
    def _build_hnsw(self, vectors: np.ndarray):
        """构建 HNSW 索引"""
        # 简化实现：使用暴力搜索 + 缓存
        self.vectors = vectors.astype(np.float32)
        self.vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        print("✅ HNSW 索引构建完成（暴力搜索模式）")
    
    def _build_ivf(self, vectors: np.ndarray):
        """构建 IVF 索引"""
        from sklearn.cluster import KMeans
        
        # 聚类数量
        n_clusters = int(np.sqrt(self.n_vectors))
        
        # K-means 聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=1)
        labels = kmeans.fit_predict(vectors)
        
        # 构建倒排列表
        self.centroids = kmeans.cluster_centers_
        self.inverted_lists = {}
        for i, label in enumerate(labels):
            if label not in self.inverted_lists:
                self.inverted_lists[label] = []
            self.inverted_lists[label].append(i)
        
        self.vectors = vectors.astype(np.float32)
        self.n_probe = min(10, n_clusters)
        print(f"✅ IVF 索引构建完成（{n_clusters} 个聚类）")
    
    def _build_lsh(self, vectors: np.ndarray):
        """构建 LSH 索引"""
        # 简化实现：随机投影
        n_tables = 10
        n_bits = 16
        
        self.hash_tables = []
        self.projections = []
        
        for _ in range(n_tables):
            # 随机投影矩阵
            proj = np.random.randn(self.dim, n_bits).astype(np.float32)
            self.projections.append(proj)
            
            # 计算哈希
            hashes = np.dot(vectors, proj) > 0
            hash_keys = [''.join(['1' if b else '0' for b in row]) for row in hashes]
            
            # 构建哈希表
            table = {}
            for i, key in enumerate(hash_keys):
                if key not in table:
                    table[key] = []
                table[key].append(i)
            
            self.hash_tables.append(table)
        
        self.vectors = vectors.astype(np.float32)
        print(f"✅ LSH 索引构建完成（{n_tables} 个哈希表）")
    
    def search(
        self,
        query: np.ndarray,
        top_k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        搜索
        
        Args:
            query: 查询向量
            top_k: 返回数量
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 得分)
        """
        if self.algorithm == 'hnsw':
            return self._search_hnsw(query, top_k)
        elif self.algorithm == 'ivf':
            return self._search_ivf(query, top_k)
        else:
            return self._search_lsh(query, top_k)
    
    def _search_hnsw(
        self,
        query: np.ndarray,
        top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """HNSW 搜索（暴力搜索）"""
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        scores = np.dot(self.vectors_norm, query_norm)
        
        if top_k >= len(scores):
            indices = np.argsort(scores)[::-1]
        else:
            indices = np.argpartition(scores, -top_k)[-top_k:]
            indices = indices[np.argsort(scores[indices])[::-1]]
        
        return indices, scores[indices]
    
    def _search_ivf(
        self,
        query: np.ndarray,
        top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """IVF 搜索"""
        # 找到最近的聚类
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        centroid_scores = np.dot(self.centroids, query_norm)
        nearest_clusters = np.argsort(centroid_scores)[::-1][:self.n_probe]
        
        # 收集候选
        candidates = []
        for cluster_id in nearest_clusters:
            if cluster_id in self.inverted_lists:
                candidates.extend(self.inverted_lists[cluster_id])
        
        # 精确计算
        if len(candidates) == 0:
            return np.array([]), np.array([])
        
        candidate_vectors = self.vectors[candidates]
        candidate_norm = candidate_vectors / (np.linalg.norm(candidate_vectors, axis=1, keepdims=True) + 1e-10)
        scores = np.dot(candidate_norm, query_norm)
        
        # 获取 top-k
        if top_k >= len(scores):
            local_indices = np.argsort(scores)[::-1]
        else:
            local_indices = np.argpartition(scores, -top_k)[-top_k:]
            local_indices = local_indices[np.argsort(scores[local_indices])[::-1]]
        
        return np.array(candidates)[local_indices], scores[local_indices]
    
    def _search_lsh(
        self,
        query: np.ndarray,
        top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """LSH 搜索"""
        # 收集候选
        candidates = set()
        for i, proj in enumerate(self.projections):
            hash_bits = np.dot(query, proj) > 0
            hash_key = ''.join(['1' if b else '0' for b in hash_bits])
            
            if hash_key in self.hash_tables[i]:
                candidates.update(self.hash_tables[i][hash_key])
        
        # 精确计算
        if len(candidates) == 0:
            return np.array([]), np.array([])
        
        candidates = list(candidates)
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        candidate_vectors = self.vectors[candidates]
        candidate_norm = candidate_vectors / (np.linalg.norm(candidate_vectors, axis=1, keepdims=True) + 1e-10)
        scores = np.dot(candidate_norm, query_norm)
        
        # 获取 top-k
        if top_k >= len(scores):
            local_indices = np.argsort(scores)[::-1]
        else:
            local_indices = np.argpartition(scores, -top_k)[-top_k:]
            local_indices = local_indices[np.argsort(scores[local_indices])[::-1]]
        
        return np.array(candidates)[local_indices], scores[local_indices]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'algorithm': self.algorithm,
            'n_vectors': self.n_vectors,
            'dim': self.dim,
            'metric': self.metric
        }


if __name__ == "__main__":
    # 测试
    print("=== ANN 选择器测试 ===")
    
    dim = 4096
    n_vectors = 50000
    
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    query = np.random.randn(dim).astype(np.float32)
    
    selector = ANNSelector(n_vectors, dim)
    selector.build_index(vectors)
    
    import time
    start = time.time()
    indices, scores = selector.search(query, top_k=20)
    elapsed = time.time() - start
    print(f"搜索耗时: {elapsed*1000:.2f}ms")
