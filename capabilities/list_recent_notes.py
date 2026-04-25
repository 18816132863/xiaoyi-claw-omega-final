"""列出最近备忘录能力"""

from typing import Dict, Any
from datetime import datetime, timedelta
import json


def list_recent_notes(
    limit: int = 20,
    days: int = 7,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    列出最近的备忘录
    
    Args:
        limit: 返回数量限制
        days: 查询最近N天
        offset: 偏移量
        
    Returns:
        包含备忘录列表的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    
    pass
    
    # 查询 STORAGE 类型的记录
    records = ledger_module.query_by_capability(capability="STORAGE", limit=100)
    
    # 格式化
    notes = []
    for r in records:
        request_params = r.get("request_params", {})
        if isinstance(request_params, str):
            try:
                request_params = json.loads(request_params)
            except:
                request_params = {}
        
        notes.append({
            "invocation_id": r.get("id"),
            "note_id": request_params.get("note_id"),
            "title": request_params.get("title"),
            "content_preview": request_params.get("content", "")[:50] + "..." if len(request_params.get("content", "")) > 50 else request_params.get("content", ""),
            "status": r.get("normalized_status"),
            "created_at": r.get("created_at"),
        })
    
    # 分页
    paginated = notes[offset:offset + limit]
    
    return {
        "success": True,
        "count": len(paginated),
        "total": len(notes),
        "limit": limit,
        "offset": offset,
        "notes": paginated
    }


def run(**kwargs):
    """能力入口"""
    return list_recent_notes(**kwargs)
