"""查询通知状态能力"""

from typing import Optional, Dict, Any
import json


def query_notification_status(
    notification_id: Optional[str] = None,
    task_id: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    查询通知状态
    
    Args:
        notification_id: 通知ID
        task_id: 任务ID
        limit: 返回数量限制
        
    Returns:
        包含通知状态的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    
    pass
    
    # 查询 NOTIFICATION 类型的记录
    records = ledger_module.query_by_capability(capability="NOTIFICATION", limit=100)
    
    # 过滤
    filtered = []
    for r in records:
        request_params = r.get("request_params", {})
        if isinstance(request_params, str):
            try:
                request_params = json.loads(request_params)
            except:
                request_params = {}
        
        if notification_id:
            if request_params.get("notification_id") != notification_id:
                continue
        
        if task_id:
            if r.get("task_id") != task_id:
                continue
        
        filtered.append({
            "invocation_id": r.get("id"),
            "notification_id": request_params.get("notification_id"),
            "title": request_params.get("title"),
            "status": r.get("status"),
            "normalized_status": r.get("normalized_status"),
            "created_at": r.get("created_at"),
            "error_code": r.get("error_code"),
        })
    
    return {
        "success": True,
        "count": len(filtered[:limit]),
        "notifications": filtered[:limit]
    }


def run(**kwargs):
    """能力入口"""
    return query_notification_status(**kwargs)
