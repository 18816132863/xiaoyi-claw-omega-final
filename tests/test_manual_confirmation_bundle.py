"""测试人工确认闭环模板"""

import pytest


def test_manual_confirmation_bundle_dry_run():
    """测试人工确认闭环模板（dry_run）"""
    from orchestration.templates.manual_confirmation_bundle import manual_confirmation_bundle
    
    result = manual_confirmation_bundle(dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_confirm_and_close_dry_run():
    """测试确认并关闭（dry_run）"""
    from orchestration.templates.manual_confirmation_bundle import confirm_and_close
    
    result = confirm_and_close(
        invocation_id=1,
        confirmed_status="confirmed_success",
        dry_run=True
    )
    assert result["success"] == True
    assert result["dry_run"] == True
