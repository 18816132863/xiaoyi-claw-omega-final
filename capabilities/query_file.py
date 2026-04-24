"""查询文件能力"""

from typing import Optional, Dict, Any, List


def query_file(
    file_id: Optional[str] = None,
    path: Optional[str] = None,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    查询文件
    
    Args:
        file_id: 文件ID
        path: 文件路径
        name: 文件名（模糊匹配）
        
    Returns:
        文件信息
    """
    try:
        result = _call_xiaoyi_file("query", {
            "file_id": file_id,
            "path": path,
            "name": name
        })
        
        return {
            "success": True,
            "files": result.get("files", []),
            "count": len(result.get("files", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "files": []
        }


def list_files(
    directory: str = "/",
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    列出目录下的文件
    
    Args:
        directory: 目录路径
        limit: 返回数量限制
        offset: 偏移量
        
    Returns:
        文件列表
    """
    try:
        result = _call_xiaoyi_file("list", {
            "directory": directory,
            "limit": limit,
            "offset": offset
        })
        
        return {
            "success": True,
            "directory": directory,
            "files": result.get("files", []),
            "count": len(result.get("files", [])),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "files": []
        }


def search_files(
    keyword: str,
    file_type: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    搜索文件
    
    Args:
        keyword: 搜索关键词
        file_type: 文件类型（如 pdf, doc, image）
        limit: 返回数量限制
        
    Returns:
        搜索结果
    """
    try:
        result = _call_xiaoyi_file("search", {
            "keyword": keyword,
            "file_type": file_type,
            "limit": limit
        })
        
        return {
            "success": True,
            "keyword": keyword,
            "file_type": file_type,
            "files": result.get("files", []),
            "count": len(result.get("files", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "keyword": keyword,
            "files": []
        }


def _call_xiaoyi_file(action: str, params: dict) -> dict:
    """调用小艺文件管理能力"""
    from platform_adapter.device_tool_adapter import call_device_tool
    return call_device_tool("file", action, params)


def run(**kwargs):
    """能力入口"""
    action = kwargs.pop("action", "query")
    
    if action == "query":
        return query_file(**kwargs)
    elif action == "list":
        return list_files(**kwargs)
    elif action == "search":
        return search_files(**kwargs)
    else:
        return {"success": False, "error": f"未知操作: {action}"}
