#!/usr/bin/env python3
"""
INT8 + VNNI 搜索模块 (v4.1)
INT8 量化 + AVX-512 VNNI 加速

两阶段搜索：
1. INT8 量化粗筛（VNNI 加速）
2. FP32 精确重排
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import os


def check_vnni_support() -> bool:
    """
    检查 CPU 是否支持 AVX-512 VNNI
    
    Returns:
        bool: 是否支持 VNNI
    """
    if os.path.exists('/proc/cpuinfo'):
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read().lower()
            return 'avx512_vnni' in cpuinfo
    return False


class INT8Quantizer:
    """
    INT8 量化器
    将 FP32 向量量化为 INT8
    """
    
    def __init__(self, calibration_data: Optional[np.ndarray] = None):
        """
        初始化量化器
        
        Args:
            calibration_data: 校准数据（用于确定量化范围）
        """
        self.scale = None
        self.zero_point = None
        
        if calibration_data is not None:
            self.calibrate(calibration_data)
    
    def calibrate(self, data: np.ndarray):
        """
        校准量化参数
        
        Args:
            data: 校准数据 (n, dim)
        """
        # 计算范围
        min_val = np.min(data)
        max_val = np.max(data)
        
        # 对称量化
        abs_max = max(abs(min_val), abs(max_val))
        self.scale = abs_max / 127.0
        self.zero_point = 0
    
    def encode(self, vectors: np.ndarray) -> np.ndarray:
        """
        量化为 INT8
        
        Args:
            vectors: FP32 向量 (n, dim)
        
        Returns:
            np.ndarray: INT8 向量
        """
        if self.scale is None:
            self.calibrate(vectors)
        
        # 量化
        quantized = np.clip(np.round(vectors / self.scale), -128, 127)
        return quantized.astype(np.int8)
    
    def decode(self, vectors: np.ndarray) -> np.ndarray:
        """
        反量化为 FP32
        
        Args:
            vectors: INT8 向量
        
        Returns:
            np.ndarray: FP32 向量
        """
        return vectors.astype(np.float32) * self.scale


class VNNISearcher:
    """
    VNNI 加速搜索器
    INT8 量化 + VNNI 加速 + 两阶段搜索
    """
    
    def __init__(
        self,
        vectors: np.ndarray,
        use_vnni: bool = True,
        rerank_top_k: int = 100
    ):
        """
        初始化 VNNI 搜索器
        
        Args:
            vectors: 原始向量 (n, dim)
            use_vnni: 是否使用 VNNI 加速
            rerank_top_k: 重排数量
        """
        self.vectors_fp32 = vectors.astype(np.float32)
        self.n_vectors = len(vectors)
        self.dim = vectors.shape[1]
        self.use_vnni = use_vnni and check_vnni_support()
        self.rerank_top_k = rerank_top_k
        
        # 量化
        self.quantizer = INT8Quantizer(vectors)
        self.vectors_int8 = self.quantizer.encode(vectors)
        
        print(f"VNNI 搜索器初始化:")
        print(f"  向量数: {self.n_vectors}")
        print(f"  维度: {self.dim}")
        print(f"  VNNI: {'✅' if self.use_vnni else '❌'}")
        print(f"  重排数量: {self.rerank_top_k}")
    
    def search(
        self,
        query: np.ndarray,
        top_k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        两阶段搜索
        
        Args:
            query: 查询向量 (dim,)
            top_k: 返回数量
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 得分)
        """
        # 阶段1：INT8 粗筛
        query_int8 = self.quantizer.encode(query.reshape(1, -1))[0]
        coarse_top_k = min(self.rerank_top_k, self.n_vectors)
        
        if self.use_vnni:
            coarse_indices, coarse_scores = self._vnni_dot_product(query_int8, coarse_top_k)
        else:
            coarse_indices, coarse_scores = self._int8_dot_product(query_int8, coarse_top_k)
        
        # 阶段2：FP32 精确重排
        rerank_vectors = self.vectors_fp32[coarse_indices]
        query_fp32 = query.astype(np.float32)
        
        # 归一化
        query_norm = query_fp32 / (np.linalg.norm(query_fp32) + 1e-10)
        vectors_norm = rerank_vectors / (np.linalg.norm(rerank_vectors, axis=1, keepdims=True) + 1e-10)
        
        # 计算精确相似度
        exact_scores = np.dot(vectors_norm, query_norm)
        
        # 获取 top-k
        if top_k >= len(exact_scores):
            final_indices = np.argsort(exact_scores)[::-1]
        else:
            final_indices = np.argpartition(exact_scores, -top_k)[-top_k:]
            final_indices = final_indices[np.argsort(exact_scores[final_indices])[::-1]]
        
        return coarse_indices[final_indices], exact_scores[final_indices]
    
    def _vnni_dot_product(
        self,
        query: np.ndarray,
        top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        VNNI 加速的 INT8 点积
        
        Args:
            query: INT8 查询向量
            top_k: 返回数量
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 得分)
        """
        # 使用 Numba VNNI 加速（如果可用）
        try:
            from numba_accel import int8_dot_product_vnni
            scores = int8_dot_product_vnni(query, self.vectors_int8)
        except Exception:
            scores = self._int8_dot_product_naive(query)
        
        # 获取 top-k
        if top_k >= len(scores):
            indices = np.argsort(scores)[::-1]
        else:
            indices = np.argpartition(scores, -top_k)[-top_k:]
            indices = indices[np.argsort(scores[indices])[::-1]]
        
        return indices, scores[indices].astype(np.float32)
    
    def _int8_dot_product(
        self,
        query: np.ndarray,
        top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        INT8 点积（无 VNNI）
        
        Args:
            query: INT8 查询向量
            top_k: 返回数量
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 得分)
        """
        scores = self._int8_dot_product_naive(query)
        
        # 获取 top-k
        if top_k >= len(scores):
            indices = np.argsort(scores)[::-1]
        else:
            indices = np.argpartition(scores, -top_k)[-top_k:]
            indices = indices[np.argsort(scores[indices])[::-1]]
        
        return indices, scores[indices].astype(np.float32)
    
    def _int8_dot_product_naive(self, query: np.ndarray) -> np.ndarray:
        """
        朴素 INT8 点积
        
        Args:
            query: INT8 查询向量
        
        Returns:
            np.ndarray: 点积结果
        """
        # 转换为 int32 避免溢出
        query_int32 = query.astype(np.int32)
        vectors_int32 = self.vectors_int8.astype(np.int32)
        
        # 点积
        return np.dot(vectors_int32, query_int32)
    
    def batch_search(
        self,
        queries: np.ndarray,
        top_k: int = 10
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        批量搜索
        
        Args:
            queries: 查询向量矩阵 (n_queries, dim)
            top_k: 每个查询返回的数量
        
        Returns:
            List[Tuple[np.ndarray, np.ndarray]]: 每个查询的结果
        """
        results = []
        for query in queries:
            indices, scores = self.search(query, top_k)
            results.append((indices, scores))
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'n_vectors': self.n_vectors,
            'dim': self.dim,
            'use_vnni': self.use_vnni,
            'rerank_top_k': self.rerank_top_k,
            'memory_fp32_mb': (self.n_vectors * self.dim * 4) / (1024**2),
            'memory_int8_mb': (self.n_vectors * self.dim * 1) / (1024**2),
            'compression_ratio': 4.0
        }


if __name__ == "__main__":
    # 测试
    print("=== VNNI 搜索器测试 ===")
    
    # 创建测试数据
    dim = 4096
    n_vectors = 10000
    n_queries = 10
    
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    queries = np.random.randn(n_queries, dim).astype(np.float32)
    
    # 初始化搜索器
    searcher = VNNISearcher(vectors, use_vnni=True, rerank_top_k=100)
    
    # 单次搜索
    import time
    start = time.time()
    indices, scores = searcher.search(queries[0], top_k=20)
    elapsed = time.time() - start
    print(f"单次搜索耗时: {elapsed*1000:.2f}ms")
    
    # 批量搜索
    start = time.time()
    results = searcher.batch_search(queries, top_k=20)
    elapsed = time.time() - start
    print(f"批量搜索耗时: {elapsed*1000:.2f}ms ({n_queries} 个查询)")
    
    # 统计信息
    stats = searcher.get_stats()
    print(f"\n统计信息:")
    print(f"  FP32 内存: {stats['memory_fp32_mb']:.2f} MB")
    print(f"  INT8 内存: {stats['memory_int8_mb']:.2f} MB")
    print(f"  压缩比: {stats['compression_ratio']}x")
