"""Skill Enable/Disable Manager - 技能启用/禁用管理器"""

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime
import json
import os


@dataclass
class EnableDisableResult:
    """启用/禁用结果"""
    success: bool
    skill_id: str
    action: str
    message: str
    error: Optional[str] = None


class EnableDisableManager:
    """
    技能启用/禁用管理器
    
    职责：
    - 启用技能
    - 禁用技能
    - 同步更新 registry 和 lifecycle state
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
    
    def enable(self, skill_id: str) -> EnableDisableResult:
        """
        启用技能
        
        Args:
            skill_id: 技能 ID
        
        Returns:
            EnableDisableResult
        """
        registry = self._load_registry()
        skills = registry.get("skills", [])
        
        for skill in skills:
            if skill.get("skill_id") == skill_id:
                # 更新状态
                skill["status"] = "stable"
                
                # 更新 lifecycle
                if "lifecycle" not in skill:
                    skill["lifecycle"] = {}
                skill["lifecycle"]["enabled"] = True
                skill["lifecycle"]["enabled_at"] = datetime.now().isoformat()
                
                self._save_registry(registry)
                
                return EnableDisableResult(
                    success=True,
                    skill_id=skill_id,
                    action="enable",
                    message=f"Skill {skill_id} enabled successfully"
                )
        
        return EnableDisableResult(
            success=False,
            skill_id=skill_id,
            action="enable",
            message=f"Skill {skill_id} not found",
            error="skill_not_found"
        )
    
    def disable(self, skill_id: str, reason: str = "") -> EnableDisableResult:
        """
        禁用技能
        
        Args:
            skill_id: 技能 ID
            reason: 禁用原因
        
        Returns:
            EnableDisableResult
        """
        registry = self._load_registry()
        skills = registry.get("skills", [])
        
        for skill in skills:
            if skill.get("skill_id") == skill_id:
                # 更新状态
                skill["status"] = "disabled"
                
                # 更新 lifecycle
                if "lifecycle" not in skill:
                    skill["lifecycle"] = {}
                skill["lifecycle"]["enabled"] = False
                skill["lifecycle"]["disabled_at"] = datetime.now().isoformat()
                skill["lifecycle"]["disabled_reason"] = reason
                
                self._save_registry(registry)
                
                return EnableDisableResult(
                    success=True,
                    skill_id=skill_id,
                    action="disable",
                    message=f"Skill {skill_id} disabled successfully"
                )
        
        return EnableDisableResult(
            success=False,
            skill_id=skill_id,
            action="disable",
            message=f"Skill {skill_id} not found",
            error="skill_not_found"
        )
    
    def is_enabled(self, skill_id: str) -> bool:
        """检查是否启用"""
        registry = self._load_registry()
        for skill in registry.get("skills", []):
            if skill.get("skill_id") == skill_id:
                lifecycle = skill.get("lifecycle", {})
                return lifecycle.get("enabled", True) and skill.get("status") != "disabled"
        return False
    
    def get_enabled_skills(self) -> list:
        """获取已启用技能列表"""
        registry = self._load_registry()
        return [
            s for s in registry.get("skills", [])
            if s.get("lifecycle", {}).get("enabled", True) and s.get("status") != "disabled"
        ]
    
    def get_disabled_skills(self) -> list:
        """获取已禁用技能列表"""
        registry = self._load_registry()
        return [
            s for s in registry.get("skills", [])
            if not s.get("lifecycle", {}).get("enabled", True) or s.get("status") == "disabled"
        ]
    
    def batch_enable(self, skill_ids: list) -> Dict[str, EnableDisableResult]:
        """批量启用"""
        results = {}
        for skill_id in skill_ids:
            results[skill_id] = self.enable(skill_id)
        return results
    
    def batch_disable(self, skill_ids: list, reason: str = "") -> Dict[str, EnableDisableResult]:
        """批量禁用"""
        results = {}
        for skill_id in skill_ids:
            results[skill_id] = self.disable(skill_id, reason)
        return results
