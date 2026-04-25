"""
Skill Version Selector
技能版本选择器
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import threading
from pathlib import Path


class VersionStrategy(Enum):
    """版本选择策略"""
    LATEST = "latest"
    STABLE = "stable"
    COMPATIBLE = "compatible"
    PINNED = "pinned"


@dataclass
class SelectionCriteria:
    """选择条件"""
    strategy: VersionStrategy = VersionStrategy.LATEST
    min_health_score: float = 0.0
    require_stable: bool = False
    require_compatible: bool = False


@dataclass
class VersionInfo:
    """版本信息"""
    version: str
    stable: bool
    compatible: bool
    health_score: float = 1.0


class SkillVersionSelector:
    """技能版本选择器"""
    
    def __init__(self):
        self._versions: Dict[str, List[VersionInfo]] = {}
        self._pinned: Dict[str, str] = {}
        self._lock = threading.RLock()
    
    def register_version(self, skill_id: str, version: str, 
                         stable: bool = True, compatible: bool = True,
                         health_score: float = 1.0):
        """注册版本"""
        with self._lock:
            if skill_id not in self._versions:
                self._versions[skill_id] = []
            
            self._versions[skill_id].append(VersionInfo(
                version=version,
                stable=stable,
                compatible=compatible,
                health_score=health_score
            ))
    
    def pin_version(self, skill_id: str, version: str):
        """锁定版本"""
        with self._lock:
            self._pinned[skill_id] = version
    
    def unpin_version(self, skill_id: str):
        """解锁版本"""
        with self._lock:
            self._pinned.pop(skill_id, None)
    
    def select(self, skill_id: str, 
               strategy: VersionStrategy = VersionStrategy.LATEST) -> Optional[str]:
        """选择版本"""
        with self._lock:
            # 检查锁定版本
            if skill_id in self._pinned:
                return self._pinned[skill_id]
            
            versions = self._versions.get(skill_id, [])
            if not versions:
                return None
            
            if strategy == VersionStrategy.LATEST:
                return versions[-1].version
            
            elif strategy == VersionStrategy.STABLE:
                stable_versions = [v for v in versions if v.stable]
                return stable_versions[-1].version if stable_versions else None
            
            elif strategy == VersionStrategy.COMPATIBLE:
                compatible_versions = [v for v in versions if v.compatible]
                return compatible_versions[-1].version if compatible_versions else None
            
            else:
                return versions[-1].version
    
    def get_versions(self, skill_id: str) -> List[str]:
        """获取所有版本"""
        versions = self._versions.get(skill_id, [])
        return [v.version for v in versions]
    
    def get_latest(self, skill_id: str) -> Optional[str]:
        """获取最新版本"""
        return self.select(skill_id, VersionStrategy.LATEST)
    
    def get_stable(self, skill_id: str) -> Optional[str]:
        """获取稳定版本"""
        return self.select(skill_id, VersionStrategy.STABLE)
