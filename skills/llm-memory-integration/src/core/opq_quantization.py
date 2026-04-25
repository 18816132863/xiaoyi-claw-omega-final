#!/usr/bin/env python3
"""
OPQ 量化模块 (v4.2)
优化乘积量化，更高压缩比，精度损失更小
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from sklearn.decomposition import PCA


class OPQQuantizer:
    """
    OPQ (Optimized Product Quantization) 量化器
    通过旋转矩阵优化量化效果
    """
    
    def __init__(
        self,
        dim: int,
        n_subspaces: int = 8,
        n_centroids: int = 256,
        n_iter: int = 20
    ):
        """
        初始化 OPQ 量化器
        
        Args:
            dim: 向量维度
            n_subspaces: 子空间数量
            n_centroids: 每个子空间的质心数量
            n_iter: 迭代次数
        """
        self.dim = dim
        self.n_subspaces = n_subspaces
        self.n_centroids = n_centroids
        self.n_iter = n_iter
        
        # 子空间维度
        assert dim % n_subspaces == 0, "维度必须能被子空间数量整除"
        self.subspace_dim = dim // n_subspaces
        
        # 旋转矩阵
        self.rotation = np.eye(dim, dtype=np.float32)
        
        # 质心
        self.centroids = None
        
        # 编码表
        self.codebook = None
        
        print(f"OPQ 量化器初始化:")
        print(f"  维度: {dim}")
        print(f"  子空间数: {n_subspaces}")
        print(f"  子空间维度: {self.subspace_dim}")
        print(f"  质心数: {n_centroids}")
    
    def train(self, vectors: np.ndarray):
        """
        训练量化器
        
        Args:
            vectors: 训练向量 (n, dim)
        """
        n_vectors = len(vectors)
        print(f"训练 OPQ 量化器 ({n_vectors} 个向量)...")
        
        # 初始化旋转矩阵（使用 PCA）
        pca = PCA(n_components=self.dim)
        pca.fit(vectors)
        self.rotation = pca.components_.T.astype(np.float32)
        
        # 迭代优化
        for iteration in range(self.n_iter):
            # 应用旋转
            rotated = np.dot(vectors, self.rotation)
            
            # 训练子空间量化器
            self._train_subspace_quantizers(rotated)
            
            # 更新旋转矩阵
            self._update_rotation(vectors)
            
            if (iteration + 1) % 5 == 0:
                print(f"  迭代 {iteration + 1}/{self.n_iter}")
        
        print("✅ 训练完成")
    
    def _train_subspace_quantizers(self, rotated: np.ndarray):
        """
        训练子空间量化器
        
        Args:
            rotated: 旋转后的向量
        """
        self.centroids = []
        
        for i in range(self.n_subspaces):
            # 提取子空间
            start = i * self.subspace_dim
            end = start + self.subspace_dim
            subspace = rotated[:, start:end]
            
            # K-means 聚类
            centroids = self._kmeans(subspace, self.n_centroids)
            self.centroids.append(centroids)
        
        self.centroids = np.array(self.centroids, dtype=np.float32)
    
    def _kmeans(self, data: np.ndarray, k: int) -> np.ndarray:
        """
        K-means 聚类
        
        Args:
            data: 数据
            k: 聚类数量
        
        Returns:
            np.ndarray: 质心
        """
        # 随机初始化
        indices = np.random.choice(len(data), k, replace=False)
        centroids = data[indices].copy()
        
        for _ in range(10):
            # 分配
            distances = np.sum((data[:, np.newaxis] - centroids) ** 2, axis=2)
            labels = np.argmin(distances, axis=1)
            
            # 更新
            new_centroids = np.zeros_like(centroids)
            for j in range(k):
                mask = labels == j
                if np.any(mask):
                    new_centroids[j] = data[mask].mean(axis=0)
                else:
                    new_centroids[j] = centroids[j]
            
            # 收敛检查
            if np.allclose(centroids, new_centroids):
                break
            
            centroids = new_centroids
        
        return centroids
    
    def _update_rotation(self, vectors: np.ndarray):
        """
        更新旋转矩阵
        
        Args:
            vectors: 原始向量
        """
        # 简化实现：保持当前旋转矩阵
        # 完整实现应使用 SVD 优化
        pass
    
    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """
        编码向量
        
        Args:
            vectors: 原始向量 (n, dim)
        
        Returns:
            np.ndarray: 编码结果 (n, n_subspaces) uint8
        """
        if self.centroids is None:
            raise ValueError("量化器未训练")
        
        # 应用旋转
        rotated = np.dot(vectors, self.rotation)
        
        # 编码
        codes = np.zeros((len(vectors), self.n_subspaces), dtype=np.uint8)
        
        for i in range(self.n_subspaces):
            start = i * self.subspace_dim
            end = start + self.subspace_dim
            subspace = rotated[:, start:end]
            
            # 找到最近的质心
            distances = np.sum((subspace[:, np.newaxis] - self.centroids[i]) ** 2, axis=2)
            codes[:, i] = np.argmin(distances, axis=1)
        
        return codes
    
    def decode(self, codes: np.ndarray) -> np.ndarray:
        """
        解码向量
        
        Args:
            codes: 编码结果 (n, n_subspaces)
        
        Returns:
            np.ndarray: 解码后的向量 (n, dim)
        """
        if self.centroids is None:
            raise ValueError("量化器未训练")
        
        # 解码
        rotated = np.zeros((len(codes), self.dim), dtype=np.float32)
        
        for i in range(self.n_subspaces):
            start = i * self.subspace_dim
            end = start + self.subspace_dim
            rotated[:, start:end] = self.centroids[i][codes[:, i]]
        
        # 逆旋转
        vectors = np.dot(rotated, self.rotation.T)
        
        return vectors
    
    def compute_distance_table(
        self,
        query: np.ndarray
    ) -> np.ndarray:
        """
        计算距离表
        
        Args:
            query: 查询向量
        
        Returns:
            np.ndarray: 距离表 (n_subspaces, n_centroids)
        """
        if self.centroids is None:
            raise ValueError("量化器未训练")
        
        # 应用旋转
        query_rotated = np.dot(query, self.rotation)
        
        # 计算距离表
        distance_table = np.zeros((self.n_subspaces, self.n_centroids), dtype=np.float32)
        
        for i in range(self.n_subspaces):
            start = i * self.subspace_dim
            end = start + self.subspace_dim
            query_sub = query_rotated[start:end]
            
            # 计算到所有质心的距离
            distance_table[i] = np.sum((self.centroids[i] - query_sub) ** 2, axis=1)
        
        return distance_table
    
    def search(
        self,
        query: np.ndarray,
        codes: np.ndarray,
        top_k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        使用 OPQ 编码搜索
        
        Args:
            query: 查询向量
            codes: 编码后的向量
            top_k: 返回数量
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 距离)
        """
        # 计算距离表
        distance_table = self.compute_distance_table(query)
        
        # 计算距离
        distances = np.zeros(len(codes), dtype=np.float32)
        for i in range(self.n_subspaces):
            distances += distance_table[i, codes[:, i]]
        
        # 获取 top-k
        if top_k >= len(distances):
            indices = np.argsort(distances)
        else:
            indices = np.argpartition(distances, top_k)[:top_k]
            indices = indices[np.argsort(distances[indices])]
        
        return indices, np.sqrt(distances[indices])
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'dim': self.dim,
            'n_subspaces': self.n_subspaces,
            'n_centroids': self.n_centroids,
            'bytes_per_vector': self.n_subspaces,
            'compression_ratio': self.dim * 4 / self.n_subspaces
        }


if __name__ == "__main__":
    # 测试
    print("=== OPQ 量化器测试 ===")
    
    dim = 4096
    n_vectors = 1000
    
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    query = np.random.randn(dim).astype(np.float32)
    
    # 创建量化器
    quantizer = OPQQuantizer(dim, n_subspaces=16, n_centroids=256)
    
    # 训练
    quantizer.train(vectors)
    
    # 编码
    codes = quantizer.encode(vectors)
    print(f"编码大小: {codes.nbytes} bytes")
    print(f"原始大小: {vectors.nbytes} bytes")
    print(f"压缩比: {vectors.nbytes / codes.nbytes:.1f}x")
    
    # 解码
    decoded = quantizer.decode(codes)
    reconstruction_error = np.mean((vectors - decoded) ** 2)
    print(f"重建误差: {reconstruction_error:.6f}")
    
    # 搜索
    indices, distances = quantizer.search(query, codes, top_k=10)
    print(f"搜索结果: {len(indices)} 个")
    
    # 统计
    stats = quantizer.get_stats()
    print(f"统计: {stats}")
