"""
解释调用状态能力
根据 normalized_status / confirmed_status 生成用户友好的解释
"""

from typing import Optional, Dict, Any
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.invocation_ledger import get_invocation_by_id


class ExplainInvocationStatus:
    """解释调用状态"""
    
    # 状态解释模板
    EXPLANATIONS = {
        "completed": {
            "title": "操作已完成",
            "description": "该操作已成功执行。",
            "action": "无需额外操作。",
        },
        "queued_for_delivery": {
            "title": "已提交等待处理",
            "description": "请求已提交，正在等待平台处理。",
            "action": "请稍后检查结果。",
        },
        "timeout": {
            "title": "请求超时",
            "description": "请求超时，当前无法确认操作是否已执行。",
            "action": "请检查实际结果，并告知助手以便记录确认状态。",
        },
        "result_uncertain": {
            "title": "结果不确定",
            "description": "操作结果不确定，为避免重复操作，系统未自动重试。",
            "action": "请人工确认实际结果，并告知助手。",
        },
        "auth_required": {
            "title": "需要授权",
            "description": "该能力需要授权才能使用。",
            "action": "请完成授权后再试。",
        },
        "failed": {
            "title": "操作失败",
            "description": "操作执行失败。",
            "action": "可以稍后重试，或联系支持。",
        },
    }
    
    # 确认状态解释
    CONFIRMED_EXPLANATIONS = {
        "confirmed_success": {
            "title": "已确认成功",
            "description": "经人工确认，该操作已成功执行。",
            "action": "无需额外操作。",
        },
        "confirmed_failed": {
            "title": "已确认失败",
            "description": "经人工确认，该操作未能成功执行。",
            "action": "可以手动重试或联系支持。",
        },
        "confirmed_duplicate": {
            "title": "已确认重复",
            "description": "经人工确认，该操作与其他记录重复。",
            "action": "无需额外操作。",
        },
    }
    
    # 能力名称映射
    CAPABILITY_NAMES = {
        "MESSAGE_SENDING": "短信发送",
        "TASK_SCHEDULING": "日程创建",
        "STORAGE": "备忘录",
        "NOTIFICATION": "通知推送",
    }
    
    @staticmethod
    def explain(record_id: int) -> Dict[str, Any]:
        """
        解释指定记录的状态
        
        Args:
            record_id: 记录 ID
        
        Returns:
            dict: 解释结果
        """
        record = get_invocation_by_id(record_id)
        if not record:
            return {
                "found": False,
                "error": f"记录 #{record_id} 不存在",
            }
        
        return ExplainInvocationStatus.explain_record(record)
    
    @staticmethod
    def explain_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        解释记录状态
        
        Args:
            record: 记录字典
        
        Returns:
            dict: 解释结果
        """
        status = record.get("normalized_status", "unknown")
        confirmed_status = record.get("confirmed_status")
        capability = record.get("capability", "unknown")
        
        # 获取基础解释
        if confirmed_status and confirmed_status in ExplainInvocationStatus.CONFIRMED_EXPLANATIONS:
            explanation = ExplainInvocationStatus.CONFIRMED_EXPLANATIONS[confirmed_status].copy()
        elif status in ExplainInvocationStatus.EXPLANATIONS:
            explanation = ExplainInvocationStatus.EXPLANATIONS[status].copy()
        else:
            explanation = {
                "title": "未知状态",
                "description": f"状态: {status}",
                "action": "请联系支持。",
            }
        
        # 添加能力名称
        cap_name = ExplainInvocationStatus.CAPABILITY_NAMES.get(capability, capability)
        
        # 构建完整解释
        result = {
            "found": True,
            "record_id": record.get("id"),
            "capability": capability,
            "capability_name": cap_name,
            "status": status,
            "confirmed_status": confirmed_status,
            "title": f"{cap_name}: {explanation['title']}",
            "description": explanation["description"],
            "action": explanation["action"],
            "created_at": record.get("created_at"),
            "elapsed_ms": record.get("elapsed_ms"),
        }
        
        # 添加确认信息
        if confirmed_status:
            result["confirmed_at"] = record.get("confirmed_at")
            result["confirm_note"] = record.get("confirm_note")
        
        # 添加特殊建议
        if status in ["timeout", "result_uncertain"] and not confirmed_status:
            result["recommendation"] = ExplainInvocationStatus._get_recommendation(capability)
        
        return result
    
    @staticmethod
    def _get_recommendation(capability: str) -> str:
        """获取特殊建议"""
        recommendations = {
            "MESSAGE_SENDING": "请检查手机是否收到短信。",
            "TASK_SCHEDULING": "请检查日历是否有该日程。",
            "STORAGE": "请检查备忘录列表。",
            "NOTIFICATION": "请检查负一屏是否有该通知。",
        }
        return recommendations.get(capability, "请检查实际结果。")
    
    @staticmethod
    def format_explanation(explanation: Dict[str, Any]) -> str:
        """
        格式化解释为用户友好的文本
        
        Args:
            explanation: 解释字典
        
        Returns:
            str: 格式化的文本
        """
        if not explanation.get("found"):
            return explanation.get("error", "记录不存在")
        
        lines = [
            f"📋 {explanation['title']}",
            "",
            f"状态: {explanation['status']}",
            f"时间: {explanation.get('created_at', '未知')}",
            "",
            f"📖 {explanation['description']}",
            "",
            f"💡 {explanation['action']}",
        ]
        
        if explanation.get("recommendation"):
            lines.append("")
            lines.append(f"🔍 {explanation['recommendation']}")
        
        if explanation.get("confirmed_status"):
            lines.append("")
            lines.append(f"✅ 已确认: {explanation['confirmed_status']}")
            if explanation.get("confirm_note"):
                lines.append(f"   备注: {explanation['confirm_note']}")
        
        return "\n".join(lines)


# 便捷函数
def explain_status(record_id: int) -> str:
    """解释状态并返回格式化文本"""
    explanation = ExplainInvocationStatus.explain(record_id)
    return ExplainInvocationStatus.format_explanation(explanation)


def explain_record(record: Dict[str, Any]) -> str:
    """解释记录并返回格式化文本"""
    explanation = ExplainInvocationStatus.explain_record(record)
    return ExplainInvocationStatus.format_explanation(explanation)
