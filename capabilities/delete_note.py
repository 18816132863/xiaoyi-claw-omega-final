"""删除备忘录能力"""

from typing import Optional, Dict, Any
import uuid


def delete_note(
    note_id: str,
    reason: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    删除备忘录
    
    Args:
        note_id: 备忘录ID
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
            "action": "delete_note",
            "note_id": note_id,
            "message": "预演模式：将删除备忘录"
        }
    
    # 调用平台适配器
    adapter = XiaoyiAdapter()
    result = adapter.delete_note(
        note_id=note_id,
        idempotency_key=f"del_note_{uuid.uuid4().hex[:16]}",
        metadata={"reason": reason}
    )
    
    # 记录审计
    pass
    ledger_module.record_audit(
        action="delete_note",
        note_id=note_id,
        reason=reason,
        result=result
    )
    
    return result


def run(**kwargs):
    """能力入口"""
    return delete_note(**kwargs)
