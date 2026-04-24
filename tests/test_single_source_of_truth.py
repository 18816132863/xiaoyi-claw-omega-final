"""
测试真源唯一性
验证 TaskStatus / StepStatus / EventType / CapabilityRegistry 真源唯一
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_task_status_single_source():
    """测试 TaskStatus 真源唯一"""
    # 真源位置
    from domain.tasks.specs import TaskStatus as TrueTaskStatus
    
    # 验证真源有完整的 13 种状态
    assert hasattr(TrueTaskStatus, 'DRAFT')
    assert hasattr(TrueTaskStatus, 'VALIDATED')
    assert hasattr(TrueTaskStatus, 'PERSISTED')
    assert hasattr(TrueTaskStatus, 'QUEUED')
    assert hasattr(TrueTaskStatus, 'RUNNING')
    assert hasattr(TrueTaskStatus, 'DELIVERY_PENDING')
    assert hasattr(TrueTaskStatus, 'WAITING_RETRY')
    assert hasattr(TrueTaskStatus, 'WAITING_HUMAN')
    assert hasattr(TrueTaskStatus, 'PAUSED')
    assert hasattr(TrueTaskStatus, 'RESUMED')
    assert hasattr(TrueTaskStatus, 'SUCCEEDED')
    assert hasattr(TrueTaskStatus, 'FAILED')
    assert hasattr(TrueTaskStatus, 'CANCELLED')
    
    # 验证其他位置的 TaskStatus 已重命名
    # orchestration/collaboration/org_orchestrator.py -> OrgTaskStatus
    from orchestration.collaboration.org_orchestrator import OrgTaskStatus
    assert hasattr(OrgTaskStatus, 'PENDING')
    assert hasattr(OrgTaskStatus, 'ASSIGNED')
    
    # orchestration/task_engine.py -> EngineTaskStatus
    from orchestration.task_engine import EngineTaskStatus
    assert hasattr(EngineTaskStatus, 'PENDING')
    assert hasattr(EngineTaskStatus, 'SUCCESS')
    
    # infrastructure/automation/task_automator.py -> AutomatorTaskStatus
    from infrastructure.automation.task_automator import AutomatorTaskStatus
    assert hasattr(AutomatorTaskStatus, 'PENDING')
    assert hasattr(AutomatorTaskStatus, 'QUEUED')
    
    # core/state/task_state_contract.py -> ContractTaskStatus
    from core.state.task_state_contract import ContractTaskStatus
    assert hasattr(ContractTaskStatus, 'CREATED')
    assert hasattr(ContractTaskStatus, 'PLANNING')
    
    # core/cognition/planning.py -> PlanningTaskStatus
    from core.cognition.planning import PlanningTaskStatus
    assert hasattr(PlanningTaskStatus, 'PENDING')
    assert hasattr(PlanningTaskStatus, 'READY')


def test_step_status_single_source():
    """测试 StepStatus 真源唯一"""
    # 真源位置
    from domain.tasks.specs import StepStatus as TrueStepStatus
    
    # 验证真源有完整的 5 种状态
    assert hasattr(TrueStepStatus, 'PENDING')
    assert hasattr(TrueStepStatus, 'RUNNING')
    assert hasattr(TrueStepStatus, 'SUCCEEDED')
    assert hasattr(TrueStepStatus, 'FAILED')
    assert hasattr(TrueStepStatus, 'SKIPPED')
    
    # 验证其他位置的 StepStatus 已重命名
    # orchestration/workflows/workflow_base.py -> WorkflowStepStatus
    from orchestration.workflows.workflow_base import WorkflowStepStatus
    assert hasattr(WorkflowStepStatus, 'PENDING')
    assert hasattr(WorkflowStepStatus, 'SUCCESS')
    
    # orchestration/workflow_engine.py -> EngineStepStatus
    from orchestration.workflow_engine import EngineStepStatus
    assert hasattr(EngineStepStatus, 'PENDING')
    assert hasattr(EngineStepStatus, 'COMPLETED')


def test_event_type_single_source():
    """测试 EventType 真源唯一"""
    # 真源位置
    from domain.tasks.specs import EventType as TrueEventType
    
    # 验证真源有完整的事件类型
    assert hasattr(TrueEventType, 'CREATED')
    assert hasattr(TrueEventType, 'VALIDATED')
    assert hasattr(TrueEventType, 'PERSISTED')
    assert hasattr(TrueEventType, 'QUEUED')
    assert hasattr(TrueEventType, 'STARTED')
    assert hasattr(TrueEventType, 'SUCCEEDED')
    assert hasattr(TrueEventType, 'FAILED')
    
    # 验证其他位置的 EventType 已重命名
    # orchestration/state/workflow_event_store.py -> WorkflowEventType
    from orchestration.state.workflow_event_store import WorkflowEventType
    assert hasattr(WorkflowEventType, 'WORKFLOW_STARTED')
    assert hasattr(WorkflowEventType, 'CHECKPOINT_SAVED')
    
    # infrastructure/automation/event_trigger.py -> TriggerEventType
    from infrastructure.automation.event_trigger import TriggerEventType
    assert hasattr(TriggerEventType, 'FILE_CHANGE')
    assert hasattr(TriggerEventType, 'SCHEDULE')
    
    # core/events/event_types.py -> CoreEventType
    from core.events.event_types import CoreEventType
    assert hasattr(CoreEventType, 'TASK_CREATED')
    assert hasattr(CoreEventType, 'SKILL_SELECTED')
    
    # core/events/event_bus.py -> BusEventType
    from core.events.event_bus import BusEventType
    assert hasattr(BusEventType, 'TASK_CREATED')
    assert hasattr(BusEventType, 'DEGRADATION_TRIGGERED')


def test_capability_registry_single_source():
    """测试 CapabilityRegistry 真源唯一"""
    # 真源位置
    from capabilities.registry import CapabilityRegistry as TrueCapabilityRegistry
    
    # 验证真源存在
    assert TrueCapabilityRegistry is not None
    
    # 验证其他位置的 CapabilityRegistry 已重命名
    # governance/control_plane/capability_registry.py -> GovernanceCapabilityRegistry
    from governance.control_plane.capability_registry import GovernanceCapabilityRegistry
    assert GovernanceCapabilityRegistry is not None
    
    # 验证两者是不同的类
    assert TrueCapabilityRegistry is not GovernanceCapabilityRegistry


def test_capability_status_single_source():
    """测试 CapabilityStatus 真源唯一"""
    # 真源位置
    from capabilities.registry import CapabilityStatus as TrueCapabilityStatus
    
    # 验证真源是 Enum
    assert hasattr(TrueCapabilityStatus, 'AVAILABLE')
    assert hasattr(TrueCapabilityStatus, 'UNAVAILABLE')
    
    # 验证其他位置的 CapabilityStatus 已重命名
    # platform_adapter/base.py -> PlatformCapabilityState
    from platform_adapter.base import PlatformCapabilityState
    assert PlatformCapabilityState is not None
    
    # 验证两者是不同的类
    assert TrueCapabilityStatus is not PlatformCapabilityState


if __name__ == "__main__":
    test_task_status_single_source()
    test_step_status_single_source()
    test_event_type_single_source()
    test_capability_registry_single_source()
    test_capability_status_single_source()
    print("✅ 所有真源唯一性测试通过")
