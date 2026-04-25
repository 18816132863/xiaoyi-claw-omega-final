#!/usr/bin/env python3
"""
GPU 加速集成模块 (v4.1)
自动检测 GPU 可用性，GPU 优先，CPU 回退

支持的 GPU 后端：
1. CUDA（NVIDIA GPU）
2. OpenCL（通用 GPU）
3. CPU 回退（自动）

与主流程无缝集成。
"""

import numpy as np
from typing import List, Tuple, Optional, Union, Dict, Any
import os
import warnings

# GPU 后端检测
GPU_BACKEND = None
CUDA_AVAILABLE = False
OPENCL_AVAILABLE = False
GPU_INFO = {}


def detect_gpu() -> Dict[str, Any]:
    """
    检测 GPU 可用性
    
    Returns:
        Dict: GPU 信息
    """
    global GPU_BACKEND, CUDA_AVAILABLE, OPENCL_AVAILABLE, GPU_INFO
    
    info = {
        'backend': 'cpu',
        'cuda': {'available': False, 'version': None, 'devices': []},
        'opencl': {'available': False, 'platforms': []},
        'memory': {'total': 0, 'free': 0}
    }
    
    # 检测 CUDA
    try:
        import cupy as cp
        CUDA_AVAILABLE = True
        info['cuda']['available'] = True
        info['cuda']['version'] = cp.__version__
        
        # 获取设备信息
        n_devices = cp.cuda.runtime.getDeviceCount()
        for i in range(n_devices):
            device = cp.cuda.Device(i)
            props = cp.cuda.runtime.getDeviceProperties(i)
            info['cuda']['devices'].append({
                'id': i,
                'name': props['name'].decode() if isinstance(props['name'], bytes) else props['name'],
                'memory': props['totalGlobalMem'] // (1024**3),  # GB
                'compute_capability': f"{props['major']}.{props['minor']}"
            })
        
        # 设置为 CUDA 后端
        if n_devices > 0:
            GPU_BACKEND = 'cuda'
            info['backend'] = 'cuda'
            
            # 获取内存信息
            mempool = cp.get_default_memory_pool()
            info['memory']['total'] = mempool.total_bytes() // (1024**2)  # MB
            info['memory']['free'] = mempool.free_bytes() // (1024**2)  # MB
    except ImportError:
        pass
    except Exception as e:
        warnings.warn(f"CUDA 检测失败: {e}")
    
    # 检测 OpenCL（如果 CUDA 不可用）
    if not CUDA_AVAILABLE:
        try:
            import pyopencl as cl
            OPENCL_AVAILABLE = True
            info['opencl']['available'] = True
            
            # 获取平台信息
            platforms = cl.get_platforms()
            for platform in platforms:
                devices = platform.get_devices()
                info['opencl']['platforms'].append({
                    'name': platform.name,
                    'vendor': platform.vendor,
                    'devices': [{'name': d.name, 'type': cl.device_type.to_string(d.type)} for d in devices]
                })
            
            # 设置为 OpenCL 后端
            if len(platforms) > 0:
                GPU_BACKEND = 'opencl'
                info['backend'] = 'opencl'
        except ImportError:
            pass
        except Exception as e:
            warnings.warn(f"OpenCL 检测失败: {e}")
    
    GPU_INFO = info
    return info


class GPUAccelerator:
    """
    GPU 加速器
    自动选择最优后端
    """
    
    def __init__(self, prefer_gpu: bool = True):
        """
        初始化 GPU 加速器
        
        Args:
            prefer_gpu: 是否优先使用 GPU
        """
        self.prefer_gpu = prefer_gpu
        self.info = detect_gpu()
        self.backend = self.info['backend'] if prefer_gpu else 'cpu'
        
        # 初始化后端
        self._cp = None  # CuPy
        self._cl = None  # PyOpenCL
        self._ctx = None  # OpenCL 上下文
        self._queue = None  # OpenCL 队列
        
        if self.backend == 'cuda':
            try:
                import cupy as cp
                self._cp = cp
            except Exception:
                self.backend = 'cpu'
        elif self.backend == 'opencl':
            try:
                import pyopencl as cl
                self._cl = cl
                self._ctx = cl.create_some_context()
                self._queue = cl.CommandQueue(self._ctx)
            except Exception:
                self.backend = 'cpu'
        
        print(f"GPU 加速器初始化: {self.backend.upper()}")
    
    def is_gpu_available(self) -> bool:
        """检查 GPU 是否可用"""
        return self.backend in ['cuda', 'opencl']
    
    def to_gpu(self, data: np.ndarray) -> Any:
        """
        将数据传输到 GPU
        
        Args:
            data: NumPy 数组
        
        Returns:
            GPU 数组或原数组
        """
        if self.backend == 'cuda':
            return self._cp.asarray(data)
        elif self.backend == 'opencl':
            # OpenCL 使用 numpy 数组，但创建缓冲区
            return data
        else:
            return data
    
    def to_cpu(self, data: Any) -> np.ndarray:
        """
        将数据传输回 CPU
        
        Args:
            data: GPU 数组或 NumPy 数组
        
        Returns:
            NumPy 数组
        """
        if self.backend == 'cuda' and hasattr(data, 'get'):
            return data.get()
        else:
            return np.asarray(data)
    
    def cosine_similarity(
        self,
        query: np.ndarray,
        vectors: np.ndarray,
        top_k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        GPU 加速的余弦相似度计算
        
        Args:
            query: 查询向量 (dim,)
            vectors: 向量矩阵 (n, dim)
            top_k: 返回数量
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 得分)
        """
        if self.backend == 'cuda':
            return self._cosine_similarity_cuda(query, vectors, top_k)
        else:
            return self._cosine_similarity_cpu(query, vectors, top_k)
    
    def _cosine_similarity_cuda(
        self,
        query: np.ndarray,
        vectors: np.ndarray,
        top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """CUDA 加速的余弦相似度"""
        # 传输到 GPU
        query_gpu = self._cp.asarray(query)
        vectors_gpu = self._cp.asarray(vectors)
        
        # 归一化
        query_norm = query_gpu / (self._cp.linalg.norm(query_gpu) + 1e-10)
        vectors_norm = vectors_gpu / (self._cp.linalg.norm(vectors_gpu, axis=1, keepdims=True) + 1e-10)
        
        # 计算相似度
        scores = self._cp.dot(vectors_norm, query_norm)
        
        # 获取 top-k
        if top_k >= len(scores):
            indices = self._cp.argsort(scores)[::-1]
        else:
            # 使用 argpartition 加速
            indices = self._cp.argpartition(scores, -top_k)[-top_k:]
            indices = indices[self._cp.argsort(scores[indices])[::-1]]
        
        # 传输回 CPU
        return self._cp.asnumpy(indices), self._cp.asnumpy(scores[indices])
    
    def _cosine_similarity_cpu(
        self,
        query: np.ndarray,
        vectors: np.ndarray,
        top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """CPU 回退的余弦相似度"""
        # 归一化
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        
        # 计算相似度
        scores = np.dot(vectors_norm, query_norm)
        
        # 获取 top-k
        if top_k >= len(scores):
            indices = np.argsort(scores)[::-1]
        else:
            indices = np.argpartition(scores, -top_k)[-top_k:]
            indices = indices[np.argsort(scores[indices])[::-1]]
        
        return indices, scores[indices]
    
    def batch_cosine_similarity(
        self,
        queries: np.ndarray,
        vectors: np.ndarray,
        top_k: int = 10
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        批量余弦相似度计算
        
        Args:
            queries: 查询向量矩阵 (n_queries, dim)
            vectors: 向量矩阵 (n_vectors, dim)
            top_k: 每个查询返回的数量
        
        Returns:
            List[Tuple[np.ndarray, np.ndarray]]: 每个查询的结果
        """
        if self.backend == 'cuda':
            return self._batch_cosine_similarity_cuda(queries, vectors, top_k)
        else:
            return self._batch_cosine_similarity_cpu(queries, vectors, top_k)
    
    def _batch_cosine_similarity_cuda(
        self,
        queries: np.ndarray,
        vectors: np.ndarray,
        top_k: int
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """CUDA 批量计算"""
        # 传输到 GPU
        queries_gpu = self._cp.asarray(queries)
        vectors_gpu = self._cp.asarray(vectors)
        
        # 归一化
        queries_norm = queries_gpu / (self._cp.linalg.norm(queries_gpu, axis=1, keepdims=True) + 1e-10)
        vectors_norm = vectors_gpu / (self._cp.linalg.norm(vectors_gpu, axis=1, keepdims=True) + 1e-10)
        
        # 批量计算相似度
        scores_matrix = self._cp.dot(queries_norm, vectors_norm.T)
        
        # 获取每个查询的 top-k
        results = []
        for i in range(len(queries)):
            scores = scores_matrix[i]
            if top_k >= len(scores):
                indices = self._cp.argsort(scores)[::-1]
            else:
                indices = self._cp.argpartition(scores, -top_k)[-top_k:]
                indices = indices[self._cp.argsort(scores[indices])[::-1]]
            results.append((self._cp.asnumpy(indices), self._cp.asnumpy(scores[indices])))
        
        return results
    
    def _batch_cosine_similarity_cpu(
        self,
        queries: np.ndarray,
        vectors: np.ndarray,
        top_k: int
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """CPU 批量计算"""
        # 归一化
        queries_norm = queries / (np.linalg.norm(queries, axis=1, keepdims=True) + 1e-10)
        vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        
        # 批量计算相似度
        scores_matrix = np.dot(queries_norm, vectors_norm.T)
        
        # 获取每个查询的 top-k
        results = []
        for i in range(len(queries)):
            scores = scores_matrix[i]
            if top_k >= len(scores):
                indices = np.argsort(scores)[::-1]
            else:
                indices = np.argpartition(scores, -top_k)[-top_k:]
                indices = indices[np.argsort(scores[indices])[::-1]]
            results.append((indices, scores[indices]))
        
        return results
    
    def get_memory_info(self) -> Dict[str, int]:
        """
        获取 GPU 内存信息
        
        Returns:
            Dict: 内存信息（MB）
        """
        if self.backend == 'cuda':
            mempool = self._cp.get_default_memory_pool()
            return {
                'total_mb': mempool.total_bytes() // (1024**2),
                'used_mb': mempool.used_bytes() // (1024**2),
                'free_mb': mempool.free_bytes() // (1024**2)
            }
        else:
            return {'total_mb': 0, 'used_mb': 0, 'free_mb': 0}
    
    def clear_memory(self):
        """清空 GPU 内存"""
        if self.backend == 'cuda':
            mempool = self._cp.get_default_memory_pool()
            mempool.free_all_blocks()
            print("✅ GPU 内存已清空")


# 全局加速器实例
_accelerator = None


def get_accelerator(prefer_gpu: bool = True) -> GPUAccelerator:
    """
    获取全局加速器实例
    
    Args:
        prefer_gpu: 是否优先使用 GPU
    
    Returns:
        GPUAccelerator: 加速器实例
    """
    global _accelerator
    if _accelerator is None:
        _accelerator = GPUAccelerator(prefer_gpu)
    return _accelerator


def is_gpu_available() -> bool:
    """检查 GPU 是否可用"""
    info = detect_gpu()
    return info['backend'] in ['cuda', 'opencl']


if __name__ == "__main__":
    # 测试
    print("=== GPU 加速器测试 ===")
    
    accel = get_accelerator()
    print(f"后端: {accel.backend}")
    print(f"GPU 可用: {accel.is_gpu_available()}")
    
    # 测试向量搜索
    dim = 4096
    n_vectors = 10000
    n_queries = 10
    
    query = np.random.randn(dim).astype(np.float32)
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    queries = np.random.randn(n_queries, dim).astype(np.float32)
    
    import time
    
    # 单次搜索
    start = time.time()
    indices, scores = accel.cosine_similarity(query, vectors, top_k=20)
    elapsed = time.time() - start
    print(f"单次搜索耗时: {elapsed*1000:.2f}ms")
    
    # 批量搜索
    start = time.time()
    results = accel.batch_cosine_similarity(queries, vectors, top_k=20)
    elapsed = time.time() - start
    print(f"批量搜索耗时: {elapsed*1000:.2f}ms ({n_queries} 个查询)")
    
    # 内存信息
    if accel.is_gpu_available():
        mem_info = accel.get_memory_info()
        print(f"GPU 内存: {mem_info['used_mb']}/{mem_info['total_mb']} MB")
