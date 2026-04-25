"""检查日程冲突能力"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json


def check_calendar_conflicts(
    start_time: str,
    end_time: str,
    exclude_event_id: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    检查日程冲突
    
    Args:
        start_time: 开始时间
        end_time: 结束时间
        exclude_event_id: 排除的事件ID（用于更新时排除自身）
        title: 标题（检查标题重复）
        
    Returns:
        包含冲突信息的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    
    pass
    
    # 查询所有日程
    records = ledger_module.query_by_capability(capability="TASK_SCHEDULING", limit=200)
    
    conflicts = []
    
    for r in records:
        request_params = r.get("request_params", {})
        if isinstance(request_params, str):
            try:
                request_params = json.loads(request_params)
            except:
                request_params = {}
        
        event_id = request_params.get("event_id")
        
        # 排除指定事件
        if exclude_event_id and event_id == exclude_event_id:
            continue
        
        # 检查时间重叠
        existing_start = request_params.get("start_time")
        existing_end = request_params.get("end_time")
        
        if existing_start and existing_end:
            # 时间重叠检测
            if _times_overlap(start_time, end_time, existing_start, existing_end):
                conflicts.append({
                    "type": "time_overlap",
                    "event_id": event_id,
                    "title": request_params.get("title"),
                    "start_time": existing_start,
                    "end_time": existing_end,
                    "message": f"与 '{request_params.get('title')}' 时间重叠"
                })
        
        # 检查标题重复
        if title and request_params.get("title"):
            if title.lower() == request_params.get("title", "").lower():
                conflicts.append({
                    "type": "title_duplicate",
                    "event_id": event_id,
                    "title": request_params.get("title"),
                    "message": f"标题与现有日程重复: '{title}'"
                })
    
    return {
        "success": True,
        "has_conflicts": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "checked_period": {
            "start_time": start_time,
            "end_time": end_time
        }
    }


def _times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """检查两个时间段是否重叠"""
    try:
        s1 = datetime.fromisoformat(start1.replace("Z", "+00:00"))
        e1 = datetime.fromisoformat(end1.replace("Z", "+00:00"))
        s2 = datetime.fromisoformat(start2.replace("Z", "+00:00"))
        e2 = datetime.fromisoformat(end2.replace("Z", "+00:00"))
        
        # 重叠条件：s1 < e2 AND s2 < e1
        return s1 < e2 and s2 < e1
    except:
        return False


def run(**kwargs):
    """能力入口"""
    return check_calendar_conflicts(**kwargs)
