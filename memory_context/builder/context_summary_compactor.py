"""
Context Summary Compactor - 上下文摘要压缩器
压缩和总结上下文内容
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


@dataclass
class CompactionResult:
    """压缩结果"""
    original_tokens: int
    compacted_tokens: int
    compression_ratio: float
    method: str
    summary: str
    preserved_items: List[Dict[str, Any]] = field(default_factory=list)
    removed_items: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_tokens": self.original_tokens,
            "compacted_tokens": self.compacted_tokens,
            "compression_ratio": self.compression_ratio,
            "method": self.method,
            "summary": self.summary,
            "preserved_items": len(self.preserved_items),
            "removed_items": len(self.removed_items),
            "timestamp": self.timestamp
        }


class ContextSummaryCompactor:
    """
    上下文摘要压缩器

    职责：
    - 压缩冗余内容
    - 生成摘要
    - 保留关键信息
    - 控制压缩比例
    """

    def __init__(self):
        # 压缩策略
        self._strategies = {
            "aggressive": {"target_ratio": 0.3, "min_preserve": 0.2},
            "moderate": {"target_ratio": 0.5, "min_preserve": 0.4},
            "conservative": {"target_ratio": 0.7, "min_preserve": 0.6}
        }

        # 关键词权重
        self._keyword_weights: Dict[str, float] = {}

    def compact(
        self,
        content: List[Dict[str, Any]],
        target_tokens: int,
        strategy: str = "moderate",
        preserve_keywords: List[str] = None
    ) -> CompactionResult:
        """
        压缩内容

        Args:
            content: 内容列表
            target_tokens: 目标 token 数
            strategy: 压缩策略
            preserve_keywords: 需要保留的关键词

        Returns:
            CompactionResult
        """
        preserve_keywords = preserve_keywords or []
        strategy_config = self._strategies.get(strategy, self._strategies["moderate"])

        # 计算原始 token 数
        original_tokens = sum(item.get("tokens", 0) for item in content)

        if original_tokens <= target_tokens:
            # 不需要压缩
            return CompactionResult(
                original_tokens=original_tokens,
                compacted_tokens=original_tokens,
                compression_ratio=1.0,
                method="none",
                summary="No compaction needed",
                preserved_items=content
            )

        # 计算目标压缩比例
        target_ratio = target_tokens / original_tokens
        target_ratio = max(target_ratio, strategy_config["min_preserve"])

        # 评分和排序
        scored_items = []
        for item in content:
            score = self._score_item(item, preserve_keywords)
            scored_items.append((score, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)

        # 选择保留的内容
        preserved = []
        preserved_tokens = 0
        removed = []

        for score, item in scored_items:
            item_tokens = item.get("tokens", 0)
            if preserved_tokens + item_tokens <= target_tokens:
                preserved.append(item)
                preserved_tokens += item_tokens
            else:
                removed.append(item)

        # 生成摘要
        summary = self._generate_summary(preserved)

        return CompactionResult(
            original_tokens=original_tokens,
            compacted_tokens=preserved_tokens,
            compression_ratio=preserved_tokens / original_tokens if original_tokens > 0 else 1.0,
            method=strategy,
            summary=summary,
            preserved_items=preserved,
            removed_items=removed
        )

    def _score_item(
        self,
        item: Dict[str, Any],
        keywords: List[str]
    ) -> float:
        """评分内容项"""
        score = 0.0

        # 基础分数
        source_type = item.get("source_type", "")
        type_scores = {
            "session_history": 1.0,
            "user_preference": 0.9,
            "long_term_memory": 0.8,
            "workflow_history": 0.7,
            "skill_history": 0.6,
            "report_memory": 0.5
        }
        score += type_scores.get(source_type, 0.5)

        # 关键词匹配
        content = item.get("content", "")
        for keyword in keywords:
            if keyword.lower() in content.lower():
                score += 0.2

        # 可信度
        confidence = item.get("confidence", 0.5)
        score += confidence * 0.5

        # 时效性（越新越好）
        timestamp = item.get("timestamp", "")
        if timestamp:
            try:
                ts = datetime.fromisoformat(timestamp)
                age_hours = (datetime.now() - ts).total_seconds() / 3600
                if age_hours < 1:
                    score += 0.3
                elif age_hours < 24:
                    score += 0.2
                elif age_hours < 168:  # 一周
                    score += 0.1
            except Exception:
                pass

        return score

    def _generate_summary(self, items: List[Dict[str, Any]]) -> str:
        """生成摘要"""
        if not items:
            return "No content preserved"

        # 按来源类型分组
        by_type: Dict[str, List[str]] = {}
        for item in items:
            source_type = item.get("source_type", "unknown")
            content = item.get("content", "")
            if source_type not in by_type:
                by_type[source_type] = []
            # 提取前 100 字符
            summary = content[:100] + "..." if len(content) > 100 else content
            by_type[source_type].append(summary)

        # 构建摘要
        parts = []
        for source_type, contents in by_type.items():
            parts.append(f"{source_type}: {len(contents)} items")

        return "; ".join(parts)

    def summarize_content(self, content: str, max_length: int = 200) -> str:
        """总结单个内容"""
        if len(content) <= max_length:
            return content

        # 简单截断
        return content[:max_length - 3] + "..."

    def set_keyword_weight(self, keyword: str, weight: float):
        """设置关键词权重"""
        self._keyword_weights[keyword] = weight


# 全局单例
_context_summary_compactor = None


def get_context_summary_compactor() -> ContextSummaryCompactor:
    """获取上下文摘要压缩器单例"""
    global _context_summary_compactor
    if _context_summary_compactor is None:
        _context_summary_compactor = ContextSummaryCompactor()
    return _context_summary_compactor
