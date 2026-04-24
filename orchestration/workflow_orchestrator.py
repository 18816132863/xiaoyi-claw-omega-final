"""
Workflow Orchestrator - 工作流编排器
负责多步骤工作流的编排和执行
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import uuid
import logging
import asyncio

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """工作流状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepState(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep:
    """工作流步骤"""
    
    def __init__(
        self,
        step_id: str,
        name: str,
        action: Callable,
        dependencies: Optional[List[str]] = None,
        condition: Optional[Callable] = None,
        retry_policy: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ):
        self.step_id = step_id
        self.name = name
        self.action = action
        self.dependencies = dependencies or []
        self.condition = condition
        self.retry_policy = retry_policy or {"max_retries": 3, "delay": 1}
        self.timeout = timeout
        self.state = StepState.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "state": self.state.value,
            "dependencies": self.dependencies,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class Workflow:
    """工作流"""
    
    def __init__(
        self,
        workflow_id: str,
        name: str,
        steps: List[WorkflowStep],
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.steps = {step.step_id: step for step in steps}
        self.step_order = [step.step_id for step in steps]
        self.context = context or {}
        self.metadata = metadata or {}
        self.state = WorkflowState.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.current_step_id: Optional[str] = None
        self.checkpoints: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "state": self.state.value,
            "context": self.context,
            "metadata": self.metadata,
            "steps": [step.to_dict() for step in self.steps.values()],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "current_step_id": self.current_step_id,
            "checkpoints": self.checkpoints
        }
    
    def save_checkpoint(self, step_id: str) -> None:
        """保存检查点"""
        checkpoint = {
            "step_id": step_id,
            "timestamp": datetime.now().isoformat(),
            "context_snapshot": dict(self.context),
            "step_states": {sid: step.state.value for sid, step in self.steps.items()}
        }
        self.checkpoints.append(checkpoint)
    
    def restore_from_checkpoint(self, checkpoint_index: int) -> None:
        """从检查点恢复"""
        if 0 <= checkpoint_index < len(self.checkpoints):
            checkpoint = self.checkpoints[checkpoint_index]
            self.context = dict(checkpoint["context_snapshot"])
            for sid, state in checkpoint["step_states"].items():
                if sid in self.steps:
                    self.steps[sid].state = StepState(state)


class WorkflowOrchestrator:
    """
    工作流编排器
    管理多步骤工作流的执行
    """
    
    def __init__(self, storage=None, task_orchestrator=None):
        self.storage = storage
        self.task_orchestrator = task_orchestrator
        self._workflows: Dict[str, Workflow] = {}
        self._workflow_templates: Dict[str, Dict[str, Any]] = {}
    
    def register_template(self, name: str, template: Dict[str, Any]) -> None:
        """注册工作流模板"""
        self._workflow_templates[name] = template
        logger.info(f"Registered workflow template: {name}")
    
    async def create_workflow(
        self,
        name: str,
        steps: List[WorkflowStep],
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None
    ) -> Workflow:
        """
        创建工作流
        
        Args:
            name: 工作流名称
            steps: 步骤列表
            context: 上下文数据
            metadata: 元数据
            template_name: 模板名称（如果使用模板）
            
        Returns:
            创建的工作流对象
        """
        workflow_id = str(uuid.uuid4())
        
        # 如果指定了模板，合并模板配置
        if template_name and template_name in self._workflow_templates:
            template = self._workflow_templates[template_name]
            metadata = {**template.get("metadata", {}), **(metadata or {})}
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            steps=steps,
            context=context,
            metadata=metadata
        )
        
        self._workflows[workflow_id] = workflow
        
        if self.storage:
            await self.storage.save_workflow(workflow)
        
        logger.info(f"Created workflow: {workflow_id}")
        return workflow
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """获取工作流"""
        if workflow_id in self._workflows:
            return self._workflows[workflow_id]
        
        if self.storage:
            workflow = await self.storage.get_workflow(workflow_id)
            if workflow:
                self._workflows[workflow_id] = workflow
            return workflow
        
        return None
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """执行工作流"""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        if workflow.state == WorkflowState.RUNNING:
            raise ValueError(f"Workflow already running: {workflow_id}")
        
        workflow.state = WorkflowState.RUNNING
        workflow.started_at = datetime.now()
        workflow.updated_at = datetime.now()
        
        logger.info(f"Starting workflow: {workflow_id}")
        
        try:
            # 按顺序执行步骤
            for step_id in workflow.step_order:
                step = workflow.steps[step_id]
                workflow.current_step_id = step_id
                
                # 检查依赖
                if not await self._check_dependencies(workflow, step):
                    step.state = StepState.SKIPPED
                    logger.info(f"Skipped step {step_id} due to unmet dependencies")
                    continue
                
                # 检查条件
                if step.condition and not step.condition(workflow.context):
                    step.state = StepState.SKIPPED
                    logger.info(f"Skipped step {step_id} due to condition")
                    continue
                
                # 执行步骤
                await self._execute_step(workflow, step)
                
                # 保存检查点
                workflow.save_checkpoint(step_id)
                
                if workflow.state == WorkflowState.PAUSED:
                    logger.info(f"Workflow paused at step {step_id}")
                    return {"status": "paused", "step_id": step_id}
            
            # 完成
            workflow.state = WorkflowState.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.updated_at = datetime.now()
            
            if self.storage:
                await self.storage.save_workflow(workflow)
            
            logger.info(f"Workflow completed: {workflow_id}")
            
            return {
                "status": "completed",
                "workflow_id": workflow_id,
                "context": workflow.context
            }
            
        except Exception as e:
            workflow.state = WorkflowState.FAILED
            workflow.updated_at = datetime.now()
            
            if self.storage:
                await self.storage.save_workflow(workflow)
            
            logger.error(f"Workflow failed: {workflow_id} - {e}")
            raise
    
    async def _check_dependencies(self, workflow: Workflow, step: WorkflowStep) -> bool:
        """检查步骤依赖"""
        for dep_id in step.dependencies:
            if dep_id not in workflow.steps:
                return False
            dep_step = workflow.steps[dep_id]
            if dep_step.state != StepState.COMPLETED:
                return False
        return True
    
    async def _execute_step(self, workflow: Workflow, step: WorkflowStep) -> None:
        """执行单个步骤"""
        step.state = StepState.RUNNING
        step.started_at = datetime.now()
        
        retry_count = 0
        max_retries = step.retry_policy.get("max_retries", 3)
        delay = step.retry_policy.get("delay", 1)
        
        while retry_count <= max_retries:
            try:
                result = await step.action(workflow.context)
                step.result = result
                step.state = StepState.COMPLETED
                step.completed_at = datetime.now()
                
                # 更新上下文
                workflow.context[f"{step.step_id}_result"] = result
                workflow.updated_at = datetime.now()
                
                logger.info(f"Step completed: {step.step_id}")
                return
                
            except Exception as e:
                retry_count += 1
                step.error = str(e)
                
                if retry_count <= max_retries:
                    logger.warning(f"Step {step.step_id} failed, retrying ({retry_count}/{max_retries})")
                    await asyncio.sleep(delay)
                else:
                    step.state = StepState.FAILED
                    logger.error(f"Step failed permanently: {step.step_id}")
                    raise
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """暂停工作流"""
        workflow = await self.get_workflow(workflow_id)
        if not workflow or workflow.state != WorkflowState.RUNNING:
            return False
        
        workflow.state = WorkflowState.PAUSED
        workflow.updated_at = datetime.now()
        
        if self.storage:
            await self.storage.save_workflow(workflow)
        
        logger.info(f"Workflow paused: {workflow_id}")
        return True
    
    async def resume_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """恢复工作流"""
        workflow = await self.get_workflow(workflow_id)
        if not workflow or workflow.state != WorkflowState.PAUSED:
            raise ValueError(f"Cannot resume workflow: {workflow_id}")
        
        workflow.state = WorkflowState.RUNNING
        workflow.updated_at = datetime.now()
        
        return await self.execute_workflow(workflow_id)
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """取消工作流"""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        if workflow.state in [WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED]:
            return False
        
        workflow.state = WorkflowState.CANCELLED
        workflow.updated_at = datetime.now()
        
        if self.storage:
            await self.storage.save_workflow(workflow)
        
        logger.info(f"Workflow cancelled: {workflow_id}")
        return True
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流状态"""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            return None
        
        completed_steps = sum(1 for s in workflow.steps.values() if s.state == StepState.COMPLETED)
        total_steps = len(workflow.steps)
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "state": workflow.state.value,
            "progress": {
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0
            },
            "current_step": workflow.current_step_id,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat()
        }
