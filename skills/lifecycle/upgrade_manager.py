"""
Upgrade Manager - 技能升级管理器
负责技能版本升级
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


@dataclass
class UpgradePlan:
    """升级计划"""
    skill_id: str
    current_version: str
    target_version: str
    compatibility_check: bool
    dependencies_valid: bool
    backup_created: bool
    steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "current_version": self.current_version,
            "target_version": self.target_version,
            "compatibility_check": self.compatibility_check,
            "dependencies_valid": self.dependencies_valid,
            "backup_created": self.backup_created,
            "steps": self.steps
        }


@dataclass
class UpgradeResult:
    """升级结果"""
    success: bool
    skill_id: str
    previous_version: Optional[str] = None
    new_version: Optional[str] = None
    backup_id: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    rollback_available: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "skill_id": self.skill_id,
            "previous_version": self.previous_version,
            "new_version": self.new_version,
            "backup_id": self.backup_id,
            "errors": self.errors,
            "warnings": self.warnings,
            "rollback_available": self.rollback_available
        }


@dataclass
class VersionRecord:
    """版本记录"""
    skill_id: str
    version: str
    installed_at: str
    status: str
    backup_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "installed_at": self.installed_at,
            "status": self.status,
            "backup_path": self.backup_path
        }


class UpgradeManager:
    """
    技能升级管理器

    职责：
    - 检查升级兼容性
    - 创建备份
    - 执行升级
    - 记录版本历史
    - 支持回滚
    """

    def __init__(
        self,
        registry_path: str = "skills/registry/skill_registry.json",
        history_path: str = "skills/registry/version_history.json",
        backup_dir: str = "skills/backups"
    ):
        self.registry_path = registry_path
        self.history_path = history_path
        self.backup_dir = backup_dir
        self._version_history: Dict[str, List[VersionRecord]] = {}
        self._ensure_dirs()
        self._load_history()

    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

    def _load_history(self):
        """加载版本历史"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for skill_id, records in data.items():
                        self._version_history[skill_id] = [
                            VersionRecord(**r) for r in records
                        ]
            except Exception:
                pass

    def _save_history(self):
        """保存版本历史"""
        try:
            data = {
                skill_id: [r.to_dict() for r in records]
                for skill_id, records in self._version_history.items()
            }
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def plan_upgrade(
        self,
        skill_id: str,
        target_version: str,
        profile: str = "default"
    ) -> UpgradePlan:
        """
        规划升级

        Args:
            skill_id: 技能 ID
            target_version: 目标版本
            profile: 执行配置

        Returns:
            UpgradePlan
        """
        steps = []

        # 1. 获取当前版本
        current_version = self._get_current_version(skill_id)
        if not current_version:
            return UpgradePlan(
                skill_id=skill_id,
                current_version="none",
                target_version=target_version,
                compatibility_check=False,
                dependencies_valid=False,
                backup_created=False,
                steps=["Skill not found in registry"]
            )

        steps.append(f"Current version: {current_version}")

        # 2. 检查兼容性
        from skills.lifecycle.compatibility_manager import get_compatibility_manager
        compat_manager = get_compatibility_manager()
        compat_result = compat_manager.check_compatibility(
            skill_id, target_version, profile
        )

        compatibility_check = compat_result.compatible
        if compatibility_check:
            steps.append(f"Compatibility check passed for profile {profile}")
        else:
            steps.append(f"Compatibility check failed: {compat_result.reasons}")

        # 3. 检查依赖
        from skills.runtime.skill_dependency_resolver import get_skill_dependency_resolver
        dep_resolver = get_skill_dependency_resolver()
        dep_result = dep_resolver.resolve(skill_id, target_version, profile)

        dependencies_valid = dep_result.success
        if dependencies_valid:
            steps.append("Dependencies validated")
        else:
            steps.append(f"Dependency issues: {dep_result.missing_required}")

        # 4. 创建备份计划
        steps.append("Backup will be created before upgrade")

        return UpgradePlan(
            skill_id=skill_id,
            current_version=current_version,
            target_version=target_version,
            compatibility_check=compatibility_check,
            dependencies_valid=dependencies_valid,
            backup_created=False,
            steps=steps
        )

    def upgrade(
        self,
        skill_id: str,
        target_version: str,
        profile: str = "default",
        force: bool = False
    ) -> UpgradeResult:
        """
        执行升级

        Args:
            skill_id: 技能 ID
            target_version: 目标版本
            profile: 执行配置
            force: 强制升级（跳过兼容性检查）

        Returns:
            UpgradeResult
        """
        errors = []
        warnings = []

        # 1. 规划升级
        plan = self.plan_upgrade(skill_id, target_version, profile)

        if not plan.compatibility_check and not force:
            errors.append("Compatibility check failed. Use force=True to override.")

        if not plan.dependencies_valid and not force:
            errors.append("Dependency validation failed. Use force=True to override.")

        if errors:
            return UpgradeResult(
                success=False,
                skill_id=skill_id,
                previous_version=plan.current_version,
                errors=errors
            )

        # 2. 创建备份
        backup_id = self._create_backup(skill_id, plan.current_version)

        # 3. 记录旧版本
        previous_version = plan.current_version

        # 4. 更新注册表
        self._update_registry(skill_id, target_version)

        # 5. 记录版本历史
        self._record_version(skill_id, target_version, backup_id)

        return UpgradeResult(
            success=True,
            skill_id=skill_id,
            previous_version=previous_version,
            new_version=target_version,
            backup_id=backup_id,
            warnings=warnings,
            rollback_available=backup_id is not None
        )

    def _get_current_version(self, skill_id: str) -> Optional[str]:
        """获取当前版本"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                    skill_info = registry.get("skills", {}).get(skill_id, {})
                    return skill_info.get("version")
            except Exception:
                pass
        return None

    def _create_backup(self, skill_id: str, version: str) -> Optional[str]:
        """创建备份"""
        import uuid
        backup_id = f"backup_{uuid.uuid4().hex[:8]}"
        backup_path = os.path.join(self.backup_dir, f"{skill_id}_{version}_{backup_id}.json")

        # 备份当前注册信息
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)

                backup_data = {
                    "backup_id": backup_id,
                    "skill_id": skill_id,
                    "version": version,
                    "created_at": datetime.now().isoformat(),
                    "registry_entry": registry.get("skills", {}).get(skill_id, {})
                }

                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2, ensure_ascii=False)

                return backup_id
            except Exception:
                pass

        return None

    def _update_registry(self, skill_id: str, new_version: str):
        """更新注册表"""
        registry = {"skills": {}}

        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
            except Exception:
                pass

        if "skills" not in registry:
            registry["skills"] = {}

        if skill_id in registry["skills"]:
            registry["skills"][skill_id]["version"] = new_version
            registry["skills"][skill_id]["updated_at"] = datetime.now().isoformat()

        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

    def _record_version(self, skill_id: str, version: str, backup_id: Optional[str]):
        """记录版本"""
        if skill_id not in self._version_history:
            self._version_history[skill_id] = []

        # 标记旧版本为 inactive
        for record in self._version_history[skill_id]:
            if record.status == "active":
                record.status = "superseded"

        # 添加新记录
        backup_path = None
        if backup_id:
            backup_path = os.path.join(self.backup_dir, f"{skill_id}_*_*.json")

        self._version_history[skill_id].append(VersionRecord(
            skill_id=skill_id,
            version=version,
            installed_at=datetime.now().isoformat(),
            status="active",
            backup_path=backup_path
        ))

        self._save_history()

    def rollback(self, skill_id: str, backup_id: str) -> UpgradeResult:
        """
        回滚到备份版本

        Args:
            skill_id: 技能 ID
            backup_id: 备份 ID

        Returns:
            UpgradeResult
        """
        # 查找备份文件
        backup_pattern = f"{skill_id}_*_{backup_id}.json"
        backup_file = None

        for filename in os.listdir(self.backup_dir):
            if filename.endswith(f"_{backup_id}.json") and filename.startswith(skill_id):
                backup_file = os.path.join(self.backup_dir, filename)
                break

        if not backup_file:
            return UpgradeResult(
                success=False,
                skill_id=skill_id,
                errors=[f"Backup not found: {backup_id}"]
            )

        # 读取备份
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
        except Exception as e:
            return UpgradeResult(
                success=False,
                skill_id=skill_id,
                errors=[f"Failed to read backup: {e}"]
            )

        previous_version = self._get_current_version(skill_id)

        # 恢复注册表
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)

                registry["skills"][skill_id] = backup_data.get("registry_entry", {})

                with open(self.registry_path, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
            except Exception as e:
                return UpgradeResult(
                    success=False,
                    skill_id=skill_id,
                    previous_version=previous_version,
                    errors=[f"Failed to restore registry: {e}"]
                )

        # 记录回滚
        self._record_version(skill_id, backup_data["version"], None)

        return UpgradeResult(
            success=True,
            skill_id=skill_id,
            previous_version=previous_version,
            new_version=backup_data["version"],
            backup_id=backup_id
        )

    def get_version_history(self, skill_id: str) -> List[VersionRecord]:
        """获取版本历史"""
        return self._version_history.get(skill_id, [])


# 全局单例
_upgrade_manager = None


def get_upgrade_manager() -> UpgradeManager:
    """获取升级管理器单例"""
    global _upgrade_manager
    if _upgrade_manager is None:
        _upgrade_manager = UpgradeManager()
    return _upgrade_manager
