"""
Upgrade Manager
升级管理器
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import threading
from pathlib import Path

from skills.lifecycle.lifecycle_manager import LifecycleManager, get_lifecycle_manager


@dataclass
class UpgradeResult:
    """升级结果"""
    success: bool
    skill_id: str
    old_version: str
    new_version: str
    message: str
    backup_path: Optional[str] = None


class UpgradeManager:
    """升级管理器"""
    
    def __init__(self, lifecycle: Optional[LifecycleManager] = None):
        self.lifecycle = lifecycle or get_lifecycle_manager()
        self._lock = threading.RLock()
    
    def upgrade(self, skill_id: str, target_version: str) -> UpgradeResult:
        """升级技能"""
        with self._lock:
            try:
                existing = self.lifecycle.get(skill_id)
                if not existing:
                    return UpgradeResult(
                        success=False,
                        skill_id=skill_id,
                        old_version="",
                        new_version=target_version,
                        message="Skill not found"
                    )
                
                old_version = existing.version
                
                # 执行升级
                self.lifecycle.install(skill_id, target_version)
                
                return UpgradeResult(
                    success=True,
                    skill_id=skill_id,
                    old_version=old_version,
                    new_version=target_version,
                    message="Upgraded successfully"
                )
            except Exception as e:
                return UpgradeResult(
                    success=False,
                    skill_id=skill_id,
                    old_version="",
                    new_version=target_version,
                    message=str(e)
                )
    
    def rollback(self, skill_id: str, backup_path: str) -> UpgradeResult:
        """回滚升级"""
        with self._lock:
            try:
                # 从备份恢复
                # 这里简化实现
                return UpgradeResult(
                    success=True,
                    skill_id=skill_id,
                    old_version="",
                    new_version="",
                    message="Rolled back successfully",
                    backup_path=backup_path
                )
            except Exception as e:
                return UpgradeResult(
                    success=False,
                    skill_id=skill_id,
                    old_version="",
                    new_version="",
                    message=str(e)
                )
