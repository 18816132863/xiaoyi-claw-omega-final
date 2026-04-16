"""
Compatibility Manager - 兼容性管理器
负责检查技能兼容性
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


@dataclass
class CompatibilityResult:
    """兼容性检查结果"""
    skill_id: str
    version: str
    profile: str
    runtime_version: str
    compatible: bool
    reasons: List[str] = field(default_factory=list)
    matched_profile: bool = False
    matched_runtime: bool = False
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "profile": self.profile,
            "runtime_version": self.runtime_version,
            "compatible": self.compatible,
            "reasons": self.reasons,
            "matched_profile": self.matched_profile,
            "matched_runtime": self.matched_runtime,
            "warnings": self.warnings
        }


@dataclass
class CompatibilityIndex:
    """兼容性索引"""
    skill_id: str
    version: str
    compatible_profiles: List[str]
    compatible_runtime_versions: List[str]
    last_checked: str
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "compatible_profiles": self.compatible_profiles,
            "compatible_runtime_versions": self.compatible_runtime_versions,
            "last_checked": self.last_checked,
            "status": self.status
        }


class CompatibilityManager:
    """
    兼容性管理器

    职责：
    - 检查技能与配置的兼容性
    - 检查技能与运行时的兼容性
    - 维护兼容性索引
    - 提供兼容性查询
    """

    def __init__(
        self,
        index_path: str = "skills/registry/skill_compatibility_index.json"
    ):
        self.index_path = index_path
        self._compatibility_index: Dict[str, CompatibilityIndex] = {}
        self._ensure_dir()
        self._load_index()

    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

    def _load_index(self):
        """加载兼容性索引"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, index_data in data.get("skills", {}).items():
                        self._compatibility_index[key] = CompatibilityIndex(
                            skill_id=index_data["skill_id"],
                            version=index_data["version"],
                            compatible_profiles=index_data.get("compatible_profiles", ["default"]),
                            compatible_runtime_versions=index_data.get("compatible_runtime_versions", []),
                            last_checked=index_data.get("last_checked", ""),
                            status=index_data.get("status", "unknown")
                        )
            except Exception:
                pass

    def _save_index(self):
        """保存兼容性索引"""
        try:
            data = {
                "updated_at": datetime.now().isoformat(),
                "skills": {
                    key: index.to_dict()
                    for key, index in self._compatibility_index.items()
                }
            }
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def check_compatibility(
        self,
        skill_id: str,
        version: str = None,
        profile: str = "default",
        runtime_version: str = None,
        package_loader=None
    ) -> CompatibilityResult:
        """
        检查兼容性

        Args:
            skill_id: 技能 ID
            version: 版本（可选）
            profile: 执行配置
            runtime_version: 运行时版本
            package_loader: 技能包加载器（可选）

        Returns:
            CompatibilityResult
        """
        reasons = []
        warnings = []

        # 获取技能包
        if package_loader:
            loader = package_loader
        else:
            from skills.runtime.skill_package_loader import get_skill_package_loader
            loader = get_skill_package_loader()

        package = loader.get(skill_id, version)

        if not package:
            return CompatibilityResult(
                skill_id=skill_id,
                version=version or "unknown",
                profile=profile,
                runtime_version=runtime_version or "unknown",
                compatible=False,
                reasons=["Skill package not found"]
            )

        # 检查配置兼容性
        matched_profile = profile in package.compatible_profiles
        if not matched_profile:
            # 检查是否有 default 配置
            if "default" in package.compatible_profiles:
                matched_profile = True
                warnings.append(f"Profile {profile} not explicitly supported, using default")
            else:
                reasons.append(
                    f"Profile {profile} not compatible. "
                    f"Supported: {package.compatible_profiles}"
                )

        # 检查运行时兼容性
        matched_runtime = True
        if runtime_version and package.compatible_runtime_versions:
            matched_runtime = self._check_runtime_version(
                runtime_version,
                package.compatible_runtime_versions
            )
            if not matched_runtime:
                reasons.append(
                    f"Runtime {runtime_version} not compatible. "
                    f"Supported: {package.compatible_runtime_versions}"
                )

        # 检查状态
        if package.status == "deprecated":
            warnings.append("Skill is deprecated")
        elif package.status == "retired":
            reasons.append("Skill is retired")

        compatible = len(reasons) == 0

        # 更新索引
        self._update_index(skill_id, package.version, package, compatible)

        return CompatibilityResult(
            skill_id=skill_id,
            version=package.version,
            profile=profile,
            runtime_version=runtime_version or "unknown",
            compatible=compatible,
            reasons=reasons,
            matched_profile=matched_profile,
            matched_runtime=matched_runtime,
            warnings=warnings
        )

    def _check_runtime_version(
        self,
        runtime_version: str,
        compatible_versions: List[str]
    ) -> bool:
        """检查运行时版本"""
        # 简单匹配：检查是否在兼容列表中
        for compat in compatible_versions:
            if compat == runtime_version:
                return True

            # 支持通配符
            if compat.endswith("*"):
                prefix = compat[:-1]
                if runtime_version.startswith(prefix):
                    return True

            # 支持版本范围
            if compat.startswith("^"):
                # ^1.0.0 表示 >=1.0.0 <2.0.0
                try:
                    min_parts = [int(p) for p in compat[1:].split('.')]
                    rt_parts = [int(p) for p in runtime_version.split('.')]

                    if rt_parts[0] == min_parts[0] and rt_parts >= min_parts:
                        return True
                except (ValueError, IndexError):
                    pass

        return False

    def _update_index(
        self,
        skill_id: str,
        version: str,
        package: Any,
        compatible: bool
    ):
        """更新兼容性索引"""
        key = f"{skill_id}@{version}"

        self._compatibility_index[key] = CompatibilityIndex(
            skill_id=skill_id,
            version=version,
            compatible_profiles=package.compatible_profiles,
            compatible_runtime_versions=package.compatible_runtime_versions,
            last_checked=datetime.now().isoformat(),
            status="compatible" if compatible else "incompatible"
        )

        self._save_index()

    def get_compatible_skills(
        self,
        profile: str = "default",
        runtime_version: str = None
    ) -> List[str]:
        """
        获取兼容的技能列表

        Args:
            profile: 执行配置
            runtime_version: 运行时版本

        Returns:
            List of skill_id
        """
        compatible = []

        for key, index in self._compatibility_index.items():
            if index.status != "compatible":
                continue

            if profile not in index.compatible_profiles:
                if "default" not in index.compatible_profiles:
                    continue

            if runtime_version and index.compatible_runtime_versions:
                if not self._check_runtime_version(
                    runtime_version,
                    index.compatible_runtime_versions
                ):
                    continue

            compatible.append(index.skill_id)

        return list(set(compatible))

    def get_incompatible_skills(self) -> List[str]:
        """获取不兼容的技能列表"""
        return [
            index.skill_id
            for key, index in self._compatibility_index.items()
            if index.status == "incompatible"
        ]

    def refresh_index(self):
        """刷新兼容性索引"""
        from skills.runtime.skill_package_loader import get_skill_package_loader
        loader = get_skill_package_loader()

        for package in loader.list_loaded():
            self._update_index(
                package.skill_id,
                package.version,
                package,
                True  # 默认兼容
            )

    def get_index(self) -> Dict[str, Any]:
        """获取兼容性索引"""
        return {
            "updated_at": datetime.now().isoformat(),
            "skills": {
                key: index.to_dict()
                for key, index in self._compatibility_index.items()
            }
        }


# 全局单例
_compatibility_manager = None


def get_compatibility_manager() -> CompatibilityManager:
    """获取兼容性管理器单例"""
    global _compatibility_manager
    if _compatibility_manager is None:
        _compatibility_manager = CompatibilityManager()
    return _compatibility_manager
