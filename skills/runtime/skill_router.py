from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Dict, Optional, List

from skills.registry.skill_registry import (
    SkillRegistry,
    SkillManifest,
    SkillStatus,
)


@dataclass
class SkillExecutionContext:
    profile: str = "default"
    constraints: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillExecutionResult:
    success: bool
    skill_id: str
    output: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    error: Optional[str] = None


class SkillRouter:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def discover(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        matches = self.registry.search(query)
        return [m.skill_id for m in matches if m.status != SkillStatus.DISABLED]

    def select_skill(
        self,
        intent: str,
        profile: str,
        constraints: Optional[Dict[str, Any]] = None,
        governance_decision: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        选择技能
        
        Args:
            intent: 意图
            profile: 执行配置
            constraints: 约束条件
            governance_decision: governance decision object
        
        Returns:
            选择结果
        """
        constraints = constraints or {}
        governance_decision = governance_decision or {}
        
        # 1. 按 intent 搜索
        candidates = self.registry.search(intent)
        
        # 2. 没搜到就退化为所有可用技能
        if not candidates:
            candidates = [
                s for s in self.registry.list()
                if s.status not in {SkillStatus.DISABLED, SkillStatus.DEPRECATED}
            ]
        
        if not candidates:
            return {
                "success": False,
                "skill_id": None,
                "confidence": 0.0,
                "reason": "no_available_skill",
                "profile": profile,
            }
        
        # 3. 按 profile 过滤
        allowed_categories = self._get_allowed_categories(profile)
        if "*" not in allowed_categories:
            candidates = [
                c for c in candidates
                if c.category.value in allowed_categories
            ]
        
        if not candidates:
            return {
                "success": False,
                "skill_id": None,
                "confidence": 0.0,
                "reason": "no_skill_in_allowed_categories",
                "profile": profile,
                "allowed_categories": allowed_categories,
            }
        
        # 4. 按 status 过滤
        candidates = [
            c for c in candidates
            if c.status == SkillStatus.STABLE or c.status == SkillStatus.EXPERIMENTAL
        ]
        
        if not candidates:
            return {
                "success": False,
                "skill_id": None,
                "confidence": 0.0,
                "reason": "no_stable_or_experimental_skill",
                "profile": profile,
            }
        
        # 5. 按 tags 过滤
        required_tags = constraints.get("required_tags", [])
        if required_tags:
            candidates = [
                c for c in candidates
                if any(tag in c.tags for tag in required_tags)
            ]
        
        if not candidates:
            return {
                "success": False,
                "skill_id": None,
                "confidence": 0.0,
                "reason": "no_skill_with_required_tags",
                "profile": profile,
                "required_tags": required_tags,
            }
        
        # 6. 按 governance decision 过滤
        if governance_decision:
            allowed_capabilities = governance_decision.get("allowed_capabilities", [])
            blocked_capabilities = governance_decision.get("blocked_capabilities", [])
            
            # 过滤掉被禁止的技能
            candidates = [
                c for c in candidates
                if c.skill_id not in blocked_capabilities
            ]
        
        if not candidates:
            return {
                "success": False,
                "skill_id": None,
                "confidence": 0.0,
                "reason": "no_skill_after_governance_filter",
                "profile": profile,
            }
        
        # 7. 选择最佳候选
        chosen = candidates[0]
        
        return {
            "success": True,
            "skill_id": chosen.skill_id,
            "confidence": 0.9,
            "reason": "matched_by_intent" if self.registry.search(intent) else "fallback_first_available",
            "profile": profile,
            "category": chosen.category.value,
            "status": chosen.status.value,
            "tags": chosen.tags,
        }
    
    def _get_allowed_categories(self, profile: str) -> List[str]:
        """获取配置允许的分类"""
        profile_categories = {
            "admin": ["*"],
            "developer": ["code", "git", "docker", "utility", "search", "document", "data"],
            "default": ["utility", "search", "document"],
            "operator": ["search", "document", "data"],
            "auditor": ["search", "document"],
            "restricted": ["utility"]
        }
        return profile_categories.get(profile, ["utility"])

    def route(
        self,
        skill_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> SkillExecutionResult:
        started = perf_counter()
        manifest = self.registry.get(skill_id)

        if not manifest:
            return SkillExecutionResult(
                success=False,
                skill_id=skill_id,
                output={},
                duration_ms=int((perf_counter() - started) * 1000),
                error="skill_not_found",
            )

        if manifest.status in {SkillStatus.DISABLED, SkillStatus.DEPRECATED}:
            return SkillExecutionResult(
                success=False,
                skill_id=skill_id,
                output={},
                duration_ms=int((perf_counter() - started) * 1000),
                error=f"skill_not_runnable:{manifest.status.value}",
            )

        # 第一阶段最小执行器：不做复杂真实执行，只返回统一结果对象
        output = {
            "executed": True,
            "skill_id": manifest.skill_id,
            "skill_name": manifest.name,
            "executor_type": manifest.executor_type,
            "input": input_data,
            "context": context or {},
            "message": f"skill '{manifest.skill_id}' executed successfully",
        }

        return SkillExecutionResult(
            success=True,
            skill_id=skill_id,
            output=output,
            duration_ms=int((perf_counter() - started) * 1000),
            error=None,
        )

    # 给 WorkflowEngine 用的统一入口
    def execute(self, action: str, step_input: Dict[str, Any]) -> Dict[str, Any]:
        context = {}
        if isinstance(step_input, dict):
            context = step_input.get("context", {}) or {}

        result = self.route(action, step_input, context=context)
        if not result.success:
            raise RuntimeError(result.error or f"skill '{action}' failed")
        return result.output
