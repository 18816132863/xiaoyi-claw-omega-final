"""小艺帮记查询能力"""

from typing import Optional, Dict, Any, List


def query_xiaoyi_note(
    note_id: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
) -> Dict[str, Any]:
    """
    查询小艺帮记中的笔记
    
    Args:
        note_id: 笔记ID
        category: 分类
        keyword: 关键词
        
    Returns:
        笔记信息
    """
    try:
        result = _call_xiaoyi_notes("query", {
            "note_id": note_id,
            "category": category,
            "keyword": keyword
        })
        
        return {
            "success": True,
            "notes": result.get("notes", []),
            "count": len(result.get("notes", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "notes": []
        }


def list_xiaoyi_notes(
    limit: int = 20,
    category: Optional[str] = None,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    列出小艺帮记中的笔记
    
    Args:
        limit: 返回数量限制
        category: 分类
        offset: 偏移量
        
    Returns:
        笔记列表
    """
    try:
        result = _call_xiaoyi_notes("list", {
            "limit": limit,
            "category": category,
            "offset": offset
        })
        
        return {
            "success": True,
            "notes": result.get("notes", []),
            "count": len(result.get("notes", [])),
            "limit": limit,
            "category": category
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "notes": []
        }


def search_xiaoyi_notes(
    keyword: str,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    搜索小艺帮记中的笔记
    
    Args:
        keyword: 搜索关键词
        limit: 返回数量限制
        
    Returns:
        搜索结果
    """
    try:
        result = _call_xiaoyi_notes("search", {
            "keyword": keyword,
            "limit": limit
        })
        
        return {
            "success": True,
            "keyword": keyword,
            "notes": result.get("notes", []),
            "count": len(result.get("notes", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "keyword": keyword,
            "notes": []
        }


def _call_xiaoyi_notes(action: str, params: dict) -> dict:
    """调用小艺帮记能力"""
    from platform_adapter.device_tool_adapter import call_device_tool
    return call_device_tool("note", action, params)


def run(**kwargs):
    """能力入口"""
    action = kwargs.pop("action", "query")
    
    if action == "query":
        return query_xiaoyi_note(**kwargs)
    elif action == "list":
        return list_xiaoyi_notes(**kwargs)
    elif action == "search":
        return search_xiaoyi_notes(**kwargs)
    else:
        return {"success": False, "error": f"未知操作: {action}"}
