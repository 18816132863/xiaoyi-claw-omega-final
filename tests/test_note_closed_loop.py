"""测试备忘录闭环能力"""

import pytest


def test_query_note():
    """测试查询备忘录"""
    from capabilities.query_note import query_note
    
    result = query_note()
    assert result["success"] == True
    assert "notes" in result


def test_search_notes():
    """测试搜索备忘录"""
    from capabilities.search_notes import search_notes
    
    result = search_notes(keyword="测试")
    assert result["success"] == True
    assert "results" in result
    assert result["keyword"] == "测试"


def test_list_recent_notes():
    """测试列出最近备忘录"""
    from capabilities.list_recent_notes import list_recent_notes
    
    result = list_recent_notes(limit=10)
    assert result["success"] == True
    assert "notes" in result
    assert result["limit"] == 10


def test_update_note_dry_run():
    """测试更新备忘录（dry_run）"""
    from capabilities.update_note import update_note
    
    result = update_note(
        note_id="test_note",
        title="更新后的标题",
        dry_run=True
    )
    assert result["success"] == True
    assert result["dry_run"] == True


def test_delete_note_dry_run():
    """测试删除备忘录（dry_run）"""
    from capabilities.delete_note import delete_note
    
    result = delete_note(
        note_id="test_note",
        dry_run=True
    )
    assert result["success"] == True
    assert result["dry_run"] == True
