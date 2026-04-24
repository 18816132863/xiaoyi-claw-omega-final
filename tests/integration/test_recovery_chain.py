"""
恢复链集成测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest


def test_recovery_store_exists():
    """测试恢复存储存在"""
    from orchestration.state import get_recovery_store
    store = get_recovery_store()
    assert store is not None


def test_checkpoint_store_exists():
    """测试检查点存储存在"""
    from orchestration.state import get_checkpoint_store
    store = get_checkpoint_store()
    assert store is not None


def test_workflow_event_store_exists():
    """测试工作流事件存储存在"""
    from orchestration.state import get_workflow_event_store
    store = get_workflow_event_store()
    assert store is not None


def test_workflow_instance_store_exists():
    """测试工作流实例存储存在"""
    from orchestration.state import get_workflow_instance_store
    store = get_workflow_instance_store()
    assert store is not None


def test_recovery_chain():
    """测试恢复链基本功能"""
    from orchestration.state import get_recovery_store, ErrorType, RecoveryAction
    
    store = get_recovery_store()
    
    # 记录错误
    record = store.record_error(
        instance_id="test_instance",
        step_id="test_step",
        error_type=ErrorType.TRANSIENT,
        error_message="Test error",
        recovery_action=RecoveryAction.RETRY
    )
    
    assert record is not None
    assert record.error_type == ErrorType.TRANSIENT


def test_rollback_scenario():
    """测试回滚场景"""
    from orchestration.state import get_checkpoint_store
    
    store = get_checkpoint_store()
    
    # 保存检查点
    checkpoint = store.save(
        instance_id="test_instance",
        step_id="test_step",
        state_data={"key": "value"}
    )
    
    assert checkpoint is not None
    assert checkpoint.instance_id == "test_instance"
