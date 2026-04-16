"""Skill registry - central registration for all skills."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json
import os


class SkillStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"
    TESTING = "testing"


class SkillCategory(Enum):
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


@dataclass
class SkillManifest:
    """Skill manifest containing all skill metadata."""
    skill_id: str
    name: str
    version: str
    description: str
    category: SkillCategory
    status: SkillStatus = SkillStatus.ACTIVE
    author: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Execution
    executor_type: str = "skill_md"  # skill_md, python, http, subprocess
    entry_point: str = ""
    timeout_seconds: int = 60
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)
    
    # Contracts
    input_contract: Dict = field(default_factory=dict)
    output_contract: Dict = field(default_factory=dict)
    
    # Metadata
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
            "author": self.author,
            "tags": self.tags,
            "executor_type": self.executor_type,
            "entry_point": self.entry_point,
            "timeout_seconds": self.timeout_seconds,
            "dependencies": self.dependencies,
            "required_skills": self.required_skills,
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
            status=SkillStatus(data.get("status", "active")),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            executor_type=data.get("executor_type", "skill_md"),
            entry_point=data.get("entry_point", ""),
            timeout_seconds=data.get("timeout_seconds", 60),
            dependencies=data.get("dependencies", []),
            required_skills=data.get("required_skills", []),
            required_permissions=data.get("required_permissions", []),
            input_contract=data.get("input_contract", {}),
            output_contract=data.get("output_contract", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            metadata=data.get("metadata", {})
        )


class SkillRegistry:
    """
    Central registry for all skills.
    
    Provides:
    - Skill registration and discovery
    - Version management
    - Dependency resolution
    - Status tracking
    """
    
    def __init__(self, registry_path: str = "infrastructure/inventory/skill_registry.json"):
        self.registry_path = registry_path
        self._skills: Dict[str, SkillManifest] = {}
        self._category_index: Dict[SkillCategory, List[str]] = {cat: [] for cat in SkillCategory}
        self._tag_index: Dict[str, List[str]] = {}
        self._load()
    
    def _load(self):
        """Load registry from file."""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    data = json.load(f)
                    for skill_data in data.get("skills", []):
                        manifest = SkillManifest.from_dict(skill_data)
                        self._register(manifest, save=False)
            except Exception as e:
                print(f"Warning: Failed to load skill registry: {e}")
    
    def _save(self):
        """Save registry to file."""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        data = {
            "version": "1.0",
            "skills": [s.to_dict() for s in self._skills.values()]
        }
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register(self, manifest: SkillManifest) -> str:
        """Register a skill."""
        return self._register(manifest, save=True)
    
    def _register(self, manifest: SkillManifest, save: bool) -> str:
        """Internal registration."""
        skill_id = manifest.skill_id
        
        # Check for existing version
        if skill_id in self._skills:
            existing = self._skills[skill_id]
            if existing.version == manifest.version:
                # Update existing
                manifest.created_at = existing.created_at
            # else: new version replaces old
        
        self._skills[skill_id] = manifest
        
        # Update indexes
        if skill_id not in self._category_index[manifest.category]:
            self._category_index[manifest.category].append(skill_id)
        
        for tag in manifest.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            if skill_id not in self._tag_index[tag]:
                self._tag_index[tag].append(skill_id)
        
        if save:
            self._save()
        
        return skill_id
    
    def unregister(self, skill_id: str) -> bool:
        """Unregister a skill."""
        if skill_id not in self._skills:
            return False
        
        manifest = self._skills[skill_id]
        
        # Remove from indexes
        self._category_index[manifest.category].remove(skill_id)
        for tag in manifest.tags:
            if tag in self._tag_index and skill_id in self._tag_index[tag]:
                self._tag_index[tag].remove(skill_id)
        
        del self._skills[skill_id]
        self._save()
        return True
    
    def get(self, skill_id: str) -> Optional[SkillManifest]:
        """Get skill by ID."""
        return self._skills.get(skill_id)
    
    def get_by_name(self, name: str) -> Optional[SkillManifest]:
        """Get skill by name."""
        for manifest in self._skills.values():
            if manifest.name == name:
                return manifest
        return None
    
    def search(
        self,
        query: str = None,
        category: SkillCategory = None,
        tags: List[str] = None,
        status: SkillStatus = None
    ) -> List[SkillManifest]:
        """Search for skills."""
        results = list(self._skills.values())
        
        if category:
            results = [s for s in results if s.category == category]
        
        if tags:
            results = [s for s in results if any(t in s.tags for t in tags)]
        
        if status:
            results = [s for s in results if s.status == status]
        
        if query:
            query_lower = query.lower()
            results = [
                s for s in results
                if query_lower in s.name.lower() or query_lower in s.description.lower()
            ]
        
        return results
    
    def get_by_category(self, category: SkillCategory) -> List[SkillManifest]:
        """Get all skills in a category."""
        skill_ids = self._category_index.get(category, [])
        return [self._skills[sid] for sid in skill_ids if sid in self._skills]
    
    def get_by_tag(self, tag: str) -> List[SkillManifest]:
        """Get all skills with a tag."""
        skill_ids = self._tag_index.get(tag, [])
        return [self._skills[sid] for sid in skill_ids if sid in self._skills]
    
    def get_dependencies(self, skill_id: str) -> List[SkillManifest]:
        """Get all dependencies for a skill."""
        manifest = self.get(skill_id)
        if not manifest:
            return []
        
        deps = []
        for dep_id in manifest.dependencies:
            dep = self.get(dep_id)
            if dep:
                deps.append(dep)
        
        return deps
    
    def resolve_dependencies(self, skill_id: str) -> List[str]:
        """Resolve all dependencies in order."""
        resolved = []
        visited = set()
        
        def resolve(sid):
            if sid in visited:
                return
            visited.add(sid)
            
            manifest = self.get(sid)
            if manifest:
                for dep_id in manifest.dependencies:
                    resolve(dep_id)
                resolved.append(sid)
        
        resolve(skill_id)
        return resolved
    
    def list_all(self) -> List[SkillManifest]:
        """List all registered skills."""
        return list(self._skills.values())
    
    def count(self) -> int:
        """Count total registered skills."""
        return len(self._skills)
    
    def count_by_category(self) -> Dict[SkillCategory, int]:
        """Count skills by category."""
        return {cat: len(ids) for cat, ids in self._category_index.items()}
