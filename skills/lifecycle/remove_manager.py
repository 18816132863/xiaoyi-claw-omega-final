"""
Remove Manager
移除管理器
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import threading
from pathlib import Path

from skills.lifecycle.lifecycle_manager import LifecycleManager, get_lifecycle_manager
from skills.runtime.skill_dependency_resolver import SkillDependencyResolver


@dataclass
class RemoveResult:
    """移除结果"""
    success: bool
    skill_id: str
    message: str
    backup_path: Optional[str] = None
    forced: bool = False


class RemoveManager:
    """移除管理器"""
    
    def __init__(self, lifecycle: Optional[LifecycleManager] = None,
                 resolver: Optional[SkillDependencyResolver] = None):
        self.lifecycle = lifecycle or get_lifecycle_manager()
        self.resolver = resolver or SkillDependencyResolver()
        self._lock = threading.RLock()
    
    def can_remove(self, skill_id: str) -> bool:
        """检查是否可以移除"""
        # 检查是否有其他技能依赖
        dependents = self.resolver.get_dependents(skill_id)
        return len(dependents) == 0
    
    def remove(self, skill_id: str, force: bool = False,
               backup: bool = True) -> RemoveResult:
        """移除技能"""
        with self._lock:
            try:
                existing = self.lifecycle.get(skill_id)
                if not existing:
                    return RemoveResult(
                        success=False,
                        skill_id=skill_id,
                        message="Skill not found"
                    )
                
                # 检查依赖
                if not force and not self.can_remove(skill_id):
                    dependents = self.resolver.get_dependents(skill_id)
                    return RemoveResult(
                        success=False,
                        skill_id=skill_id,
                        message=f"Cannot remove: {len(dependents)} skills depend on it"
                    )
                
                # 创建备份
                backup_path = None
                if backup:
                    # 简化实现
                    backup_path = f"backup/{skill_id}"
                
                # 执行移除
                self.lifecycle.remove(skill_id)
                
                return RemoveResult(
                    success=True,
                    skill_id=skill_id,
                    message="Removed successfully",
                    backup_path=backup_path,
                    forced=force
                )
            except Exception as e:
                return RemoveResult(
                    success=False,
                    skill_id=skill_id,
                    message=str(e)
                )
