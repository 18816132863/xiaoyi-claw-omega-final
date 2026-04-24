"""更新闹钟能力"""

from typing import Optional, Dict, Any, List


def update_alarm(
    alarm_id: str,
    time: Optional[str] = None,
    label: Optional[str] = None,
    repeat: Optional[List[str]] = None,
    enabled: Optional[bool] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    更新闹钟
    
    Args:
        alarm_id: 闹钟ID
        time: 新时间
        label: 新标签
        repeat: 新重复日期
        enabled: 是否启用
        dry_run: 是否预演模式
        
    Returns:
        更新结果
    """
    updates = {}
    if time:
        updates["time"] = time
    if label is not None:
        updates["label"] = label
    if repeat is not None:
        updates["repeat"] = repeat
    if enabled is not None:
        updates["enabled"] = enabled
    
    if not updates:
        return {
            "success": False,
            "error": "没有提供要更新的字段"
        }
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "update_alarm",
            "alarm_id": alarm_id,
            "updates": updates,
            "message": "预演模式：将更新闹钟"
        }
    
    # TODO: 调用小艺闹钟更新接口
    return {
        "success": True,
        "alarm_id": alarm_id,
        "updates": updates,
        "message": "闹钟已更新"
    }


def enable_alarm(alarm_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """启用闹钟"""
    return update_alarm(alarm_id, enabled=True, dry_run=dry_run)


def disable_alarm(alarm_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """禁用闹钟"""
    return update_alarm(alarm_id, enabled=False, dry_run=dry_run)


def run(**kwargs):
    """能力入口"""
    action = kwargs.pop("action", "update")
    
    if action == "enable":
        return enable_alarm(**kwargs)
    elif action == "disable":
        return disable_alarm(**kwargs)
    else:
        return update_alarm(**kwargs)
