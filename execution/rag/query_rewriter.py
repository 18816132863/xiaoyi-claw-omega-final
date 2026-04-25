#!/usr/bin/env python3
"""
查询重写模块 (v4.2)
查询向量优化、自适应 top_k、查询扩展
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Callable


class QueryRewriter:
    """
    查询重写器
    优化查询向量以提高搜索效果
    """
    
    def __init__(
        self,
        dim: int = 4096,
        expansion_factor: float = 1.5,
        min_top_k: int = 10,
        max_top_k: int = 100
    ):
        """
        初始化查询重写器
        
        Args:
            dim: 向量维度
            expansion_factor: 扩展因子
            min_top_k: 最小 top_k
            max_top_k: 最大 top_k
        """
        self.dim = dim
        self.expansion_factor = expansion_factor
        self.min_top_k = min_top_k
        self.max_top_k = max_top_k
        
        # 历史查询（用于学习）
        self.query_history = []
        self.feedback_history = []
        
        print(f"查询重写器初始化:")
        print(f"  维度: {dim}")
        print(f"  扩展因子: {expansion_factor}")
        print(f"  top_k 范围: [{min_top_k}, {max_top_k}]")
    
    def normalize(self, query: np.ndarray) -> np.ndarray:
        """
        归一化查询向量
        
        Args:
            query: 查询向量
        
        Returns:
            np.ndarray: 归一化后的向量
        """
        norm = np.linalg.norm(query)
        if norm < 1e-10:
            return query
        return query / norm
    
    def expand_query(
        self,
        query: np.ndarray,
        relevant_vectors: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        扩展查询向量
        
        Args:
            query: 查询向量
            relevant_vectors: 相关向量（用于 Rocchio 扩展）
        
        Returns:
            np.ndarray: 扩展后的查询向量
        """
        query_norm = self.normalize(query)
        
        if relevant_vectors is not None and len(relevant_vectors) > 0:
            # Rocchio 扩展
            # q_new = alpha * q + beta * mean(relevant)
            alpha = 1.0
            beta = 0.5
            
            relevant_mean = np.mean(relevant_vectors, axis=0)
            relevant_norm = self.normalize(relevant_mean)
            
            expanded = alpha * query_norm + beta * relevant_norm
            return self.normalize(expanded)
        
        return query_norm
    
    def adaptive_top_k(
        self,
        query: np.ndarray,
        estimated_results: int = 100
    ) -> int:
        """
        自适应调整 top_k
        
        Args:
            query: 查询向量
            estimated_results: 预估结果数量
        
        Returns:
            int: 建议的 top_k
        """
        # 基础 top_k
        base_top_k = max(self.min_top_k, min(estimated_results, self.max_top_k))
        
        # 根据查询复杂度调整
        # 简单查询（低熵）-> 较小的 top_k
        # 复杂查询（高熵）-> 较大的 top_k
        query_entropy = self._estimate_entropy(query)
        
        if query_entropy < 0.3:
            # 简单查询
            top_k = int(base_top_k * 0.7)
        elif query_entropy > 0.7:
            # 复杂查询
            top_k = int(base_top_k * self.expansion_factor)
        else:
            top_k = base_top_k
        
        return max(self.min_top_k, min(top_k, self.max_top_k))
    
    def _estimate_entropy(self, query: np.ndarray) -> float:
        """
        估计查询熵（复杂度）
        
        Args:
            query: 查询向量
        
        Returns:
            float: 熵值 [0, 1]
        """
        # 归一化
        query_norm = self.normalize(query)
        
        # 计算熵（基于向量分布）
        abs_values = np.abs(query_norm)
        abs_values = abs_values / (np.sum(abs_values) + 1e-10)
        
        # 熵
        entropy = -np.sum(abs_values * np.log(abs_values + 1e-10))
        max_entropy = np.log(len(query))
        
        return entropy / max_entropy if max_entropy > 0 else 0
    
    def rewrite(
        self,
        query: np.ndarray,
        relevant_vectors: Optional[np.ndarray] = None,
        estimated_results: int = 100
    ) -> Tuple[np.ndarray, int]:
        """
        重写查询
        
        Args:
            query: 查询向量
            relevant_vectors: 相关向量
            estimated_results: 预估结果数量
        
        Returns:
            Tuple[np.ndarray, int]: (重写后的查询, top_k)
        """
        # 归一化
        rewritten = self.normalize(query)
        
        # 扩展
        rewritten = self.expand_query(rewritten, relevant_vectors)
        
        # 自适应 top_k
        top_k = self.adaptive_top_k(query, estimated_results)
        
        return rewritten, top_k
    
    def record_feedback(
        self,
        query: np.ndarray,
        results: List[Tuple[str, float]],
        clicked_indices: List[int]
    ):
        """
        记录反馈
        
        Args:
            query: 查询向量
            results: 搜索结果
            clicked_indices: 点击的索引
        """
        self.query_history.append(query)
        self.feedback_history.append({
            'results': results,
            'clicked_indices': clicked_indices
        })
    
    def learn_from_feedback(self) -> Dict[str, Any]:
        """
        从反馈中学习
        
        Returns:
            Dict: 学习结果
        """
        if not self.feedback_history:
            return {'status': 'no_feedback'}
        
        # 分析点击模式
        click_positions = []
        for feedback in self.feedback_history:
            click_positions.extend(feedback['clicked_indices'])
        
        if not click_positions:
            return {'status': 'no_clicks'}
        
        # 统计
        mean_position = np.mean(click_positions)
        std_position = np.std(click_positions)
        
        # 调整建议
        if mean_position > 10:
            suggestion = "建议增加 top_k 或优化查询扩展"
        elif mean_position < 3:
            suggestion = "当前配置良好"
        else:
            suggestion = "可适当调整 top_k"
        
        return {
            'status': 'learned',
            'mean_click_position': mean_position,
            'std_click_position': std_position,
            'suggestion': suggestion
        }


class QueryOptimizer:
    """
    查询优化器
    综合优化查询
    """
    
    def __init__(self, rewriter: QueryRewriter):
        """
        初始化查询优化器
        
        Args:
            rewriter: 查询重写器
        """
        self.rewriter = rewriter
        self.stats = {
            'total_queries': 0,
            'rewritten_queries': 0,
            'expanded_queries': 0
        }
    
    def optimize(
        self,
        query: np.ndarray,
        search_func: Callable,
        relevant_vectors: Optional[np.ndarray] = None
    ) -> List[Tuple[str, float]]:
        """
        优化查询并搜索
        
        Args:
            query: 查询向量
            search_func: 搜索函数
            relevant_vectors: 相关向量
        
        Returns:
            List[Tuple[str, float]]: 搜索结果
        """
        self.stats['total_queries'] += 1
        
        # 重写查询
        rewritten, top_k = self.rewriter.rewrite(query, relevant_vectors)
        
        if not np.allclose(query, rewritten):
            self.stats['rewritten_queries'] += 1
        
        if relevant_vectors is not None:
            self.stats['expanded_queries'] += 1
        
        # 搜索
        results = search_func(rewritten, top_k)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            **self.stats,
            'rewrite_rate': self.stats['rewritten_queries'] / max(1, self.stats['total_queries']),
            'expansion_rate': self.stats['expanded_queries'] / max(1, self.stats['total_queries'])
        }


if __name__ == "__main__":
    # 测试
    print("=== 查询重写器测试 ===")
    
    dim = 4096
    rewriter = QueryRewriter(dim=dim)
    
    # 创建测试数据
    query = np.random.randn(dim).astype(np.float32)
    relevant_vectors = np.random.randn(5, dim).astype(np.float32)
    
    # 归一化
    normalized = rewriter.normalize(query)
    print(f"归一化: 范数 = {np.linalg.norm(normalized):.4f}")
    
    # 扩展
    expanded = rewriter.expand_query(query, relevant_vectors)
    print(f"扩展: 相似度 = {np.dot(rewriter.normalize(query), expanded):.4f}")
    
    # 自适应 top_k
    top_k = rewriter.adaptive_top_k(query, estimated_results=50)
    print(f"自适应 top_k: {top_k}")
    
    # 重写
    rewritten, top_k = rewriter.rewrite(query, relevant_vectors, estimated_results=50)
    print(f"重写: top_k = {top_k}")
    
    # 熵估计
    entropy = rewriter._estimate_entropy(query)
    print(f"查询熵: {entropy:.4f}")
