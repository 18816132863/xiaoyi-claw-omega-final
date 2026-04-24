"""
Skill Dependency Resolver
技能依赖解析器
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
import threading
from pathlib import Path

from skills.runtime.skill_package_loader import SkillPackage, SkillPackageLoader


@dataclass
class DependencyNode:
    """依赖节点"""
    skill_id: str
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)


class SkillDependencyResolver:
    """技能依赖解析器"""
    
    def __init__(self, loader: Optional[SkillPackageLoader] = None):
        self.loader = loader or SkillPackageLoader()
        self._dependency_graph: Dict[str, DependencyNode] = {}
        self._lock = threading.RLock()
        self._build_graph()
    
    def _build_graph(self):
        """构建依赖图"""
        for package in self.loader.list_all():
            node = DependencyNode(
                skill_id=package.package_id,
                dependencies=package.dependencies.copy()
            )
            self._dependency_graph[package.package_id] = node
        
        # 构建反向依赖
        for skill_id, node in self._dependency_graph.items():
            for dep_id in node.dependencies:
                if dep_id in self._dependency_graph:
                    self._dependency_graph[dep_id].dependents.append(skill_id)
    
    def resolve(self, skill_id: str) -> List[str]:
        """解析依赖顺序"""
        visited: Set[str] = set()
        result: List[str] = []
        
        def visit(sid: str):
            if sid in visited:
                return
            visited.add(sid)
            
            node = self._dependency_graph.get(sid)
            if node:
                for dep_id in node.dependencies:
                    visit(dep_id)
            
            result.append(sid)
        
        visit(skill_id)
        return result
    
    def check_circular(self, skill_id: str) -> bool:
        """检查循环依赖"""
        visited: Set[str] = set()
        path: Set[str] = set()
        
        def visit(sid: str) -> bool:
            if sid in path:
                return True  # 发现循环
            if sid in visited:
                return False
            
            visited.add(sid)
            path.add(sid)
            
            node = self._dependency_graph.get(sid)
            if node:
                for dep_id in node.dependencies:
                    if visit(dep_id):
                        return True
            
            path.remove(sid)
            return False
        
        return visit(skill_id)
    
    def get_dependents(self, skill_id: str) -> List[str]:
        """获取依赖于指定技能的所有技能"""
        node = self._dependency_graph.get(skill_id)
        return node.dependents.copy() if node else []
    
    def can_remove(self, skill_id: str) -> bool:
        """检查是否可以移除"""
        dependents = self.get_dependents(skill_id)
        return len(dependents) == 0
    
    def reload(self):
        """重新构建"""
        with self._lock:
            self.loader.reload()
            self._dependency_graph.clear()
            self._build_graph()
