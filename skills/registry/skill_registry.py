"""
Skill Registry
技能注册表

管理所有已注册技能的元数据和状态
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import threading
from pathlib import Path


def _get_project_root() -> Path:
    """动态获取项目根目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "core").exists() and (parent / "infrastructure").exists():
            return parent
    return current.parents[4]


class SkillStatus(Enum):
    """技能状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ERROR = "error"
    LOADING = "loading"
    STABLE = "stable"
    UNSTABLE = "unstable"


class SkillCategory(Enum):
    """技能分类"""
    AI = "ai"
    SEARCH = "search"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    FINANCE = "finance"
    CODE = "code"
    DATA = "data"
    MEMORY = "memory"
    AUDIO = "audio"
    AUTOMATION = "automation"
    COMMUNICATION = "communication"
    UTILITY = "utility"
    OTHER = "other"


@dataclass
class SkillManifest:
    """技能清单"""
    skill_id: str
    name: str
    version: str
    description: str
    status: SkillStatus
    entry_point: str
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    category: 'SkillCategory' = None
    executor_type: str = "skill_md"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "entry_point": self.entry_point,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "config": self.config,
            "metadata": self.metadata,
            "category": self.category.value if self.category else None,
            "executor_type": self.executor_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillManifest':
        category_val = data.get("category")
        category = SkillCategory(category_val) if category_val else None
        
        return cls(
            skill_id=data["skill_id"],
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            status=SkillStatus(data.get("status", "active")),
            entry_point=data.get("entry_point", ""),
            dependencies=data.get("dependencies", []),
            tags=data.get("tags", []),
            author=data.get("author"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            config=data.get("config", {}),
            metadata=data.get("metadata", {}),
            category=category,
            executor_type=data.get("executor_type", "skill_md")
        )


class SkillRegistry:
    """技能注册表"""
    
    def __init__(self, registry_path: Optional[Path] = None):
        if registry_path is None:
            project_root = _get_project_root()
            registry_path = project_root / "infrastructure" / "inventory" / "skill_registry.json"
        
        self.registry_path = Path(registry_path)
        self._skills: Dict[str, SkillManifest] = {}
        self._lock = threading.RLock()
        self._load()
    
    def _load(self):
        """从文件加载注册表"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 支持两种格式
                    skills_data = data.get("skills", data)
                    if isinstance(skills_data, dict):
                        for skill_id, skill_data in skills_data.items():
                            if isinstance(skill_data, dict):
                                skill_data["skill_id"] = skill_id
                                self._skills[skill_id] = SkillManifest.from_dict(skill_data)
                    elif isinstance(skills_data, list):
                        for skill_data in skills_data:
                            skill_id = skill_data.get("skill_id", skill_data.get("name", ""))
                            skill_data["skill_id"] = skill_id
                            self._skills[skill_id] = SkillManifest.from_dict(skill_data)
            except Exception as e:
                self._skills = {}
    
    def _save(self):
        """保存注册表到文件"""
        with self._lock:
            data = {
                "skills": {skill_id: skill.to_dict() 
                           for skill_id, skill in self._skills.items()}
            }
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register(self, manifest: SkillManifest) -> bool:
        """注册技能"""
        with self._lock:
            manifest.created_at = manifest.created_at or datetime.now().isoformat()
            manifest.updated_at = datetime.now().isoformat()
            self._skills[manifest.skill_id] = manifest
            self._save()
            return True
    
    def unregister(self, skill_id: str) -> bool:
        """注销技能"""
        with self._lock:
            if skill_id in self._skills:
                del self._skills[skill_id]
                self._save()
                return True
            return False
    
    def get(self, skill_id: str) -> Optional[SkillManifest]:
        """获取技能"""
        return self._skills.get(skill_id)
    
    def get_by_name(self, name: str) -> Optional[SkillManifest]:
        """按名称获取技能"""
        for skill in self._skills.values():
            if skill.name == name:
                return skill
        return None
    
    def list_all(self) -> List[SkillManifest]:
        """列出所有技能"""
        return list(self._skills.values())
    
    def list_by_status(self, status: SkillStatus) -> List[SkillManifest]:
        """按状态列出技能"""
        return [s for s in self._skills.values() if s.status == status]
    
    def list_by_tag(self, tag: str) -> List[SkillManifest]:
        """按标签列出技能"""
        return [s for s in self._skills.values() if tag in s.tags]
    
    def update_status(self, skill_id: str, status: SkillStatus) -> Optional[SkillManifest]:
        """更新技能状态"""
        with self._lock:
            skill = self._skills.get(skill_id)
            if skill:
                skill.status = status
                skill.updated_at = datetime.now().isoformat()
                self._save()
                return skill
            return None
    
    def search(self, query: str) -> List[SkillManifest]:
        """搜索技能"""
        query_lower = query.lower()
        results = []
        for skill in self._skills.values():
            if (query_lower in skill.name.lower() or
                query_lower in skill.description.lower() or
                any(query_lower in tag.lower() for tag in skill.tags)):
                results.append(skill)
        return results
    
    def count(self) -> int:
        """统计技能数量"""
        return len(self._skills)
    
    def exists(self, skill_id: str) -> bool:
        """检查技能是否存在"""
        return skill_id in self._skills
    
    def persist(self) -> bool:
        """持久化注册表"""
        try:
            self._save()
            return True
        except Exception as e:
            print(f"持久化失败: {e}")
            return False
    
    def load(self) -> bool:
        """从文件加载注册表"""
        try:
            self._load()
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False
    
    def reload(self) -> bool:
        """重新加载注册表（别名）"""
        return self.load()
    
    def export_to_json(self, path: str) -> bool:
        """导出到 JSON 文件"""
        try:
            with self._lock:
                data = {
                    "skills": {skill_id: skill.to_dict() 
                               for skill_id, skill in self._skills.items()},
                    "exported_at": datetime.now().isoformat(),
                }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def import_from_json(self, path: str, merge: bool = True) -> bool:
        """从 JSON 文件导入"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            skills_data = data.get("skills", {})
            
            with self._lock:
                if not merge:
                    self._skills.clear()
                
                for skill_id, skill_dict in skills_data.items():
                    manifest = SkillManifest(
                        skill_id=skill_id,
                        name=skill_dict.get("name", skill_id),
                        description=skill_dict.get("description", ""),
                        version=skill_dict.get("version", "1.0.0"),
                        category=SkillCategory(skill_dict.get("category", "other")),
                        status=SkillStatus(skill_dict.get("status", "active")),
                        tags=skill_dict.get("tags", []),
                        dependencies=skill_dict.get("dependencies", []),
                        entry_point=skill_dict.get("entry_point", ""),
                        config=skill_dict.get("config", {}),
                    )
                    self._skills[skill_id] = manifest
                
                self._save()
            
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False


# 单例实例
_registry: Optional[SkillRegistry] = None
_registry_lock = threading.Lock()


def get_skill_registry() -> SkillRegistry:
    """获取技能注册表单例"""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = SkillRegistry()
    return _registry
