"""删除日程事件能力"""

from typing import Optional, Dict, Any
import uuid


def delete_calendar_event(
    event_id: str,
    reason: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    删除日程事件
    
    Args:
        event_id: 事件ID
        reason: 删除原因
        dry_run: 是否预演模式
        
    Returns:
        包含删除结果的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "delete_calendar_event",
            "event_id": event_id,
            "message": "预演模式：将删除日程事件"
        }
    
    # 调用平台适配器
    adapter = XiaoyiAdapter()
    result = adapter.delete_calendar_event(
        event_id=event_id,
        idempotency_key=f"del_cal_{uuid.uuid4().hex[:16]}",
        metadata={"reason": reason}
    )
    
    # 记录审计
    pass
    ledger_module.record_audit(
        action="delete_calendar_event",
        event_id=event_id,
        reason=reason,
        result=result
    )
    
    # 解释结果
    if result.get("success"):
        result["explanation"] = "日程事件已删除"
    elif result.get("error_code") == "EVENT_NOT_FOUND":
        result["explanation"] = "日程事件不存在或已被删除"
    else:
        result["explanation"] = f"删除失败: {result.get('error', '未知原因')}"
    
    return result


def run(**kwargs):
    """能力入口"""
    return delete_calendar_event(**kwargs)
