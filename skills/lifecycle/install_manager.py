"""
Install Manager
安装管理器
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
import threading
from pathlib import Path

from skills.lifecycle.lifecycle_manager import LifecycleManager, get_lifecycle_manager


@dataclass
class InstallResult:
    """安装结果"""
    success: bool
    skill_id: str
    version: str
    message: str
    metadata: Dict[str, Any] = None


class InstallManager:
    """安装管理器"""
    
    def __init__(self, lifecycle: Optional[LifecycleManager] = None):
        self.lifecycle = lifecycle or get_lifecycle_manager()
        self._lock = threading.RLock()
    
    def install(self, skill_id: str, version: str = "latest",
                source: Optional[str] = None) -> InstallResult:
        """安装技能"""
        with self._lock:
            try:
                # 检查是否已安装
                existing = self.lifecycle.get(skill_id)
                if existing and existing.state.value in ["installed", "active"]:
                    return InstallResult(
                        success=False,
                        skill_id=skill_id,
                        version=version,
                        message="Skill already installed"
                    )
                
                # 执行安装
                record = self.lifecycle.install(skill_id, version)
                
                return InstallResult(
                    success=True,
                    skill_id=skill_id,
                    version=version,
                    message="Installed successfully",
                    metadata={"source": source}
                )
            except Exception as e:
                return InstallResult(
                    success=False,
                    skill_id=skill_id,
                    version=version,
                    message=str(e)
                )
    
    def reinstall(self, skill_id: str, version: str = "latest") -> InstallResult:
        """重新安装"""
        with self._lock:
            try:
                record = self.lifecycle.install(skill_id, version)
                return InstallResult(
                    success=True,
                    skill_id=skill_id,
                    version=version,
                    message="Reinstalled successfully"
                )
            except Exception as e:
                return InstallResult(
                    success=False,
                    skill_id=skill_id,
                    version=version,
                    message=str(e)
                )
