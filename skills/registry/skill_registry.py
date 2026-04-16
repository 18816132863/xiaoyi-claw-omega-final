"""Skill Registry - 技能注册中心

真实可用的技能注册、发现、管理功能。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os


class SkillCategory(Enum):
    """技能分类"""
    AI = "ai"
    SEARCH = "search"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    FINANCE = "finance"
    CODE = "code"
    ECOMMERCE = "ecommerce"
    DATA = "data"
    MEMORY = "memory"
    AUDIO = "audio"
    AUTOMATION = "automation"
    COMMUNICATION = "communication"
    UTILITY = "utility"
    OTHER = "other"


class SkillStatus(Enum):
    """技能状态"""
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"


@dataclass
class SkillManifest:
    """技能清单 - 技能的完整元数据"""
    skill_id: str
    name: str
    version: str
    description: str
    category: SkillCategory
    status: SkillStatus = SkillStatus.STABLE
    executor_type: str = "skill_md"  # skill_md, python, http, subprocess
    entry_point: str = ""
    timeout_seconds: int = 60
    author: str = ""
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)
    input_contract: Dict = field(default_factory=dict)
    output_contract: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "category": self.category.value,
            "status": self.status.value,
            "executor_type": self.executor_type,
            "entry_point": self.entry_point,
            "timeout_seconds": self.timeout_seconds,
            "author": self.author,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "required_permissions": self.required_permissions,
            "input_contract": self.input_contract,
            "output_contract": self.output_contract,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SkillManifest":
        return cls(
            skill_id=data["skill_id"],
            name=data["name"],
            version=data["version"],
            description=data["description"],
            category=SkillCategory(data.get("category", "other")),
            status=SkillStatus(data.get("status", "stable")),
            executor_type=data.get("executor_type", "skill_md"),
            entry_point=data.get("entry_point", ""),
            timeout_seconds=data.get("timeout_seconds", 60),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            required_permissions=data.get("required_permissions", []),
            input_contract=data.get("input_contract", {}),
            output_contract=data.get("output_contract", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            metadata=data.get("metadata", {})
        )


class SkillRegistry:
    """
    技能注册中心
    
    真实可用的技能注册、发现、管理功能。
    """
    
    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path
        self._skills: Dict[str, SkillManifest] = {}
        self._category_index: Dict[SkillCategory, List[str]] = {cat: [] for cat in SkillCategory}
        self._tag_index: Dict[str, List[str]] = {}
        
        if registry_path and os.path.exists(registry_path):
            self._load()
    
    def _load(self):
        """从文件加载注册表"""
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                for skill_data in data.get("skills", []):
                    manifest = SkillManifest.from_dict(skill_data)
                    self._skills[manifest.skill_id] = manifest
                    self._update_indexes(manifest)
        except Exception as e:
            print(f"Warning: Failed to load skill registry: {e}")
    
    def _save(self):
        """保存注册表到文件"""
        if not self.registry_path:
            return
        os.makedirs(os.path.dirname(self.registry_path) or ".", exist_ok=True)
        data = {
            "version": "1.0",
            "skills": [s.to_dict() for s in self._skills.values()]
        }
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _update_indexes(self, manifest: SkillManifest):
        """更新索引"""
        # 分类索引
        if manifest.skill_id not in self._category_index[manifest.category]:
            self._category_index[manifest.category].append(manifest.skill_id)
        
        # 标签索引
        for tag in manifest.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            if manifest.skill_id not in self._tag_index[tag]:
                self._tag_index[tag].append(manifest.skill_id)
    
    def _remove_from_indexes(self, manifest: SkillManifest):
        """从索引中移除"""
        if manifest.skill_id in self._category_index.get(manifest.category, []):
            self._category_index[manifest.category].remove(manifest.skill_id)
        
        for tag in manifest.tags:
            if manifest.skill_id in self._tag_index.get(tag, []):
                self._tag_index[tag].remove(manifest.skill_id)
    
    def register(self, manifest: SkillManifest) -> str:
        """注册技能"""
        skill_id = manifest.skill_id
        self._skills[skill_id] = manifest
        self._update_indexes(manifest)
        self._save()
        return skill_id
    
    def unregister(self, skill_id: str) -> bool:
        """注销技能"""
        if skill_id not in self._skills:
            return False
        
        manifest = self._skills[skill_id]
        self._remove_from_indexes(manifest)
        del self._skills[skill_id]
        self._save()
        return True
    
    def get(self, skill_id: str) -> Optional[SkillManifest]:
        """获取技能"""
        return self._skills.get(skill_id)
    
    def list(self, category: SkillCategory = None, status: SkillStatus = None) -> List[SkillManifest]:
        """列出技能"""
        results = list(self._skills.values())
        
        if category:
            results = [s for s in results if s.category == category]
        
        if status:
            results = [s for s in results if s.status == status]
        
        return results
    
    def search(self, query: str = None, tags: List[str] = None) -> List[SkillManifest]:
        """搜索技能"""
        results = list(self._skills.values())
        
        if query:
            query_lower = query.lower()
            results = [
                s for s in results
                if query_lower in s.name.lower() or query_lower in s.description.lower()
            ]
        
        if tags:
            results = [s for s in results if any(t in s.tags for t in tags)]
        
        return results
    
    def enable(self, skill_id: str) -> bool:
        """启用技能"""
        manifest = self._skills.get(skill_id)
        if not manifest:
            return False
        manifest.status = SkillStatus.STABLE
        manifest.updated_at = datetime.now()
        self._save()
        return True
    
    def disable(self, skill_id: str) -> bool:
        """禁用技能"""
        manifest = self._skills.get(skill_id)
        if not manifest:
            return False
        manifest.status = SkillStatus.DISABLED
        manifest.updated_at = datetime.now()
        self._save()
        return True
    
    def count(self) -> int:
        """统计技能数量"""
        return len(self._skills)
    
    def get_by_category(self, category: SkillCategory) -> List[SkillManifest]:
        """按分类获取技能"""
        skill_ids = self._category_index.get(category, [])
        return [self._skills[sid] for sid in skill_ids if sid in self._skills]
    
    def get_by_tag(self, tag: str) -> List[SkillManifest]:
        """按标签获取技能"""
        skill_ids = self._tag_index.get(tag, [])
        return [self._skills[sid] for sid in skill_ids if sid in self._skills]
