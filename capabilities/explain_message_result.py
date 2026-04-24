"""解释消息发送结果能力"""

from typing import Dict, Any
from platform_adapter import invocation_ledger as ledger_module
from platform_adapter.user_messages import get_user_message


def explain_message_result(invocation_id: int) -> Dict[str, Any]:
    """
    解释消息发送结果
    
    Args:
        invocation_id: 调用记录ID
        
    Returns:
        包含解释信息的字典
    """
    ledger = ledger_module
    
    records = ledger_module.get_invocation_by_id(invocation_id)
    if not records:
        return {
            "success": False,
            "error": f"未找到记录 #{invocation_id}"
        }
    
    record = records[0] if isinstance(records, list) else records
    
    # 检查是否是消息发送
    if record.get("capability") != "MESSAGE_SENDING":
        return {
            "success": False,
            "error": "只能解释 MESSAGE_SENDING 类型的记录"
        }
    
    normalized_status = record.get("normalized_status", "unknown")
    error_code = record.get("error_code")
    confirmed_status = record.get("confirmed_status")
    
    # 生成用户友好的解释
    explanation = _generate_explanation(
        normalized_status=normalized_status,
        error_code=error_code,
        confirmed_status=confirmed_status
    )
    
    return {
        "success": True,
        "invocation_id": invocation_id,
        "current_status": normalized_status,
        "confirmed_status": confirmed_status,
        "error_code": error_code,
        "is_success": normalized_status == "completed",
        "needs_confirmation": normalized_status == "result_uncertain",
        "explanation": explanation["summary"],
        "details": explanation["details"],
        "next_steps": explanation["next_steps"],
        "user_message": get_user_message(error_code) if error_code else None
    }


def _generate_explanation(
    normalized_status: str,
    error_code: str,
    confirmed_status: str
) -> Dict[str, Any]:
    """生成解释"""
    
    explanations = {
        "completed": {
            "summary": "消息发送成功",
            "details": "消息已成功送达目标设备。",
            "next_steps": ["无需进一步操作"]
        },
        "queued_for_delivery": {
            "summary": "消息正在排队发送",
            "details": "消息已加入发送队列，等待处理。",
            "next_steps": ["稍后查询状态确认是否发送成功"]
        },
        "failed": {
            "summary": "消息发送失败",
            "details": f"发送过程中发生错误: {error_code or '未知错误'}",
            "next_steps": ["检查错误原因", "考虑重发消息"]
        },
        "timeout": {
            "summary": "消息发送超时",
            "details": "发送请求超时，无法确定消息是否送达。",
            "next_steps": ["查询消息状态", "如未送达可考虑重发"]
        },
        "result_uncertain": {
            "summary": "消息发送结果不确定",
            "details": "发送请求已发出，但无法确认是否成功送达。",
            "next_steps": [
                "等待一段时间后查询状态",
                "手动确认发送结果",
                "如确认失败可重发"
            ]
        },
        "auth_required": {
            "summary": "需要授权",
            "details": "消息发送需要授权，请先完成授权流程。",
            "next_steps": ["完成授权后重试"]
        }
    }
    
    base = explanations.get(normalized_status, {
        "summary": f"状态: {normalized_status}",
        "details": "未知状态",
        "next_steps": ["联系支持"]
    })
    
    # 如果已确认，补充确认信息
    if confirmed_status:
        if confirmed_status == "confirmed_success":
            base["summary"] += " (已确认成功)"
            base["next_steps"] = ["无需进一步操作"]
        elif confirmed_status == "confirmed_failed":
            base["summary"] += " (已确认失败)"
            base["next_steps"] = ["考虑重发消息"]
        elif confirmed_status == "confirmed_duplicate":
            base["summary"] += " (已确认重复)"
            base["next_steps"] = ["无需进一步操作"]
    
    return base


def run(**kwargs):
    """能力入口"""
    return explain_message_result(**kwargs)
