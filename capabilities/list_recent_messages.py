"""列出最近消息能力"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from platform_adapter import invocation_ledger as ledger_module


def list_recent_messages(
    limit: int = 20,
    status: Optional[str] = None,
    normalized_status: Optional[str] = None,
    confirmed_status: Optional[str] = None,
    days: int = 7,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    列出最近的消息发送记录
    
    Args:
        limit: 返回数量限制
        status: 按原始状态过滤
        normalized_status: 按归一化状态过滤
        confirmed_status: 按确认状态过滤
        days: 查询最近N天
        offset: 偏移量
        
    Returns:
        包含消息列表的字典
    """
    ledger = ledger_module
    
    # 构建查询条件
    since = datetime.now() - timedelta(days=days)
    
    records = ledger_module.query_by_capability(
        capability="MESSAGE_SENDING",
        limit=limit + offset
    )
    
    # 过滤
    filtered = []
    for r in records:
        if status and r.get("status") != status:
            continue
        if normalized_status and r.get("normalized_status") != normalized_status:
            continue
        if confirmed_status and r.get("confirmed_status") != confirmed_status:
            continue
        filtered.append(r)
    
    # 分页
    paginated = filtered[offset:offset + limit]
    
    # 格式化输出
    formatted = []
    for r in paginated:
        formatted.append({
            "invocation_id": r.get("id"),
            "status": r.get("status"),
            "normalized_status": r.get("normalized_status"),
            "confirmed_status": r.get("confirmed_status"),
            "created_at": r.get("created_at"),
            "error_code": r.get("error_code"),
            "has_error": bool(r.get("error_code")),
        })
    
    return {
        "success": True,
        "count": len(formatted),
        "total": len(filtered),
        "limit": limit,
        "offset": offset,
        "messages": formatted
    }


def run(**kwargs):
    """能力入口"""
    return list_recent_messages(**kwargs)
