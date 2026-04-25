"""查询消息发送状态能力"""

from typing import Optional, Dict, Any
from platform_adapter import invocation_ledger as ledger_module


def query_message_status(
    task_id: Optional[str] = None,
    task_run_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    invocation_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    查询消息发送状态
    
    Args:
        task_id: 任务ID
        task_run_id: 任务运行ID
        idempotency_key: 幂等键
        invocation_id: 调用记录ID
        
    Returns:
        包含状态信息的字典
    """
    ledger = ledger_module
    
    # 枹据不同查询条件查询
    if invocation_id:
        records = ledger_module.get_invocation_by_id(invocation_id)
    elif idempotency_key:
        records = ledger_module.get_invocation_by_idempotency_key(idempotency_key)
    elif task_id:
        records = ledger_module.query_by_task_id(task_id)
    elif task_run_id:
        records = ledger.query_by_task_run_id(task_run_id)
    else:
        return {
            "success": False,
            "error": "必须提供至少一个查询条件",
            "records": []
        }
    
    if not records:
        return {
            "success": True,
            "found": False,
            "message": "未找到匹配的记录",
            "records": []
        }
    
    # 格式化输出
    formatted_records = []
    for r in records:
        formatted_records.append({
            "invocation_id": r.get("id"),
            "capability": r.get("capability"),
            "status": r.get("status"),
            "normalized_status": r.get("normalized_status"),
            "confirmed_status": r.get("confirmed_status"),
            "created_at": r.get("created_at"),
            "error_code": r.get("error_code"),
            "error_message": r.get("error_message"),
            "idempotency_key": r.get("idempotency_key"),
            "task_id": r.get("task_id"),
            "task_run_id": r.get("task_run_id"),
        })
    
    return {
        "success": True,
        "found": True,
        "count": len(formatted_records),
        "records": formatted_records
    }


def run(**kwargs):
    """能力入口"""
    return query_message_status(**kwargs)
