"""查询闹钟能力"""

from typing import Optional, Dict, Any, List


def query_alarm(
    alarm_id: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    查询闹钟
    
    Args:
        alarm_id: 闹钟ID
        enabled: 是否启用
        
    Returns:
        闹钟信息
    """
    try:
        result = _call_xiaoyi_alarm("query", {
            "alarm_id": alarm_id,
            "enabled": enabled
        })
        
        return {
            "success": True,
            "alarms": result.get("alarms", []),
            "count": len(result.get("alarms", []))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "alarms": []
        }


def list_alarms(
    limit: int = 50,
    enabled_only: bool = False,
) -> Dict[str, Any]:
    """
    列出所有闹钟
    
    Args:
        limit: 返回数量限制
        enabled_only: 只返回启用的闹钟
        
    Returns:
        闹钟列表
    """
    try:
        result = _call_xiaoyi_alarm("list", {
            "limit": limit,
            "enabled_only": enabled_only
        })
        
        return {
            "success": True,
            "alarms": result.get("alarms", []),
            "count": len(result.get("alarms", [])),
            "enabled_only": enabled_only
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "alarms": []
        }


def _call_xiaoyi_alarm(action: str, params: dict) -> dict:
    """调用小艺闹钟能力"""
    from platform_adapter.device_tool_adapter import call_device_tool
    return call_device_tool("alarm", action, params)


def run(**kwargs):
    """能力入口"""
    action = kwargs.pop("action", "query")
    
    if action == "query":
        return query_alarm(**kwargs)
    elif action == "list":
        return list_alarms(**kwargs)
    else:
        return {"success": False, "error": f"未知操作: {action}"}
