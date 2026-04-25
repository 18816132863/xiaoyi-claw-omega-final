#!/usr/bin/env python3
"""
rrf - V4.3.2 融合版

融合自:
- orchestration/router/rrf.py
- memory_context/search/rrf.py

此模块为统一实现，其他位置通过兼容层引用
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict

def reciprocal_rank_fusion(
    rankings: List[List[Tuple[str, float]]],
    k: int = 60
) -> List[Tuple[str, float]]:
    """
    Reciprocal Rank Fusion (RRF) 算法
    
    Args:
        rankings: 多个排序列表，每个元素是 (item_id, score) 元组列表
        k: RRF 参数，默认 60
    
    Returns:
        融合后的排序列表
    """
    scores = defaultdict(float)
    
    for ranking in rankings:
        for rank, (item_id, _) in enumerate(ranking, 1):
            scores[item_id] += 1.0 / (k + rank)
    
    # 按分数降序排序
    result = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return result

def weighted_rrf(
    rankings: List[Tuple[List[Tuple[str, float]], float]],
    k: int = 60
) -> List[Tuple[str, float]]:
    """
    加权 RRF
    
    Args:
        rankings: 列表 of (ranking, weight) 元组
        k: RRF 参数
    
    Returns:
        融合后的排序列表
    """
    scores = defaultdict(float)
    
    for ranking, weight in rankings:
        for rank, (item_id, _) in enumerate(ranking, 1):
            scores[item_id] += weight / (k + rank)
    
    result = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return result
