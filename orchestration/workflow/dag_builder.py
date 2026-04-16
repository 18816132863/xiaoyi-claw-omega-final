"""DAG builder for workflow construction."""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class DAGNode:
    """Node in a DAG."""
    node_id: str
    data: Dict
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)


@dataclass
class DAG:
    """Directed Acyclic Graph."""
    nodes: Dict[str, DAGNode] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    
    def add_node(self, node_id: str, data: Dict = None, dependencies: List[str] = None):
        """Add a node to the DAG."""
        node = DAGNode(
            node_id=node_id,
            data=data or {},
            dependencies=set(dependencies or [])
        )
        self.nodes[node_id] = node
        
        # Update edges
        for dep in node.dependencies:
            self.edges.append((dep, node_id))
            if dep in self.nodes:
                self.nodes[dep].dependents.add(node_id)
    
    def get_entry_points(self) -> List[str]:
        """Get nodes with no dependencies."""
        return [n for n, node in self.nodes.items() if not node.dependencies]
    
    def get_exit_points(self) -> List[str]:
        """Get nodes with no dependents."""
        return [n for n, node in self.nodes.items() if not node.dependents]
    
    def topological_sort(self) -> List[str]:
        """Return nodes in topological order."""
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
        """Get groups of nodes that can run in parallel."""
        groups = []
        remaining = set(self.nodes.keys())
        completed = set()
        
        while remaining:
            # Find nodes whose dependencies are all completed
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
        """Validate DAG structure."""
        errors = []
        
        # Check for cycles
        try:
            self.topological_sort()
        except ValueError as e:
            errors.append(str(e))
        
        # Check for missing dependencies
        for node_id, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    errors.append(f"Node {node_id} depends on non-existent node {dep}")
        
        # Check for orphan nodes (no path to entry)
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


class DAGBuilder:
    """Builds DAGs from workflow specifications."""
    
    def __init__(self):
        self._validators = []
    
    def build_from_steps(self, steps: List[Dict]) -> DAG:
        """Build DAG from step specifications."""
        dag = DAG()
        
        for step in steps:
            step_id = step.get("step_id")
            depends_on = step.get("depends_on", [])
            dag.add_node(step_id, step, depends_on)
        
        return dag
    
    def build_from_dependencies(self, dependencies: Dict[str, List[str]]) -> DAG:
        """Build DAG from dependency map."""
        dag = DAG()
        
        for node_id, deps in dependencies.items():
            dag.add_node(node_id, {}, deps)
        
        return dag
    
    def merge_dags(self, dags: List[DAG]) -> DAG:
        """Merge multiple DAGs into one."""
        merged = DAG()
        
        for dag in dags:
            for node_id, node in dag.nodes.items():
                merged.add_node(node_id, node.data, list(node.dependencies))
        
        return merged
    
    def add_validator(self, validator: callable):
        """Add a DAG validator."""
        self._validators.append(validator)
    
    def validate(self, dag: DAG) -> Tuple[bool, List[str]]:
        """Validate DAG with all registered validators."""
        # Basic validation
        valid, errors = dag.validate()
        
        # Custom validators
        for validator in self._validators:
            try:
                validator_errors = validator(dag)
                errors.extend(validator_errors)
            except Exception as e:
                errors.append(f"Validator error: {e}")
        
        return len(errors) == 0, errors
