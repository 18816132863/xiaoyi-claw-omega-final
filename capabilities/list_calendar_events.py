"""列出日程事件能力"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json


def list_calendar_events(
    limit: int = 20,
    start_after: Optional[str] = None,
    start_before: Optional[str] = None,
    days: int = 7,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    列出日程事件
    
    Args:
        limit: 返回数量限制
        start_after: 开始时间下限
        start_before: 开始时间上限
        days: 查询最近N天
        offset: 偏移量
        
    Returns:
        包含事件列表的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    
    pass
    
    # 默认时间范围
    if not start_after:
        start_after = datetime.now().isoformat()
    if not start_before:
        start_before = (datetime.now() + timedelta(days=days)).isoformat()
    
    # 查询 TASK_SCHEDULING 类型的记录
    records = ledger_module.query_by_capability(capability="TASK_SCHEDULING", limit=100)
    
    # 过滤和格式化
    events = []
    for r in records:
        request_params = r.get("request_params", {})
        if isinstance(request_params, str):
            try:
                request_params = json.loads(request_params)
            except:
                request_params = {}
        
        start_time = request_params.get("start_time")
        if start_time:
            if start_time < start_after or start_time > start_before:
                continue
        
        events.append({
            "invocation_id": r.get("id"),
            "event_id": request_params.get("event_id"),
            "title": request_params.get("title"),
            "start_time": start_time,
            "end_time": request_params.get("end_time"),
            "location": request_params.get("location"),
            "status": r.get("normalized_status"),
            "created_at": r.get("created_at"),
        })
    
    # 分页
    paginated = events[offset:offset + limit]
    
    return {
        "success": True,
        "count": len(paginated),
        "total": len(events),
        "limit": limit,
        "offset": offset,
        "events": paginated
    }


def run(**kwargs):
    """能力入口"""
    return list_calendar_events(**kwargs)
