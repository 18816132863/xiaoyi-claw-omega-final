"""查询日程事件能力"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json


def query_calendar_event(
    event_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    title: Optional[str] = None,
    start_after: Optional[str] = None,
    start_before: Optional[str] = None,
) -> Dict[str, Any]:
    """
    查询日程事件
    
    Args:
        event_id: 事件ID
        entity_id: 实体ID（用于追踪）
        title: 标题（模糊匹配）
        start_after: 开始时间下限
        start_before: 开始时间上限
        
    Returns:
        包含事件信息的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    
    pass
    
    # 查询 TASK_SCHEDULING 类型的记录
    records = ledger_module.query_by_capability(capability="TASK_SCHEDULING", limit=100)
    
    # 过滤
    filtered = []
    for r in records:
        request_params = r.get("request_params", {})
        if isinstance(request_params, str):
            try:
                request_params = json.loads(request_params)
            except:
                request_params = {}
        
        # 检查 event_id
        if event_id:
            if request_params.get("event_id") != event_id:
                continue
        
        # 检查 entity_id
        if entity_id:
            if request_params.get("entity_id") != entity_id:
                continue
        
        # 检查标题
        if title:
            event_title = request_params.get("title", "")
            if title.lower() not in event_title.lower():
                continue
        
        # 检查时间范围
        start_time = request_params.get("start_time")
        if start_after and start_time:
            if start_time < start_after:
                continue
        if start_before and start_time:
            if start_time > start_before:
                continue
        
        filtered.append({
            "invocation_id": r.get("id"),
            "event_id": request_params.get("event_id"),
            "entity_id": request_params.get("entity_id"),
            "title": request_params.get("title"),
            "start_time": request_params.get("start_time"),
            "end_time": request_params.get("end_time"),
            "status": r.get("status"),
            "normalized_status": r.get("normalized_status"),
            "created_at": r.get("created_at"),
        })
    
    return {
        "success": True,
        "count": len(filtered),
        "events": filtered
    }


def run(**kwargs):
    """能力入口"""
    return query_calendar_event(**kwargs)
