"""测试文件管理闭环能力"""

import pytest


def test_query_file():
    """测试查询文件"""
    from capabilities.query_file import query_file
    
    result = query_file()
    assert result["success"] == True
    assert "files" in result


def test_list_files():
    """测试列出文件"""
    from capabilities.query_file import list_files
    
    result = list_files(directory="/")
    assert result["success"] == True
    assert "files" in result


def test_search_files():
    """测试搜索文件"""
    from capabilities.query_file import search_files
    
    result = search_files(keyword="报告")
    assert result["success"] == True
    assert result["keyword"] == "报告"


def test_delete_file_dry_run():
    """测试删除文件（dry_run）"""
    from capabilities.delete_file import delete_file
    
    result = delete_file(file_id="test_file", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_move_file_dry_run():
    """测试移动文件（dry_run）"""
    from capabilities.manage_file import move_file
    
    result = move_file(file_id="test", destination="/new/path", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_copy_file_dry_run():
    """测试复制文件（dry_run）"""
    from capabilities.manage_file import copy_file
    
    result = copy_file(file_id="test", destination="/new/path", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_rename_file_dry_run():
    """测试重命名文件（dry_run）"""
    from capabilities.manage_file import rename_file
    
    result = rename_file(file_id="test", new_name="new_name.txt", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True
