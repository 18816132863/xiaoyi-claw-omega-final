"""Task planner - decomposes tasks into executable steps."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import json


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    MULTI_STAGE = "multi_stage"


@dataclass
class PlanStep:
    """Single step in execution plan."""
    step_id: str
    name: str
    action: str
    depends_on: List[str] = field(default_factory=list)
    input_contract: Dict = field(default_factory=dict)
    output_contract: Dict = field(default_factory=dict)
    timeout_seconds: int = 300
    retry_policy: Dict = field(default_factory=lambda: {"max_retries": 3})
    fallback: Optional[str] = None
    can_run_parallel: bool = False
    criticality: str = "medium"


@dataclass
class ExecutionPlan:
    """Complete execution plan for a task."""
    plan_id: str
    task_id: str
    task_description: str
    complexity: TaskComplexity
    steps: List[PlanStep]
    created_at: datetime = field(default_factory=datetime.now)
    estimated_duration_seconds: int = 0
    required_skills: List[str] = field(default_factory=list)
    required_permissions: List[str] = field(default_factory=list)
    
    def to_workflow_spec(self) -> Dict:
        """Convert to workflow specification."""
        return {
            "workflow_id": self.plan_id,
            "name": f"Plan for {self.task_id}",
            "description": self.task_description,
            "version": "1.0",
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "action": step.action,
                    "depends_on": step.depends_on,
                    "input_contract": step.input_contract,
                    "output_contract": step.output_contract,
                    "timeout_seconds": step.timeout_seconds,
                    "retry_policy": step.retry_policy,
                    "fallback": step.fallback,
                    "can_run_parallel": step.can_run_parallel,
                    "criticality": step.criticality
                }
                for step in self.steps
            ],
            "metadata": {
                "task_id": self.task_id,
                "complexity": self.complexity.value,
                "estimated_duration": self.estimated_duration_seconds,
                "required_skills": self.required_skills,
                "required_permissions": self.required_permissions
            }
        }


class TaskPlanner:
    """
    Decomposes tasks into executable plans.
    
    Uses intent analysis and skill matching to create optimal execution plans.
    """
    
    def __init__(self, skill_registry=None, context_builder=None):
        self.skill_registry = skill_registry
        self.context_builder = context_builder
        self._plan_counter = 0
    
    def plan(self, task_id: str, task_description: str, context: Dict = None) -> ExecutionPlan:
        """
        Create execution plan for a task.
        
        Args:
            task_id: Unique task identifier
            task_description: Natural language task description
            context: Additional context for planning
        
        Returns:
            ExecutionPlan ready for execution
        """
        # 1. Analyze task complexity
        complexity = self._analyze_complexity(task_description, context)
        
        # 2. Identify required skills
        required_skills = self._identify_skills(task_description, context)
        
        # 3. Decompose into steps
        steps = self._decompose(task_description, complexity, required_skills, context)
        
        # 4. Estimate duration
        estimated_duration = self._estimate_duration(steps)
        
        # 5. Identify required permissions
        required_permissions = self._identify_permissions(steps)
        
        # Generate plan ID
        self._plan_counter += 1
        plan_id = f"plan_{task_id}_{self._plan_counter}"
        
        return ExecutionPlan(
            plan_id=plan_id,
            task_id=task_id,
            task_description=task_description,
            complexity=complexity,
            steps=steps,
            estimated_duration_seconds=estimated_duration,
            required_skills=required_skills,
            required_permissions=required_permissions
        )
    
    def _analyze_complexity(self, description: str, context: Dict) -> TaskComplexity:
        """Analyze task complexity."""
        desc_lower = description.lower()
        
        # Multi-stage indicators
        multi_stage_keywords = ["然后", "接着", "之后", "then", "after", "finally", "最后"]
        if any(kw in desc_lower for kw in multi_stage_keywords):
            return TaskComplexity.MULTI_STAGE
        
        # Complex indicators
        complex_keywords = ["架构", "设计", "实现", "重构", "architecture", "design", "implement", "refactor"]
        if any(kw in desc_lower for kw in complex_keywords):
            return TaskComplexity.COMPLEX
        
        # Moderate indicators
        moderate_keywords = ["修改", "更新", "创建", "modify", "update", "create", "build"]
        if any(kw in desc_lower for kw in moderate_keywords):
            return TaskComplexity.MODERATE
        
        return TaskComplexity.SIMPLE
    
    def _identify_skills(self, description: str, context: Dict) -> List[str]:
        """Identify skills needed for the task."""
        if not self.skill_registry:
            return []
        
        # TODO: Use skill registry to match skills
        skills = []
        desc_lower = description.lower()
        
        # Simple keyword matching for now
        skill_keywords = {
            "git": ["git", "commit", "push", "pull"],
            "docker": ["docker", "container", "image"],
            "file": ["file", "read", "write", "edit"],
            "web": ["web", "http", "fetch", "browser"],
            "memory": ["memory", "remember", "recall", "store"]
        }
        
        for skill, keywords in skill_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                skills.append(skill)
        
        return skills
    
    def _decompose(
        self,
        description: str,
        complexity: TaskComplexity,
        skills: List[str],
        context: Dict
    ) -> List[PlanStep]:
        """Decompose task into steps."""
        steps = []
        
        if complexity == TaskComplexity.SIMPLE:
            # Single step
            steps.append(PlanStep(
                step_id="step_1",
                name="Execute task",
                action=description,
                criticality="medium"
            ))
        
        elif complexity == TaskComplexity.MODERATE:
            # Prepare -> Execute -> Verify
            steps.append(PlanStep(
                step_id="prepare",
                name="Prepare context",
                action="Prepare execution context and gather required resources",
                criticality="medium"
            ))
            steps.append(PlanStep(
                step_id="execute",
                name="Execute main task",
                action=description,
                depends_on=["prepare"],
                criticality="high"
            ))
            steps.append(PlanStep(
                step_id="verify",
                name="Verify results",
                action="Verify task completion and validate results",
                depends_on=["execute"],
                criticality="medium"
            ))
        
        elif complexity == TaskComplexity.COMPLEX:
            # Analyze -> Plan -> Execute -> Verify -> Report
            steps.append(PlanStep(
                step_id="analyze",
                name="Analyze requirements",
                action="Analyze task requirements and constraints",
                criticality="high"
            ))
            steps.append(PlanStep(
                step_id="plan",
                name="Create detailed plan",
                action="Create detailed execution plan",
                depends_on=["analyze"],
                criticality="high"
            ))
            steps.append(PlanStep(
                step_id="execute",
                name="Execute plan",
                action=description,
                depends_on=["plan"],
                criticality="critical"
            ))
            steps.append(PlanStep(
                step_id="verify",
                name="Verify and validate",
                action="Verify execution results and validate against requirements",
                depends_on=["execute"],
                criticality="high"
            ))
            steps.append(PlanStep(
                step_id="report",
                name="Generate report",
                action="Generate execution report and update records",
                depends_on=["verify"],
                criticality="medium"
            ))
        
        else:  # MULTI_STAGE
            # Parse stages from description
            # TODO: Implement proper stage parsing
            stages = self._parse_stages(description)
            prev_step = None
            for i, stage in enumerate(stages):
                step_id = f"stage_{i+1}"
                depends_on = [prev_step] if prev_step else []
                steps.append(PlanStep(
                    step_id=step_id,
                    name=f"Stage {i+1}: {stage[:30]}...",
                    action=stage,
                    depends_on=depends_on,
                    criticality="high" if i == len(stages) - 1 else "medium"
                ))
                prev_step = step_id
        
        return steps
    
    def _parse_stages(self, description: str) -> List[str]:
        """Parse multi-stage description into stages."""
        # Simple split by common delimiters
        import re
        delimiters = ["然后", "接着", "之后", "then", "after that", "finally", "最后", "，", ","]
        pattern = "|".join(delimiters)
        parts = re.split(pattern, description)
        return [p.strip() for p in parts if p.strip()]
    
    def _estimate_duration(self, steps: List[PlanStep]) -> int:
        """Estimate total duration in seconds."""
        base_duration = 30  # Base time per step
        complexity_multiplier = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0,
            "critical": 3.0
        }
        
        total = 0
        for step in steps:
            multiplier = complexity_multiplier.get(step.criticality, 1.0)
            total += int(base_duration * multiplier)
        
        return total
    
    def _identify_permissions(self, steps: List[PlanStep]) -> List[str]:
        """Identify required permissions."""
        permissions = set()
        
        for step in steps:
            action_lower = step.action.lower()
            
            if any(kw in action_lower for kw in ["write", "create", "delete", "修改", "创建", "删除"]):
                permissions.add("write")
            if any(kw in action_lower for kw in ["execute", "run", "执行", "运行"]):
                permissions.add("execute")
            if any(kw in action_lower for kw in ["network", "http", "web", "网络"]):
                permissions.add("network")
        
        return list(permissions)
