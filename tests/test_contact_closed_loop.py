"""测试联系人闭环能力"""

import pytest


def test_query_contact():
    """测试查询联系人"""
    from capabilities.query_contact import query_contact
    
    result = query_contact()
    assert result["success"] == True
    assert "contacts" in result


def test_list_contacts():
    """测试列出联系人"""
    from capabilities.query_contact import list_contacts
    
    result = list_contacts(limit=10)
    assert result["success"] == True
    assert "contacts" in result


def test_search_contacts():
    """测试搜索联系人"""
    from capabilities.query_contact import search_contacts
    
    result = search_contacts(keyword="张")
    assert result["success"] == True
    assert result["keyword"] == "张"


def test_create_contact_dry_run():
    """测试创建联系人（dry_run）"""
    from capabilities.create_contact import create_contact
    
    result = create_contact(name="测试联系人", phone="13800138000", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_update_contact_dry_run():
    """测试更新联系人（dry_run）"""
    from capabilities.update_contact import update_contact
    
    result = update_contact(contact_id="test", name="新名字", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True


def test_delete_contact_dry_run():
    """测试删除联系人（dry_run）"""
    from capabilities.delete_contact import delete_contact
    
    result = delete_contact(contact_id="test", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True
