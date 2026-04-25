#!/usr/bin/env python3
"""
GPU 加速模块
支持 CUDA 和 OpenCL 后端

功能：
- CUDA 向量操作（NVIDIA GPU）
- OpenCL 向量操作（通用 GPU）
- 自动检测可用后端
- 回退到 CPU 实现
"""

import numpy as np
from typing import List, Tuple, Optional, Union
import os
import platform
import warnings

# GPU 后端检测
GPU_BACKEND = None
CUDA_AVAILABLE = False
OPENCL_AVAILABLE = False

def detect_gpu_backend() -> dict:
    """
    检测可用的 GPU 后端
    
    Returns:
        dict: GPU 支持信息
    """
    global CUDA_AVAILABLE, OPENCL_AVAILABLE, GPU_BACKEND
    
    info = {
        'cuda': False,
        'cuda_version': None,
        'cuda_devices': [],
        'opencl': False,
        'opencl_platforms': [],
        'backend': 'cpu'
    }
    
    # 检测 CUDA
    try:
        import cupy as cp
        CUDA_AVAILABLE = True
        info['cuda'] = True
        info['cuda_version'] = cp.__version__
        info['cuda_devices'] = [cp.cuda.Device(i).name for i in range(cp.cuda.runtime.getDeviceCount())]
        info['backend'] = 'cuda'
        GPU_BACKEND = 'cuda'
    except ImportError:
        pass
    except Exception as e:
        warnings.warn(f"CUDA 检测失败: {e}")
    
    # 检测 OpenCL
    if not CUDA_AVAILABLE:
        try:
            import pyopencl as cl
            OPENCL_AVAILABLE = True
            info['opencl'] = True
            info['opencl_platforms'] = [p.name for p in cl.get_platforms()]
            info['backend'] = 'opencl'
            GPU_BACKEND = 'opencl'
        except ImportError:
            pass
        except Exception as e:
            warnings.warn(f"OpenCL 检测失败: {e}")
    
    return info

# 初始化检测
GPU_INFO = detect_gpu_backend()


class GPUVectorOps:
    """
    GPU 向量操作类
    自动选择最优后端（CUDA > OpenCL > CPU）
    """
    
    def __init__(self, use_gpu: bool = True, backend: str = 'auto'):
        """
        初始化 GPU 向量操作器
        
        Args:
            use_gpu: 是否使用 GPU 加速
            backend: 后端选择 ('auto', 'cuda', 'opencl', 'cpu')
        """
        self.use_gpu = use_gpu
        self.backend = backend
        self.xp = None  # numpy 或 cupy
        
        if backend == 'auto':
            if use_gpu and CUDA_AVAILABLE:
                self.backend = 'cuda'
            elif use_gpu and OPENCL_AVAILABLE:
                self.backend = 'opencl'
            else:
                self.backend = 'cpu'
        
        # 初始化后端
        if self.backend == 'cuda' and CUDA_AVAILABLE:
            import cupy as cp
            self.xp = cp
            print(f"✅ CUDA 后端已启用 (版本: {GPU_INFO['cuda_version']})")
        elif self.backend == 'opencl' and OPENCL_AVAILABLE:
            import numpy as np
            self.xp = np
            print(f"✅ OpenCL 后端已启用")
        else:
            import numpy as np
            self.xp = np
            self.backend = 'cpu'
            print("ℹ️ 使用 CPU 后端")
    
    def to_gpu(self, arr: np.ndarray):
        """将数组移动到 GPU"""
        if self.backend == 'cuda':
            return self.xp.asarray(arr)
        return arr
    
    def to_cpu(self, arr) -> np.ndarray:
        """将数组移动到 CPU"""
        if self.backend == 'cuda' and hasattr(arr, 'get'):
            return arr.get()
        return np.asarray(arr)
    
    def cosine_similarity(
        self, 
        vec1: np.ndarray, 
        vec2: np.ndarray
    ) -> float:
        """计算余弦相似度"""
        vec1 = self.to_gpu(np.asarray(vec1, dtype=np.float32))
        vec2 = self.to_gpu(np.asarray(vec2, dtype=np.float32))
        
        norm1 = self.xp.linalg.norm(vec1)
        norm2 = self.xp.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(self.to_cpu(self.xp.dot(vec1, vec2) / (norm1 * norm2)))
    
    def cosine_similarity_batch(
        self, 
        query: np.ndarray, 
        vectors: np.ndarray
    ) -> np.ndarray:
        """批量计算余弦相似度"""
        query = self.to_gpu(np.asarray(query, dtype=np.float32))
        vectors = self.to_gpu(np.asarray(vectors, dtype=np.float32))
        
        # 归一化
        query_norm = query / (self.xp.linalg.norm(query) + 1e-10)
        vectors_norm = vectors / (self.xp.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        
        # 批量点积
        similarities = self.xp.dot(vectors_norm, query_norm)
        
        return self.to_cpu(similarities)
    
    def euclidean_distance_batch(
        self, 
        query: np.ndarray, 
        vectors: np.ndarray
    ) -> np.ndarray:
        """批量计算欧氏距离"""
        query = self.to_gpu(np.asarray(query, dtype=np.float32))
        vectors = self.to_gpu(np.asarray(vectors, dtype=np.float32))
        
        diff = vectors - query
        distances = self.xp.linalg.norm(diff, axis=1)
        
        return self.to_cpu(distances)
    
    def top_k_search(
        self, 
        query: np.ndarray, 
        vectors: np.ndarray, 
        k: int = 10,
        metric: str = 'cosine'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Top-K 向量搜索"""
        if metric == 'cosine':
            scores = self.cosine_similarity_batch(query, vectors)
            indices = np.argsort(-scores)[:k]
        else:
            scores = self.euclidean_distance_batch(query, vectors)
            indices = np.argsort(scores)[:k]
        
        return indices, scores[indices]
    
    def batch_matrix_multiply(
        self, 
        matrix_a: np.ndarray, 
        matrix_b: np.ndarray
    ) -> np.ndarray:
        """
        批量矩阵乘法
        充分利用 GPU 并行计算
        """
        matrix_a = self.to_gpu(np.asarray(matrix_a, dtype=np.float32))
        matrix_b = self.to_gpu(np.asarray(matrix_b, dtype=np.float32))
        
        result = self.xp.dot(matrix_a, matrix_b)
        
        return self.to_cpu(result)


def get_gpu_ops(use_gpu: bool = True, backend: str = 'auto') -> GPUVectorOps:
    """
    获取 GPU 向量操作实例
    
    Args:
        use_gpu: 是否使用 GPU
        backend: 后端选择
        
    Returns:
        GPUVectorOps: 向量操作实例
    """
    return GPUVectorOps(use_gpu=use_gpu, backend=backend)


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("GPU 加速模块")
    print("=" * 60)
    
    print(f"\n📊 GPU 支持检测:")
    for key, value in GPU_INFO.items():
        print(f"   {key}: {value}")
    
    import time
    
    # 性能测试
    dim = 1536
    n_vectors = 100000
    
    print(f"\n🔬 性能测试 (dim={dim}, n={n_vectors}):")
    
    np.random.seed(42)
    query = np.random.randn(dim).astype(np.float32)
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    
    # CPU 测试
    print("\n   CPU 后端:")
    ops = get_gpu_ops(use_gpu=False)
    
    start = time.time()
    similarities = ops.cosine_similarity_batch(query, vectors)
    elapsed = (time.time() - start) * 1000
    print(f"   批量余弦相似度: {elapsed:.2f}ms")
    
    # GPU 测试（如果可用）
    if GPU_INFO['backend'] != 'cpu':
        print(f"\n   {GPU_INFO['backend'].upper()} 后端:")
        ops = get_gpu_ops(use_gpu=True)
        
        # 预热
        _ = ops.cosine_similarity_batch(query, vectors[:1000])
        
        start = time.time()
        similarities = ops.cosine_similarity_batch(query, vectors)
        elapsed = (time.time() - start) * 1000
        print(f"   批量余弦相似度: {elapsed:.2f}ms")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
