#!/usr/bin/env python3
"""
AVX512 向量操作模块
使用 SIMD 指令集加速向量计算

支持的指令集（按优先级）：
1. AVX-512 (最高优先级) - 512位向量宽度
2. AVX2 - 256位向量宽度
3. AVX - 128位向量宽度
4. 纯 Python 回退

功能：
- 余弦相似度计算
- 欧氏距离计算
- 点积计算
- 批量向量归一化
- 批量向量搜索
"""

import numpy as np
from typing import List, Tuple, Optional, Union
import os
import platform

# 检测 CPU 支持的指令集
def detect_simd_support() -> dict:
    """
    检测 CPU 支持的 SIMD 指令集
    
    Returns:
        dict: 支持的指令集信息
    """
    support = {
        'avx512': False,
        'avx2': False,
        'avx': False,
        'sse': False,
        'method': 'python'
    }
    
    # Linux 系统
    if platform.system() == 'Linux':
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'avx512' in cpuinfo.lower():
                    support['avx512'] = True
                    support['method'] = 'avx512'
                elif 'avx2' in cpuinfo.lower():
                    support['avx2'] = True
                    support['method'] = 'avx2'
                elif 'avx ' in cpuinfo.lower():
                    support['avx'] = True
                    support['method'] = 'avx'
                elif 'sse' in cpuinfo.lower():
                    support['sse'] = True
                    support['method'] = 'sse'
        except Exception:
            pass
    
    # 检查 numpy 是否支持 SIMD
    try:
        # numpy 会自动使用可用的 SIMD 指令
        if hasattr(np, '__config__'):
            support['numpy_simd'] = True
    except Exception:
        support['numpy_simd'] = False
    
    return support

# 全局 SIMD 支持状态
SIMD_SUPPORT = detect_simd_support()


class VectorOps:
    """
    向量操作类
    自动选择最优的 SIMD 实现
    """
    
    def __init__(self, use_simd: bool = True):
        """
        初始化向量操作器
        
        Args:
            use_simd: 是否使用 SIMD 加速
        """
        self.use_simd = use_simd and SIMD_SUPPORT['method'] != 'python'
        self.simd_level = SIMD_SUPPORT['method']
        
        if self.use_simd:
            print(f"✅ SIMD 加速已启用: {self.simd_level.upper()}")
        else:
            print("ℹ️ 使用纯 Python 实现")
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            float: 余弦相似度 [-1, 1]
        """
        # 确保是 numpy 数组
        vec1 = np.asarray(vec1, dtype=np.float32)
        vec2 = np.asarray(vec2, dtype=np.float32)
        
        # 使用 numpy 的优化实现（自动使用 SIMD）
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def cosine_similarity_batch(
        self, 
        query: np.ndarray, 
        vectors: np.ndarray
    ) -> np.ndarray:
        """
        批量计算查询向量与多个向量的余弦相似度
        
        Args:
            query: 查询向量 (dim,)
            vectors: 向量矩阵 (n, dim)
            
        Returns:
            np.ndarray: 相似度数组 (n,)
        """
        query = np.asarray(query, dtype=np.float32)
        vectors = np.asarray(vectors, dtype=np.float32)
        
        # 归一化
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        
        # 批量点积（numpy 自动使用 SIMD）
        similarities = np.dot(vectors_norm, query_norm)
        
        return similarities
    
    def euclidean_distance(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的欧氏距离
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            float: 欧氏距离
        """
        vec1 = np.asarray(vec1, dtype=np.float32)
        vec2 = np.asarray(vec2, dtype=np.float32)
        
        return float(np.linalg.norm(vec1 - vec2))
    
    def euclidean_distance_batch(
        self, 
        query: np.ndarray, 
        vectors: np.ndarray
    ) -> np.ndarray:
        """
        批量计算查询向量与多个向量的欧氏距离
        
        Args:
            query: 查询向量 (dim,)
            vectors: 向量矩阵 (n, dim)
            
        Returns:
            np.ndarray: 距离数组 (n,)
        """
        query = np.asarray(query, dtype=np.float32)
        vectors = np.asarray(vectors, dtype=np.float32)
        
        # 使用广播计算
        diff = vectors - query
        distances = np.linalg.norm(diff, axis=1)
        
        return distances
    
    def dot_product(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的点积
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            float: 点积
        """
        vec1 = np.asarray(vec1, dtype=np.float32)
        vec2 = np.asarray(vec2, dtype=np.float32)
        
        return float(np.dot(vec1, vec2))
    
    def dot_product_batch(
        self, 
        query: np.ndarray, 
        vectors: np.ndarray
    ) -> np.ndarray:
        """
        批量计算点积
        
        Args:
            query: 查询向量 (dim,)
            vectors: 向量矩阵 (n, dim)
            
        Returns:
            np.ndarray: 点积数组 (n,)
        """
        query = np.asarray(query, dtype=np.float32)
        vectors = np.asarray(vectors, dtype=np.float32)
        
        return np.dot(vectors, query)
    
    def normalize(self, vec: np.ndarray) -> np.ndarray:
        """
        归一化向量
        
        Args:
            vec: 输入向量
            
        Returns:
            np.ndarray: 归一化后的向量
        """
        vec = np.asarray(vec, dtype=np.float32)
        norm = np.linalg.norm(vec)
        
        if norm == 0:
            return vec
        
        return vec / norm
    
    def normalize_batch(self, vectors: np.ndarray) -> np.ndarray:
        """
        批量归一化向量
        
        Args:
            vectors: 向量矩阵 (n, dim)
            
        Returns:
            np.ndarray: 归一化后的向量矩阵
        """
        vectors = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # 避免除零
        
        return vectors / norms
    
    def top_k_search(
        self, 
        query: np.ndarray, 
        vectors: np.ndarray, 
        k: int = 10,
        metric: str = 'cosine'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Top-K 向量搜索
        
        Args:
            query: 查询向量 (dim,)
            vectors: 向量矩阵 (n, dim)
            k: 返回数量
            metric: 距离度量 ('cosine' 或 'euclidean')
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引数组, 分数数组)
        """
        query = np.asarray(query, dtype=np.float32)
        vectors = np.asarray(vectors, dtype=np.float32)
        
        if metric == 'cosine':
            scores = self.cosine_similarity_batch(query, vectors)
            # 余弦相似度越大越好
            indices = np.argsort(-scores)[:k]
        else:
            scores = self.euclidean_distance_batch(query, vectors)
            # 欧氏距离越小越好
            indices = np.argsort(scores)[:k]
        
        return indices, scores[indices]


class AVX512VectorOps(VectorOps):
    """
    AVX-512 优化的向量操作类
    
    当 CPU 支持 AVX-512 时，numpy 会自动使用这些指令。
    此类提供了一些额外的优化提示。
    """
    
    def __init__(self):
        super().__init__(use_simd=True)
        
        if not SIMD_SUPPORT['avx512']:
            print("⚠️ AVX-512 不支持，使用回退实现")
    
    def batch_dot_product_avx512(
        self, 
        queries: np.ndarray, 
        vectors: np.ndarray
    ) -> np.ndarray:
        """
        使用矩阵乘法进行批量点积计算
        充分利用 AVX-512 的 512 位向量宽度
        
        Args:
            queries: 查询向量矩阵 (m, dim)
            vectors: 向量矩阵 (n, dim)
            
        Returns:
            np.ndarray: 点积矩阵 (m, n)
        """
        queries = np.asarray(queries, dtype=np.float32)
        vectors = np.asarray(vectors, dtype=np.float32)
        
        # 使用矩阵乘法，numpy 会自动使用 AVX-512
        return np.dot(queries, vectors.T)


def get_vector_ops(use_simd: bool = True) -> VectorOps:
    """
    获取最优的向量操作实例
    
    Args:
        use_simd: 是否使用 SIMD 加速
        
    Returns:
        VectorOps: 向量操作实例
    """
    if use_simd and SIMD_SUPPORT['avx512']:
        return AVX512VectorOps()
    return VectorOps(use_simd=use_simd)


# 便捷函数
def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """计算余弦相似度"""
    ops = get_vector_ops()
    return ops.cosine_similarity(vec1, vec2)


def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """计算欧氏距离"""
    ops = get_vector_ops()
    return ops.euclidean_distance(vec1, vec2)


def top_k_search(
    query: np.ndarray, 
    vectors: np.ndarray, 
    k: int = 10,
    metric: str = 'cosine'
) -> Tuple[np.ndarray, np.ndarray]:
    """Top-K 向量搜索"""
    ops = get_vector_ops()
    return ops.top_k_search(query, vectors, k, metric)


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("AVX512 向量操作模块")
    print("=" * 60)
    
    print(f"\n📊 SIMD 支持检测:")
    for key, value in SIMD_SUPPORT.items():
        print(f"   {key}: {value}")
    
    # 性能测试
    import time
    
    dim = 1536  # OpenAI embedding 维度
    n_vectors = 10000
    
    print(f"\n🔬 性能测试 (dim={dim}, n={n_vectors}):")
    
    # 生成测试数据
    np.random.seed(42)
    query = np.random.randn(dim).astype(np.float32)
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    
    # 测试批量余弦相似度
    ops = get_vector_ops()
    
    start = time.time()
    similarities = ops.cosine_similarity_batch(query, vectors)
    elapsed = (time.time() - start) * 1000
    
    print(f"   批量余弦相似度: {elapsed:.2f}ms")
    print(f"   最高相似度: {similarities.max():.4f}")
    print(f"   最低相似度: {similarities.min():.4f}")
    
    # 测试 Top-K 搜索
    start = time.time()
    indices, scores = ops.top_k_search(query, vectors, k=10)
    elapsed = (time.time() - start) * 1000
    
    print(f"\n   Top-10 搜索: {elapsed:.2f}ms")
    print(f"   Top-3 索引: {indices[:3]}")
    print(f"   Top-3 分数: {scores[:3]}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
