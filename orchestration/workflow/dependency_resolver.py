"""
Dependency Resolver - 依赖解析器
解析 workflow 步骤依赖并生成执行顺序
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum

from orchestration.workflow.workflow_registry import WorkflowStep


class ResolutionStrategy(Enum):
    """解析策略"""
    TOPOLOGICAL = "topological"  # 拓扑排序
    PARALLEL = "parallel"  # 并行优先
    SEQUENTIAL = "sequential"  # 严格顺序


@dataclass
class ResolutionResult:
    """解析结果"""
    execution_order: List[str]
    parallel_groups: List[List[str]]
    has_cycle: bool
    cycle_path: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_order": self.execution_order,
            "parallel_groups": self.parallel_groups,
            "has_cycle": self.has_cycle,
            "cycle_path": self.cycle_path
        }


class DependencyResolver:
    """
    依赖解析器
    
    解析 workflow 步骤依赖并生成执行顺序：
    - 拓扑排序
    - 循环依赖检测
    - 并行组识别
    """
    
    def __init__(self, strategy: ResolutionStrategy = ResolutionStrategy.TOPOLOGICAL):
        self._strategy = strategy
    
    def resolve(self, steps: List[WorkflowStep]) -> List[str]:
        """
        解析依赖并生成执行顺序
        
        Args:
            steps: 步骤列表
            
        Returns:
            执行顺序（step_id 列表）
        """
        result = self.resolve_with_details(steps)
        
        if result.has_cycle:
            raise ValueError(f"Circular dependency detected: {result.cycle_path}")
        
        return result.execution_order
    
    def resolve_with_details(self, steps: List[WorkflowStep]) -> ResolutionResult:
        """
        解析依赖并返回详细信息
        
        Args:
            steps: 步骤列表
            
        Returns:
            解析结果
        """
        # 构建依赖图
        step_ids = {s.step_id for s in steps}
        graph: Dict[str, List[str]] = {}
        reverse_graph: Dict[str, List[str]] = {}
        
        for step in steps:
            graph[step.step_id] = step.depends_on
            reverse_graph[step.step_id] = []
        
        # 构建反向图
        for step in steps:
            for dep in step.depends_on:
                if dep in reverse_graph:
                    reverse_graph[dep].append(step.step_id)
        
        # 检测循环依赖
        cycle = self._detect_cycle(graph)
        if cycle:
            return ResolutionResult(
                execution_order=[],
                parallel_groups=[],
                has_cycle=True,
                cycle_path=cycle
            )
        
        # 拓扑排序
        execution_order = self._topological_sort(graph, step_ids)
        
        # 识别并行组
        parallel_groups = self._identify_parallel_groups(graph, reverse_graph, step_ids)
        
        return ResolutionResult(
            execution_order=execution_order,
            parallel_groups=parallel_groups,
            has_cycle=False
        )
    
    def _topological_sort(
        self,
        graph: Dict[str, List[str]],
        step_ids: Set[str]
    ) -> List[str]:
        """
        拓扑排序
        
        Args:
            graph: 依赖图
            step_ids: 步骤 ID 集合
            
        Returns:
            执行顺序
        """
        # 计算入度
        in_degree: Dict[str, int] = {sid: 0 for sid in step_ids}
        for sid, deps in graph.items():
            for dep in deps:
                if dep in step_ids:
                    in_degree[sid] += 1
        
        # 找出入度为 0 的节点
        queue = [sid for sid, deg in in_degree.items() if deg == 0]
        result = []
        
        while queue:
            # 按名称排序保证确定性
            queue.sort()
            node = queue.pop(0)
            result.append(node)
            
            # 更新入度
            for sid, deps in graph.items():
                if node in deps:
                    in_degree[sid] -= 1
                    if in_degree[sid] == 0:
                        queue.append(sid)
        
        return result
    
    def _detect_cycle(self, graph: Dict[str, List[str]]) -> Optional[List[str]]:
        """
        检测循环依赖
        
        Args:
            graph: 依赖图
            
        Returns:
            循环路径（如果存在）
        """
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for dep in graph.get(node, []):
                if dep not in visited:
                    result = dfs(dep)
                    if result:
                        return result
                elif dep in rec_stack:
                    # 找到循环
                    cycle_start = path.index(dep)
                    return path[cycle_start:] + [dep]
            
            path.pop()
            rec_stack.remove(node)
            return None
        
        for node in graph:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    return cycle
        
        return None
    
    def _identify_parallel_groups(
        self,
        graph: Dict[str, List[str]],
        reverse_graph: Dict[str, List[str]],
        step_ids: Set[str]
    ) -> List[List[str]]:
        """
        识别可并行执行的步骤组
        
        Args:
            graph: 依赖图
            reverse_graph: 反向依赖图
            step_ids: 步骤 ID 集合
            
        Returns:
            并行组列表
        """
        # 计算层级
        levels: Dict[str, int] = {}
        
        # 找出没有依赖的步骤（层级 0）
        for sid in step_ids:
            deps = graph.get(sid, [])
            if not deps or all(d not in step_ids for d in deps):
                levels[sid] = 0
        
        # BFS 计算层级
        changed = True
        while changed:
            changed = False
            for sid in step_ids:
                if sid in levels:
                    continue
                
                deps = graph.get(sid, [])
                if not deps:
                    levels[sid] = 0
                    changed = True
                elif all(d in levels for d in deps if d in step_ids):
                    max_dep_level = max(levels[d] for d in deps if d in step_ids)
                    levels[sid] = max_dep_level + 1
                    changed = True
        
        # 按层级分组
        max_level = max(levels.values()) if levels else 0
        groups: List[List[str]] = [[] for _ in range(max_level + 1)]
        
        for sid, level in levels.items():
            groups[level].append(sid)
        
        # 排序保证确定性
        for group in groups:
            group.sort()
        
        return groups
    
    def get_dependencies(self, step_id: str, steps: List[WorkflowStep]) -> List[str]:
        """
        获取步骤的直接依赖
        
        Args:
            step_id: 步骤 ID
            steps: 步骤列表
            
        Returns:
            依赖列表
        """
        for step in steps:
            if step.step_id == step_id:
                return step.depends_on
        return []
    
    def get_all_dependencies(self, step_id: str, steps: List[WorkflowStep]) -> Set[str]:
        """
        获取步骤的所有依赖（传递闭包）
        
        Args:
            step_id: 步骤 ID
            steps: 步骤列表
            
        Returns:
            所有依赖集合
        """
        step_map = {s.step_id: s for s in steps}
        all_deps = set()
        queue = [step_id]
        
        while queue:
            current = queue.pop(0)
            step = step_map.get(current)
            if step:
                for dep in step.depends_on:
                    if dep not in all_deps:
                        all_deps.add(dep)
                        queue.append(dep)
        
        return all_deps
    
    def get_dependents(self, step_id: str, steps: List[WorkflowStep]) -> List[str]:
        """
        获取依赖于指定步骤的步骤
        
        Args:
            step_id: 步骤 ID
            steps: 步骤列表
            
        Returns:
            依赖者列表
        """
        dependents = []
        for step in steps:
            if step_id in step.depends_on:
                dependents.append(step.step_id)
        return dependents
    
    def get_all_dependents(self, step_id: str, steps: List[WorkflowStep]) -> Set[str]:
        """
        获取所有依赖于指定步骤的步骤（传递闭包）
        
        Args:
            step_id: 步骤 ID
            steps: 步骤列表
            
        Returns:
            所有依赖者集合
        """
        step_map = {s.step_id: s for s in steps}
        all_dependents = set()
        queue = [step_id]
        
        while queue:
            current = queue.pop(0)
            for step in steps:
                if current in step.depends_on and step.step_id not in all_dependents:
                    all_dependents.add(step.step_id)
                    queue.append(step.step_id)
        
        return all_dependents
    
    def validate_dependencies(self, steps: List[WorkflowStep]) -> List[str]:
        """
        验证依赖关系
        
        Args:
            steps: 步骤列表
            
        Returns:
            错误列表
        """
        errors = []
        step_ids = {s.step_id for s in steps}
        
        for step in steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step '{step.step_id}' depends on non-existent step '{dep}'")
        
        # 检测循环
        graph = {s.step_id: s.depends_on for s in steps}
        cycle = self._detect_cycle(graph)
        if cycle:
            errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
        
        return errors


# 全局单例
_dependency_resolver = None

def get_dependency_resolver() -> DependencyResolver:
    """获取依赖解析器单例"""
    global _dependency_resolver
    if _dependency_resolver is None:
        _dependency_resolver = DependencyResolver()
    return _dependency_resolver
