"""
Workflow Engine - 正式任务编排内核主链入口
Phase3 第二组核心模块 + Group5 事件接入
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import asyncio
import json

from orchestration.workflow.workflow_registry import (
    WorkflowTemplate,
    WorkflowStep,
    get_workflow_registry
)
from orchestration.workflow.state_machine import (
    WorkflowStateMachine,
    WorkflowState,
    StepState,
    get_workflow_state_machine
)
from orchestration.workflow.dependency_resolver import (
    DependencyResolver,
    get_dependency_resolver
)
from orchestration.validators.workflow_contract_validator import (
    get_workflow_contract_validator
)
from orchestration.state.workflow_instance_store import (
    get_workflow_instance_store,
    InstanceStatus
)
from orchestration.state.workflow_event_store import (
    get_workflow_event_store,
    WorkflowEventType
)
from orchestration.state.recovery_store import (
    get_recovery_store,
    ErrorType,
    RecoveryAction
)
from orchestration.state.checkpoint_store import CheckpointStore
from orchestration.execution_control.fallback_policy import FallbackPolicy, FallbackAction
from orchestration.execution_control.rollback_manager import RollbackManager

# ========== Group5 事件系统接入 ==========
try:
    from core.events.event_persistence import get_event_persistence
    _event_persistence = None
except ImportError:
    _event_persistence = None


def _emit_event(event_type: str, payload: Dict[str, Any], **kwargs):
    """发送事件到正式事件系统"""
    global _event_persistence
    if _event_persistence is None:
        try:
            _event_persistence = get_event_persistence()
        except Exception:
            return
    
    try:
        _event_persistence.append(event_type, payload, validate=False, **kwargs)
    except Exception:
        pass


# ========== 兼容性别名 ==========
# WorkflowStatus 是旧接口名称，保持向后兼容
WorkflowStatus = WorkflowState


@dataclass
class StepResult:
    """步骤执行结果"""
    step_id: str
    status: StepState
    started_at: str
    completed_at: Optional[str] = None
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    retry_count: int = 0
    duration_ms: int = 0
    fallback_used: bool = False
    rollback_used: bool = False
    checkpoint_id: Optional[str] = None
    rollback_point_id: Optional[str] = None
    fallback_decision: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "output": self.output,
            "error": self.error,
            "retry_count": self.retry_count,
            "duration_ms": self.duration_ms,
            "fallback_used": self.fallback_used,
            "rollback_used": self.rollback_used,
            "checkpoint_id": self.checkpoint_id,
            "rollback_point_id": self.rollback_point_id,
            "fallback_decision": self.fallback_decision
        }


@dataclass
class WorkflowResult:
    """Workflow 执行结果"""
    instance_id: str
    workflow_id: str
    version: str
    status: WorkflowState
    started_at: str
    completed_at: Optional[str] = None
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    final_output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    total_duration_ms: int = 0
    failed_step_id: Optional[str] = None
    total_retry_count: int = 0
    fallback_used: bool = False
    rollback_used: bool = False
    checkpoint_id: Optional[str] = None
    control_decision_id: Optional[str] = None
    rollback_to_step: Optional[str] = None
    rollback_point_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "workflow_id": self.workflow_id,
            "version": self.version,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "step_results": {k: v.to_dict() for k, v in self.step_results.items()},
            "final_output": self.final_output,
            "error": self.error,
            "total_duration_ms": self.total_duration_ms,
            "failed_step_id": self.failed_step_id,
            "total_retry_count": self.total_retry_count,
            "fallback_used": self.fallback_used,
            "rollback_used": self.rollback_used,
            "checkpoint_id": self.checkpoint_id,
            "control_decision_id": self.control_decision_id,
            "rollback_to_step": self.rollback_to_step,
            "rollback_point_id": self.rollback_point_id
        }


class WorkflowEngine:
    """
    正式任务编排内核主链入口
    
    主流程：
    1. 接收 workflow_id + version 或 template
    2. 从 workflow_registry resolve 模板
    3. 通过 workflow_contract_validator 校验
    4. 用 workflow_instance_store 创建 instance
    5. 用 workflow_event_store 写 workflow_started
    6. 用 dependency_resolver 生成执行顺序
    7. 每个 step：step_started -> 执行 -> retry/fallback/rollback/checkpoint -> recovery record -> step_completed/step_failed
    8. 更新 instance 状态
    9. 写 workflow_completed
    10. 返回正式 workflow result
    """
    
    def __init__(
        self,
        skill_router=None,
        checkpoint_store=None,
        fallback_policy=None,
        rollback_manager=None,
        max_parallel_steps: int = 4
    ):
        self.skill_router = skill_router
        # 初始化或使用传入的恢复模块
        self.checkpoint_store = checkpoint_store or CheckpointStore()
        self.fallback_policy = fallback_policy or FallbackPolicy()
        self.rollback_manager = rollback_manager or RollbackManager()
        self.max_parallel_steps = max_parallel_steps
        
        # 正式模块
        self._registry = get_workflow_registry()
        self._validator = get_workflow_contract_validator()
        self._instance_store = get_workflow_instance_store()
        self._event_store = get_workflow_event_store()
        self._recovery_store = get_recovery_store()
        self._state_machine = get_workflow_state_machine()
        self._dependency_resolver = get_dependency_resolver()
        
        # 动作处理器
        self._action_handlers: Dict[str, Callable] = {}
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """注册动作处理器"""
        self._action_handlers[action_type] = handler

    def _create_template_from_spec(self, spec: Dict) -> WorkflowTemplate:
        """从旧格式 spec 创建 WorkflowTemplate"""
        from orchestration.workflow.workflow_registry import RecoveryPolicy, RecoveryPolicyType

        steps = []
        for step_spec in spec.get("steps", []):
            step = WorkflowStep(
                step_id=step_spec.get("step_id", "unknown"),
                name=step_spec.get("name", step_spec.get("step_id", "unknown")),
                action=step_spec.get("action", "noop"),
                description=step_spec.get("description", ""),
                depends_on=step_spec.get("depends_on", []),
                params=step_spec.get("params", {}),
                timeout_ms=step_spec.get("timeout_ms", 30000)
            )
            steps.append(step)

        return WorkflowTemplate(
            workflow_id=spec.get("workflow_id", "compat_workflow"),
            version=spec.get("version", "1.0.0"),
            name=spec.get("name", spec.get("workflow_id", "Compat Workflow")),
            description=spec.get("description", ""),
            steps=steps,
            profile_compatibility=spec.get("profile_compatibility", ["default", "developer", "admin"]),
            recovery_policy=RecoveryPolicy(
                policy_type=RecoveryPolicyType.RETRY,
                max_retries=spec.get("max_retries", 3)
            )
        )

    def run_workflow(
        self,
        workflow_id: str = None,
        version: str = None,
        template: WorkflowTemplate = None,
        profile: str = "default",
        context_bundle: Dict = None,
        control_decision: Dict = None,
        resume_from_checkpoint: str = None,
        workflow_spec: Dict = None  # 兼容旧接口
    ) -> WorkflowResult:
        """
        执行 workflow

        Args:
            workflow_id: Workflow ID（与 version 配合使用）
            version: 版本（可选，默认最新）
            template: Workflow 模板（直接传入）
            profile: 执行配置
            context_bundle: 执行上下文
            control_decision: Control Plane 决策
            resume_from_checkpoint: 恢复检查点 ID
            workflow_spec: 兼容旧接口的 workflow 规格字典

        Returns:
            WorkflowResult
        """
        # ========== 兼容旧接口 ==========
        # 如果第一个参数是 dict，当作 workflow_spec 处理
        if isinstance(workflow_id, dict):
            workflow_spec = workflow_id
            workflow_id = None

        if workflow_spec and isinstance(workflow_spec, dict):
            # 从 dict 创建 template
            template = self._create_template_from_spec(workflow_spec)
            # 注册到 registry（兼容旧接口）
            self._registry.register(template)
            workflow_id = template.workflow_id
            version = template.version

        # 1. 解析模板
        if template is None:
            template = self._registry.get(workflow_id, version)
            if template is None:
                raise ValueError(f"Workflow template not found: {workflow_id}:{version or 'latest'}")
        
        workflow_id = template.workflow_id
        version = template.version
        
        # 2. 校验契约
        allowed_capabilities = []
        if control_decision:
            allowed_capabilities = control_decision.get("allowed_capabilities", [])
        
        validation = self._validator.validate(
            workflow_id=workflow_id,
            version=version,
            profile=profile,
            allowed_capabilities=allowed_capabilities
        )
        
        if not validation.valid:
            raise ValueError(f"Workflow validation failed: {validation.errors}")
        
        # 3. 创建实例
        control_decision_id = control_decision.get("decision_id") if control_decision else None
        instance = self._instance_store.create(
            workflow_id=workflow_id,
            version=version,
            task_id=context_bundle.get("task_id", "") if context_bundle else "",
            profile=profile,
            control_decision_id=control_decision_id,
            input_data=context_bundle
        )
        
        # 4. 写 workflow_started 事件
        self._event_store.record_workflow_started(
            instance_id=instance.instance_id,
            workflow_id=workflow_id,
            version=version,
            profile=profile,
            control_decision_id=control_decision_id
        )
        
        # ========== Group5: 发送正式事件 ==========
        _emit_event(
            "workflow_started",
            {
                "workflow_id": workflow_id,
                "version": version,
                "profile": profile
            },
            workflow_instance_id=instance.instance_id
        )
        
        # 5. 更新状态为 running
        self._state_machine.transition_workflow(instance.instance_id, WorkflowState.RUNNING)
        self._instance_store.update(instance.instance_id, status=InstanceStatus.RUNNING)
        
        # 6. 生成执行顺序
        execution_order = self._dependency_resolver.resolve(template.steps)
        
        # 7. 初始化结果
        result = WorkflowResult(
            instance_id=instance.instance_id,
            workflow_id=workflow_id,
            version=version,
            status=WorkflowState.RUNNING,
            started_at=instance.started_at,
            control_decision_id=control_decision_id
        )
        
        # 8. 执行步骤
        try:
            self._execute_steps(
                template=template,
                execution_order=execution_order,
                result=result,
                context=context_bundle or {},
                control_decision=control_decision
            )
            
            # 成功完成
            result.status = WorkflowState.COMPLETED
            result.completed_at = datetime.now().isoformat()
            
            self._state_machine.transition_workflow(instance.instance_id, WorkflowState.COMPLETED)
            self._instance_store.update(
                instance.instance_id,
                status=InstanceStatus.COMPLETED,
                output=result.final_output
            )
            
            self._event_store.record_workflow_completed(
                instance_id=instance.instance_id,
                status="completed",
                output=result.final_output
            )
            
        except Exception as e:
            result.status = WorkflowState.FAILED
            result.error = str(e)
            result.completed_at = datetime.now().isoformat()
            
            self._state_machine.transition_workflow(instance.instance_id, WorkflowState.FAILED)
            self._instance_store.update(
                instance.instance_id,
                status=InstanceStatus.FAILED,
                output={"error": str(e)}
            )
            
            self._event_store.record_workflow_completed(
                instance_id=instance.instance_id,
                status="failed",
                output={"error": str(e)}
            )
        
        # 9. 计算时长
        if result.completed_at:
            start = datetime.fromisoformat(result.started_at)
            end = datetime.fromisoformat(result.completed_at)
            result.total_duration_ms = int((end - start).total_seconds() * 1000)
        
        # 10. 汇总恢复信息
        for step_result in result.step_results.values():
            result.total_retry_count += step_result.retry_count
            if step_result.fallback_used:
                result.fallback_used = True
            if step_result.rollback_used:
                result.rollback_used = True
        
        return result
    
    def _execute_steps(
        self,
        template: WorkflowTemplate,
        execution_order: List[str],
        result: WorkflowResult,
        context: Dict,
        control_decision: Dict = None
    ):
        """执行步骤序列"""
        step_map = {s.step_id: s for s in template.steps}
        blocked_capabilities = control_decision.get("blocked_capabilities", []) if control_decision else []
        degradation_mode = control_decision.get("degradation_mode") if control_decision else None
        
        for step_id in execution_order:
            step = step_map.get(step_id)
            if not step:
                continue
            
            # 检查能力是否被阻止
            if any(cap in blocked_capabilities for cap in step.required_capabilities):
                self._event_store.record(
                    instance_id=result.instance_id,
                    event_type=WorkflowEventType.CAPABILITY_BLOCKED,
                    step_id=step_id,
                    data={"blocked_capabilities": step.required_capabilities}
                )
                
                step_result = StepResult(
                    step_id=step_id,
                    status=StepState.SKIPPED,
                    started_at=datetime.now().isoformat(),
                    completed_at=datetime.now().isoformat(),
                    error="Capability blocked by control decision"
                )
                result.step_results[step_id] = step_result
                continue
            
            # 检查 safe mode
            if degradation_mode in ["safe", "restricted"] and step.is_high_risk:
                if not step.safe_mode_supported:
                    step_result = StepResult(
                        step_id=step_id,
                        status=StepState.SKIPPED,
                        started_at=datetime.now().isoformat(),
                        completed_at=datetime.now().isoformat(),
                        error="High risk step skipped in safe mode"
                    )
                    result.step_results[step_id] = step_result
                    continue
            
            # 执行步骤
            step_result = self._execute_step(
                step=step,
                result=result,
                context=context,
                template=template
            )
            result.step_results[step_id] = step_result
            
            # 处理失败
            if step_result.status == StepState.FAILED:
                result.failed_step_id = step_id
                raise RuntimeError(f"Step {step_id} failed: {step_result.error}")
    
    def _execute_step(
        self,
        step: WorkflowStep,
        result: WorkflowResult,
        context: Dict,
        template: WorkflowTemplate
    ) -> StepResult:
        """执行单个步骤（完整恢复链）"""
        started_at = datetime.now().isoformat()

        # 写 step_started 事件
        self._event_store.record_step_started(
            instance_id=result.instance_id,
            step_id=step.step_id,
            step_name=step.name,
            action=step.action
        )

        # 更新状态机
        self._state_machine.transition_step(result.instance_id, step.step_id, StepState.RUNNING)

        step_result = StepResult(
            step_id=step.step_id,
            status=StepState.RUNNING,
            started_at=started_at
        )

        # 构建步骤输入
        step_input = self._build_step_input(step, result.step_results, context)

        # 获取恢复策略
        recovery_policy = step.recovery_policy or template.recovery_policy
        max_retries = recovery_policy.max_retries if recovery_policy else 3

        # 计算已完成和待执行步骤
        completed_steps = [sid for sid, sr in result.step_results.items() if sr.status == StepState.COMPLETED]
        pending_steps = [s.step_id for s in template.steps if s.step_id not in completed_steps and s.step_id != step.step_id]

        # ========== 第一组：step 开始前保存 checkpoint ==========
        checkpoint = self.checkpoint_store.save(
            workflow_id=result.workflow_id,
            step_id=step.step_id,
            state={
                "instance_id": result.instance_id,
                "step_input": step_input,
                "step_results": {k: v.to_dict() for k, v in result.step_results.items()}
            },
            completed_steps=completed_steps,
            pending_steps=[step.step_id] + pending_steps,
            metadata={"phase": "before_step", "attempt": 0}
        )
        step_result.checkpoint_id = checkpoint.checkpoint_id

        # 写 checkpoint_saved 事件
        self._event_store.record(
            instance_id=result.instance_id,
            event_type=WorkflowEventType.CHECKPOINT_SAVED,
            step_id=step.step_id,
            data={
                "checkpoint_id": checkpoint.checkpoint_id,
                "phase": "before_step"
            }
        )

        # ========== 第三组：step 执行前创建 rollback point ==========
        if step.supports_rollback if hasattr(step, 'supports_rollback') else True:
            rollback_point = self.rollback_manager.create_point(
                step_id=step.step_id,
                state={
                    "instance_id": result.instance_id,
                    "step_input": step_input,
                    "completed_steps": completed_steps,
                    "step_results": {k: v.to_dict() for k, v in result.step_results.items()}
                },
                metadata={"phase": "before_step"}
            )
            step_result.rollback_point_id = rollback_point.point_id

        # 执行（带重试和恢复链）
        for attempt in range(max_retries + 1):
            try:
                output = self._execute_action(step.action, step_input, step.timeout_ms)

                step_result.status = StepState.COMPLETED
                step_result.output = output
                break

            except Exception as e:
                step_result.error = str(e)
                step_result.retry_count = attempt

                # ========== 第一组：step 失败后保存 checkpoint ==========
                checkpoint = self.checkpoint_store.save(
                    workflow_id=result.workflow_id,
                    step_id=step.step_id,
                    state={
                        "instance_id": result.instance_id,
                        "error": str(e),
                        "attempt": attempt,
                        "step_results": {k: v.to_dict() for k, v in result.step_results.items()}
                    },
                    completed_steps=completed_steps,
                    pending_steps=[step.step_id] + pending_steps,
                    metadata={"phase": "on_error", "attempt": attempt}
                )
                step_result.checkpoint_id = checkpoint.checkpoint_id

                self._event_store.record(
                    instance_id=result.instance_id,
                    event_type=WorkflowEventType.CHECKPOINT_SAVED,
                    step_id=step.step_id,
                    data={
                        "checkpoint_id": checkpoint.checkpoint_id,
                        "phase": "on_error",
                        "attempt": attempt
                    }
                )

                # ========== 第二组：通过 fallback_policy 决策 ==========
                fallback_decision = self.fallback_policy.decide(
                    step_id=step.step_id,
                    error=str(e),
                    error_type="exception",
                    retry_count=attempt,
                    context={
                        "instance_id": result.instance_id,
                        "recovery_policy": recovery_policy.to_dict() if recovery_policy and hasattr(recovery_policy, 'to_dict') else {},
                        "max_retries": max_retries
                    }
                )
                step_result.fallback_decision = fallback_decision.action.value

                if fallback_decision.action == FallbackAction.RETRY and attempt < max_retries:
                    # 记录重试
                    self._recovery_store.record_retry(
                        instance_id=result.instance_id,
                        step_id=step.step_id,
                        error_type=ErrorType.EXCEPTION,
                        error_message=str(e),
                        retry_count=attempt + 1,
                        max_retries=max_retries
                    )

                    self._event_store.record_retry_triggered(
                        instance_id=result.instance_id,
                        step_id=step.step_id,
                        retry_count=attempt + 1,
                        max_retries=max_retries
                    )

                    step_result.status = StepState.RETRYING
                    continue

                elif fallback_decision.action == FallbackAction.FALLBACK:
                    # 执行 fallback skill
                    fallback_skill = fallback_decision.fallback_skill_id
                    if not fallback_skill and recovery_policy:
                        fallback_skill = recovery_policy.fallback_skill

                    if fallback_skill:
                        try:
                            output = self._execute_action(fallback_skill, step_input, step.timeout_ms)

                            step_result.status = StepState.COMPLETED
                            step_result.output = output
                            step_result.fallback_used = True

                            # 记录 fallback
                            self._recovery_store.record_fallback(
                                instance_id=result.instance_id,
                                step_id=step.step_id,
                                error_type=ErrorType.EXCEPTION,
                                error_message=str(e),
                                fallback_skill=fallback_skill
                            )

                            self._event_store.record_fallback_triggered(
                                instance_id=result.instance_id,
                                step_id=step.step_id,
                                fallback_skill=fallback_skill
                            )

                            # ========== 第一组：fallback 成功后保存 checkpoint ==========
                            checkpoint = self.checkpoint_store.save(
                                workflow_id=result.workflow_id,
                                step_id=step.step_id,
                                state={
                                    "instance_id": result.instance_id,
                                    "output": output,
                                    "fallback_used": True,
                                    "step_results": {k: v.to_dict() for k, v in result.step_results.items()}
                                },
                                completed_steps=completed_steps + [step.step_id],
                                pending_steps=pending_steps,
                                metadata={"phase": "after_fallback"}
                            )
                            step_result.checkpoint_id = checkpoint.checkpoint_id

                            self._event_store.record(
                                instance_id=result.instance_id,
                                event_type=WorkflowEventType.CHECKPOINT_SAVED,
                                step_id=step.step_id,
                                data={
                                    "checkpoint_id": checkpoint.checkpoint_id,
                                    "phase": "after_fallback"
                                }
                            )

                            break

                        except Exception as fe:
                            step_result.error = f"Primary: {e}, Fallback: {fe}"

                            # ========== 第三组：fallback 失败，尝试 rollback ==========
                            if step_result.rollback_point_id:
                                rollback_result = self.rollback_manager.rollback(step_result.rollback_point_id)

                                if rollback_result.success:
                                    step_result.rollback_used = True
                                    result.rollback_used = True
                                    result.rollback_point_id = step_result.rollback_point_id
                                    result.rollback_to_step = step.step_id

                                    # 记录 rollback
                                    self._recovery_store.record_rollback(
                                        instance_id=result.instance_id,
                                        step_id=step.step_id,
                                        error_type=ErrorType.EXCEPTION,
                                        error_message=step_result.error,
                                        rollback_to_step=step.step_id
                                    )

                                    self._event_store.record(
                                        instance_id=result.instance_id,
                                        event_type=WorkflowEventType.ROLLBACK_TRIGGERED,
                                        step_id=step.step_id,
                                        data={
                                            "rollback_point_id": step_result.rollback_point_id,
                                            "rollback_to_step": step.step_id,
                                            "reason": "fallback_failed"
                                        }
                                    )

                elif fallback_decision.action == FallbackAction.SKIP:
                    # 跳过步骤
                    step_result.status = StepState.SKIPPED
                    step_result.error = f"Skipped: {e}"
                    break

                else:
                    # ABORT
                    step_result.status = StepState.FAILED

                    # ========== 第三组：终止前尝试 rollback ==========
                    if step_result.rollback_point_id:
                        rollback_result = self.rollback_manager.rollback(step_result.rollback_point_id)

                        if rollback_result.success:
                            step_result.rollback_used = True
                            result.rollback_used = True
                            result.rollback_point_id = step_result.rollback_point_id
                            result.rollback_to_step = step.step_id

                            self._recovery_store.record_rollback(
                                instance_id=result.instance_id,
                                step_id=step.step_id,
                                error_type=ErrorType.EXCEPTION,
                                error_message=step_result.error,
                                rollback_to_step=step.step_id
                            )

                            self._event_store.record(
                                instance_id=result.instance_id,
                                event_type=WorkflowEventType.ROLLBACK_TRIGGERED,
                                step_id=step.step_id,
                                data={
                                    "rollback_point_id": step_result.rollback_point_id,
                                    "rollback_to_step": step.step_id,
                                    "reason": "abort"
                                }
                            )

                    break

        step_result.completed_at = datetime.now().isoformat()

        # 计算时长
        start = datetime.fromisoformat(step_result.started_at)
        end = datetime.fromisoformat(step_result.completed_at)
        step_result.duration_ms = int((end - start).total_seconds() * 1000)

        # ========== 第一组：step 成功后保存 checkpoint ==========
        if step_result.status == StepState.COMPLETED:
            checkpoint = self.checkpoint_store.save(
                workflow_id=result.workflow_id,
                step_id=step.step_id,
                state={
                    "instance_id": result.instance_id,
                    "output": step_result.output,
                    "step_results": {k: v.to_dict() for k, v in result.step_results.items()}
                },
                completed_steps=completed_steps + [step.step_id],
                pending_steps=pending_steps,
                metadata={"phase": "after_step"}
            )
            step_result.checkpoint_id = checkpoint.checkpoint_id
            result.checkpoint_id = checkpoint.checkpoint_id

            self._event_store.record(
                instance_id=result.instance_id,
                event_type=WorkflowEventType.CHECKPOINT_SAVED,
                step_id=step.step_id,
                data={
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "phase": "after_step"
                }
            )

            self._event_store.record_step_completed(
                instance_id=result.instance_id,
                step_id=step.step_id,
                output=step_result.output,
                duration_ms=step_result.duration_ms
            )
            self._state_machine.transition_step(result.instance_id, step.step_id, StepState.COMPLETED)
        else:
            self._event_store.record_step_failed(
                instance_id=result.instance_id,
                step_id=step.step_id,
                error_type="exception",
                error_message=step_result.error or ""
            )
            self._state_machine.transition_step(result.instance_id, step.step_id, StepState.FAILED)

        return step_result
    
    def _build_step_input(
        self,
        step: WorkflowStep,
        previous_results: Dict[str, StepResult],
        context: Dict
    ) -> Dict:
        """构建步骤输入"""
        step_input = {
            "context": context,
            "dependencies": {},
            "params": step.params
        }
        
        for dep_id in step.depends_on:
            if dep_id in previous_results:
                step_input["dependencies"][dep_id] = previous_results[dep_id].output
        
        return step_input
    
    def _execute_action(self, action: str, step_input: Dict, timeout_ms: int) -> Dict:
        """执行动作"""
        timeout_seconds = timeout_ms / 1000 if timeout_ms else 30
        
        # 1. 检查注册的处理器
        for action_type, handler in self._action_handlers.items():
            if action.startswith(action_type) or action == action_type:
                return handler(action, step_input)
        
        # 2. 使用技能路由器
        if self.skill_router:
            try:
                return self.skill_router.execute(action, step_input)
            except Exception as e:
                raise RuntimeError(f"Skill router error: {e}")
        
        # 3. 测试动作
        if action.lower() in ["test", "noop", "mock", "initialize", "execute", "finalize"]:
            return {
                "executed": True,
                "action": action,
                "input": step_input,
                "message": f"Action '{action}' executed (test mode)"
            }
        
        # 4. 无处理器
        raise RuntimeError(f"No handler for action '{action}'")


def run_workflow(
    workflow_id: str = None,
    version: str = None,
    template: WorkflowTemplate = None,
    profile: str = "default",
    context_bundle: Dict = None,
    control_decision: Dict = None
) -> WorkflowResult:
    """
    便捷函数：执行 workflow
    
    Usage:
        result = run_workflow(
            workflow_id="minimum_loop",
            version="1.0.0",
            profile="default"
        )
    """
    engine = WorkflowEngine()
    return engine.run_workflow(
        workflow_id=workflow_id,
        version=version,
        template=template,
        profile=profile,
        context_bundle=context_bundle,
        control_decision=control_decision
    )


# ========== 对外导出 ==========
__all__ = [
    # 核心类
    "WorkflowEngine",
    "WorkflowResult",
    "StepResult",
    # 状态枚举
    "WorkflowState",
    "WorkflowStatus",  # 兼容旧接口
    "StepState",
    # 便捷函数
    "run_workflow",
]
