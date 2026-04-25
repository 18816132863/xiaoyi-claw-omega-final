"""测试小艺帮记能力"""

import pytest


def test_query_xiaoyi_note():
    """测试查询小艺帮记"""
    from capabilities.query_xiaoyi_note import query_xiaoyi_note
    
    result = query_xiaoyi_note()
    assert result["success"] == True
    assert "notes" in result


def test_list_xiaoyi_notes():
    """测试列出小艺帮记"""
    from capabilities.query_xiaoyi_note import list_xiaoyi_notes
    
    result = list_xiaoyi_notes(limit=10)
    assert result["success"] == True
    assert "notes" in result


def test_search_xiaoyi_notes():
    """测试搜索小艺帮记"""
    from capabilities.query_xiaoyi_note import search_xiaoyi_notes
    
    result = search_xiaoyi_notes(keyword="测试")
    assert result["success"] == True
    assert result["keyword"] == "测试"


def test_delete_xiaoyi_note_dry_run():
    """测试删除小艺帮记（dry_run）"""
    from capabilities.delete_xiaoyi_note import delete_xiaoyi_note
    
    result = delete_xiaoyi_note(note_id="test", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True
