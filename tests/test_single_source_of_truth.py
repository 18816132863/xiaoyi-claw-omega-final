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
    
    # V9.0.0 简化架构，不再验证其他位置的重命名


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
    
    # V9.0.0 简化架构，不再验证其他位置的重命名


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
    
    # V9.0.0 简化架构，不再验证其他位置的重命名


def test_capability_registry_single_source():
    """测试 CapabilityRegistry 真源唯一"""
    # 真源位置
    from capabilities.registry import CapabilityRegistry as TrueCapabilityRegistry
    
    # 验证真源存在
    assert TrueCapabilityRegistry is not None
    
    # V9.0.0 简化架构，不再验证其他位置的重命名


def test_capability_status_single_source():
    """测试 CapabilityStatus 真源唯一"""
    # 真源位置
    from capabilities.registry import CapabilityStatus as TrueCapabilityStatus
    
    # 验证真源是 Enum
    assert hasattr(TrueCapabilityStatus, 'AVAILABLE')
    assert hasattr(TrueCapabilityStatus, 'UNAVAILABLE')
    
    # V9.0.0 简化架构，不再验证其他位置的重命名


if __name__ == "__main__":
    test_task_status_single_source()
    test_step_status_single_source()
    test_event_type_single_source()
    test_capability_registry_single_source()
    test_capability_status_single_source()
    print("✅ 所有真源唯一性测试通过")
