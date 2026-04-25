#!/usr/bin/env python3
"""
工作流引擎 - V1.0.0

管理和执行复杂的工作流任务。
"""

import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class WorkflowStatus(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class EngineStepStatus(Enum):
    """工作流引擎步骤状态（与 domain.tasks.specs.StepStatus 不同）"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """工作流步骤"""
    id: str
    name: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: EngineStepStatus = EngineStepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Workflow:
    """工作流定义"""
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.action_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认处理器"""
        self.action_handlers["skill"] = self._execute_skill
        self.action_handlers["tool"] = self._execute_tool
        self.action_handlers["condition"] = self._evaluate_condition
        self.action_handlers["parallel"] = self._execute_parallel
    
    def _execute_skill(self, params: Dict, context: Dict) -> Any:
        """执行技能"""
        from execution.skill_gateway import SkillGateway
        gateway = SkillGateway()
        skill_name = params.get("skill")
        skill_params = params.get("params", {})
        result = gateway.execute(skill_name, skill_params)
        return result.data if result.success else None
    
    def _execute_tool(self, params: Dict, context: Dict) -> Any:
        """执行工具"""
        # 工具执行逻辑
        return {"status": "executed", "params": params}
    
    def _evaluate_condition(self, params: Dict, context: Dict) -> bool:
        """评估条件"""
        condition = params.get("condition", "true")
        # 简单条件评估
        return eval(condition, {"context": context})
    
    def _execute_parallel(self, params: Dict, context: Dict) -> List[Any]:
        """并行执行"""
        import concurrent.futures
        steps = params.get("steps", [])
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for step in steps:
                future = executor.submit(
                    self._execute_step,
                    WorkflowStep(**step),
                    context
                )
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        return results
    
    def register_handler(self, action: str, handler: Callable):
        """注册动作处理器"""
        self.action_handlers[action] = handler
    
    def create_workflow(self, definition: Dict) -> Workflow:
        """创建工作流"""
        steps = [WorkflowStep(**s) for s in definition.get("steps", [])]
        workflow = Workflow(
            id=definition.get("id"),
            name=definition.get("name"),
            description=definition.get("description", ""),
            steps=steps
        )
        self.workflows[workflow.id] = workflow
        return workflow
    
    def _get_ready_steps(self, workflow: Workflow) -> List[WorkflowStep]:
        """获取可执行的步骤"""
        ready = []
        completed_ids = {s.id for s in workflow.steps if s.status == EngineStepStatus.COMPLETED}
        
        for step in workflow.steps:
            if step.status != EngineStepStatus.PENDING:
                continue
            
            # 检查依赖是否完成
            if all(dep in completed_ids for dep in step.dependencies):
                ready.append(step)
        
        return ready
    
    def _execute_step(self, step: WorkflowStep, context: Dict) -> Any:
        """执行步骤"""
        handler = self.action_handlers.get(step.action)
        if not handler:
            raise ValueError(f"未知的动作类型: {step.action}")
        
        return handler(step.params, context)
    
    def run_workflow(self, workflow_id: str) -> Dict:
        """运行工作流"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"success": False, "error": "工作流不存在"}
        
        workflow.status = WorkflowStatus.RUNNING
        
        try:
            while True:
                ready_steps = self._get_ready_steps(workflow)
                if not ready_steps:
                    break
                
                for step in ready_steps:
                    workflow.current_step = step.id
                    step.status = EngineStepStatus.RUNNING
                    
                    try:
                        result = self._execute_step(step, workflow.context)
                        step.result = result
                        step.status = EngineStepStatus.COMPLETED
                        
                        # 更新上下文
                        workflow.context[step.id] = result
                        
                    except Exception as e:
                        step.error = str(e)
                        step.status = EngineStepStatus.FAILED
                        workflow.status = WorkflowStatus.FAILED
                        return {"success": False, "error": str(e), "step": step.id}
            
            workflow.status = WorkflowStatus.COMPLETED
            return {"success": True, "context": workflow.context}
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            return {"success": False, "error": str(e)}
    
    def pause_workflow(self, workflow_id: str):
        """暂停工作流"""
        workflow = self.workflows.get(workflow_id)
        if workflow:
            workflow.status = WorkflowStatus.PAUSED
    
    def resume_workflow(self, workflow_id: str):
        """恢复工作流"""
        workflow = self.workflows.get(workflow_id)
        if workflow and workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.RUNNING
            return self.run_workflow(workflow_id)


# 全局工作流引擎
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    """获取全局工作流引擎"""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
