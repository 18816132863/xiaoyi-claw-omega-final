#!/usr/bin/env python3
"""
向量量化模块
支持多种量化方法以减少内存占用和加速搜索

支持的量化方法：
1. FP16 (半精度浮点) - 2x 压缩，精度损失小
2. INT8 (8-bit 整数) - 4x 压缩，精度损失中等
3. PQ (Product Quantization) - 乘积量化，高压缩比
4. SQ (Scalar Quantization) - 标量量化
5. OPQ (Optimized Product Quantization) - 优化乘积量化
6. Binary Quantization - 二值量化
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from collections import defaultdict


class FP16Quantizer:
    """
    FP16 半精度量化器
    将 FP32 向量转换为 FP16，压缩 2x
    """
    
    def __init__(self):
        """初始化 FP16 量化器"""
        pass
    
    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """
        编码为 FP16
        
        Args:
            vectors: FP32 向量 (n, dim)
            
        Returns:
            np.ndarray: FP16 向量
        """
        return np.asarray(vectors, dtype=np.float16)
    
    def decode(self, vectors: np.ndarray) -> np.ndarray:
        """
        解码为 FP32
        
        Args:
            vectors: FP16 向量
            
        Returns:
            np.ndarray: FP32 向量
        """
        return np.asarray(vectors, dtype=np.float32)


class INT8Quantizer:
    """
    INT8 整数量化器
    将浮点向量量化为 8-bit 整数，压缩 4x
    """
    
    def __init__(self, symmetric: bool = True):
        """
        初始化 INT8 量化器
        
        Args:
            symmetric: 是否使用对称量化
        """
        self.symmetric = symmetric
        self.scale = None
        self.zero_point = None
    
    def fit(self, vectors: np.ndarray):
        """
        训练量化器
        
        Args:
            vectors: 训练向量 (n, dim)
        """
        vectors = np.asarray(vectors, dtype=np.float32)
        
        if self.symmetric:
            # 对称量化：[-127, 127]
            self.scale = np.max(np.abs(vectors)) / 127.0
            self.zero_point = 0
        else:
            # 非对称量化：[0, 255]
            self.min_val = vectors.min()
            self.max_val = vectors.max()
            self.scale = (self.max_val - self.min_val) / 255.0
            self.zero_point = int(-self.min_val / self.scale)
    
    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """
        编码为 INT8
        
        Args:
            vectors: 浮点向量 (n, dim)
            
        Returns:
            np.ndarray: INT8 向量
        """
        vectors = np.asarray(vectors, dtype=np.float32)
        
        if self.symmetric:
            quantized = np.clip(np.round(vectors / self.scale), -127, 127)
        else:
            quantized = np.clip(np.round(vectors / self.scale + self.zero_point), 0, 255)
        
        return quantized.astype(np.int8 if self.symmetric else np.uint8)
    
    def decode(self, quantized: np.ndarray) -> np.ndarray:
        """
        解码为浮点
        
        Args:
            quantized: INT8 向量
            
        Returns:
            np.ndarray: 浮点向量
        """
        if self.symmetric:
            return quantized.astype(np.float32) * self.scale
        else:
            return (quantized.astype(np.float32) - self.zero_point) * self.scale


class ScalarQuantizer:
    """
    标量量化器
    将浮点向量量化为 8-bit 整数
    """
    
    def __init__(self, n_bits: int = 8):
        """
        初始化标量量化器
        
        Args:
            n_bits: 量化位数（默认 8-bit）
        """
        self.n_bits = n_bits
        self.min_val = None
        self.max_val = None
        self.scale = None
    
    def fit(self, vectors: np.ndarray):
        """
        训练量化器
        
        Args:
            vectors: 训练向量 (n, dim)
        """
        vectors = np.asarray(vectors, dtype=np.float32)
        self.min_val = vectors.min(axis=0)
        self.max_val = vectors.max(axis=0)
        
        # 避免除零
        range_val = self.max_val - self.min_val
        range_val = np.where(range_val == 0, 1, range_val)
        
        self.scale = (2 ** self.n_bits - 1) / range_val
    
    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """
        编码向量
        
        Args:
            vectors: 浮点向量 (n, dim)
            
        Returns:
            np.ndarray: 量化后的整数向量
        """
        vectors = np.asarray(vectors, dtype=np.float32)
        quantized = (vectors - self.min_val) * self.scale
        quantized = np.clip(quantized, 0, 2 ** self.n_bits - 1)
        return quantized.astype(np.uint8)
    
    def decode(self, quantized: np.ndarray) -> np.ndarray:
        """
        解码向量
        
        Args:
            quantized: 量化向量
            
        Returns:
            np.ndarray: 浮点向量
        """
        return quantized.astype(np.float32) / self.scale + self.min_val
    
    # 别名方法（兼容性）
    def quantize(self, vectors: np.ndarray) -> np.ndarray:
        """encode 的别名"""
        return self.encode(vectors)
    
    def dequantize(self, quantized: np.ndarray) -> np.ndarray:
        """decode 的别名"""
        return self.decode(quantized)


class ProductQuantizer:
    """
    乘积量化器
    将向量分割为多个子向量，每个子向量独立量化
    """
    
    def __init__(self, n_subvectors: int = 8, n_centroids: int = 256):
        """
        初始化乘积量化器
        
        Args:
            n_subvectors: 子向量数量
            n_centroids: 每个子向量的聚类中心数量（默认 256 = 8-bit）
        """
        self.n_subvectors = n_subvectors
        self.n_centroids = n_centroids
        self.centroids = None  # (n_subvectors, n_centroids, sub_dim)
        self.sub_dim = None
    
    def fit(self, vectors: np.ndarray, n_iter: int = 20):
        """
        训练乘积量化器
        
        Args:
            vectors: 训练向量 (n, dim)
            n_iter: K-means 迭代次数
        """
        vectors = np.asarray(vectors, dtype=np.float32)
        n, dim = vectors.shape
        
        assert dim % self.n_subvectors == 0, "维度必须能被子向量数量整除"
        self.sub_dim = dim // self.n_subvectors
        
        # 对每个子向量进行 K-means
        self.centroids = np.zeros(
            (self.n_subvectors, self.n_centroids, self.sub_dim),
            dtype=np.float32
        )
        
        for i in range(self.n_subvectors):
            start = i * self.sub_dim
            end = start + self.sub_dim
            sub_vectors = vectors[:, start:end]
            
            # 简化的 K-means
            centroids = self._kmeans(sub_vectors, self.n_centroids, n_iter)
            self.centroids[i] = centroids
    
    def _kmeans(
        self, 
        data: np.ndarray, 
        k: int, 
        n_iter: int
    ) -> np.ndarray:
        """简化的 K-means"""
        n = len(data)
        
        # 随机初始化
        indices = np.random.choice(n, k, replace=False)
        centroids = data[indices].copy()
        
        for _ in range(n_iter):
            # 分配
            distances = np.zeros((n, k))
            for j in range(k):
                distances[:, j] = np.linalg.norm(data - centroids[j], axis=1)
            labels = np.argmin(distances, axis=1)
            
            # 更新
            for j in range(k):
                mask = labels == j
                if mask.sum() > 0:
                    centroids[j] = data[mask].mean(axis=0)
        
        return centroids
    
    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """
        编码向量
        
        Args:
            vectors: 浮点向量 (n, dim)
            
        Returns:
            np.ndarray: 编码后的索引 (n, n_subvectors)
        """
        vectors = np.asarray(vectors, dtype=np.float32)
        n = len(vectors)
        codes = np.zeros((n, self.n_subvectors), dtype=np.uint8)
        
        for i in range(self.n_subvectors):
            start = i * self.sub_dim
            end = start + self.sub_dim
            sub_vectors = vectors[:, start:end]
            
            # 找最近的聚类中心
            distances = np.zeros((n, self.n_centroids))
            for j in range(self.n_centroids):
                distances[:, j] = np.linalg.norm(
                    sub_vectors - self.centroids[i, j], axis=1
                )
            codes[:, i] = np.argmin(distances, axis=1)
        
        return codes
    
    def decode(self, codes: np.ndarray) -> np.ndarray:
        """
        解码向量
        
        Args:
            codes: 编码索引 (n, n_subvectors)
            
        Returns:
            np.ndarray: 重建的浮点向量
        """
        n = len(codes)
        vectors = np.zeros((n, self.n_subvectors * self.sub_dim), dtype=np.float32)
        
        for i in range(self.n_subvectors):
            start = i * self.sub_dim
            end = start + self.sub_dim
            vectors[:, start:end] = self.centroids[i, codes[:, i]]
        
        return vectors
    
    # 别名方法（兼容性）
    def quantize(self, vectors: np.ndarray) -> np.ndarray:
        """encode 的别名"""
        return self.encode(vectors)
    
    def dequantize(self, codes: np.ndarray) -> np.ndarray:
        """decode 的别名"""
        return self.decode(codes)
    
    def compute_distance_table(
        self, 
        query: np.ndarray
    ) -> np.ndarray:
        """
        计算查询向量与所有聚类中心的距离表
        
        Args:
            query: 查询向量 (dim,)
            
        Returns:
            np.ndarray: 距离表 (n_subvectors, n_centroids)
        """
        query = np.asarray(query, dtype=np.float32)
        distance_table = np.zeros(
            (self.n_subvectors, self.n_centroids),
            dtype=np.float32
        )
        
        for i in range(self.n_subvectors):
            start = i * self.sub_dim
            end = start + self.sub_dim
            sub_query = query[start:end]
            
            # 计算与所有聚类中心的距离
            distance_table[i] = np.linalg.norm(
                self.centroids[i] - sub_query, axis=1
            )
        
        return distance_table
    
    def search_pq(
        self,
        query: np.ndarray,
        codes: np.ndarray,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        使用 PQ 编码进行快速搜索
        
        Args:
            query: 查询向量
            codes: 数据库编码
            k: 返回数量
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 距离)
        """
        # 计算距离表
        distance_table = self.compute_distance_table(query)
        
        # 计算近似距离
        n = len(codes)
        distances = np.zeros(n, dtype=np.float32)
        
        for i in range(n):
            for j in range(self.n_subvectors):
                distances[i] += distance_table[j, codes[i, j]]
        
        # 返回 top-k
        indices = np.argsort(distances)[:k]
        return indices, distances[indices]


class BinaryQuantizer:
    """
    二值量化器
    将向量量化为二进制码，使用汉明距离进行快速搜索
    """
    
    def __init__(self):
        """初始化二值量化器"""
        pass
    
    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """
        编码为二进制码
        
        Args:
            vectors: 浮点向量 (n, dim)
            
        Returns:
            np.ndarray: 二进制码 (n, dim) - 每个元素为 0 或 1
        """
        vectors = np.asarray(vectors, dtype=np.float32)
        return (vectors > 0).astype(np.uint8)
    
    def decode(self, codes: np.ndarray) -> np.ndarray:
        """
        解码（返回 +1/-1）
        
        Args:
            codes: 二进制码
            
        Returns:
            np.ndarray: 浮点向量
        """
        return codes.astype(np.float32) * 2 - 1
    
    # 别名方法（兼容性）
    def quantize(self, vectors: np.ndarray) -> np.ndarray:
        """encode 的别名"""
        return self.encode(vectors)
    
    def dequantize(self, codes: np.ndarray) -> np.ndarray:
        """decode 的别名"""
        return self.decode(codes)
    
    def hamming_distance(
        self, 
        query_code: np.ndarray, 
        codes: np.ndarray
    ) -> np.ndarray:
        """
        计算汉明距离
        
        Args:
            query_code: 查询二进制码
            codes: 数据库二进制码
            
        Returns:
            np.ndarray: 汉明距离数组
        """
        return np.sum(query_code != codes, axis=1)
    
    def search(
        self,
        query: np.ndarray,
        codes: np.ndarray,
        k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        二值搜索
        
        Args:
            query: 查询向量
            codes: 数据库二进制码
            k: 返回数量
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 距离)
        """
        query_code = self.encode(query.reshape(1, -1))[0]
        distances = self.hamming_distance(query_code, codes)
        
        indices = np.argsort(distances)[:k]
        return indices, distances[indices]


def create_quantizer(
    method: str = 'sq',
    **kwargs
):
    """
    创建量化器
    
    Args:
        method: 量化方法 ('sq', 'pq', 'binary')
        **kwargs: 量化器参数
        
    Returns:
        量化器实例
    """
    if method == 'sq':
        return ScalarQuantizer(**kwargs)
    elif method == 'pq':
        return ProductQuantizer(**kwargs)
    elif method == 'binary':
        return BinaryQuantizer()
    else:
        raise ValueError(f"Unknown quantization method: {method}")


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("向量量化模块")
    print("=" * 60)
    
    import time
    
    # 生成测试数据
    np.random.seed(42)
    n_vectors = 10000
    dim = 128
    
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    query = np.random.randn(dim).astype(np.float32)
    
    print(f"\n📊 测试参数: n={n_vectors}, dim={dim}")
    
    # 测试标量量化
    print("\n🔬 标量量化 (SQ):")
    quantizer = ScalarQuantizer()
    
    start = time.time()
    quantizer.fit(vectors)
    elapsed = (time.time() - start) * 1000
    print(f"   训练时间: {elapsed:.2f}ms")
    
    start = time.time()
    encoded = quantizer.encode(vectors)
    elapsed = (time.time() - start) * 1000
    print(f"   编码时间: {elapsed:.2f}ms")
    print(f"   压缩比: {vectors.nbytes / encoded.nbytes:.1f}x")
    
    decoded = quantizer.decode(encoded)
    error = np.mean((vectors - decoded) ** 2)
    print(f"   重建误差 (MSE): {error:.6f}")
    
    # 测试乘积量化
    print("\n🔬 乘积量化 (PQ):")
    quantizer = ProductQuantizer(n_subvectors=8, n_centroids=256)
    
    start = time.time()
    quantizer.fit(vectors)
    elapsed = (time.time() - start) * 1000
    print(f"   训练时间: {elapsed:.2f}ms")
    
    start = time.time()
    codes = quantizer.encode(vectors)
    elapsed = (time.time() - start) * 1000
    print(f"   编码时间: {elapsed:.2f}ms")
    print(f"   压缩比: {vectors.nbytes / codes.nbytes:.1f}x")
    
    decoded = quantizer.decode(codes)
    error = np.mean((vectors - decoded) ** 2)
    print(f"   重建误差 (MSE): {error:.6f}")
    
    # 测试二值量化
    print("\n🔬 二值量化:")
    quantizer = BinaryQuantizer()
    
    start = time.time()
    codes = quantizer.encode(vectors)
    elapsed = (time.time() - start) * 1000
    print(f"   编码时间: {elapsed:.2f}ms")
    print(f"   压缩比: {vectors.nbytes / codes.nbytes:.1f}x")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
