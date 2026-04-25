"""解释通知授权状态能力"""

from typing import Dict, Any


def explain_notification_auth_state() -> Dict[str, Any]:
    """
    解释通知授权状态
    
    Returns:
        包含授权状态解释的字典
    """
    from capabilities.refresh_notification_auth import refresh_notification_auth
    
    # 获取当前状态
    auth_result = refresh_notification_auth()
    status = auth_result.get("auth_status", "unknown")
    
    # 生成用户友好的解释
    explanations = {
        "configured": {
            "summary": "通知授权已配置",
            "details": "您的设备已授权接收通知推送。",
            "can_send_notifications": True,
            "next_steps": ["可以直接发送通知", "无需额外操作"]
        },
        "not_configured": {
            "summary": "通知授权未配置",
            "details": "您尚未授权接收通知推送。需要配置授权后才能发送通知。",
            "can_send_notifications": False,
            "next_steps": [
                "请在设备上打开小艺设置",
                "找到通知权限设置",
                "开启通知授权",
                "完成后重新检查状态"
            ]
        },
        "expired": {
            "summary": "通知授权已过期",
            "details": "您的通知授权已过期，需要重新授权。",
            "can_send_notifications": False,
            "next_steps": [
                "请重新进行授权流程",
                "授权完成后重新检查状态"
            ]
        },
        "unknown": {
            "summary": "无法确定授权状态",
            "details": "系统无法确定当前的通知授权状态。",
            "can_send_notifications": False,
            "next_steps": [
                "请稍后重试",
                "如问题持续，请联系支持"
            ]
        }
    }
    
    explanation = explanations.get(status, explanations["unknown"])
    
    return {
        "success": True,
        "auth_status": status,
        "summary": explanation["summary"],
        "details": explanation["details"],
        "can_send_notifications": explanation["can_send_notifications"],
        "next_steps": explanation["next_steps"]
    }


def run(**kwargs):
    """能力入口"""
    return explain_notification_auth_state()
