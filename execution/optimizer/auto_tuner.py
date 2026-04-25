#!/usr/bin/env python3
"""
自动调优模块 (v4.2)
自动参数调整、性能基准测试、A/B 测试
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Callable
import time
import json
from pathlib import Path


class AutoTuner:
    """
    自动调优器
    自动搜索最优参数配置
    """
    
    def __init__(
        self,
        param_space: Optional[Dict[str, List]] = None,
        metric: str = 'latency',
        n_trials: int = 20
    ):
        """
        初始化自动调优器
        
        Args:
            param_space: 参数空间
            metric: 优化指标
            n_trials: 试验次数
        """
        self.param_space = param_space or {
            'top_k': [10, 20, 50, 100],
            'n_probe': [5, 10, 20, 50],
            'batch_size': [100, 500, 1000, 5000],
            'use_cache': [True, False],
            'use_quantization': [True, False]
        }
        self.metric = metric
        self.n_trials = n_trials
        
        # 结果
        self.trials = []
        self.best_params = None
        self.best_score = float('inf') if metric == 'latency' else 0
        
        print(f"自动调优器初始化:")
        print(f"  参数空间: {len(self.param_space)} 个参数")
        print(f"  优化指标: {metric}")
        print(f"  试验次数: {n_trials}")
    
    def _sample_params(self) -> Dict[str, Any]:
        """
        随机采样参数
        
        Returns:
            Dict: 参数配置
        """
        params = {}
        for name, values in self.param_space.items():
            params[name] = np.random.choice(values)
        return params
    
    def _evaluate(
        self,
        params: Dict[str, Any],
        eval_func: Callable
    ) -> float:
        """
        评估参数配置
        
        Args:
            params: 参数配置
            eval_func: 评估函数
        
        Returns:
            float: 评估分数
        """
        return eval_func(params)
    
    def optimize(
        self,
        eval_func: Callable,
        n_trials: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        优化参数
        
        Args:
            eval_func: 评估函数
            n_trials: 试验次数
        
        Returns:
            Dict: 最优参数
        """
        n_trials = n_trials or self.n_trials
        
        print(f"\n开始优化 ({n_trials} 次试验)...")
        
        for i in range(n_trials):
            # 采样参数
            params = self._sample_params()
            
            # 评估
            score = self._evaluate(params, eval_func)
            
            # 记录
            self.trials.append({
                'trial': i + 1,
                'params': params,
                'score': score
            })
            
            # 更新最优
            if self.metric == 'latency':
                if score < self.best_score:
                    self.best_score = score
                    self.best_params = params
            else:
                if score > self.best_score:
                    self.best_score = score
                    self.best_params = params
            
            if (i + 1) % 5 == 0:
                print(f"  试验 {i + 1}/{n_trials}, 最优 {self.metric}: {self.best_score:.4f}")
        
        print(f"\n✅ 优化完成")
        print(f"最优参数: {self.best_params}")
        print(f"最优 {self.metric}: {self.best_score:.4f}")
        
        return self.best_params
    
    def get_results(self) -> List[Dict]:
        """
        获取所有试验结果
        
        Returns:
            List[Dict]: 试验结果
        """
        return self.trials
    
    def save_results(self, path: str):
        """
        保存结果
        
        Args:
            path: 保存路径
        """
        results = {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'trials': self.trials
        }
        
        with open(path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ 结果已保存到 {path}")


class PerformanceBenchmark:
    """
    性能基准测试
    """
    
    def __init__(self, name: str = "benchmark"):
        """
        初始化基准测试
        
        Args:
            name: 测试名称
        """
        self.name = name
        self.results = {}
    
    def run(
        self,
        func: Callable,
        n_runs: int = 10,
        warmup: int = 3
    ) -> Dict[str, float]:
        """
        运行基准测试
        
        Args:
            func: 测试函数
            n_runs: 运行次数
            warmup: 预热次数
        
        Returns:
            Dict: 测试结果
        """
        # 预热
        for _ in range(warmup):
            func()
        
        # 正式测试
        times = []
        for _ in range(n_runs):
            start = time.perf_counter()
            func()
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        
        # 统计
        times = np.array(times)
        results = {
            'mean_ms': np.mean(times) * 1000,
            'std_ms': np.std(times) * 1000,
            'min_ms': np.min(times) * 1000,
            'max_ms': np.max(times) * 1000,
            'p50_ms': np.percentile(times, 50) * 1000,
            'p95_ms': np.percentile(times, 95) * 1000,
            'p99_ms': np.percentile(times, 99) * 1000
        }
        
        self.results[self.name] = results
        
        print(f"\n基准测试结果 ({self.name}):")
        print(f"  平均: {results['mean_ms']:.2f} ms")
        print(f"  标准差: {results['std_ms']:.2f} ms")
        print(f"  最小: {results['min_ms']:.2f} ms")
        print(f"  最大: {results['max_ms']:.2f} ms")
        print(f"  P50: {results['p50_ms']:.2f} ms")
        print(f"  P95: {results['p95_ms']:.2f} ms")
        print(f"  P99: {results['p99_ms']:.2f} ms")
        
        return results


class ABTestFramework:
    """
    A/B 测试框架
    """
    
    def __init__(self, name: str = "ab_test"):
        """
        初始化 A/B 测试
        
        Args:
            name: 测试名称
        """
        self.name = name
        self.variants = {}
        self.results = {}
    
    def add_variant(
        self,
        name: str,
        func: Callable,
        description: str = ""
    ):
        """
        添加变体
        
        Args:
            name: 变体名称
            func: 变体函数
            description: 描述
        """
        self.variants[name] = {
            'func': func,
            'description': description
        }
    
    def run(
        self,
        n_runs: int = 10,
        warmup: int = 3
    ) -> Dict[str, Dict]:
        """
        运行 A/B 测试
        
        Args:
            n_runs: 运行次数
            warmup: 预热次数
        
        Returns:
            Dict: 测试结果
        """
        print(f"\n=== A/B 测试: {self.name} ===")
        
        for name, variant in self.variants.items():
            print(f"\n测试变体: {name}")
            benchmark = PerformanceBenchmark(name)
            results = benchmark.run(variant['func'], n_runs, warmup)
            self.results[name] = results
        
        # 对比
        self._compare_results()
        
        return self.results
    
    def _compare_results(self):
        """对比结果"""
        print(f"\n=== 结果对比 ===")
        
        # 按平均延迟排序
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['mean_ms']
        )
        
        baseline = sorted_results[0][1]['mean_ms']
        
        for name, results in sorted_results:
            speedup = baseline / results['mean_ms']
            print(f"{name}: {results['mean_ms']:.2f} ms ({speedup:.2f}x)")
    
    def get_winner(self) -> str:
        """
        获取最优变体
        
        Returns:
            str: 最优变体名称
        """
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['mean_ms']
        )
        return sorted_results[0][0]


if __name__ == "__main__":
    # 测试
    print("=== 自动调优测试 ===")
    
    # 创建测试数据
    dim = 4096
    n_vectors = 10000
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    queries = np.random.randn(10, dim).astype(np.float32)
    
    # 定义评估函数
    def eval_func(params):
        top_k = params['top_k']
        use_cache = params['use_cache']
        
        # 模拟搜索
        start = time.time()
        for query in queries:
            query_norm = query / (np.linalg.norm(query) + 1e-10)
            vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
            scores = np.dot(vectors_norm, query_norm)
            _ = np.argsort(scores)[::-1][:top_k]
        elapsed = time.time() - start
        
        return elapsed
    
    # 创建调优器
    tuner = AutoTuner(
        param_space={
            'top_k': [10, 20, 50],
            'use_cache': [True, False]
        },
        metric='latency',
        n_trials=10
    )
    
    # 优化
    best_params = tuner.optimize(eval_func)
    
    # A/B 测试
    print("\n=== A/B 测试 ===")
    
    ab_test = ABTestFramework("search_comparison")
    
    ab_test.add_variant(
        "brute_force",
        lambda: np.dot(vectors, queries[0]),
        "暴力搜索"
    )
    
    ab_test.add_variant(
        "normalized",
        lambda: np.dot(
            vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10),
            queries[0] / (np.linalg.norm(queries[0]) + 1e-10)
        ),
        "归一化搜索"
    )
    
    results = ab_test.run(n_runs=5)
    print(f"最优变体: {ab_test.get_winner()}")
