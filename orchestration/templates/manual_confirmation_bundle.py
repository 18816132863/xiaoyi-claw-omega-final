"""人工确认闭环模板"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def manual_confirmation_bundle(
    check_uncertain: bool = True,
    auto_confirm_timeout: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    人工确认闭环模板：查询待确认 -> 用户确认 -> 写入状态 -> 输出结果
    
    Args:
        check_uncertain: 是否检查 uncertain 记录
        auto_confirm_timeout: 是否自动确认超时记录
        dry_run: 是否预演模式
        
    Returns:
        执行结果
    """
    from platform_adapter import invocation_ledger as ledger_module
    from orchestration.workflows.human_confirm import get_pending_confirms, respond_to_confirm
    
    ledger = ledger_module
    
    # 1. 查询待确认记录
    uncertain_records = []
    if check_uncertain:
        records = ledger_module.query_by_status(normalized_status="result_uncertain", limit=50)
        uncertain_records = [
            {
                "invocation_id": r.get("id"),
                "capability": r.get("capability"),
                "created_at": r.get("created_at"),
                "error_code": r.get("error_code")
            }
            for r in records
        ]
    
    # 2. 获取待确认节点
    pending_confirms = get_pending_confirms()
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "预演模式：人工确认闭环",
            "uncertain_count": len(uncertain_records),
            "pending_confirm_count": len(pending_confirms)
        }
    
    # 3. 处理结果
    confirmed = []
    still_pending = []
    
    for confirm in pending_confirms:
        # 这里应该等待用户输入，但在自动化场景下我们只返回待确认列表
        still_pending.append({
            "confirm_id": confirm.get("confirm_id"),
            "invocation_id": confirm.get("invocation_id"),
            "reason": confirm.get("reason"),
            "options": confirm.get("options")
        })
    
    return {
        "success": True,
        "bundle_type": "manual_confirmation",
        "dry_run": dry_run,
        "uncertain_records": uncertain_records,
        "uncertain_count": len(uncertain_records),
        "pending_confirms": still_pending,
        "pending_count": len(still_pending),
        "message": f"发现 {len(uncertain_records)} 条 uncertain 记录，{len(still_pending)} 条待确认",
        "next_steps": [
            "请逐条确认 uncertain 记录",
            "使用 confirm_invocation 能力确认状态"
        ]
    }


def confirm_and_close(
    invocation_id: int,
    confirmed_status: str,
    confirm_note: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    确认并关闭记录
    
    Args:
        invocation_id: 调用记录ID
        confirmed_status: 确认状态
        confirm_note: 确认备注
        dry_run: 是否预演模式
        
    Returns:
        确认结果
    """
    from capabilities.confirm_invocation import confirm_invocation
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"预演模式：将确认记录 #{invocation_id} 为 {confirmed_status}"
        }
    
    result = confirm_invocation(
        invocation_id=invocation_id,
        confirmed_status=confirmed_status,
        confirm_note=confirm_note
    )
    
    return {
        "success": result.get("success", False),
        "invocation_id": invocation_id,
        "confirmed_status": confirmed_status,
        "closed": result.get("success", False),
        "result": result
    }


def run(**kwargs):
    """模板入口"""
    return manual_confirmation_bundle(**kwargs)
