"""Skill Loader - 技能加载器"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import json
import os

from skills.registry.skill_registry import SkillManifest, SkillCategory, SkillStatus


@dataclass
class LoadedSkill:
    """已加载的技能"""
    manifest: SkillManifest
    skill_definition: Dict[str, Any]
    is_valid: bool
    load_errors: list


class SkillLoader:
    """
    技能加载器
    
    职责：
    - 从 registry 加载技能定义
    - 验证技能完整性
    - 解析技能配置
    """
    
    def __init__(self, registry_path: str = "skills/registry/skill_registry.json"):
        self.registry_path = registry_path
        self._cache: Dict[str, LoadedSkill] = {}
    
    def load(self, skill_id: str) -> Optional[LoadedSkill]:
        """加载单个技能"""
        if skill_id in self._cache:
            return self._cache[skill_id]
        
        # 从 registry 读取
        manifest = self._load_manifest(skill_id)
        if not manifest:
            return None
        
        # 加载技能定义
        skill_definition = self._load_definition(manifest)
        
        # 验证
        is_valid, errors = self._validate(manifest, skill_definition)
        
        loaded = LoadedSkill(
            manifest=manifest,
            skill_definition=skill_definition,
            is_valid=is_valid,
            load_errors=errors
        )
        
        self._cache[skill_id] = loaded
        return loaded
    
    def _load_manifest(self, skill_id: str) -> Optional[SkillManifest]:
        """从 registry 加载清单"""
        if not os.path.exists(self.registry_path):
            return None
        
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
            
            for skill_data in data.get("skills", []):
                if skill_data.get("skill_id") == skill_id:
                    return SkillManifest(
                        skill_id=skill_data["skill_id"],
                        name=skill_data.get("name", ""),
                        version=skill_data.get("version", "1.0.0"),
                        description=skill_data.get("description", ""),
                        category=SkillCategory(skill_data.get("category", "other")),
                        status=SkillStatus(skill_data.get("status", "stable")),
                        executor_type=skill_data.get("executor_type", "skill_md"),
                        entry_point=skill_data.get("entry_point", ""),
                        timeout_seconds=skill_data.get("timeout_seconds", 60),
                        tags=skill_data.get("tags", [])
                    )
        except:
            pass
        
        return None
    
    def _load_definition(self, manifest: SkillManifest) -> Dict[str, Any]:
        """加载技能定义"""
        definition = {
            "skill_id": manifest.skill_id,
            "name": manifest.name,
            "entry_point": manifest.entry_point,
            "category": manifest.category.value,
            "tags": manifest.tags,
            "status": manifest.status.value
        }
        
        # 如果有 entry_point，尝试加载 SKILL.md
        if manifest.entry_point and os.path.exists(manifest.entry_point):
            try:
                with open(manifest.entry_point, 'r') as f:
                    definition["content"] = f.read()
            except:
                pass
        
        return definition
    
    def _validate(
        self,
        manifest: SkillManifest,
        definition: Dict[str, Any]
    ) -> tuple[bool, list]:
        """验证技能"""
        errors = []
        
        # 检查必需字段
        if not manifest.skill_id:
            errors.append("Missing skill_id")
        if not manifest.name:
            errors.append("Missing name")
        if not manifest.version:
            errors.append("Missing version")
        
        # 检查 entry_point
        if manifest.executor_type == "skill_md":
            if not manifest.entry_point:
                errors.append("Missing entry_point for skill_md executor")
        
        return len(errors) == 0, errors
    
    def load_all(self) -> Dict[str, LoadedSkill]:
        """加载所有技能"""
        if not os.path.exists(self.registry_path):
            return {}
        
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
            
            for skill_data in data.get("skills", []):
                skill_id = skill_data.get("skill_id")
                if skill_id:
                    self.load(skill_id)
        except:
            pass
        
        return self._cache
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
