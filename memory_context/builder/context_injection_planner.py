"""
Context Injection Planner - 上下文注入规划器
规划如何注入检索到的内容
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class SourcePriority(Enum):
    """来源优先级"""
    REQUIRED = "required"
    OPTIONAL = "optional"
    SUPPRESSED = "suppressed"


@dataclass
class SourcePlan:
    """来源规划"""
    source_id: str
    source_type: str
    priority: SourcePriority
    confidence: float
    tokens: int
    reason: str = ""
    injection_order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "priority": self.priority.value,
            "confidence": self.confidence,
            "tokens": self.tokens,
            "reason": self.reason,
            "injection_order": self.injection_order
        }


@dataclass
class InjectionPlan:
    """注入规划"""
    task_id: str
    required_sources: List[SourcePlan] = field(default_factory=list)
    optional_sources: List[SourcePlan] = field(default_factory=list)
    suppressed_sources: List[SourcePlan] = field(default_factory=list)
    trimmed_sources: List[SourcePlan] = field(default_factory=list)
    conflict_sources: List[SourcePlan] = field(default_factory=list)
    final_injection_order: List[str] = field(default_factory=list)
    total_budget: int = 0
    allocated_budget: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "required_sources": [s.to_dict() for s in self.required_sources],
            "optional_sources": [s.to_dict() for s in self.optional_sources],
            "suppressed_sources": [s.to_dict() for s in self.suppressed_sources],
            "trimmed_sources": [s.to_dict() for s in self.trimmed_sources],
            "conflict_sources": [s.to_dict() for s in self.conflict_sources],
            "final_injection_order": self.final_injection_order,
            "total_budget": self.total_budget,
            "allocated_budget": self.allocated_budget,
            "timestamp": self.timestamp
        }


class ContextInjectionPlanner:
    """
    上下文注入规划器

    职责：
    - 决定哪些来源必须注入
    - 决定哪些来源可选注入
    - 决定哪些来源需要抑制
    - 处理 token 预算裁剪
    - 处理来源冲突
    - 确定最终注入顺序
    """

    def __init__(self):
        # 来源类型优先级
        self._type_priority = {
            "session_history": 100,
            "user_preference": 90,
            "long_term_memory": 80,
            "workflow_history": 70,
            "skill_history": 60,
            "report_memory": 50,
            "company_knowledge": 40,
            "external_knowledge": 30
        }

        # 必需来源类型
        self._required_types = {"session_history", "user_preference"}

        # 冲突来源对
        self._conflict_pairs = [
            ("user_preference", "company_knowledge"),
            ("session_history", "external_knowledge")
        ]

    def plan(
        self,
        task_id: str,
        sources: List[Dict[str, Any]],
        token_budget: int,
        confidence_scores: Dict[str, float] = None,
        conflicts: List[Dict[str, Any]] = None
    ) -> InjectionPlan:
        """
        规划注入

        Args:
            task_id: 任务 ID
            sources: 来源列表
            token_budget: token 预算
            confidence_scores: 可信度分数
            conflicts: 冲突列表

        Returns:
            InjectionPlan
        """
        confidence_scores = confidence_scores or {}
        conflicts = conflicts or []

        plan = InjectionPlan(
            task_id=task_id,
            total_budget=token_budget
        )

        # 1. 分类来源
        for source in sources:
            source_id = source.get("source_id", "")
            source_type = source.get("source_type", "unknown")
            tokens = source.get("tokens", 0)
            confidence = confidence_scores.get(source_id, 0.5)

            source_plan = SourcePlan(
                source_id=source_id,
                source_type=source_type,
                priority=SourcePriority.OPTIONAL,
                confidence=confidence,
                tokens=tokens
            )

            # 判断优先级
            if source_type in self._required_types:
                source_plan.priority = SourcePriority.REQUIRED
                source_plan.reason = "Required source type"
                plan.required_sources.append(source_plan)
            else:
                plan.optional_sources.append(source_plan)

        # 2. 处理冲突
        plan.conflict_sources = self._resolve_conflicts(plan, conflicts)

        # 3. 预算裁剪
        plan.trimmed_sources = self._apply_budget(plan, token_budget)

        # 4. 确定最终注入顺序
        plan.final_injection_order = self._determine_order(plan)

        # 5. 计算分配预算
        plan.allocated_budget = sum(
            s.tokens for s in plan.required_sources
        ) + sum(
            s.tokens for s in plan.optional_sources
            if s.source_id in plan.final_injection_order
        )

        return plan

    def _resolve_conflicts(
        self,
        plan: InjectionPlan,
        conflicts: List[Dict[str, Any]]
    ) -> List[SourcePlan]:
        """解决冲突"""
        conflict_sources = []

        for conflict in conflicts:
            sources_involved = conflict.get("sources", [])
            resolution = conflict.get("resolution", "higher_confidence")

            if resolution == "higher_confidence":
                # 保留可信度更高的
                if len(sources_involved) >= 2:
                    # 抑制可信度较低的
                    lower_confidence = sources_involved[1]
                    for sp in plan.optional_sources:
                        if sp.source_id == lower_confidence:
                            sp.priority = SourcePriority.SUPPRESSED
                            sp.reason = "Suppressed due to conflict"
                            conflict_sources.append(sp)
                            break

        return conflict_sources

    def _apply_budget(
        self,
        plan: InjectionPlan,
        budget: int
    ) -> List[SourcePlan]:
        """应用预算裁剪"""
        trimmed = []

        # 计算必需来源的 token
        required_tokens = sum(s.tokens for s in plan.required_sources)
        remaining = budget - required_tokens

        if remaining <= 0:
            # 预算不足，只能保留必需来源
            for sp in plan.optional_sources:
                sp.priority = SourcePriority.SUPPRESSED
                sp.reason = "Trimmed due to budget"
                trimmed.append(sp)
            return trimmed

        # 按优先级和可信度排序可选来源
        sorted_optional = sorted(
            plan.optional_sources,
            key=lambda s: (
                self._type_priority.get(s.source_type, 0),
                s.confidence
            ),
            reverse=True
        )

        # 按预算裁剪
        used = 0
        for sp in sorted_optional:
            if used + sp.tokens <= remaining:
                used += sp.tokens
            else:
                sp.priority = SourcePriority.SUPPRESSED
                sp.reason = "Trimmed due to budget"
                trimmed.append(sp)

        return trimmed

    def _determine_order(self, plan: InjectionPlan) -> List[str]:
        """确定注入顺序"""
        order = []

        # 1. 必需来源按类型优先级排序
        required_sorted = sorted(
            plan.required_sources,
            key=lambda s: self._type_priority.get(s.source_type, 0),
            reverse=True
        )
        for i, sp in enumerate(required_sorted):
            sp.injection_order = i + 1
            order.append(sp.source_id)

        # 2. 可选来源（未被抑制的）按优先级和可信度排序
        active_optional = [
            s for s in plan.optional_sources
            if s.priority != SourcePriority.SUPPRESSED
        ]
        optional_sorted = sorted(
            active_optional,
            key=lambda s: (
                self._type_priority.get(s.source_type, 0),
                s.confidence
            ),
            reverse=True
        )
        for i, sp in enumerate(optional_sorted):
            sp.injection_order = len(order) + i + 1
            order.append(sp.source_id)

        return order

    def set_type_priority(self, source_type: str, priority: int):
        """设置类型优先级"""
        self._type_priority[source_type] = priority

    def set_required_types(self, types: List[str]):
        """设置必需类型"""
        self._required_types = set(types)


# 全局单例
_context_injection_planner = None


def get_context_injection_planner() -> ContextInjectionPlanner:
    """获取上下文注入规划器单例"""
    global _context_injection_planner
    if _context_injection_planner is None:
        _context_injection_planner = ContextInjectionPlanner()
    return _context_injection_planner
