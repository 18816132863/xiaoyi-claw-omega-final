"""测试日程闭环能力"""

import pytest


def test_query_calendar_event():
    """测试查询日程事件"""
    from capabilities.query_calendar_event import query_calendar_event
    
    result = query_calendar_event()
    assert result["success"] == True
    assert "events" in result


def test_list_calendar_events():
    """测试列出日程事件"""
    from capabilities.list_calendar_events import list_calendar_events
    
    result = list_calendar_events(limit=10)
    assert result["success"] == True
    assert "events" in result
    assert result["limit"] == 10


def test_check_calendar_conflicts():
    """测试检查日程冲突"""
    from capabilities.check_calendar_conflicts import check_calendar_conflicts
    
    result = check_calendar_conflicts(
        start_time="2026-04-25T10:00:00",
        end_time="2026-04-25T11:00:00"
    )
    assert result["success"] == True
    assert "has_conflicts" in result
    assert "conflicts" in result


def test_update_calendar_event_dry_run():
    """测试更新日程事件（dry_run）"""
    from capabilities.update_calendar_event import update_calendar_event
    
    result = update_calendar_event(
        event_id="test_event",
        title="更新后的标题",
        dry_run=True
    )
    assert result["success"] == True
    assert result["dry_run"] == True


def test_delete_calendar_event_dry_run():
    """测试删除日程事件（dry_run）"""
    from capabilities.delete_calendar_event import delete_calendar_event
    
    result = delete_calendar_event(
        event_id="test_event",
        dry_run=True
    )
    assert result["success"] == True
    assert result["dry_run"] == True


def test_times_overlap():
    """测试时间重叠检测"""
    from capabilities.check_calendar_conflicts import _times_overlap
    
    # 重叠情况
    assert _times_overlap(
        "2026-04-25T10:00:00", "2026-04-25T11:00:00",
        "2026-04-25T10:30:00", "2026-04-25T11:30:00"
    ) == True
    
    # 不重叠情况
    assert _times_overlap(
        "2026-04-25T10:00:00", "2026-04-25T11:00:00",
        "2026-04-25T11:00:00", "2026-04-25T12:00:00"
    ) == False
