#!/usr/bin/env python3
"""
weights - V4.3.2 融合版

融合自:
- infrastructure/shared/weights.py
- orchestration/router/weights.py
- memory_context/search/weights.py

此模块为统一实现，其他位置通过兼容层引用
"""

from typing import Dict, List

# 默认权重配置
DEFAULT_WEIGHTS = {
    "relevance": 0.4,
    "recency": 0.2,
    "popularity": 0.2,
    "quality": 0.2,
}

def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """归一化权重"""
    total = sum(weights.values())
    if total == 0:
        return weights
    return {k: v / total for k, v in weights.items()}

def weighted_score(scores: Dict[str, float], weights: Dict[str, float] = None) -> float:
    """计算加权分数"""
    weights = weights or DEFAULT_WEIGHTS
    weights = normalize_weights(weights)
    
    total = 0.0
    for key, weight in weights.items():
        total += scores.get(key, 0) * weight
    
    return total

def combine_scores(score_lists: List[List[float]], weights: List[float] = None) -> List[float]:
    """组合多个分数列表"""
    if not score_lists:
        return []
    
    n = len(score_lists[0])
    if weights is None:
        weights = [1.0 / len(score_lists)] * len(score_lists)
    
    result = []
    for i in range(n):
        total = sum(sl[i] * w for sl, w in zip(score_lists, weights))
        result.append(total)
    
    return result
