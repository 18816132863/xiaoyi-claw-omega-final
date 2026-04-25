"""重发消息能力"""

import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from platform_adapter import invocation_ledger as ledger_module
from platform_adapter.xiaoyi_adapter import XiaoyiAdapter


def resend_message(
    original_invocation_id: int,
    reason: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    重发消息
    
    Args:
        original_invocation_id: 原始调用记录ID
        reason: 重发原因
        dry_run: 是否预演模式
        
    Returns:
        包含重发结果的字典
    """
    ledger = ledger_module
    
    # 查询原始记录
    original = ledger_module.get_invocation_by_id(original_invocation_id)
    if not original:
        return {
            "success": False,
            "error": f"未找到原始记录 #{original_invocation_id}",
            "action": "resend_message"
        }
    
    original_record = original[0] if isinstance(original, list) else original
    
    # 检查原始记录是否是消息发送
    if original_record.get("capability") != "MESSAGE_SENDING":
        return {
            "success": False,
            "error": "只能重发 MESSAGE_SENDING 类型的记录",
            "original_capability": original_record.get("capability")
        }
    
    # 解析原始请求参数
    request_params = original_record.get("request_params", {})
    if isinstance(request_params, str):
        import json
        try:
            request_params = json.loads(request_params)
        except:
            request_params = {}
    
    # 生成新的幂等键（重发需要新键）
    new_idempotency_key = f"resend_{uuid.uuid4().hex[:16]}"
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "resend_message",
            "original_invocation_id": original_invocation_id,
            "new_idempotency_key": new_idempotency_key,
            "message": "预演模式：将重发消息",
            "original_status": original_record.get("normalized_status"),
            "reason": reason
        }
    
    # 执行重发
    adapter = XiaoyiAdapter()
    result = adapter.send_message(
        to=request_params.get("to"),
        message=request_params.get("message"),
        idempotency_key=new_idempotency_key,
        metadata={
            "resend_from": original_invocation_id,
            "resend_reason": reason,
            "resend_at": datetime.now().isoformat()
        }
    )
    
    # 记录审计
    result["resend_from"] = original_invocation_id
    result["resend_reason"] = reason
    
    return result


def run(**kwargs):
    """能力入口"""
    return resend_message(**kwargs)
