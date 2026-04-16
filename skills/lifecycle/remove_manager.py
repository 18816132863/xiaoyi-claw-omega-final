"""
Remove Manager - 技能移除管理器
负责安全移除技能
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


@dataclass
class DependencyImpact:
    """依赖影响"""
    skill_id: str
    version: str
    depends_on_removed: bool
    is_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "depends_on_removed": self.depends_on_removed,
            "is_required": self.is_required
        }


@dataclass
class RemovePlan:
    """移除计划"""
    skill_id: str
    version: str
    has_dependents: bool
    dependents: List[DependencyImpact] = field(default_factory=list)
    backup_created: bool = False
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "has_dependents": self.has_dependents,
            "dependents": [d.to_dict() for d in self.dependents],
            "backup_created": self.backup_created,
            "warnings": self.warnings
        }


@dataclass
class RemoveResult:
    """移除结果"""
    success: bool
    skill_id: str
    version: Optional[str] = None
    backup_id: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    affected_skills: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "skill_id": self.skill_id,
            "version": self.version,
            "backup_id": self.backup_id,
            "errors": self.errors,
            "warnings": self.warnings,
            "affected_skills": self.affected_skills
        }


class RemoveManager:
    """
    技能移除管理器

    职责：
    - 检查依赖影响
    - 创建备份
    - 安全移除
    - 更新注册表
    - 记录移除历史
    """

    def __init__(
        self,
        registry_path: str = "skills/registry/skill_registry.json",
        history_path: str = "skills/registry/remove_history.json",
        backup_dir: str = "skills/backups"
    ):
        self.registry_path = registry_path
        self.history_path = history_path
        self.backup_dir = backup_dir
        self._remove_history: List[Dict[str, Any]] = []
        self._ensure_dirs()
        self._load_history()

    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)

    def _load_history(self):
        """加载移除历史"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    self._remove_history = json.load(f)
            except Exception:
                pass

    def _save_history(self):
        """保存移除历史"""
        try:
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(self._remove_history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def plan_remove(self, skill_id: str, version: str = None) -> RemovePlan:
        """
        规划移除

        Args:
            skill_id: 技能 ID
            version: 版本（可选，默认当前版本）

        Returns:
            RemovePlan
        """
        warnings = []

        # 获取版本
        if not version:
            version = self._get_current_version(skill_id)

        if not version:
            return RemovePlan(
                skill_id=skill_id,
                version="unknown",
                has_dependents=False,
                warnings=["Skill not found in registry"]
            )

        # 检查依赖影响
        dependents = self._check_dependents(skill_id, version)

        has_dependents = len(dependents) > 0
        if has_dependents:
            required_dependents = [d for d in dependents if d.is_required]
            if required_dependents:
                warnings.append(
                    f"Required dependents found: {[d.skill_id for d in required_dependents]}"
                )

        return RemovePlan(
            skill_id=skill_id,
            version=version,
            has_dependents=has_dependents,
            dependents=dependents,
            backup_created=False,
            warnings=warnings
        )

    def remove(
        self,
        skill_id: str,
        version: str = None,
        force: bool = False,
        create_backup: bool = True
    ) -> RemoveResult:
        """
        执行移除

        Args:
            skill_id: 技能 ID
            version: 版本（可选）
            force: 强制移除（忽略依赖检查）
            create_backup: 是否创建备份

        Returns:
            RemoveResult
        """
        errors = []
        warnings = []
        affected_skills = []

        # 规划移除
        plan = self.plan_remove(skill_id, version)

        if not plan.version or plan.version == "unknown":
            return RemoveResult(
                success=False,
                skill_id=skill_id,
                errors=["Skill not found"]
            )

        # 检查依赖
        if plan.has_dependents and not force:
            required = [d for d in plan.dependents if d.is_required]
            if required:
                errors.append(
                    f"Cannot remove: required by {[d.skill_id for d in required]}. "
                    "Use force=True to override."
                )

        if errors:
            return RemoveResult(
                success=False,
                skill_id=skill_id,
                version=plan.version,
                errors=errors
            )

        # 创建备份
        backup_id = None
        if create_backup:
            backup_id = self._create_backup(skill_id, plan.version)

        # 记录受影响的技能
        affected_skills = [d.skill_id for d in plan.dependents]

        # 从注册表移除
        self._remove_from_registry(skill_id)

        # 记录移除历史
        self._record_removal(skill_id, plan.version, backup_id, affected_skills)

        return RemoveResult(
            success=True,
            skill_id=skill_id,
            version=plan.version,
            backup_id=backup_id,
            warnings=plan.warnings + warnings,
            affected_skills=affected_skills
        )

    def _get_current_version(self, skill_id: str) -> Optional[str]:
        """获取当前版本"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                    return registry.get("skills", {}).get(skill_id, {}).get("version")
            except Exception:
                pass
        return None

    def _check_dependents(self, skill_id: str, version: str) -> List[DependencyImpact]:
        """检查依赖此技能的其他技能"""
        dependents = []

        # 从注册表获取所有技能
        if not os.path.exists(self.registry_path):
            return dependents

        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        except Exception:
            return dependents

        for other_id, other_info in registry.get("skills", {}).items():
            if other_id == skill_id:
                continue

            # 检查依赖
            dependencies = other_info.get("dependencies", [])
            for dep in dependencies:
                if dep.get("skill_id") == skill_id:
                    dependents.append(DependencyImpact(
                        skill_id=other_id,
                        version=other_info.get("version", "unknown"),
                        depends_on_removed=True,
                        is_required=not dep.get("optional", False)
                    ))

        return dependents

    def _create_backup(self, skill_id: str, version: str) -> Optional[str]:
        """创建备份"""
        import uuid
        backup_id = f"remove_{uuid.uuid4().hex[:8]}"
        backup_path = os.path.join(self.backup_dir, f"{skill_id}_{version}_{backup_id}.json")

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

    def _remove_from_registry(self, skill_id: str):
        """从注册表移除"""
        if not os.path.exists(self.registry_path):
            return

        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)

            if skill_id in registry.get("skills", {}):
                del registry["skills"][skill_id]

            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _record_removal(
        self,
        skill_id: str,
        version: str,
        backup_id: Optional[str],
        affected_skills: List[str]
    ):
        """记录移除"""
        self._remove_history.append({
            "skill_id": skill_id,
            "version": version,
            "removed_at": datetime.now().isoformat(),
            "backup_id": backup_id,
            "affected_skills": affected_skills
        })

        self._save_history()

    def get_remove_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取移除历史"""
        return self._remove_history[-limit:]

    def restore(self, backup_id: str) -> RemoveResult:
        """
        从备份恢复

        Args:
            backup_id: 备份 ID

        Returns:
            RemoveResult
        """
        # 查找备份文件
        backup_file = None
        for filename in os.listdir(self.backup_dir):
            if backup_id in filename:
                backup_file = os.path.join(self.backup_dir, filename)
                break

        if not backup_file:
            return RemoveResult(
                success=False,
                skill_id="unknown",
                errors=[f"Backup not found: {backup_id}"]
            )

        # 读取备份
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
        except Exception as e:
            return RemoveResult(
                success=False,
                skill_id="unknown",
                errors=[f"Failed to read backup: {e}"]
            )

        skill_id = backup_data["skill_id"]

        # 恢复到注册表
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)

                if "skills" not in registry:
                    registry["skills"] = {}

                registry["skills"][skill_id] = backup_data.get("registry_entry", {})

                with open(self.registry_path, 'w', encoding='utf-8') as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
            except Exception as e:
                return RemoveResult(
                    success=False,
                    skill_id=skill_id,
                    errors=[f"Failed to restore: {e}"]
                )

        return RemoveResult(
            success=True,
            skill_id=skill_id,
            version=backup_data["version"],
            backup_id=backup_id
        )


# 全局单例
_remove_manager = None


def get_remove_manager() -> RemoveManager:
    """获取移除管理器单例"""
    global _remove_manager
    if _remove_manager is None:
        _remove_manager = RemoveManager()
    return _remove_manager
