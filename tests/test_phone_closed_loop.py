"""测试电话能力"""

import pytest


def test_make_call_dry_run():
    """测试拨打电话（dry_run）"""
    from capabilities.make_call import make_call
    
    result = make_call(phone="13800138000", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_end_call_dry_run():
    """测试挂断电话（dry_run）"""
    from capabilities.make_call import end_call
    
    result = end_call(dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_get_call_history():
    """测试获取通话记录"""
    from capabilities.make_call import get_call_history
    
    result = get_call_history(limit=10)
    assert result["success"] == True
    assert "calls" in result
