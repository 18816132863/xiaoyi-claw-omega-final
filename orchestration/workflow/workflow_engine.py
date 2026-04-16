"""Workflow engine - executes DAG-based workflows with recovery chain."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class StepResult:
    """Result of a step execution."""
    step_id: str
    status: StepStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    output: Dict = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
    duration_ms: int = 0
    fallback_used: bool = False
    rollback_used: bool = False


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    final_output: Dict = field(default_factory=dict)
    error: Optional[str] = None
    total_duration_ms: int = 0
    # 恢复链字段
    failed_step_id: Optional[str] = None
    reason: Optional[str] = None
    total_retry_count: int = 0
    fallback_used: bool = False
    rollback_used: bool = False
    checkpoint_id: Optional[str] = None


class WorkflowEngine:
    """
    Executes DAG-based workflows with support for:
    - Parallel execution
    - Retry policies
    - Fallback actions
    - Checkpointing
    - Rollback
    - State management
    """
    
    def __init__(
        self,
        skill_router=None,
        state_store=None,
        checkpoint_store=None,
        fallback_policy=None,
        rollback_manager=None,
        max_parallel_steps: int = 4
    ):
        self.skill_router = skill_router
        self.state_store = state_store
        self.checkpoint_store = checkpoint_store
        self.fallback_policy = fallback_policy
        self.rollback_manager = rollback_manager
        self.max_parallel_steps = max_parallel_steps
        self._action_handlers: Dict[str, Callable] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_parallel_steps)
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """Register a handler for a specific action type."""
        self._action_handlers[action_type] = handler
    
    def run_workflow(
        self,
        workflow_spec: Dict,
        profile: str = "default",
        context_bundle: Dict = None,
        resume_from_checkpoint: str = None
    ) -> WorkflowResult:
        """
        Execute a workflow.
        
        Args:
            workflow_spec: Workflow specification
            profile: Execution profile
            context_bundle: Context for execution
            resume_from_checkpoint: Checkpoint ID to resume from
        
        Returns:
            WorkflowResult with execution details
        """
        workflow_id = workflow_spec.get("workflow_id", "unknown")
        steps = workflow_spec.get("steps", [])
        
        # Initialize result
        result = WorkflowResult(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now()
        )
        
        # Build DAG
        dag = self._build_dag(steps)
        
        # Load checkpoint if resuming
        completed_steps = []
        pending_steps = [s.get("step_id") for s in steps]
        
        if resume_from_checkpoint and self.checkpoint_store:
            checkpoint = self.checkpoint_store.load(resume_from_checkpoint)
            if checkpoint:
                result.checkpoint_id = resume_from_checkpoint
                # 恢复状态
                for step_id in checkpoint.completed_steps:
                    step_result = StepResult(
                        step_id=step_id,
                        status=StepStatus.COMPLETED,
                        started_at=datetime.now(),
                        completed_at=datetime.now()
                    )
                    result.step_results[step_id] = step_result
                    completed_steps.append(step_id)
                pending_steps = checkpoint.pending_steps
        
        try:
            # Execute DAG
            self._execute_dag(dag, result, context_bundle, completed_steps)
            
            # Mark completed
            result.status = WorkflowStatus.COMPLETED
            result.completed_at = datetime.now()
            
            # Save final checkpoint
            if self.checkpoint_store:
                cp = self.checkpoint_store.save(
                    workflow_id=workflow_id,
                    step_id="_completed",
                    state={"status": "completed"},
                    completed_steps=list(result.step_results.keys()),
                    pending_steps=[]
                )
                result.checkpoint_id = cp.checkpoint_id
            
        except Exception as e:
            result.status = WorkflowStatus.FAILED
            result.error = str(e)
            result.reason = str(e)
            result.completed_at = datetime.now()
        
        # Calculate duration
        if result.completed_at:
            result.total_duration_ms = int(
                (result.completed_at - result.started_at).total_seconds() * 1000
            )
        
        # 汇总重试次数
        for step_result in result.step_results.values():
            result.total_retry_count += step_result.retry_count
            if step_result.fallback_used:
                result.fallback_used = True
            if step_result.rollback_used:
                result.rollback_used = True
        
        return result
    
    def _build_dag(self, steps: List[Dict]) -> Dict:
        """Build DAG structure from steps."""
        dag = {
            "nodes": {},
            "edges": [],
            "entry_points": [],
            "exit_points": []
        }
        
        for step in steps:
            step_id = step.get("step_id")
            dag["nodes"][step_id] = {
                "step": step,
                "dependencies": step.get("depends_on", []),
                "dependents": []
            }
        
        # Build edges and find entry/exit points
        for step_id, node in dag["nodes"].items():
            deps = node["dependencies"]
            
            if not deps:
                dag["entry_points"].append(step_id)
            
            for dep in deps:
                if dep in dag["nodes"]:
                    dag["nodes"][dep]["dependents"].append(step_id)
                    dag["edges"].append((dep, step_id))
        
        # Find exit points (no dependents)
        for step_id, node in dag["nodes"].items():
            if not node["dependents"]:
                dag["exit_points"].append(step_id)
        
        return dag
    
    def _execute_dag(
        self,
        dag: Dict,
        result: WorkflowResult,
        context: Dict,
        completed: List[str] = None
    ):
        """Execute DAG with proper dependency handling."""
        completed = set(completed or [])
        pending = set(dag["nodes"].keys()) - completed
        running = set()
        
        while pending or running:
            # Find ready steps (all dependencies completed)
            ready = []
            for step_id in pending:
                node = dag["nodes"][step_id]
                deps = node["dependencies"]
                
                if all(d in completed for d in deps):
                    ready.append(step_id)
            
            if not ready and not running:
                # Deadlock or all done
                break
            
            # Start ready steps (up to max parallel)
            available_slots = self.max_parallel_steps - len(running)
            to_start = ready[:available_slots]
            
            for step_id in to_start:
                pending.remove(step_id)
                running.add(step_id)
                
                # Save checkpoint before step
                if self.checkpoint_store:
                    self.checkpoint_store.save(
                        workflow_id=result.workflow_id,
                        step_id=step_id,
                        state={"phase": "before"},
                        completed_steps=list(completed),
                        pending_steps=list(pending)
                    )
                
                # Execute step
                step_result = self._execute_step(
                    dag["nodes"][step_id]["step"],
                    context,
                    result.step_results
                )
                result.step_results[step_id] = step_result
                
                running.remove(step_id)
                
                if step_result.status == StepStatus.COMPLETED:
                    completed.add(step_id)
                    
                    # Save checkpoint after step
                    if self.checkpoint_store:
                        self.checkpoint_store.save(
                            workflow_id=result.workflow_id,
                            step_id=step_id,
                            state={"phase": "after", "output": step_result.output},
                            completed_steps=list(completed),
                            pending_steps=list(pending)
                        )
                        
                elif step_result.status == StepStatus.FAILED:
                    result.failed_step_id = step_id
                    result.reason = step_result.error
                    
                    # Handle failure with recovery chain
                    if not self._handle_step_failure(step_id, dag, result):
                        raise RuntimeError(f"Step {step_id} failed: {step_result.error}")
                    completed.add(step_id)  # Fallback succeeded
    
    def _execute_step(
        self,
        step: Dict,
        context: Dict,
        previous_results: Dict[str, StepResult]
    ) -> StepResult:
        """Execute a single step."""
        step_id = step.get("step_id")
        action = step.get("action")
        timeout = step.get("timeout_seconds", 300)
        retry_policy = step.get("retry_policy", {})
        
        result = StepResult(
            step_id=step_id,
            status=StepStatus.RUNNING,
            started_at=datetime.now()
        )
        
        # Build step input from dependencies
        step_input = self._build_step_input(step, previous_results, context)
        
        # Execute with retry
        max_retries = retry_policy.get("max_retries", 3)
        
        for attempt in range(max_retries + 1):
            try:
                # Execute action
                output = self._execute_action(action, step_input, timeout)
                
                result.status = StepStatus.COMPLETED
                result.output = output
                break
                
            except Exception as e:
                result.error = str(e)
                result.retry_count = attempt
                
                if attempt < max_retries:
                    result.status = StepStatus.RETRYING
                else:
                    # 使用 FallbackPolicy 决定下一步
                    if self.fallback_policy:
                        from orchestration.execution_control.fallback_policy import FallbackAction
                        
                        decision = self.fallback_policy.decide(
                            step_id=step_id,
                            error=str(e),
                            retry_count=attempt,
                            context=context
                        )
                        
                        if decision.action == FallbackAction.FALLBACK:
                            # 尝试回退技能
                            if decision.fallback_skill_id:
                                try:
                                    output = self._execute_action(
                                        decision.fallback_skill_id,
                                        step_input,
                                        timeout
                                    )
                                    result.status = StepStatus.COMPLETED
                                    result.output = output
                                    result.fallback_used = True
                                except Exception as fe:
                                    result.status = StepStatus.FAILED
                                    result.error = f"Primary: {e}, Fallback: {fe}"
                            else:
                                result.status = StepStatus.FAILED
                                
                        elif decision.action == FallbackAction.SKIP:
                            result.status = StepStatus.SKIPPED
                            
                        elif decision.action == FallbackAction.ABORT:
                            result.status = StepStatus.FAILED
                    else:
                        # 没有 FallbackPolicy，尝试 step 定义的 fallback
                        fallback = step.get("fallback")
                        if fallback:
                            try:
                                output = self._execute_action(fallback, step_input, timeout)
                                result.status = StepStatus.COMPLETED
                                result.output = output
                                result.fallback_used = True
                            except Exception as fe:
                                result.status = StepStatus.FAILED
                                result.error = f"Primary: {e}, Fallback: {fe}"
                        else:
                            result.status = StepStatus.FAILED
        
        result.completed_at = datetime.now()
        result.duration_ms = int(
            (result.completed_at - result.started_at).total_seconds() * 1000
        )
        
        return result
    
    def _build_step_input(
        self,
        step: Dict,
        previous_results: Dict[str, StepResult],
        context: Dict
    ) -> Dict:
        """Build input for a step from dependencies and context."""
        step_input = {
            "context": context,
            "dependencies": {}
        }
        
        for dep_id in step.get("depends_on", []):
            if dep_id in previous_results:
                step_input["dependencies"][dep_id] = previous_results[dep_id].output
        
        return step_input
    
    def _execute_action(self, action: str, step_input: Dict, timeout: int) -> Dict:
        """Execute an action."""
        # 1. 检查注册的处理器
        for action_type, handler in self._action_handlers.items():
            if action.startswith(action_type) or action == action_type:
                return handler(action, step_input)
        
        # 2. 使用技能路由器
        if self.skill_router:
            try:
                return self.skill_router.execute(action, step_input)
            except Exception as e:
                # 技能路由失败，继续检查是否允许默认行为
                pass
        
        # 3. 只允许显式测试动作（test/noop/mock）走默认成功
        if action.lower() in ["test", "noop", "mock"]:
            return {
                "executed": True,
                "action": action,
                "input": step_input,
                "message": f"Action '{action}' executed (test mode)"
            }
        
        # 4. 非测试动作且没有处理器：显式失败
        raise RuntimeError(
            f"No handler for action '{action}'. "
            f"Register a handler with register_action_handler() or provide a skill_router."
        )
    
    def _handle_step_failure(self, step_id: str, dag: Dict, result: WorkflowResult) -> bool:
        """Handle step failure with recovery chain. Returns True if recovered."""
        step_result = result.step_results[step_id]
        step = dag["nodes"][step_id]["step"]
        
        # Check if step has fallback
        if step_result.fallback_used:
            return True  # Already tried fallback
        
        # 尝试 rollback
        if self.rollback_manager and step.get("rollback", False):
            # 创建回滚点
            point = self.rollback_manager.create_point(
                step_id=step_id,
                state={"step_results": {k: v.__dict__ for k, v in result.step_results.items()}}
            )
            
            # 执行回滚
            rollback_result = self.rollback_manager.rollback(point.point_id)
            if rollback_result.success:
                step_result.rollback_used = True
                result.rollback_used = True
                # 恢复状态
                for k, v in rollback_result.restored_state.get("step_results", {}).items():
                    if k in result.step_results:
                        result.step_results[k].status = StepStatus.COMPLETED
                return True
        
        # Check if step is critical
        if step.get("criticality") == "critical":
            return False  # Cannot skip critical steps
        
        # Skip non-critical failed steps
        step_result.status = StepStatus.SKIPPED
        return True


def run_workflow(
    workflow_spec: Dict,
    profile: str = "default",
    context_bundle: Dict = None
) -> WorkflowResult:
    """
    Convenience function to run a workflow.
    
    Usage:
        result = run_workflow(
            workflow_spec={
                "workflow_id": "my_workflow",
                "steps": [
                    {"step_id": "step1", "action": "do_something"},
                    {"step_id": "step2", "action": "do_more", "depends_on": ["step1"]}
                ]
            },
            profile="developer"
        )
    """
    engine = WorkflowEngine()
    return engine.run_workflow(workflow_spec, profile, context_bundle)
