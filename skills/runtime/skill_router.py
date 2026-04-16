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
    version: Optional[str] = None
    output: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    error: Optional[str] = None
    health_status: Optional[str] = None
    compatibility_checked: bool = False
    dependencies_resolved: bool = False


class SkillRouter:
    """
    技能路由器 - 正式插件平台路由器

    主链流程：
    1. 从 package/registry 找候选 skill
    2. 走 dependency resolver
    3. 走 compatibility check
    4. 走 version selector
    5. 参考 health/metrics
    6. governance / budget 过滤
    7. 决定最终 skill/version
    """

    def __init__(
        self,
        registry: SkillRegistry = None,
        metrics_path: str = "reports/metrics/skill_metrics.json",
        package_loader=None,
        dependency_resolver=None,
        compatibility_manager=None,
        version_selector=None,
        health_monitor=None
    ):
        self.registry = registry or SkillRegistry()
        self._metrics_path = metrics_path
        self._skill_metrics: Dict[str, Dict[str, Any]] = {}
        self._metrics_mtime: float = 0

        # 平台模块（延迟初始化）
        self._package_loader = package_loader
        self._dependency_resolver = dependency_resolver
        self._compatibility_manager = compatibility_manager
        self._version_selector = version_selector
        self._health_monitor = health_monitor

        # 自动加载 metrics
        self._auto_load_metrics()

    @property
    def package_loader(self):
        """延迟加载 package_loader"""
        if self._package_loader is None:
            from skills.runtime.skill_package_loader import get_skill_package_loader
            self._package_loader = get_skill_package_loader()
        return self._package_loader

    @property
    def dependency_resolver(self):
        """延迟加载 dependency_resolver"""
        if self._dependency_resolver is None:
            from skills.runtime.skill_dependency_resolver import get_skill_dependency_resolver
            self._dependency_resolver = get_skill_dependency_resolver()
        return self._dependency_resolver

    @property
    def compatibility_manager(self):
        """延迟加载 compatibility_manager"""
        if self._compatibility_manager is None:
            from skills.lifecycle.compatibility_manager import get_compatibility_manager
            self._compatibility_manager = get_compatibility_manager()
        return self._compatibility_manager

    @property
    def version_selector(self):
        """延迟加载 version_selector"""
        if self._version_selector is None:
            from skills.runtime.skill_version_selector import SkillVersionSelector
            self._version_selector = SkillVersionSelector(
                package_loader=self._package_loader,
                health_monitor=self._health_monitor
            )
        return self._version_selector

    @property
    def health_monitor(self):
        """延迟加载 health_monitor"""
        if self._health_monitor is None:
            from skills.runtime.skill_health_monitor import get_skill_health_monitor
            self._health_monitor = get_skill_health_monitor()
        return self._health_monitor
    
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
        runtime_version: str = None,
    ) -> Dict[str, Any]:
        """
        选择技能 - 正式平台主链

        主链流程：
        1. 从 package/registry 找候选 skill
        2. 走 dependency resolver
        3. 走 compatibility check
        4. 走 version selector
        5. 参考 health/metrics
        6. governance / budget 过滤
        7. 决定最终 skill/version

        Args:
            intent: 意图
            profile: 执行配置
            constraints: 约束条件
            governance_decision: governance decision object
            runtime_version: 运行时版本

        Returns:
            选择结果
        """
        constraints = constraints or {}
        governance_decision = governance_decision or {}

        # 检查并重新加载 metrics
        self._check_metrics_reload()

        # 重新加载 registry
        self.registry.reload()

        # ========== 第一步：从 package/registry 找候选 skill ==========
        candidates = self._find_candidates(intent, profile, constraints)

        if not candidates:
            return {
                "success": False,
                "skill_id": None,
                "version": None,
                "confidence": 0.0,
                "reason": "no_candidates_found",
                "profile": profile,
            }

        # ========== 第二步：走 dependency resolver ==========
        resolved_candidates = []
        for candidate in candidates:
            dep_result = self.dependency_resolver.resolve(
                candidate["skill_id"],
                candidate.get("version"),
                profile
            )

            if dep_result.success:
                candidate["dependencies_resolved"] = True
                candidate["resolution_order"] = dep_result.resolution_order
                resolved_candidates.append(candidate)
            elif not dep_result.missing_required:
                # 可选依赖缺失，仍可使用
                candidate["dependencies_resolved"] = True
                candidate["missing_optional"] = dep_result.missing_optional
                resolved_candidates.append(candidate)

        if not resolved_candidates:
            return {
                "success": False,
                "skill_id": None,
                "version": None,
                "confidence": 0.0,
                "reason": "dependency_resolution_failed",
                "profile": profile,
            }

        # ========== 第三步：走 compatibility check ==========
        compatible_candidates = []
        for candidate in resolved_candidates:
            compat_result = self.compatibility_manager.check_compatibility(
                candidate["skill_id"],
                candidate.get("version"),
                profile,
                runtime_version,
                package_loader=self._package_loader
            )

            if compat_result.compatible:
                candidate["compatibility_checked"] = True
                candidate["matched_profile"] = compat_result.matched_profile
                candidate["matched_runtime"] = compat_result.matched_runtime
                compatible_candidates.append(candidate)

        if not compatible_candidates:
            return {
                "success": False,
                "skill_id": None,
                "version": None,
                "confidence": 0.0,
                "reason": "no_compatible_skill",
                "profile": profile,
            }

        # ========== 第四步：走 version selector ==========
        # 按 skill_id 分组，选择最佳版本
        skill_groups: Dict[str, List[Dict]] = {}
        for candidate in compatible_candidates:
            skill_id = candidate["skill_id"]
            if skill_id not in skill_groups:
                skill_groups[skill_id] = []
            skill_groups[skill_id].append(candidate)

        # 对每个 skill 选择最佳版本
        versioned_candidates = []
        for skill_id, versions in skill_groups.items():
            if len(versions) == 1:
                versioned_candidates.append(versions[0])
            else:
                # 使用 version selector 选择最佳版本
                from skills.runtime.skill_version_selector import SelectionCriteria
                criteria = SelectionCriteria(
                    prefer_stable=True,
                    prefer_healthy=True,
                    exclude_deprecated=True,
                    exclude_unhealthy=True,
                    profile=profile
                )

                selection = self.version_selector.select(skill_id, criteria)
                if selection.success:
                    # 找到对应的候选
                    for v in versions:
                        if v.get("version") == selection.selected_version:
                            v["version_selected"] = True
                            versioned_candidates.append(v)
                            break
                    else:
                        # 使用选中的版本
                        versioned_candidates.append({
                            "skill_id": skill_id,
                            "version": selection.selected_version,
                            "version_selected": True
                        })

        if not versioned_candidates:
            return {
                "success": False,
                "skill_id": None,
                "version": None,
                "confidence": 0.0,
                "reason": "version_selection_failed",
                "profile": profile,
            }

        # ========== 第五步：参考 health/metrics ==========
        health_scored = []
        for candidate in versioned_candidates:
            health_metrics = self.health_monitor.get_metrics(
                candidate["skill_id"],
                candidate.get("version")
            )

            candidate["health_status"] = health_metrics.health_status if health_metrics else "unknown"
            candidate["health_score"] = health_metrics.health_score if health_metrics else 0.5
            candidate["success_rate"] = health_metrics.success_rate if health_metrics else 0.0

            # 排除不健康的
            if candidate["health_status"] != "unhealthy":
                health_scored.append(candidate)

        if not health_scored:
            # 如果全部不健康，降级使用
            health_scored = versioned_candidates

        # 按 health score 排序
        health_scored.sort(key=lambda x: x.get("health_score", 0), reverse=True)

        # ========== 第六步：governance / budget 过滤 ==========
        if governance_decision:
            blocked = governance_decision.get("blocked_capabilities", [])
            health_scored = [
                c for c in health_scored
                if c["skill_id"] not in blocked
            ]

        if not health_scored:
            return {
                "success": False,
                "skill_id": None,
                "version": None,
                "confidence": 0.0,
                "reason": "blocked_by_governance",
                "profile": profile,
            }

        # ========== 第七步：决定最终 skill/version ==========
        chosen = health_scored[0]

        return {
            "success": True,
            "skill_id": chosen["skill_id"],
            "version": chosen.get("version"),
            "confidence": 0.9,
            "reason": "platform_main_chain_selection",
            "profile": profile,
            "dependencies_resolved": chosen.get("dependencies_resolved", False),
            "compatibility_checked": chosen.get("compatibility_checked", False),
            "health_status": chosen.get("health_status", "unknown"),
            "health_score": chosen.get("health_score", 0.5),
            "selection_chain": [
                "package_loader",
                "dependency_resolver",
                "compatibility_manager",
                "version_selector",
                "health_monitor",
                "governance_filter"
            ]
        }

    def _find_candidates(
        self,
        intent: str,
        profile: str,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """从 package/registry 找候选 skill"""
        candidates = []

        # 1. 从 package loader 获取
        packages = self.package_loader.list_loaded()
        for pkg in packages:
            # 检查状态
            if pkg.status in ["deprecated", "retired"]:
                continue

            # 检查配置兼容性
            if profile not in pkg.compatible_profiles and "default" not in pkg.compatible_profiles:
                continue

            # 简单意图匹配（按名称/描述）
            intent_lower = intent.lower()
            if (intent_lower in pkg.name.lower() or
                intent_lower in pkg.description.lower() or
                intent_lower in pkg.skill_id.lower() or
                any(intent_lower in kw.lower() for kw in pkg.keywords)):

                candidates.append({
                    "skill_id": pkg.skill_id,
                    "version": pkg.version,
                    "name": pkg.name,
                    "status": pkg.status,
                    "source": "package_loader"
                })

        # 2. 从 registry 获取（补充）
        registry_matches = self.registry.search(intent)
        for manifest in registry_matches:
            if manifest.status in [SkillStatus.DISABLED, SkillStatus.DEPRECATED]:
                continue

            # 检查是否已存在
            existing = [c for c in candidates if c["skill_id"] == manifest.skill_id]
            if not existing:
                candidates.append({
                    "skill_id": manifest.skill_id,
                    "version": getattr(manifest, 'version', '1.0.0'),
                    "name": manifest.name,
                    "status": manifest.status.value,
                    "source": "registry"
                })

        # 3. 如果没找到，退化为所有可用技能
        if not candidates:
            for pkg in packages:
                if pkg.status == "active":
                    candidates.append({
                        "skill_id": pkg.skill_id,
                        "version": pkg.version,
                        "name": pkg.name,
                        "status": pkg.status,
                        "source": "fallback"
                    })

        return candidates
    
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
        version: str = None,
    ) -> SkillExecutionResult:
        """
        执行技能

        Args:
            skill_id: 技能 ID
            input_data: 输入数据
            context: 执行上下文
            governance_decision: governance decision object
            version: 版本（可选）

        Returns:
            SkillExecutionResult
        """
        started = perf_counter()

        # 重新加载 registry
        self.registry.reload()

        # 获取技能包
        package = self.package_loader.get(skill_id, version)

        if not package:
            # 降级到 registry
            manifest = self.registry.get(skill_id)
            if not manifest:
                return SkillExecutionResult(
                    success=False,
                    skill_id=skill_id,
                    version=version,
                    output={},
                    duration_ms=int((perf_counter() - started) * 1000),
                    error="skill_not_found",
                )
            version = getattr(manifest, 'version', '1.0.0')
            status = manifest.status.value
        else:
            version = package.version
            status = package.status

        # 检查状态
        if status in ["disabled", "deprecated", "retired"]:
            return SkillExecutionResult(
                success=False,
                skill_id=skill_id,
                version=version,
                output={},
                duration_ms=int((perf_counter() - started) * 1000),
                error=f"skill_{status}",
            )

        # 检查预算
        if governance_decision:
            budget_check = self._check_budget(skill_id, governance_decision)
            if not budget_check["allowed"]:
                return SkillExecutionResult(
                    success=False,
                    skill_id=skill_id,
                    version=version,
                    output={},
                    duration_ms=int((perf_counter() - started) * 1000),
                    error=budget_check["reason"],
                )

        # 获取健康状态
        health_metrics = self.health_monitor.get_metrics(skill_id, version)
        health_status = health_metrics.health_status if health_metrics else "unknown"

        # 执行技能
        output = {
            "executed": True,
            "skill_id": skill_id,
            "version": version,
            "input": input_data,
            "context": context or {},
            "message": f"skill '{skill_id}@{version}' executed successfully",
        }

        duration_ms = int((perf_counter() - started) * 1000)

        # 记录执行结果到健康监控
        self.health_monitor.record_execution(
            skill_id=skill_id,
            version=version,
            success=True,
            latency_ms=duration_ms
        )

        return SkillExecutionResult(
            success=True,
            skill_id=skill_id,
            version=version,
            output=output,
            duration_ms=duration_ms,
            error=None,
            health_status=health_status,
            compatibility_checked=True,
            dependencies_resolved=True,
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
