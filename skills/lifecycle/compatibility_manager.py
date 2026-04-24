"""
Compatibility Manager
兼容性管理器
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import threading
from pathlib import Path


@dataclass
class CompatibilityInfo:
    """兼容性信息"""
    skill_id: str
    version: str
    compatible: bool
    issues: List[str] = field(default_factory=list)
    requirements: Dict[str, str] = field(default_factory=dict)


class CompatibilityManager:
    """兼容性管理器"""
    
    def __init__(self):
        self._index: Dict[str, Dict[str, CompatibilityInfo]] = {}
        self._runtime_version: str = "1.0.0"
        self._lock = threading.RLock()
    
    def set_runtime_version(self, version: str):
        """设置运行时版本"""
        self._runtime_version = version
    
    def register(self, skill_id: str, version: str,
                 compatible: bool, issues: List[str] = None,
                 requirements: Dict[str, str] = None):
        """注册兼容性信息"""
        with self._lock:
            if skill_id not in self._index:
                self._index[skill_id] = {}
            
            self._index[skill_id][version] = CompatibilityInfo(
                skill_id=skill_id,
                version=version,
                compatible=compatible,
                issues=issues or [],
                requirements=requirements or {}
            )
    
    def check(self, skill_id: str, version: str) -> CompatibilityInfo:
        """检查兼容性"""
        with self._lock:
            skill_versions = self._index.get(skill_id, {})
            info = skill_versions.get(version)
            
            if info:
                return info
            
            # 默认兼容
            return CompatibilityInfo(
                skill_id=skill_id,
                version=version,
                compatible=True
            )
    
    def check_compatibility(self, skill_id: str, version: str) -> CompatibilityInfo:
        """检查兼容性 (别名)"""
        return self.check(skill_id, version)
    
    def is_compatible(self, skill_id: str, version: str) -> bool:
        """检查是否兼容"""
        info = self.check(skill_id, version)
        return info.compatible
    
    def get_issues(self, skill_id: str, version: str) -> List[str]:
        """获取兼容性问题"""
        info = self.check(skill_id, version)
        return info.issues
    
    def list_compatible(self, skill_id: str) -> List[str]:
        """列出兼容版本"""
        with self._lock:
            skill_versions = self._index.get(skill_id, {})
            return [
                version for version, info in skill_versions.items()
                if info.compatible
            ]
    
    def list_incompatible(self, skill_id: str) -> List[str]:
        """列出不兼容版本"""
        with self._lock:
            skill_versions = self._index.get(skill_id, {})
            return [
                version for version, info in skill_versions.items()
                if not info.compatible
            ]
    
    def refresh_index(self):
        """刷新兼容性索引"""
        # 这里可以实现从配置文件或数据库加载
        pass
