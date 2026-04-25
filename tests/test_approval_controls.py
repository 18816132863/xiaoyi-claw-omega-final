"""测试审批控制"""

import pytest


def test_request_approval():
    """测试请求审批"""
    from capabilities.approve_action import request_approval
    
    result = request_approval(
        action_type="batch_sms",
        action_params={"count": 10},
        reason="批量发送短信"
    )
    assert result["success"] == True
    assert "approval_id" in result
    assert result["status"] == "pending"


def test_approve_action():
    """测试批准操作"""
    from capabilities.approve_action import request_approval, approve_action
    
    # 先请求审批
    request = request_approval(
        action_type="batch_sms",
        action_params={"count": 10},
        reason="批量发送短信"
    )
    
    # 批准
    result = approve_action(
        approval_id=request["approval_id"],
        approved_by="admin"
    )
    assert result["success"] == True
    assert result["status"] == "approved"


def test_reject_action():
    """测试拒绝操作"""
    from capabilities.approve_action import request_approval, reject_action
    
    # 先请求审批
    request = request_approval(
        action_type="batch_sms",
        action_params={"count": 10},
        reason="批量发送短信"
    )
    
    # 拒绝
    result = reject_action(
        approval_id=request["approval_id"],
        rejected_by="admin",
        reason="不允许批量发送"
    )
    assert result["success"] == True
    assert result["status"] == "rejected"


def test_check_approval_required():
    """测试检查是否需要审批"""
    from config.safety_controls import check_approval_required
    
    # 批量短信超过阈值
    result = check_approval_required("batch_sms", 10)
    assert result["approval_required"] == True
    
    # 批量短信未超过阈值
    result = check_approval_required("batch_sms", 3)
    assert result["approval_required"] == False


def test_check_batch_size():
    """测试检查批次大小"""
    from config.safety_controls import check_batch_size
    
    # 超过限制
    result = check_batch_size("batch_sms", 30)
    assert result["allowed"] == False
    
    # 未超过限制
    result = check_batch_size("batch_sms", 10)
    assert result["allowed"] == True


def test_check_rate_limit():
    """测试检查限流"""
    from config.safety_controls import check_rate_limit
    
    # 超过限制
    result = check_rate_limit("send_message", 15, "per_minute")
    assert result["allowed"] == False
    
    # 未超过限制
    result = check_rate_limit("send_message", 5, "per_minute")
    assert result["allowed"] == True
