"""
Source Confidence Ranker - 来源可信度排序器
评估和排序来源的可信度
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class ConfidenceLevel(Enum):
    """可信度等级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class ConfidenceScore:
    """可信度分数"""
    source_id: str
    source_type: str
    score: float
    level: ConfidenceLevel
    factors: Dict[str, float] = field(default_factory=dict)
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "score": self.score,
            "level": self.level.value,
            "factors": self.factors,
            "reason": self.reason
        }


@dataclass
class RankingResult:
    """排序结果"""
    total_items: int
    ranked_items: List[ConfidenceScore] = field(default_factory=list)
    ranking_method: str = "confidence"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_items": self.total_items,
            "ranked_items": [r.to_dict() for r in self.ranked_items],
            "ranking_method": self.ranking_method,
            "timestamp": self.timestamp
        }


class SourceConfidenceRanker:
    """
    来源可信度排序器

    职责：
    - 评估来源可信度
    - 考虑多种因素
    - 排序来源
    - 提供可信度等级
    """

    def __init__(self):
        # 来源类型基础可信度
        self._type_base_scores = {
            "session_history": 0.9,
            "user_preference": 0.95,
            "long_term_memory": 0.8,
            "workflow_history": 0.7,
            "skill_history": 0.7,
            "report_memory": 0.6,
            "company_knowledge": 0.75,
            "external_knowledge": 0.5
        }

        # 因素权重
        self._factor_weights = {
            "type": 0.3,
            "recency": 0.2,
            "relevance": 0.25,
            "completeness": 0.15,
            "verification": 0.1
        }

    def rank(
        self,
        sources: List[Dict[str, Any]],
        query: str = "",
        context: Dict[str, Any] = None
    ) -> RankingResult:
        """
        排序来源

        Args:
            sources: 来源列表
            query: 查询
            context: 上下文

        Returns:
            RankingResult
        """
        scores = []

        for source in sources:
            score = self._calculate_confidence(source, query, context)
            scores.append(score)

        # 按分数排序
        scores.sort(key=lambda s: s.score, reverse=True)

        return RankingResult(
            total_items=len(scores),
            ranked_items=scores
        )

    def _calculate_confidence(
        self,
        source: Dict[str, Any],
        query: str,
        context: Dict[str, Any]
    ) -> ConfidenceScore:
        """计算可信度"""
        source_id = source.get("source_id", "")
        source_type = source.get("source_type", "unknown")

        factors = {}

        # 1. 类型基础分数
        type_score = self._type_base_scores.get(source_type, 0.5)
        factors["type"] = type_score

        # 2. 时效性
        recency_score = self._calculate_recency(source)
        factors["recency"] = recency_score

        # 3. 相关性
        relevance_score = self._calculate_relevance(source, query)
        factors["relevance"] = relevance_score

        # 4. 完整性
        completeness_score = self._calculate_completeness(source)
        factors["completeness"] = completeness_score

        # 5. 验证状态
        verification_score = source.get("verified", False) and 1.0 or 0.5
        factors["verification"] = verification_score

        # 加权计算总分
        total_score = sum(
            factors.get(factor, 0) * weight
            for factor, weight in self._factor_weights.items()
        )

        # 确定等级
        if total_score >= 0.8:
            level = ConfidenceLevel.HIGH
        elif total_score >= 0.6:
            level = ConfidenceLevel.MEDIUM
        elif total_score >= 0.4:
            level = ConfidenceLevel.LOW
        else:
            level = ConfidenceLevel.UNKNOWN

        # 生成原因
        reason = self._generate_reason(factors, level)

        return ConfidenceScore(
            source_id=source_id,
            source_type=source_type,
            score=total_score,
            level=level,
            factors=factors,
            reason=reason
        )

    def _calculate_recency(self, source: Dict[str, Any]) -> float:
        """计算时效性分数"""
        timestamp = source.get("timestamp", "")
        if not timestamp:
            return 0.5

        try:
            ts = datetime.fromisoformat(timestamp)
            age_hours = (datetime.now() - ts).total_seconds() / 3600

            if age_hours < 1:
                return 1.0
            elif age_hours < 24:
                return 0.9
            elif age_hours < 168:  # 一周
                return 0.7
            elif age_hours < 720:  # 一个月
                return 0.5
            else:
                return 0.3
        except Exception:
            return 0.5

    def _calculate_relevance(self, source: Dict[str, Any], query: str) -> float:
        """计算相关性分数"""
        if not query:
            return 0.5

        content = source.get("content", "")
        if not content:
            return 0.3

        # 简单关键词匹配
        query_terms = set(query.lower().split())
        content_terms = set(content.lower().split())

        if not query_terms:
            return 0.5

        overlap = len(query_terms & content_terms)
        ratio = overlap / len(query_terms)

        return min(ratio * 2, 1.0)  # 放大但不超过 1.0

    def _calculate_completeness(self, source: Dict[str, Any]) -> float:
        """计算完整性分数"""
        required_fields = ["source_id", "source_type", "content", "timestamp"]
        present = sum(1 for f in required_fields if source.get(f))
        return present / len(required_fields)

    def _generate_reason(
        self,
        factors: Dict[str, float],
        level: ConfidenceLevel
    ) -> str:
        """生成原因说明"""
        reasons = []

        if factors.get("type", 0) >= 0.8:
            reasons.append("high-trust source type")
        if factors.get("recency", 0) >= 0.8:
            reasons.append("recent data")
        if factors.get("relevance", 0) >= 0.8:
            reasons.append("highly relevant")
        if factors.get("verification", 0) >= 0.8:
            reasons.append("verified")

        if not reasons:
            reasons.append(f"confidence level: {level.value}")

        return "; ".join(reasons)

    def get_confidence_scores(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """获取可信度分数映射"""
        scores = {}
        for source in sources:
            score = self._calculate_confidence(source, "", {})
            scores[source.get("source_id", "")] = score.score
        return scores

    def set_type_base_score(self, source_type: str, score: float):
        """设置类型基础分数"""
        self._type_base_scores[source_type] = score

    def set_factor_weight(self, factor: str, weight: float):
        """设置因素权重"""
        self._factor_weights[factor] = weight


# 全局单例
_source_confidence_ranker = None


def get_source_confidence_ranker() -> SourceConfidenceRanker:
    """获取来源可信度排序器单例"""
    global _source_confidence_ranker
    if _source_confidence_ranker is None:
        _source_confidence_ranker = SourceConfidenceRanker()
    return _source_confidence_ranker
