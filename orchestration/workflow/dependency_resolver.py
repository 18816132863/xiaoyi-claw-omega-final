"""Dependency Resolver - 依赖解析器"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class DependencyNode:
    """依赖节点"""
    node_id: str
    level: int = 0
    dependencies: Set[str] = None
    dependents: Set[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = set()
        if self.dependents is None:
            self.dependents = set()


class DependencyResolver:
    """
    依赖解析器
    
    功能：
    - 解析依赖关系
    - 检测循环依赖
    - 计算执行顺序
    - 计算并行层级
    """
    
    def __init__(self):
        self._nodes: Dict[str, DependencyNode] = {}
    
    def add_node(self, node_id: str, dependencies: List[str] = None):
        """添加节点"""
        node = DependencyNode(
            node_id=node_id,
            dependencies=set(dependencies or [])
        )
        self._nodes[node_id] = node
        
        # 更新下游关系
        for dep in node.dependencies:
            if dep in self._nodes:
                self._nodes[dep].dependents.add(node_id)
    
    def resolve(self) -> List[List[str]]:
        """
        解析依赖并返回执行层级
        
        Returns:
            按层级分组的节点列表，同一层级的可并行执行
        """
        # 计算入度
        in_degree = defaultdict(int)
        for node_id, node in self._nodes.items():
            in_degree[node_id] = len(node.dependencies)
        
        # 按层级分组
        levels = []
        remaining = set(self._nodes.keys())
        completed = set()
        
        while remaining:
            # 找到当前可执行的节点
            ready = []
            for node_id in remaining:
                if self._nodes[node_id].dependencies.issubset(completed):
                    ready.append(node_id)
            
            if not ready:
                # 检测到循环依赖
                cycle = self._find_cycle(remaining)
                raise ValueError(f"Circular dependency detected: {cycle}")
            
            # 设置层级
            for node_id in ready:
                self._nodes[node_id].level = len(levels)
            
            levels.append(ready)
            completed.update(ready)
            remaining -= set(ready)
        
        return levels
    
    def _find_cycle(self, nodes: Set[str]) -> List[str]:
        """查找循环依赖"""
        visited = set()
        path = []
        
        def dfs(node_id):
            if node_id in path:
                cycle_start = path.index(node_id)
                return path[cycle_start:] + [node_id]
            
            if node_id in visited:
                return None
            
            visited.add(node_id)
            path.append(node_id)
            
            for dep in self._nodes[node_id].dependencies:
                if dep in nodes:
                    cycle = dfs(dep)
                    if cycle:
                        return cycle
            
            path.pop()
            return None
        
        for node_id in nodes:
            cycle = dfs(node_id)
            if cycle:
                return cycle
        
        return list(nodes)
    
    def get_execution_order(self) -> List[str]:
        """获取线性执行顺序"""
        levels = self.resolve()
        return [node_id for level in levels for node_id in level]
    
    def get_dependencies(self, node_id: str) -> Set[str]:
        """获取所有依赖（递归）"""
        all_deps = set()
        
        def collect(nid):
            if nid not in self._nodes:
                return
            for dep in self._nodes[nid].dependencies:
                if dep not in all_deps:
                    all_deps.add(dep)
                    collect(dep)
        
        collect(node_id)
        return all_deps
    
    def get_dependents(self, node_id: str) -> Set[str]:
        """获取所有下游（递归）"""
        all_dependents = set()
        
        def collect(nid):
            if nid not in self._nodes:
                return
            for dep in self._nodes[nid].dependents:
                if dep not in all_dependents:
                    all_dependents.add(dep)
                    collect(dep)
        
        collect(node_id)
        return all_dependents
    
    def can_execute(self, node_id: str, completed: Set[str]) -> bool:
        """检查节点是否可执行"""
        if node_id not in self._nodes:
            return False
        
        return self._nodes[node_id].dependencies.issubset(completed)
    
    def get_ready_nodes(self, completed: Set[str], running: Set[str] = None) -> List[str]:
        """获取就绪节点"""
        running = running or set()
        ready = []
        
        for node_id, node in self._nodes.items():
            if node_id in completed or node_id in running:
                continue
            
            if node.dependencies.issubset(completed):
                ready.append(node_id)
        
        return ready
    
    def clear(self):
        """清空"""
        self._nodes.clear()
    
    def count(self) -> int:
        """节点数量"""
        return len(self._nodes)
