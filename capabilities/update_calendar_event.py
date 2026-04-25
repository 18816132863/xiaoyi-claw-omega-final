"""更新日程事件能力"""

from typing import Optional, Dict, Any
import uuid


def update_calendar_event(
    event_id: str,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    location: Optional[str] = None,
    description: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    更新日程事件
    
    Args:
        event_id: 事件ID
        title: 新标题
        start_time: 新开始时间
        end_time: 新结束时间
        location: 新地点
        description: 新描述
        dry_run: 是否预演模式
        
    Returns:
        包含更新结果的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
    
    # 构建更新参数
    updates = {}
    if title:
        updates["title"] = title
    if start_time:
        updates["start_time"] = start_time
    if end_time:
        updates["end_time"] = end_time
    if location:
        updates["location"] = location
    if description:
        updates["description"] = description
    
    if not updates:
        return {
            "success": False,
            "error": "没有提供要更新的字段"
        }
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "update_calendar_event",
            "event_id": event_id,
            "updates": updates,
            "message": "预演模式：将更新日程事件"
        }
    
    # 调用平台适配器
    adapter = XiaoyiAdapter()
    result = adapter.update_calendar_event(
        event_id=event_id,
        updates=updates,
        idempotency_key=f"update_cal_{uuid.uuid4().hex[:16]}"
    )
    
    return result


def run(**kwargs):
    """能力入口"""
    return update_calendar_event(**kwargs)
