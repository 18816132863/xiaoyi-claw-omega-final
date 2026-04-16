from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import os


class SkillCategory(str, Enum):
    UTILITY = "utility"
    CODE = "code"
    DATA = "data"
    FILE = "file"
    SEARCH = "search"
    DOCUMENT = "document"
    FINANCE = "finance"
    OTHER = "other"


class SkillStatus(str, Enum):
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"
    RESTRICTED = "restricted"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


@dataclass
class SkillManifest:
    skill_id: str
    name: str
    version: str
    description: str
    category: SkillCategory = SkillCategory.UTILITY
    status: SkillStatus = SkillStatus.STABLE
    executor_type: str = "skill_md"
    entry_point: str = ""
    timeout_seconds: int = 60
    tags: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillRegistry:
    """
    技能注册表
    
    职责：
    - 管理技能清单
    - 持久化到 JSON 文件
    - 与生命周期管理器集成
    """
    
    def __init__(self, registry_path: str = "skills/registry/skill_registry.json"):
        self.registry_path = registry_path
        self._skills: Dict[str, SkillManifest] = {}
        self._load()
    
    def _load(self):
        """从文件加载"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                
                for skill_data in data.get("skills", []):
                    manifest = SkillManifest(
                        skill_id=skill_data["skill_id"],
                        name=skill_data.get("name", ""),
                        version=skill_data.get("version", "1.0.0"),
                        description=skill_data.get("description", ""),
                        category=SkillCategory(skill_data.get("category", "other")),
                        status=SkillStatus(skill_data.get("status", "stable")),
                        executor_type=skill_data.get("executor_type", "skill_md"),
                        entry_point=skill_data.get("entry_point", ""),
                        timeout_seconds=skill_data.get("timeout_seconds", 60),
                        tags=skill_data.get("tags", []),
                        required_permissions=skill_data.get("required_permissions", []),
                        metadata=skill_data.get("metadata", {})
                    )
                    self._skills[manifest.skill_id] = manifest
            except:
                pass
    
    def _save(self):
        """保存到文件"""
        os.makedirs(os.path.dirname(self.registry_path) or ".", exist_ok=True)
        
        data = {
            "version": "1.0.0",
            "skills": [
                {
                    "skill_id": m.skill_id,
                    "name": m.name,
                    "version": m.version,
                    "description": m.description,
                    "category": m.category.value,
                    "status": m.status.value,
                    "executor_type": m.executor_type,
                    "entry_point": m.entry_point,
                    "timeout_seconds": m.timeout_seconds,
                    "tags": m.tags,
                    "required_permissions": m.required_permissions,
                    "metadata": m.metadata
                }
                for m in self._skills.values()
            ]
        }
        
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)

    def register(self, manifest: SkillManifest) -> SkillManifest:
        self._skills[manifest.skill_id] = manifest
        self._save()
        return manifest

    def unregister(self, skill_id: str) -> bool:
        if skill_id in self._skills:
            del self._skills[skill_id]
            self._save()
            return True
        return False

    def get(self, skill_id: str) -> Optional[SkillManifest]:
        return self._skills.get(skill_id)

    def list(self) -> List[SkillManifest]:
        return list(self._skills.values())

    def enable(self, skill_id: str) -> bool:
        manifest = self._skills.get(skill_id)
        if not manifest:
            return False
        if manifest.status in {SkillStatus.DISABLED, SkillStatus.DEPRECATED}:
            manifest.status = SkillStatus.STABLE
            self._save()
        return True

    def disable(self, skill_id: str) -> bool:
        manifest = self._skills.get(skill_id)
        if not manifest:
            return False
        manifest.status = SkillStatus.DISABLED
        self._save()
        return True

    def deprecate(self, skill_id: str) -> bool:
        manifest = self._skills.get(skill_id)
        if not manifest:
            return False
        manifest.status = SkillStatus.DEPRECATED
        self._save()
        return True

    def update_status(self, skill_id: str, status: SkillStatus) -> bool:
        manifest = self._skills.get(skill_id)
        if not manifest:
            return False
        manifest.status = status
        self._save()
        return True

    def search(self, query: str) -> List[SkillManifest]:
        q = (query or "").lower().strip()
        if not q:
            return self.list()

        results: List[SkillManifest] = []
        for manifest in self._skills.values():
            haystacks = [
                manifest.skill_id,
                manifest.name,
                manifest.description,
                " ".join(manifest.tags or []),
                manifest.category.value,
            ]
            text = " ".join(haystacks).lower()
            if q in text:
                results.append(manifest)
        return results
    
    def reload(self):
        """重新加载"""
        self._skills.clear()
        self._load()
