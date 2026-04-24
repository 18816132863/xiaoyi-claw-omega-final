"""取消通知能力"""

from typing import Optional, Dict, Any
import uuid


def cancel_notification(
    notification_id: str,
    reason: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    取消通知
    
    Args:
        notification_id: 通知ID
        reason: 取消原因
        dry_run: 是否预演模式
        
    Returns:
        包含取消结果的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
    
    # 先查询通知状态
    pass
    records = ledger_module.query_by_capability(capability="NOTIFICATION", limit=100)
    
    notification_record = None
    for r in records:
        request_params = r.get("request_params", {})
        if isinstance(request_params, str):
            import json
            try:
                request_params = json.loads(request_params)
            except:
                request_params = {}
        
        if request_params.get("notification_id") == notification_id:
            notification_record = r
            break
    
    if not notification_record:
        return {
            "success": False,
            "cancellable": False,
            "reason": "notification_not_found",
            "message": "通知不存在"
        }
    
    normalized_status = notification_record.get("normalized_status")
    
    # 检查是否可取消
    if normalized_status == "completed":
        return {
            "success": False,
            "cancellable": False,
            "reason": "already_sent",
            "message": "通知已发出，无法取消"
        }
    
    if normalized_status == "auth_required":
        return {
            "success": False,
            "cancellable": False,
            "reason": "auth_required",
            "message": "未授权，无法操作"
        }
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "cancellable": True,
            "action": "cancel_notification",
            "notification_id": notification_id,
            "message": "预演模式：将取消通知"
        }
    
    # 只有 queued_for_delivery 状态可以取消
    if normalized_status == "queued_for_delivery":
        # 调用平台适配器
        adapter = XiaoyiAdapter()
        result = adapter.cancel_notification(
            notification_id=notification_id,
            idempotency_key=f"cancel_notif_{uuid.uuid4().hex[:16]}"
        )
        
        return {
            "success": result.get("success", False),
            "cancellable": True,
            "cancelled": result.get("success", False),
            "notification_id": notification_id,
            "message": "通知已取消" if result.get("success") else "取消失败"
        }
    
    return {
        "success": False,
        "cancellable": False,
        "reason": "unknown_status",
        "message": f"无法确定通知状态: {normalized_status}"
    }


def run(**kwargs):
    """能力入口"""
    return cancel_notification(**kwargs)
