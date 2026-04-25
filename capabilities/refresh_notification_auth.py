"""刷新通知授权能力"""

from typing import Dict, Any


def refresh_notification_auth() -> Dict[str, Any]:
    """
    刷新通知授权状态
    
    Returns:
        包含授权状态的字典
    """
    import subprocess
    import json
    
    # 调用 check_notification_auth.py
    try:
        result = subprocess.run(
            ["python", "scripts/check_notification_auth.py"],
            capture_output=True,
            text=True,
            cwd="/home/sandbox/.openclaw/workspace"
        )
        
        output = result.stdout + result.stderr
        
        # 解析状态
        if "configured" in output.lower():
            status = "configured"
            message = "授权已配置且有效"
        elif "not_configured" in output.lower():
            status = "not_configured"
            message = "授权未配置"
        elif "expired" in output.lower():
            status = "expired"
            message = "授权已过期"
        else:
            status = "unknown"
            message = "无法确定授权状态"
        
        return {
            "success": True,
            "auth_status": status,
            "message": message,
            "raw_output": output[-500:] if len(output) > 500 else output
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "刷新授权状态失败"
        }


def run(**kwargs):
    """能力入口"""
    return refresh_notification_auth()
