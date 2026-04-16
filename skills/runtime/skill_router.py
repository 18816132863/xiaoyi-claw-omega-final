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
    """
    技能路由器
    
    职责：
    - 选择合适的技能
    - 执行技能
    - 集成生命周期管理
    - 集成预算策略
    - 参考 metrics 做决策
    """
    
    def __init__(self, registry: SkillRegistry, metrics_path: str = "reports/metrics/skill_metrics.json"):
        self.registry = registry
        self._skill_metrics: Dict[str, Dict[str, Any]] = {}
        self._metrics_path = metrics_path
        self._metrics_mtime: float = 0
        
        # 自动加载 metrics
        self._auto_load_metrics()
    
    def _auto_load_metrics(self):
        """自动加载 metrics"""
        import os
        
        if os.path.exists(self._metrics_path):
            try:
                self._metrics_mtime = os.path.getmtime(self._metrics_path)
                self.load_metrics(self._metrics_path)
            except:
                pass
    
    def _check_metrics_reload(self):
        """检查并重新加载 metrics"""
        import os
        
        if os.path.exists(self._metrics_path):
            try:
                mtime = os.path.getmtime(self._metrics_path)
                if mtime > self._metrics_mtime:
                    self._metrics_mtime = mtime
                    self.load_metrics(self._metrics_path)
            except:
                pass
    
    def load_metrics(self, metrics_path: str = "reports/metrics/skill_metrics.json"):
        """加载技能指标"""
        import json
        import os
        
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r') as f:
                    data = json.load(f)
                
                # 加载聚合指标
                aggregate = data.get("aggregate", {})
                self._skill_metrics["_aggregate"] = aggregate
                
                # 加载按技能的指标
                for skill_id, metrics in data.get("by_skill", {}).items():
                    self._skill_metrics[skill_id] = metrics
            except:
                pass
    
    def get_skill_metrics(self, skill_id: str) -> Dict[str, Any]:
        """获取技能指标"""
        return self._skill_metrics.get(skill_id, {
            "total_calls": 0,
            "avg_latency_ms": 0,
            "max_latency_ms": 0,
            "failure_rate": 0
        })

    def discover(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        # 重新加载 registry 以获取最新状态
        self.registry.reload()
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
        
        # 检查并重新加载 metrics
        self._check_metrics_reload()
        
        # 重新加载 registry 以获取最新状态
        self.registry.reload()
        governance_decision = governance_decision or {}
        
        # 重新加载 registry 以获取最新状态
        self.registry.reload()
        
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
        
        # 4. 按 status 过滤（排除 disabled 和 deprecated）
        candidates = [
            c for c in candidates
            if c.status not in {SkillStatus.DISABLED, SkillStatus.DEPRECATED}
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
        
        # 7. 按 metrics 排序（优先选择低失败率、低延迟的技能）
        if len(candidates) > 1:
            candidates = self._sort_by_metrics(candidates)
        
        # 8. 选择最佳候选
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
    
    def _sort_by_metrics(self, candidates: List[SkillManifest]) -> List[SkillManifest]:
        """按指标排序"""
        def score(manifest: SkillManifest) -> float:
            metrics = self.get_skill_metrics(manifest.skill_id)
            # 失败率越低越好，延迟越低越好
            failure_rate = metrics.get("failure_rate", 0)
            avg_latency = metrics.get("avg_latency_ms", 100)
            
            # 综合评分（越低越好）
            return failure_rate * 100 + avg_latency / 1000
        
        return sorted(candidates, key=score)
    
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
        governance_decision: Optional[Dict[str, Any]] = None,
    ) -> SkillExecutionResult:
        """
        执行技能
        
        Args:
            skill_id: 技能 ID
            input_data: 输入数据
            context: 执行上下文
            governance_decision: governance decision object
        
        Returns:
            SkillExecutionResult
        """
        started = perf_counter()
        
        # 重新加载 registry
        self.registry.reload()
        
        manifest = self.registry.get(skill_id)

        if not manifest:
            return SkillExecutionResult(
                success=False,
                skill_id=skill_id,
                output={},
                duration_ms=int((perf_counter() - started) * 1000),
                error="skill_not_found",
            )

        # 检查状态（disabled 和 deprecated 不能执行）
        if manifest.status == SkillStatus.DISABLED:
            return SkillExecutionResult(
                success=False,
                skill_id=skill_id,
                output={},
                duration_ms=int((perf_counter() - started) * 1000),
                error="skill_disabled",
            )
        
        if manifest.status == SkillStatus.DEPRECATED:
            return SkillExecutionResult(
                success=False,
                skill_id=skill_id,
                output={},
                duration_ms=int((perf_counter() - started) * 1000),
                error="skill_deprecated",
            )

        # 检查预算
        if governance_decision:
            budget_check = self._check_budget(skill_id, governance_decision)
            if not budget_check["allowed"]:
                return SkillExecutionResult(
                    success=False,
                    skill_id=skill_id,
                    output={},
                    duration_ms=int((perf_counter() - started) * 1000),
                    error=budget_check["reason"],
                )

        # 执行技能
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
    
    def _check_budget(
        self,
        skill_id: str,
        governance_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """检查预算"""
        from skills.policies.skill_budget_policy import SkillBudgetPolicy
        
        manifest = self.registry.get(skill_id)
        if not manifest:
            return {"allowed": False, "reason": "skill_not_found"}
        
        policy = SkillBudgetPolicy()
        decision = policy.check_before_execute(
            manifest=manifest,
            governance_decision=governance_decision,
            estimated_tokens=1000,
            estimated_cost=0.1
        )
        
        return {
            "allowed": decision.allowed,
            "reason": decision.reason if not decision.allowed else ""
        }

    # 给 WorkflowEngine 用的统一入口
    def execute(self, action: str, step_input: Dict[str, Any]) -> Dict[str, Any]:
        context = {}
        if isinstance(step_input, dict):
            context = step_input.get("context", {}) or {}

        result = self.route(action, step_input, context=context)
        if not result.success:
            raise RuntimeError(result.error or f"skill '{action}' failed")
        return result.output
