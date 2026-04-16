"""Skill Deprecation Manager - 技能弃用管理器"""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
import json
import os


@dataclass
class DeprecationResult:
    """弃用结果"""
    success: bool
    skill_id: str
    message: str
    deprecated_at: Optional[str] = None
    error: Optional[str] = None


class DeprecationManager:
    """
    技能弃用管理器
    
    职责：
    - 弃用技能
    - 记录弃用原因
    - 弃用后 router 不再选中
    """
    
    def __init__(self, registry_path: str = "skills/registry/skill_registry.json"):
        self.registry_path = registry_path
    
    def _load_registry(self) -> Dict:
        """加载 registry"""
        if not os.path.exists(self.registry_path):
            return {"skills": [], "version": "1.0.0"}
        with open(self.registry_path, 'r') as f:
            return json.load(f)
    
    def _save_registry(self, data: Dict):
        """保存 registry"""
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def deprecate(
        self,
        skill_id: str,
        reason: str = "",
        replacement_skill_id: str = None
    ) -> DeprecationResult:
        """
        弃用技能
        
        Args:
            skill_id: 技能 ID
            reason: 弃用原因
            replacement_skill_id: 替代技能 ID
        
        Returns:
            DeprecationResult
        """
        registry = self._load_registry()
        skills = registry.get("skills", [])
        
        for skill in skills:
            if skill.get("skill_id") == skill_id:
                # 更新状态
                skill["status"] = "deprecated"
                
                # 更新 lifecycle
                if "lifecycle" not in skill:
                    skill["lifecycle"] = {}
                
                deprecated_at = datetime.now().isoformat()
                skill["lifecycle"]["deprecated"] = True
                skill["lifecycle"]["deprecated_at"] = deprecated_at
                skill["lifecycle"]["deprecated_reason"] = reason
                skill["lifecycle"]["replacement_skill_id"] = replacement_skill_id
                
                self._save_registry(registry)
                
                return DeprecationResult(
                    success=True,
                    skill_id=skill_id,
                    message=f"Skill {skill_id} deprecated successfully",
                    deprecated_at=deprecated_at
                )
        
        return DeprecationResult(
            success=False,
            skill_id=skill_id,
            message=f"Skill {skill_id} not found",
            error="skill_not_found"
        )
    
    def undeprecate(self, skill_id: str) -> DeprecationResult:
        """
        取消弃用
        
        Args:
            skill_id: 技能 ID
        
        Returns:
            DeprecationResult
        """
        registry = self._load_registry()
        skills = registry.get("skills", [])
        
        for skill in skills:
            if skill.get("skill_id") == skill_id:
                # 恢复状态
                skill["status"] = "stable"
                
                # 更新 lifecycle
                if "lifecycle" in skill:
                    skill["lifecycle"]["deprecated"] = False
                    skill["lifecycle"]["undeprecated_at"] = datetime.now().isoformat()
                
                self._save_registry(registry)
                
                return DeprecationResult(
                    success=True,
                    skill_id=skill_id,
                    message=f"Skill {skill_id} undeprecated successfully"
                )
        
        return DeprecationResult(
            success=False,
            skill_id=skill_id,
            message=f"Skill {skill_id} not found",
            error="skill_not_found"
        )
    
    def is_deprecated(self, skill_id: str) -> bool:
        """检查是否已弃用"""
        registry = self._load_registry()
        for skill in registry.get("skills", []):
            if skill.get("skill_id") == skill_id:
                return skill.get("status") == "deprecated" or \
                       skill.get("lifecycle", {}).get("deprecated", False)
        return False
    
    def get_deprecated_skills(self) -> list:
        """获取已弃用技能列表"""
        registry = self._load_registry()
        return [
            s for s in registry.get("skills", [])
            if s.get("status") == "deprecated" or
               s.get("lifecycle", {}).get("deprecated", False)
        ]
    
    def get_replacement(self, skill_id: str) -> Optional[str]:
        """获取替代技能"""
        registry = self._load_registry()
        for skill in registry.get("skills", []):
            if skill.get("skill_id") == skill_id:
                return skill.get("lifecycle", {}).get("replacement_skill_id")
        return None
    
    def get_deprecation_info(self, skill_id: str) -> Optional[Dict]:
        """获取弃用信息"""
        registry = self._load_registry()
        for skill in registry.get("skills", []):
            if skill.get("skill_id") == skill_id:
                lifecycle = skill.get("lifecycle", {})
                if lifecycle.get("deprecated"):
                    return {
                        "skill_id": skill_id,
                        "deprecated_at": lifecycle.get("deprecated_at"),
                        "reason": lifecycle.get("deprecated_reason"),
                        "replacement_skill_id": lifecycle.get("replacement_skill_id")
                    }
        return None
