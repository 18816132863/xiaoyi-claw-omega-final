"""DAG Builder - DAG 构建器"""

from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class DAGNode:
    """DAG 节点"""
    node_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)


@dataclass
class DAG:
    """有向无环图"""
    nodes: Dict[str, DAGNode] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    
    def add_node(
        self,
        node_id: str,
        data: Dict = None,
        dependencies: List[str] = None
    ):
        """添加节点"""
        node = DAGNode(
            node_id=node_id,
            data=data or {},
            dependencies=set(dependencies or [])
        )
        self.nodes[node_id] = node
        
        # 更新边
        for dep in node.dependencies:
            self.edges.append((dep, node_id))
            if dep in self.nodes:
                self.nodes[dep].dependents.add(node_id)
    
    def get_entry_points(self) -> List[str]:
        """获取入口节点（无依赖）"""
        return [n for n, node in self.nodes.items() if not node.dependencies]
    
    def get_exit_points(self) -> List[str]:
        """获取出口节点（无下游）"""
        return [n for n, node in self.nodes.items() if not node.dependents]
    
    def topological_sort(self) -> List[str]:
        """拓扑排序"""
        in_degree = defaultdict(int)
        for node_id in self.nodes:
            in_degree[node_id] = len(self.nodes[node_id].dependencies)
        
        queue = [n for n in self.nodes if in_degree[n] == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for dependent in self.nodes[node_id].dependents:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self.nodes):
            raise ValueError("DAG contains a cycle")
        
        return result
    
    def get_parallel_groups(self) -> List[List[str]]:
        """获取可并行执行的组"""
        groups = []
        remaining = set(self.nodes.keys())
        completed = set()
        
        while remaining:
            # 找到所有依赖已完成的节点
            ready = []
            for node_id in remaining:
                node = self.nodes[node_id]
                if node.dependencies.issubset(completed):
                    ready.append(node_id)
            
            if not ready:
                raise ValueError("DAG contains a cycle or invalid dependencies")
            
            groups.append(ready)
            completed.update(ready)
            remaining -= set(ready)
        
        return groups
    
    def validate(self) -> Tuple[bool, List[str]]:
        """验证 DAG"""
        errors = []
        
        # 检查环
        try:
            self.topological_sort()
        except ValueError as e:
            errors.append(str(e))
        
        # 检查缺失的依赖
        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    errors.append(f"Node {node_id} depends on non-existent node {dep}")
        
        # 检查孤立节点
        entry_points = set(self.get_entry_points())
        reachable = set()
        
        def dfs(node_id):
            reachable.add(node_id)
            for dep in self.nodes[node_id].dependents:
                if dep not in reachable:
                    dfs(dep)
        
        for entry in entry_points:
            dfs(entry)
        
        orphans = set(self.nodes.keys()) - reachable
        if orphans:
            errors.append(f"Orphan nodes (no path from entry): {orphans}")
        
        return len(errors) == 0, errors
    
    def get_dependencies(self, node_id: str) -> Set[str]:
        """获取节点的所有依赖（递归）"""
        all_deps = set()
        
        def collect(nid):
            if nid not in self.nodes:
                return
            for dep in self.nodes[nid].dependencies:
                if dep not in all_deps:
                    all_deps.add(dep)
                    collect(dep)
        
        collect(node_id)
        return all_deps
    
    def get_dependents(self, node_id: str) -> Set[str]:
        """获取节点的所有下游（递归）"""
        all_dependents = set()
        
        def collect(nid):
            if nid not in self.nodes:
                return
            for dep in self.nodes[nid].dependents:
                if dep not in all_dependents:
                    all_dependents.add(dep)
                    collect(dep)
        
        collect(node_id)
        return all_dependents


class DAGBuilder:
    """DAG 构建器"""
    
    def __init__(self):
        self._validators = []
    
    def build_from_steps(self, steps: List[Dict]) -> DAG:
        """从步骤列表构建 DAG"""
        dag = DAG()
        
        for step in steps:
            step_id = step.get("step_id")
            depends_on = step.get("depends_on", [])
            dag.add_node(step_id, step, depends_on)
        
        return dag
    
    def build_from_dependencies(
        self,
        dependencies: Dict[str, List[str]]
    ) -> DAG:
        """从依赖映射构建 DAG"""
        dag = DAG()
        
        for node_id, deps in dependencies.items():
            dag.add_node(node_id, {}, deps)
        
        return dag
    
    def merge_dags(self, dags: List[DAG]) -> DAG:
        """合并多个 DAG"""
        merged = DAG()
        
        for dag in dags:
            for node_id, node in dag.nodes.items():
                merged.add_node(node_id, node.data, list(node.dependencies))
        
        return merged
    
    def add_validator(self, validator):
        """添加验证器"""
        self._validators.append(validator)
    
    def validate(self, dag: DAG) -> Tuple[bool, List[str]]:
        """验证 DAG"""
        valid, errors = dag.validate()
        
        for validator in self._validators:
            try:
                validator_errors = validator(dag)
                errors.extend(validator_errors)
            except Exception as e:
                errors.append(f"Validator error: {e}")
        
        return len(errors) == 0, errors


from typing import Any
