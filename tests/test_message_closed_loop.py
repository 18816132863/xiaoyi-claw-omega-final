"""测试消息发送闭环能力"""

import pytest


def test_query_message_status():
    """测试查询消息状态"""
    from capabilities.query_message_status import query_message_status
    
    # 测试无参数查询
    result = query_message_status()
    assert result["success"] == False
    assert "必须提供至少一个查询条件" in result["error"]
    
    # 测试不存在的记录
    result = query_message_status(invocation_id=999999)
    assert result["success"] == True
    assert result["found"] == False


def test_list_recent_messages():
    """测试列出最近消息"""
    from capabilities.list_recent_messages import list_recent_messages
    
    result = list_recent_messages(limit=10)
    assert result["success"] == True
    assert "messages" in result
    assert result["limit"] == 10


def test_explain_message_result():
    """测试解释消息结果"""
    from capabilities.explain_message_result import explain_message_result
    
    # 测试不存在的记录
    result = explain_message_result(invocation_id=999999)
    assert result["success"] == False
    
    # 测试解释生成
    from capabilities.explain_message_result import _generate_explanation
    
    explanation = _generate_explanation("completed", None, None)
    assert explanation["summary"] == "消息发送成功"
    
    explanation = _generate_explanation("timeout", None, None)
    assert "超时" in explanation["summary"]
    
    explanation = _generate_explanation("result_uncertain", None, None)
    assert "不确定" in explanation["summary"]


def test_resend_message_dry_run():
    """测试重发消息（dry_run）"""
    from capabilities.resend_message import resend_message
    
    # 测试不存在的记录
    result = resend_message(original_invocation_id=999999, dry_run=True)
    assert result["success"] == False
