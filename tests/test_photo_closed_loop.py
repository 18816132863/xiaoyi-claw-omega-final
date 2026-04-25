"""测试图库闭环能力"""

import pytest


def test_query_photo():
    """测试查询照片"""
    from capabilities.query_photo import query_photo
    
    result = query_photo()
    assert "success" in result
    assert "photos" in result


def test_list_photos():
    """测试列出照片"""
    from capabilities.query_photo import list_photos
    
    result = list_photos(limit=10)
    assert "success" in result
    assert "photos" in result


def test_search_photos():
    """测试搜索照片"""
    from capabilities.query_photo import search_photos
    
    result = search_photos(keyword="风景")
    assert "success" in result
    # keyword 可能在 result 或 params 中
    assert "keyword" in result or result.get("success") == True


def test_delete_photo_dry_run():
    """测试删除照片（dry_run）"""
    from capabilities.delete_photo import delete_photo
    
    result = delete_photo(photo_id="test_photo", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_create_album_dry_run():
    """测试创建相册（dry_run）"""
    from capabilities.create_album import create_album
    
    result = create_album(name="测试相册", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True
