"""删除闹钟能力"""

from typing import Dict, Any


def delete_alarm(
    alarm_id: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    删除闹钟
    
    Args:
        alarm_id: 闹钟ID
        dry_run: 是否预演模式
        
    Returns:
        删除结果
    """
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "delete_alarm",
            "alarm_id": alarm_id,
            "message": "预演模式：将删除闹钟"
        }
    
    # TODO: 调用小艺闹钟删除接口
    return {
        "success": True,
        "alarm_id": alarm_id,
        "deleted": True,
        "message": "闹钟已删除"
    }


def delete_alarms_batch(
    alarm_ids: list,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    批量删除闹钟
    
    Args:
        alarm_ids: 闹钟ID列表
        dry_run: 是否预演模式
        
    Returns:
        删除结果
    """
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "delete_alarms_batch",
            "count": len(alarm_ids),
            "message": f"预演模式：将删除 {len(alarm_ids)} 个闹钟"
        }
    
    deleted = []
    failed = []
    
    for alarm_id in alarm_ids:
        result = delete_alarm(alarm_id, dry_run=False)
        if result.get("success"):
            deleted.append(alarm_id)
        else:
            failed.append(alarm_id)
    
    return {
        "success": len(failed) == 0,
        "deleted_count": len(deleted),
        "failed_count": len(failed),
        "deleted": deleted,
        "failed": failed
    }


def run(**kwargs):
    """能力入口"""
    if "alarm_ids" in kwargs:
        return delete_alarms_batch(**kwargs)
    else:
        return delete_alarm(**kwargs)
