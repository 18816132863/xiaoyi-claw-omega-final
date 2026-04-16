"""
Skill Version Selector - 技能版本选择器
负责选择最合适的技能版本
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re


@dataclass
class VersionInfo:
    """版本信息"""
    version: str
    status: str
    health_status: str
    release_date: Optional[str] = None
    deprecated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "status": self.status,
            "health_status": self.health_status,
            "release_date": self.release_date,
            "deprecated": self.deprecated
        }


@dataclass
class SelectionCriteria:
    """选择条件"""
    version_range: Optional[str] = None
    prefer_stable: bool = True
    prefer_healthy: bool = True
    exclude_deprecated: bool = True
    exclude_unhealthy: bool = True
    min_health_score: float = 0.5
    profile: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_range": self.version_range,
            "prefer_stable": self.prefer_stable,
            "prefer_healthy": self.prefer_healthy,
            "exclude_deprecated": self.exclude_deprecated,
            "exclude_unhealthy": self.exclude_unhealthy,
            "min_health_score": self.min_health_score,
            "profile": self.profile
        }


@dataclass
class SelectionResult:
    """选择结果"""
    success: bool
    skill_id: str
    selected_version: Optional[str] = None
    selected_package: Optional[Any] = None
    candidates: List[VersionInfo] = field(default_factory=list)
    rejected: List[Tuple[str, str]] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "skill_id": self.skill_id,
            "selected_version": self.selected_version,
            "candidates": [c.to_dict() for c in self.candidates],
            "rejected": [(v, r) for v, r in self.rejected],
            "reason": self.reason
        }


class SkillVersionSelector:
    """
    技能版本选择器

    职责：
    - 根据条件选择最合适的版本
    - 支持版本范围约束
    - 考虑健康状态
    - 考虑稳定性
    - 支持排除已废弃版本
    """

    def __init__(self, package_loader=None, health_monitor=None):
        self.package_loader = package_loader
        self.health_monitor = health_monitor
        self._selection_cache: Dict[str, SelectionResult] = {}

    def select(
        self,
        skill_id: str,
        criteria: SelectionCriteria = None
    ) -> SelectionResult:
        """
        选择技能版本

        Args:
            skill_id: 技能 ID
            criteria: 选择条件

        Returns:
            SelectionResult
        """
        criteria = criteria or SelectionCriteria()

        # 获取所有版本
        versions = self._get_all_versions(skill_id)

        if not versions:
            return SelectionResult(
                success=False,
                skill_id=skill_id,
                reason=f"No versions found for skill: {skill_id}"
            )

        candidates = []
        rejected = []

        # 过滤版本
        for v in versions:
            reject_reason = self._check_version(v, criteria)
            if reject_reason:
                rejected.append((v.version, reject_reason))
            else:
                candidates.append(v)

        if not candidates:
            return SelectionResult(
                success=False,
                skill_id=skill_id,
                candidates=versions,
                rejected=rejected,
                reason="No version matches criteria"
            )

        # 排序候选版本
        candidates = self._sort_candidates(candidates, criteria)

        # 选择最佳版本
        selected = candidates[0]

        # 获取完整 package
        selected_package = self._get_package(skill_id, selected.version)

        return SelectionResult(
            success=True,
            skill_id=skill_id,
            selected_version=selected.version,
            selected_package=selected_package,
            candidates=candidates,
            rejected=rejected,
            reason=f"Selected version {selected.version} based on criteria"
        )

    def _get_all_versions(self, skill_id: str) -> List[VersionInfo]:
        """获取技能的所有版本"""
        versions = []

        if self.package_loader:
            packages = self.package_loader.list_loaded()
        else:
            from skills.runtime.skill_package_loader import get_skill_package_loader
            packages = get_skill_package_loader().list_loaded()

        for pkg in packages:
            if pkg.skill_id == skill_id:
                versions.append(VersionInfo(
                    version=pkg.version,
                    status=pkg.status,
                    health_status=pkg.health_status,
                    deprecated=pkg.status == "deprecated"
                ))

        return versions

    def _check_version(self, v: VersionInfo, criteria: SelectionCriteria) -> Optional[str]:
        """检查版本是否符合条件，返回拒绝原因或 None"""
        # 检查版本范围
        if criteria.version_range:
            if not self._version_in_range(v.version, criteria.version_range):
                return f"Version {v.version} not in range {criteria.version_range}"

        # 检查是否排除已废弃
        if criteria.exclude_deprecated and v.deprecated:
            return "Version is deprecated"

        # 检查是否排除不健康
        if criteria.exclude_unhealthy and v.health_status == "unhealthy":
            return "Version is unhealthy"

        # 检查配置兼容性
        if criteria.profile != "default":
            pkg = self._get_package_by_version(v.version)
            if pkg and criteria.profile not in pkg.compatible_profiles:
                return f"Version not compatible with profile {criteria.profile}"

        return None

    def _version_in_range(self, version: str, version_range: str) -> bool:
        """检查版本是否在范围内"""
        try:
            v_parts = [int(p) for p in version.split('-')[0].split('.')]
        except ValueError:
            return False

        if version_range.startswith('^'):
            # ^1.0.0 表示 >=1.0.0 <2.0.0
            min_parts = [int(p) for p in version_range[1:].split('.')]
            if len(min_parts) >= 1:
                max_parts = [min_parts[0] + 1, 0, 0]
                return self._version_gte(v_parts, min_parts) and self._version_lt(v_parts, max_parts)

        elif version_range.startswith('>='):
            min_parts = [int(p) for p in version_range[2:].split('.')[0:3]]
            return self._version_gte(v_parts, min_parts)

        elif version_range.startswith('>'):
            min_parts = [int(p) for p in version_range[1:].split('.')[0:3]]
            return self._version_gt(v_parts, min_parts)

        elif version_range.startswith('<='):
            max_parts = [int(p) for p in version_range[2:].split('.')[0:3]]
            return self._version_lte(v_parts, max_parts)

        elif version_range.startswith('<'):
            max_parts = [int(p) for p in version_range[1:].split('.')[0:3]]
            return self._version_lt(v_parts, max_parts)

        elif version_range.startswith('='):
            target_parts = [int(p) for p in version_range[1:].split('.')]
            return v_parts == target_parts

        else:
            target_parts = [int(p) for p in version_range.split('.')]
            return v_parts == target_parts

    def _version_gte(self, v: List[int], target: List[int]) -> bool:
        for i in range(max(len(v), len(target))):
            v_i = v[i] if i < len(v) else 0
            t_i = target[i] if i < len(target) else 0
            if v_i > t_i:
                return True
            if v_i < t_i:
                return False
        return True

    def _version_gt(self, v: List[int], target: List[int]) -> bool:
        for i in range(max(len(v), len(target))):
            v_i = v[i] if i < len(v) else 0
            t_i = target[i] if i < len(target) else 0
            if v_i > t_i:
                return True
            if v_i < t_i:
                return False
        return False

    def _version_lte(self, v: List[int], target: List[int]) -> bool:
        return not self._version_gt(v, target)

    def _version_lt(self, v: List[int], target: List[int]) -> bool:
        return not self._version_gte(v, target)

    def _sort_candidates(
        self,
        candidates: List[VersionInfo],
        criteria: SelectionCriteria
    ) -> List[VersionInfo]:
        """排序候选版本"""
        def sort_key(v: VersionInfo) -> Tuple:
            # 解析版本号
            try:
                v_parts = tuple(int(p) for p in v.version.split('-')[0].split('.'))
            except ValueError:
                v_parts = (0, 0, 0)

            # 健康分数
            health_scores = {
                "healthy": 3,
                "degraded": 2,
                "unknown": 1,
                "unhealthy": 0
            }
            health_score = health_scores.get(v.health_status, 1)

            # 状态分数
            status_scores = {
                "active": 2,
                "draft": 1,
                "deprecated": 0,
                "retired": -1
            }
            status_score = status_scores.get(v.status, 0)

            # 排序优先级：
            # 1. 如果 prefer_stable，优先 active 状态
            # 2. 如果 prefer_healthy，优先健康状态
            # 3. 版本号降序（最新优先）

            if criteria.prefer_stable and criteria.prefer_healthy:
                return (-status_score, -health_score, -v_parts[0], -v_parts[1], -v_parts[2])
            elif criteria.prefer_stable:
                return (-status_score, -v_parts[0], -v_parts[1], -v_parts[2])
            elif criteria.prefer_healthy:
                return (-health_score, -v_parts[0], -v_parts[1], -v_parts[2])
            else:
                return (-v_parts[0], -v_parts[1], -v_parts[2])

        return sorted(candidates, key=sort_key)

    def _get_package(self, skill_id: str, version: str):
        """获取技能包"""
        if self.package_loader:
            return self.package_loader.get(skill_id, version)
        else:
            from skills.runtime.skill_package_loader import get_skill_package_loader
            return get_skill_package_loader().get(skill_id, version)

    def _get_package_by_version(self, version: str):
        """通过版本获取包（简化版）"""
        # 这个方法用于检查配置兼容性
        return None

    def get_latest(self, skill_id: str) -> Optional[str]:
        """获取最新版本"""
        versions = self._get_all_versions(skill_id)
        if not versions:
            return None

        # 过滤掉废弃版本
        active = [v for v in versions if v.status == "active"]
        if not active:
            active = versions

        # 排序取最新
        sorted_versions = self._sort_candidates(active, SelectionCriteria())
        return sorted_versions[0].version if sorted_versions else None


# 全局单例
_skill_version_selector = None


def get_skill_version_selector() -> SkillVersionSelector:
    """获取版本选择器单例"""
    global _skill_version_selector
    if _skill_version_selector is None:
        _skill_version_selector = SkillVersionSelector()
    return _skill_version_selector
