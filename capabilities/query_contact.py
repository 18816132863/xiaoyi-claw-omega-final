"""查询联系人能力"""

from typing import Optional, Dict, Any, List


def query_contact(
    contact_id: Optional[str] = None,
    name: Optional[str] = None,
    phone: Optional[str] = None,
) -> Dict[str, Any]:
    """
    查询联系人
    
    Args:
        contact_id: 联系人ID
        name: 姓名（模糊匹配）
        phone: 电话号码
        
    Returns:
        联系人信息
    """
    try:
        # 调用小艺联系人能力
        result = _call_xiaoyi_contact("query", {
            "contact_id": contact_id,
            "name": name,
            "phone": phone
        })
        
        return {
            "success": True,
            "contacts": result.get("contacts", []),
            "count": len(result.get("contacts", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "contacts": []
        }


def list_contacts(
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    列出联系人
    
    Args:
        limit: 返回数量限制
        offset: 偏移量
        
    Returns:
        联系人列表
    """
    try:
        result = _call_xiaoyi_contact("list", {
            "limit": limit,
            "offset": offset
        })
        
        return {
            "success": True,
            "contacts": result.get("contacts", []),
            "count": len(result.get("contacts", [])),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "contacts": []
        }


def search_contacts(
    keyword: str,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    搜索联系人
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量限制
        
    Returns:
        搜索结果
    """
    try:
        result = _call_xiaoyi_contact("search", {
            "keyword": keyword,
            "limit": limit
        })
        
        return {
            "success": True,
            "keyword": keyword,
            "contacts": result.get("contacts", []),
            "count": len(result.get("contacts", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "keyword": keyword,
            "contacts": []
        }


def _call_xiaoyi_contact(action: str, params: dict) -> dict:
    """调用小艺联系人能力"""
    from platform_adapter.device_tool_adapter import call_device_tool
    return call_device_tool("contact", action, params)


def run(**kwargs):
    """能力入口"""
    action = kwargs.pop("action", "query")
    
    if action == "query":
        return query_contact(**kwargs)
    elif action == "list":
        return list_contacts(**kwargs)
    elif action == "search":
        return search_contacts(**kwargs)
    else:
        return {"success": False, "error": f"未知操作: {action}"}
