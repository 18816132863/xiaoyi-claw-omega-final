"""
用户可见消息
统一给用户返回的话术
"""

from typing import Optional


# 用户消息模板
USER_MESSAGES = {
    # 成功
    "completed": "已完成",
    
    # 已提交等待处理
    "queued_for_delivery": "已提交，等待平台处理",
    
    # 超时
    "timeout": "请求超时，当前无法确认是否已执行，请稍后检查结果",
    
    # 结果不确定
    "result_uncertain": "结果未知，为避免重复操作，系统未自动重试，请人工确认",
    
    # 授权缺失
    "auth_required": "该能力未授权，请先完成授权后再试",
    
    # 能力未接通
    "not_available": "该能力当前不可用",
    
    # 平台失败
    "failed": "操作失败，请稍后重试",
    
    # fallback 已使用
    "fallback_used": "平台能力当前不可直接调用，已转入待处理队列",
}


def get_user_message(
    status: str,
    error_code: Optional[str] = None,
) -> str:
    """
    获取用户可见消息
    
    Args:
        status: 状态
        error_code: 错误码
    
    Returns:
        str: 用户消息
    """
    # 根据状态获取基础消息
    base_message = USER_MESSAGES.get(status, "操作完成")
    
    # 根据错误码调整
    if error_code:
        if "AUTH" in error_code:
            return USER_MESSAGES["auth_required"]
        if "TIMEOUT" in error_code:
            return USER_MESSAGES["timeout"]
        if "UNCERTAIN" in error_code:
            return USER_MESSAGES["result_uncertain"]
        if "FALLBACK" in error_code:
            return USER_MESSAGES["fallback_used"]
    
    return base_message


def format_user_result(
    capability: str,
    status: str,
    error_code: Optional[str] = None,
    details: Optional[str] = None,
) -> str:
    """
    格式化用户结果
    
    Args:
        capability: 能力名称
        status: 状态
        error_code: 错误码
        details: 额外细节
    
    Returns:
        str: 格式化的用户结果
    """
    message = get_user_message(status, error_code)
    
    # 能力名称映射
    capability_names = {
        "MESSAGE_SENDING": "短信发送",
        "TASK_SCHEDULING": "日程创建",
        "STORAGE": "备忘录",
        "NOTIFICATION": "通知推送",
    }
    
    cap_name = capability_names.get(capability, capability)
    
    result = f"{cap_name}: {message}"
    
    if details:
        result += f" ({details})"
    
    return result
