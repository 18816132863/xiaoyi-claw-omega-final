#!/usr/bin/env python3
"""
决策审查模块 - V1.0.0

审查系统决策的合理性和可解释性。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DecisionQuality(Enum):
    """决策质量"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class DecisionReview:
    """决策审查结果"""
    id: str
    decision_type: str
    quality: DecisionQuality
    reasoning_quality: float
    evidence_quality: float
    bias_check: bool
    consistency_check: bool
    issues: List[str]
    suggestions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class DecisionReviewer:
    """决策审查器"""
    
    def __init__(self):
        self.reviews: List[DecisionReview] = []
        self.decision_history: List[Dict] = []
    
    def review_decision(self,
                        decision_type: str,
                        reasoning: str,
                        evidence: List[str],
                        context: Dict = None) -> DecisionReview:
        """
        审查决策
        
        Args:
            decision_type: 决策类型
            reasoning: 推理过程
            evidence: 证据列表
            context: 上下文
        
        Returns:
            审查结果
        """
        issues = []
        suggestions = []
        
        # 1. 检查推理质量
        reasoning_quality = self._evaluate_reasoning(reasoning)
        if reasoning_quality < 0.5:
            issues.append("推理过程不充分")
            suggestions.append("建议: 提供更详细的推理步骤")
        
        # 2. 检查证据质量
        evidence_quality = self._evaluate_evidence(evidence)
        if evidence_quality < 0.5:
            issues.append("证据支持不足")
            suggestions.append("建议: 提供更多支持证据")
        
        # 3. 检查偏见
        bias_check = self._check_bias(reasoning, evidence)
        if not bias_check:
            issues.append("可能存在偏见")
            suggestions.append("建议: 考虑替代观点")
        
        # 4. 检查一致性
        consistency_check = self._check_consistency(decision_type, reasoning, context)
        if not consistency_check:
            issues.append("与历史决策不一致")
            suggestions.append("建议: 解释差异原因")
        
        # 计算质量
        quality = self._calculate_quality(
            reasoning_quality, evidence_quality, bias_check, consistency_check
        )
        
        review = DecisionReview(
            id=f"dec_review_{len(self.reviews)}",
            decision_type=decision_type,
            quality=quality,
            reasoning_quality=reasoning_quality,
            evidence_quality=evidence_quality,
            bias_check=bias_check,
            consistency_check=consistency_check,
            issues=issues,
            suggestions=suggestions
        )
        
        self.reviews.append(review)
        return review
    
    def _evaluate_reasoning(self, reasoning: str) -> float:
        """评估推理质量"""
        if not reasoning:
            return 0.0
        
        score = 0.5
        
        # 检查推理步骤
        if "因为" in reasoning or "因此" in reasoning or "所以" in reasoning:
            score += 0.1
        
        # 检查逻辑连接词
        if "首先" in reasoning and "然后" in reasoning:
            score += 0.1
        
        # 检查长度
        if len(reasoning) > 100:
            score += 0.1
        
        # 检查是否考虑替代方案
        if "或者" in reasoning or "备选" in reasoning:
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_evidence(self, evidence: List[str]) -> float:
        """评估证据质量"""
        if not evidence:
            return 0.0
        
        score = min(len(evidence) * 0.2, 0.6)
        
        # 检查证据多样性
        if len(set(evidence)) == len(evidence):
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_bias(self, reasoning: str, evidence: List[str]) -> bool:
        """检查偏见"""
        bias_indicators = [
            "总是", "从不", "所有", "没有", "肯定", "绝对"
        ]
        
        text = reasoning + " ".join(evidence)
        for indicator in bias_indicators:
            if indicator in text:
                return False
        
        return True
    
    def _check_consistency(self, decision_type: str, reasoning: str, context: Dict) -> bool:
        """检查一致性"""
        if not context:
            return True
        
        # 检查与历史决策的一致性
        similar_decisions = [
            d for d in self.decision_history
            if d.get("type") == decision_type
        ]
        
        if similar_decisions:
            # 简化：假设一致
            return True
        
        return True
    
    def _calculate_quality(self,
                           reasoning_quality: float,
                           evidence_quality: float,
                           bias_check: bool,
                           consistency_check: bool) -> DecisionQuality:
        """计算决策质量"""
        score = (reasoning_quality + evidence_quality) / 2
        
        if not bias_check:
            score -= 0.2
        if not consistency_check:
            score -= 0.1
        
        if score >= 0.9:
            return DecisionQuality.EXCELLENT
        elif score >= 0.7:
            return DecisionQuality.GOOD
        elif score >= 0.5:
            return DecisionQuality.ACCEPTABLE
        elif score >= 0.3:
            return DecisionQuality.POOR
        else:
            return DecisionQuality.UNACCEPTABLE
    
    def record_decision(self, decision: Dict):
        """记录决策"""
        self.decision_history.append(decision)


# 全局决策审查器
_decision_reviewer: Optional[DecisionReviewer] = None


def get_decision_reviewer() -> DecisionReviewer:
    """获取全局决策审查器"""
    global _decision_reviewer
    if _decision_reviewer is None:
        _decision_reviewer = DecisionReviewer()
    return _decision_reviewer
