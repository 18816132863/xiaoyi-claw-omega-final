"""
Skill Dependency Resolver - 技能依赖解析器
负责解析和验证技能依赖关系
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import re


@dataclass
class DependencyInfo:
    """依赖信息"""
    skill_id: str
    version_range: str
    optional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version_range": self.version_range,
            "optional": self.optional
        }


@dataclass
class DependencyStatus:
    """依赖状态"""
    skill_id: str
    version_range: str
    optional: bool
    satisfied: bool
    installed_version: Optional[str] = None
    enabled: bool = False
    compatible: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version_range": self.version_range,
            "optional": self.optional,
            "satisfied": self.satisfied,
            "installed_version": self.installed_version,
            "enabled": self.enabled,
            "compatible": self.compatible,
            "error": self.error
        }


@dataclass
class ResolutionResult:
    """解析结果"""
    success: bool
    skill_id: str
    version: str
    dependencies: List[DependencyStatus] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)
    missing_optional: List[str] = field(default_factory=list)
    resolution_order: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "skill_id": self.skill_id,
            "version": self.version,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "missing_required": self.missing_required,
            "missing_optional": self.missing_optional,
            "resolution_order": self.resolution_order,
            "errors": self.errors
        }


class SkillDependencyResolver:
    """
    技能依赖解析器

    职责：
    - 读取技能依赖
    - 检查依赖技能是否存在
    - 检查依赖技能是否启用/兼容
    - 输出依赖解析结果
    - 检测循环依赖
    """

    def __init__(self, package_loader=None, registry=None):
        self.package_loader = package_loader
        self.registry = registry
        self._resolution_cache: Dict[str, ResolutionResult] = {}

    def resolve(
        self,
        skill_id: str,
        version: str = None,
        profile: str = "default"
    ) -> ResolutionResult:
        """
        解析技能依赖

        Args:
            skill_id: 技能 ID
            version: 版本（可选）
            profile: 执行配置

        Returns:
            ResolutionResult
        """
        # 获取技能包
        if self.package_loader:
            package = self.package_loader.get(skill_id, version)
        else:
            from skills.runtime.skill_package_loader import get_skill_package_loader
            package = get_skill_package_loader().get(skill_id, version)

        if not package:
            return ResolutionResult(
                success=False,
                skill_id=skill_id,
                version=version or "unknown",
                errors=[f"Skill package not found: {skill_id}"]
            )

        # 解析依赖
        dependencies = []
        missing_required = []
        missing_optional = []
        errors = []
        resolution_order = []

        for dep in package.dependencies:
            dep_info = DependencyInfo(
                skill_id=dep["skill_id"],
                version_range=dep["version_range"],
                optional=dep.get("optional", False)
            )

            dep_status = self._check_dependency(dep_info, profile)
            dependencies.append(dep_status)

            if not dep_status.satisfied:
                if dep_info.optional:
                    missing_optional.append(dep_info.skill_id)
                else:
                    missing_required.append(dep_info.skill_id)

        # 检测循环依赖
        cycle = self._detect_cycle(skill_id, package.version)
        if cycle:
            errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")

        # 计算解析顺序（拓扑排序）
        if not errors and not missing_required:
            resolution_order = self._compute_resolution_order(skill_id, package.version)

        success = len(missing_required) == 0 and len(errors) == 0

        result = ResolutionResult(
            success=success,
            skill_id=skill_id,
            version=package.version,
            dependencies=dependencies,
            missing_required=missing_required,
            missing_optional=missing_optional,
            resolution_order=resolution_order,
            errors=errors
        )

        # 缓存
        cache_key = f"{skill_id}@{package.version}:{profile}"
        self._resolution_cache[cache_key] = result

        return result

    def _check_dependency(
        self,
        dep_info: DependencyInfo,
        profile: str
    ) -> DependencyStatus:
        """检查单个依赖"""
        # 获取依赖技能包
        if self.package_loader:
            dep_package = self.package_loader.get(dep_info.skill_id)
        else:
            from skills.runtime.skill_package_loader import get_skill_package_loader
            dep_package = get_skill_package_loader().get(dep_info.skill_id)

        if not dep_package:
            return DependencyStatus(
                skill_id=dep_info.skill_id,
                version_range=dep_info.version_range,
                optional=dep_info.optional,
                satisfied=False,
                error="Skill not found"
            )

        # 检查版本范围
        version_match = self._check_version_range(
            dep_package.version,
            dep_info.version_range
        )

        if not version_match:
            return DependencyStatus(
                skill_id=dep_info.skill_id,
                version_range=dep_info.version_range,
                optional=dep_info.optional,
                satisfied=False,
                installed_version=dep_package.version,
                error=f"Version mismatch: {dep_package.version} not in {dep_info.version_range}"
            )

        # 检查是否启用
        enabled = dep_package.status == "active"

        # 检查配置兼容性
        compatible = profile in dep_package.compatible_profiles or "default" in dep_package.compatible_profiles

        satisfied = enabled and compatible

        return DependencyStatus(
            skill_id=dep_info.skill_id,
            version_range=dep_info.version_range,
            optional=dep_info.optional,
            satisfied=satisfied,
            installed_version=dep_package.version,
            enabled=enabled,
            compatible=compatible,
            error=None if satisfied else "Not enabled or incompatible"
        )

    def _check_version_range(self, version: str, version_range: str) -> bool:
        """检查版本是否在范围内"""
        # 解析版本
        try:
            v_parts = [int(p) for p in version.split('-')[0].split('.')]
        except ValueError:
            return False

        # 简单范围检查
        if version_range.startswith('^'):
            # ^1.0.0 表示 >=1.0.0 <2.0.0
            min_parts = [int(p) for p in version_range[1:].split('.')]
            if len(min_parts) >= 1:
                max_parts = [min_parts[0] + 1, 0, 0]
                return self._version_gte(v_parts, min_parts) and self._version_lt(v_parts, max_parts)

        elif version_range.startswith('>='):
            # >=1.0.0
            min_parts = [int(p) for p in version_range[2:].split('.')[0:3]]
            return self._version_gte(v_parts, min_parts)

        elif version_range.startswith('>'):
            # >1.0.0
            min_parts = [int(p) for p in version_range[1:].split('.')[0:3]]
            return self._version_gt(v_parts, min_parts)

        elif version_range.startswith('<='):
            # <=1.0.0
            max_parts = [int(p) for p in version_range[2:].split('.')[0:3]]
            return self._version_lte(v_parts, max_parts)

        elif version_range.startswith('<'):
            # <1.0.0
            max_parts = [int(p) for p in version_range[1:].split('.')[0:3]]
            return self._version_lt(v_parts, max_parts)

        elif version_range.startswith('='):
            # =1.0.0 精确匹配
            target_parts = [int(p) for p in version_range[1:].split('.')]
            return v_parts == target_parts

        else:
            # 精确匹配
            target_parts = [int(p) for p in version_range.split('.')]
            return v_parts == target_parts

    def _version_gte(self, v: List[int], target: List[int]) -> bool:
        """v >= target"""
        for i in range(max(len(v), len(target))):
            v_i = v[i] if i < len(v) else 0
            t_i = target[i] if i < len(target) else 0
            if v_i > t_i:
                return True
            if v_i < t_i:
                return False
        return True

    def _version_gt(self, v: List[int], target: List[int]) -> bool:
        """v > target"""
        for i in range(max(len(v), len(target))):
            v_i = v[i] if i < len(v) else 0
            t_i = target[i] if i < len(target) else 0
            if v_i > t_i:
                return True
            if v_i < t_i:
                return False
        return False

    def _version_lte(self, v: List[int], target: List[int]) -> bool:
        """v <= target"""
        return not self._version_gt(v, target)

    def _version_lt(self, v: List[int], target: List[int]) -> bool:
        """v < target"""
        return not self._version_gte(v, target)

    def _detect_cycle(self, skill_id: str, version: str, visited: Set[str] = None) -> List[str]:
        """检测循环依赖"""
        if visited is None:
            visited = set()

        cache_key = f"{skill_id}@{version}"

        if cache_key in visited:
            return [skill_id]

        visited.add(cache_key)

        # 获取技能包
        if self.package_loader:
            package = self.package_loader.get(skill_id, version)
        else:
            from skills.runtime.skill_package_loader import get_skill_package_loader
            package = get_skill_package_loader().get(skill_id, version)

        if not package:
            return []

        for dep in package.dependencies:
            dep_skill_id = dep["skill_id"]
            cycle = self._detect_cycle(dep_skill_id, None, visited.copy())
            if cycle:
                return [skill_id] + cycle

        return []

    def _compute_resolution_order(self, skill_id: str, version: str) -> List[str]:
        """计算解析顺序（拓扑排序）"""
        order = []
        visited = set()

        def visit(sid: str, ver: str = None):
            cache_key = f"{sid}@{ver}" if ver else sid
            if cache_key in visited:
                return
            visited.add(cache_key)

            # 获取技能包
            if self.package_loader:
                package = self.package_loader.get(sid, ver)
            else:
                from skills.runtime.skill_package_loader import get_skill_package_loader
                package = get_skill_package_loader().get(sid, ver)

            if package:
                for dep in package.dependencies:
                    visit(dep["skill_id"])

            order.append(sid)

        visit(skill_id, version)
        return order

    def get_resolution(self, skill_id: str, version: str = None) -> Optional[ResolutionResult]:
        """获取缓存的解析结果"""
        cache_key = f"{skill_id}@{version}" if version else skill_id
        return self._resolution_cache.get(cache_key)


# 全局单例
_skill_dependency_resolver = None


def get_skill_dependency_resolver() -> SkillDependencyResolver:
    """获取依赖解析器单例"""
    global _skill_dependency_resolver
    if _skill_dependency_resolver is None:
        _skill_dependency_resolver = SkillDependencyResolver()
    return _skill_dependency_resolver
