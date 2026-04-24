"""测试通知闭环能力"""

import pytest


def test_query_notification_status():
    """测试查询通知状态"""
    from capabilities.query_notification_status import query_notification_status
    
    result = query_notification_status()
    assert result["success"] == True
    assert "notifications" in result


def test_cancel_notification_dry_run():
    """测试取消通知（dry_run）"""
    from capabilities.cancel_notification import cancel_notification
    
    result = cancel_notification(
        notification_id="test_notification",
        dry_run=True
    )
    # 可能返回 not_found 或 dry_run
    assert result.get("dry_run") == True or result.get("success") == False


def test_refresh_notification_auth():
    """测试刷新通知授权"""
    from capabilities.refresh_notification_auth import refresh_notification_auth
    
    result = refresh_notification_auth()
    assert result["success"] == True
    assert "auth_status" in result


def test_explain_notification_auth_state():
    """测试解释通知授权状态"""
    from capabilities.explain_notification_auth_state import explain_notification_auth_state
    
    result = explain_notification_auth_state()
    assert result["success"] == True
    assert "summary" in result
    assert "can_send_notifications" in result
    assert "next_steps" in result
