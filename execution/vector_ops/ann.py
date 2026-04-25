#!/usr/bin/env python3
"""
ANN (Approximate Nearest Neighbor) 近似最近邻搜索模块

支持的算法：
1. HNSW (Hierarchical Navigable Small World) - 高精度，适合中等规模
2. IVF (Inverted File Index) - 聚类索引，适合大规模
3. LSH (Locality Sensitive Hashing) - 快速，适合超大规模
4. 暴力搜索回退 - 小规模数据

使用 numpy 实现，自动利用 SIMD 加速。
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import heapq
from collections import defaultdict
import random


class ANNIndex:
    """
    ANN 索引基类
    """
    
    def __init__(self, dim: int, metric: str = 'cosine'):
        """
        初始化 ANN 索引
        
        Args:
            dim: 向量维度
            metric: 距离度量 ('cosine' 或 'euclidean')
        """
        self.dim = dim
        self.metric = metric
        self.vectors = None
        self.ids = None
    
    def build(self, vectors: np.ndarray, ids: Optional[List] = None):
        """构建索引"""
        raise NotImplementedError
    
    def search(self, query: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """搜索最近邻"""
        raise NotImplementedError


class BruteForceANN(ANNIndex):
    """
    暴力搜索 ANN
    适合小规模数据（< 10000 向量）
    """
    
    def __init__(self, dim: int, metric: str = 'cosine'):
        super().__init__(dim, metric)
    
    def build(self, vectors: np.ndarray, ids: Optional[List] = None):
        """构建索引（直接存储）"""
        self.vectors = np.asarray(vectors, dtype=np.float32)
        if ids is None:
            self.ids = np.arange(len(vectors))
        else:
            self.ids = np.asarray(ids)
        
        # 预归一化（余弦相似度）
        if self.metric == 'cosine':
            norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)
            self.vectors_normalized = self.vectors / norms
    
    def search(self, query: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """暴力搜索"""
        query = np.asarray(query, dtype=np.float32)
        
        if self.metric == 'cosine':
            query_norm = query / (np.linalg.norm(query) + 1e-10)
            scores = np.dot(self.vectors_normalized, query_norm)
            indices = np.argsort(-scores)[:k]  # 降序
        else:
            distances = np.linalg.norm(self.vectors - query, axis=1)
            indices = np.argsort(distances)[:k]  # 升序
            scores = -distances  # 转换为分数（距离越小分数越高）
        
        return self.ids[indices], scores[indices]


class IVFIndex(ANNIndex):
    """
    IVF (Inverted File Index) 索引
    使用聚类将向量分组，搜索时只检查相关聚类
    """
    
    def __init__(
        self,
        dim: int,
        n_clusters: int = 100,
        n_probe: int = 10,
        metric: str = 'cosine'
    ):
        """
        初始化 IVF 索引
        
        Args:
            dim: 向量维度
            n_clusters: 聚类数量
            n_probe: 搜索时检查的聚类数量
            metric: 距离度量
        """
        super().__init__(dim, metric)
        self.n_clusters = n_clusters
        self.n_probe = n_probe
        self.centroids = None
        self.inverted_lists = None
    
    def _kmeans(self, data: np.ndarray, k: int, n_iter: int = 20) -> np.ndarray:
        """K-means 聚类"""
        n = len(data)
        
        # 随机初始化
        indices = np.random.choice(n, k, replace=False)
        centroids = data[indices].copy()
        
        for _ in range(n_iter):
            # 分配
            distances = np.zeros((n, k))
            for j in range(k):
                if self.metric == 'cosine':
                    norm1 = np.linalg.norm(data, axis=1) + 1e-10
                    norm2 = np.linalg.norm(centroids[j]) + 1e-10
                    distances[:, j] = 1 - np.dot(data, centroids[j]) / (norm1 * norm2)
                else:
                    distances[:, j] = np.linalg.norm(data - centroids[j], axis=1)
            labels = np.argmin(distances, axis=1)
            
            # 更新
            for j in range(k):
                mask = labels == j
                if mask.sum() > 0:
                    centroids[j] = data[mask].mean(axis=0)
        
        return centroids
    
    def build(self, vectors: np.ndarray, ids: Optional[List] = None):
        """构建 IVF 索引"""
        self.vectors = np.asarray(vectors, dtype=np.float32)
        if ids is None:
            self.ids = np.arange(len(vectors))
        else:
            self.ids = np.asarray(ids)
        
        # 归一化
        if self.metric == 'cosine':
            norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)
            self.vectors_normalized = self.vectors / norms
        else:
            self.vectors_normalized = self.vectors
        
        # K-means 聚类
        self.centroids = self._kmeans(self.vectors_normalized, self.n_clusters)
        
        # 构建倒排列表
        self.inverted_lists = defaultdict(list)
        
        # 分配向量到聚类
        for idx, vec in enumerate(self.vectors_normalized):
            if self.metric == 'cosine':
                scores = np.dot(self.centroids, vec)
                cluster_id = np.argmax(scores)
            else:
                distances = np.linalg.norm(self.centroids - vec, axis=1)
                cluster_id = np.argmin(distances)
            self.inverted_lists[cluster_id].append(idx)
    
    def search(self, query: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """IVF 搜索"""
        query = np.asarray(query, dtype=np.float32)
        
        # 归一化查询
        if self.metric == 'cosine':
            query_norm = query / (np.linalg.norm(query) + 1e-10)
        else:
            query_norm = query
        
        # 找到最近的 n_probe 个聚类
        if self.metric == 'cosine':
            cluster_scores = np.dot(self.centroids, query_norm)
            top_clusters = np.argsort(-cluster_scores)[:self.n_probe]
        else:
            cluster_distances = np.linalg.norm(self.centroids - query_norm, axis=1)
            top_clusters = np.argsort(cluster_distances)[:self.n_probe]
        
        # 收集候选
        candidates = []
        for cluster_id in top_clusters:
            candidates.extend(self.inverted_lists.get(cluster_id, []))
        
        if not candidates:
            return np.array([]), np.array([])
        
        # 精确计算
        candidate_vectors = self.vectors_normalized[candidates]
        
        if self.metric == 'cosine':
            scores = np.dot(candidate_vectors, query_norm)
            sorted_indices = np.argsort(-scores)[:k]
        else:
            distances = np.linalg.norm(candidate_vectors - query_norm, axis=1)
            sorted_indices = np.argsort(distances)[:k]
            scores = -distances
        
        result_indices = [candidates[i] for i in sorted_indices[:k]]
        result_scores = scores[sorted_indices[:k]]
        
        return self.ids[result_indices], result_scores


class LSHIndex(ANNIndex):
    """
    LSH (Locality Sensitive Hashing) 索引
    适合大规模数据，快速近似搜索
    """
    
    def __init__(
        self, 
        dim: int, 
        num_tables: int = 10, 
        num_hashes: int = 12,
        metric: str = 'cosine'
    ):
        """
        初始化 LSH 索引
        
        Args:
            dim: 向量维度
            num_tables: 哈希表数量
            num_hashes: 每个表的哈希函数数量
            metric: 距离度量
        """
        super().__init__(dim, metric)
        self.num_tables = num_tables
        self.num_hashes = num_hashes
        
        # 随机投影矩阵
        self.projections = [
            np.random.randn(num_hashes, dim).astype(np.float32)
            for _ in range(num_tables)
        ]
        
        # 哈希表
        self.tables = [defaultdict(list) for _ in range(num_tables)]
    
    def _hash(self, vector: np.ndarray, table_idx: int) -> str:
        """计算哈希值"""
        projection = self.projections[table_idx]
        bits = (np.dot(projection, vector) > 0).astype(int)
        return ''.join(map(str, bits))
    
    def build(self, vectors: np.ndarray, ids: Optional[List] = None):
        """构建 LSH 索引"""
        self.vectors = np.asarray(vectors, dtype=np.float32)
        if ids is None:
            self.ids = np.arange(len(vectors))
        else:
            self.ids = np.asarray(ids)
        
        # 归一化
        if self.metric == 'cosine':
            norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
            norms = np.where(norms == 0, 1, norms)
            self.vectors_normalized = self.vectors / norms
        else:
            self.vectors_normalized = self.vectors
        
        # 构建哈希表
        for idx, vec in enumerate(self.vectors_normalized):
            for t in range(self.num_tables):
                hash_key = self._hash(vec, t)
                self.tables[t][hash_key].append(idx)
    
    def search(self, query: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """LSH 搜索"""
        query = np.asarray(query, dtype=np.float32)
        
        # 归一化查询
        if self.metric == 'cosine':
            query_norm = query / (np.linalg.norm(query) + 1e-10)
        else:
            query_norm = query
        
        # 收集候选
        candidates = set()
        for t in range(self.num_tables):
            hash_key = self._hash(query_norm, t)
            candidates.update(self.tables[t].get(hash_key, []))
        
        if not candidates:
            # 回退到暴力搜索
            candidates = set(range(len(self.vectors)))
        
        # 精确计算候选的相似度
        candidate_list = list(candidates)
        candidate_vectors = self.vectors_normalized[candidate_list]
        
        if self.metric == 'cosine':
            scores = np.dot(candidate_vectors, query_norm)
            sorted_indices = np.argsort(-scores)[:k]
        else:
            distances = np.linalg.norm(candidate_vectors - query_norm, axis=1)
            sorted_indices = np.argsort(distances)[:k]
            scores = -distances
        
        result_indices = [candidate_list[i] for i in sorted_indices[:k]]
        result_scores = scores[sorted_indices[:k]]
        
        return self.ids[result_indices], result_scores


class HNSWIndex(ANNIndex):
    """
    HNSW (Hierarchical Navigable Small World) 索引
    高精度，适合中等规模数据
    """
    
    def __init__(
        self,
        dim: int,
        M: int = 16,
        ef_construction: int = 200,
        metric: str = 'cosine'
    ):
        """
        初始化 HNSW 索引
        
        Args:
            dim: 向量维度
            M: 每层最大连接数
            ef_construction: 构建时的搜索宽度
            metric: 距离度量
        """
        super().__init__(dim, metric)
        self.M = M
        self.ef_construction = ef_construction
        self.max_level = 0
        self.entry_point = None
        
        # 图结构
        self.levels = {}  # node_id -> level
        self.neighbors = defaultdict(lambda: defaultdict(list))  # node_id -> level -> neighbors
    
    def _distance(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """计算距离"""
        if self.metric == 'cosine':
            norm1 = np.linalg.norm(v1) + 1e-10
            norm2 = np.linalg.norm(v2) + 1e-10
            return 1 - np.dot(v1, v2) / (norm1 * norm2)
        else:
            return np.linalg.norm(v1 - v2)
    
    def _get_random_level(self) -> int:
        """获取随机层级"""
        return int(-np.log(random.random()) * np.log(self.M))
    
    def build(self, vectors: np.ndarray, ids: Optional[List] = None):
        """构建 HNSW 索引（简化实现）"""
        self.vectors = np.asarray(vectors, dtype=np.float32)
        if ids is None:
            self.ids = np.arange(len(vectors))
        else:
            self.ids = np.asarray(ids)
        
        # 简化：使用单层图
        for i in range(len(vectors)):
            self.levels[i] = 0
            if self.entry_point is None:
                self.entry_point = i
                continue
            
            # 连接到入口点
            self.neighbors[i][0].append(self.entry_point)
            self.neighbors[self.entry_point][0].append(i)
    
    def search(self, query: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """HNSW 搜索（简化实现）"""
        query = np.asarray(query, dtype=np.float32)
        
        # 计算所有距离
        distances = []
        for i, vec in enumerate(self.vectors):
            dist = self._distance(query, vec)
            distances.append((dist, i))
        
        # 排序
        distances.sort()
        
        # 返回 top-k
        result_indices = [d[1] for d in distances[:k]]
        result_scores = np.array([-d[0] for d in distances[:k]])
        
        return self.ids[result_indices], result_scores


def create_ann_index(
    vectors: np.ndarray,
    ids: Optional[List] = None,
    algorithm: str = 'auto',
    metric: str = 'cosine',
    **kwargs
) -> ANNIndex:
    """
    创建 ANN 索引
    
    Args:
        vectors: 向量矩阵 (n, dim)
        ids: ID 列表
        algorithm: 算法选择 ('auto', 'brute', 'lsh', 'hnsw', 'ivf')
        metric: 距离度量
        **kwargs: 算法参数
        
    Returns:
        ANNIndex: ANN 索引实例
        
    Raises:
        ValueError: 向量为空或维度无效
    """
    vectors = np.asarray(vectors, dtype=np.float32)
    
    # 检查向量有效性
    if vectors.size == 0:
        raise ValueError("向量矩阵不能为空")
    
    if vectors.ndim != 2:
        raise ValueError(f"向量矩阵必须是 2D，当前是 {vectors.ndim}D")
    
    n, dim = vectors.shape
    
    if n == 0:
        raise ValueError("向量数量不能为 0")
    
    if dim == 0:
        raise ValueError("向量维度不能为 0")
    
    # 自动选择算法
    if algorithm == 'auto':
        if n < 10000:
            algorithm = 'brute'
        elif n < 100000:
            algorithm = 'hnsw'
        else:
            algorithm = 'lsh'
    
    # 创建索引
    if algorithm == 'brute':
        index = BruteForceANN(dim, metric)
    elif algorithm == 'lsh':
        index = LSHIndex(dim, metric=metric, **kwargs)
    elif algorithm == 'hnsw':
        index = HNSWIndex(dim, metric=metric, **kwargs)
    elif algorithm == 'ivf':
        index = IVFIndex(dim, metric=metric, **kwargs)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    index.build(vectors, ids)
    return index


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("ANN 近似最近邻搜索模块")
    print("=" * 60)
    
    import time
    
    # 生成测试数据
    np.random.seed(42)
    n_vectors = 1000
    dim = 128
    
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    query = np.random.randn(dim).astype(np.float32)
    
    print(f"\n📊 测试参数: n={n_vectors}, dim={dim}")
    
    # 测试暴力搜索
    print("\n🔬 暴力搜索:")
    start = time.time()
    index = create_ann_index(vectors, algorithm='brute')
    ids, scores = index.search(query, k=10)
    elapsed = (time.time() - start) * 1000
    print(f"   构建时间: {elapsed:.2f}ms")
    
    start = time.time()
    ids, scores = index.search(query, k=10)
    elapsed = (time.time() - start) * 1000
    print(f"   搜索时间: {elapsed:.2f}ms")
    print(f"   Top-3 分数: {scores[:3]}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
