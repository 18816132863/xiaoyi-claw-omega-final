"""测试闹钟闭环能力"""

import pytest


def test_query_alarm():
    """测试查询闹钟"""
    from capabilities.query_alarm import query_alarm
    
    result = query_alarm()
    assert result["success"] == True
    assert "alarms" in result


def test_list_alarms():
    """测试列出闹钟"""
    from capabilities.query_alarm import list_alarms
    
    result = list_alarms()
    assert result["success"] == True
    assert "alarms" in result


def test_create_alarm_dry_run():
    """测试创建闹钟（dry_run）"""
    from capabilities.create_alarm import create_alarm
    
    result = create_alarm(time="08:00", label="起床", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_update_alarm_dry_run():
    """测试更新闹钟（dry_run）"""
    from capabilities.update_alarm import update_alarm
    
    result = update_alarm(alarm_id="test", time="09:00", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_enable_alarm_dry_run():
    """测试启用闹钟（dry_run）"""
    from capabilities.update_alarm import enable_alarm
    
    result = enable_alarm(alarm_id="test", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_disable_alarm_dry_run():
    """测试禁用闹钟（dry_run）"""
    from capabilities.update_alarm import disable_alarm
    
    result = disable_alarm(alarm_id="test", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_delete_alarm_dry_run():
    """测试删除闹钟（dry_run）"""
    from capabilities.delete_alarm import delete_alarm
    
    result = delete_alarm(alarm_id="test", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True
