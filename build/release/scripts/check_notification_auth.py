#!/usr/bin/env python
"""
检查 NOTIFICATION 授权状态
输出 configured / not_configured / invalid 三态
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_notification_auth() -> dict:
    """
    检查 NOTIFICATION 授权状态
    
    Returns:
        dict: {
            "status": "configured" | "not_configured" | "invalid",
            "message": str,
            "details": dict
        }
    """
    import os
    
    # 检查环境变量
    auth_code = os.environ.get("XIAOYI_AUTH_CODE", "")
    
    # 检查配置文件
    config_paths = [
        project_root / "config" / "xiaoyi_config.json",
        project_root / ".xiaoyi_auth",
        Path.home() / ".xiaoyi" / "auth_code",
    ]
    
    config_source = None
    
    for path in config_paths:
        if path.exists():
            try:
                if path.suffix == ".json":
                    import json
                    with open(path) as f:
                        config = json.load(f)
                        if "auth_code" in config or "authCode" in config:
                            auth_code = config.get("auth_code") or config.get("authCode")
                            config_source = str(path)
                            break
                else:
                    with open(path) as f:
                        auth_code = f.read().strip()
                        config_source = str(path)
                        break
            except Exception as e:
                pass
    
    # 判断状态
    if not auth_code:
        return {
            "status": "not_configured",
            "message": "authCode 未配置",
            "details": {
                "auth_code_found": False,
                "config_source": None,
                "hint": "请配置 XIAOYI_AUTH_CODE 环境变量或在 config/xiaoyi_config.json 中设置 auth_code",
            }
        }
    
    # 尝试验证 authCode
    try:
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        
        adapter = XiaoyiAdapter()
        adapter._ensure_initialized_sync()
        
        cap = adapter._capabilities.get("NOTIFICATION")
        
        if cap and cap.available:
            return {
                "status": "configured",
                "message": "authCode 已配置且有效",
                "details": {
                    "auth_code_found": True,
                    "config_source": config_source,
                    "capability_available": True,
                    "hint": "NOTIFICATION 能力已就绪",
                }
            }
        else:
            return {
                "status": "invalid",
                "message": "authCode 已配置但无效",
                "details": {
                    "auth_code_found": True,
                    "config_source": config_source,
                    "capability_available": False,
                    "hint": "请检查 authCode 是否正确，或是否已过期",
                }
            }
    except Exception as e:
        return {
            "status": "invalid",
            "message": f"验证失败: {str(e)}",
            "details": {
                "auth_code_found": True,
                "config_source": config_source,
                "error": str(e),
                "hint": "请检查配置和网络连接",
            }
        }


def format_report(result: dict) -> str:
    """格式化报告"""
    lines = [
        "=" * 60,
        "NOTIFICATION 授权状态检查",
        "=" * 60,
        "",
        f"状态: {result['status']}",
        f"说明: {result['message']}",
        "",
        "详细信息:",
        "-" * 40,
    ]
    
    details = result.get("details", {})
    
    if details.get("auth_code_found"):
        lines.append(f"  authCode: 已找到")
        lines.append(f"  来源: {details.get('config_source', '未知')}")
    else:
        lines.append(f"  authCode: 未找到")
    
    if "capability_available" in details:
        lines.append(f"  能力可用: {'是' if details['capability_available'] else '否'}")
    
    if details.get("error"):
        lines.append(f"  错误: {details['error']}")
    
    lines.append("")
    lines.append(f"💡 {details.get('hint', '')}")
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    """主函数"""
    result = check_notification_auth()
    print(format_report(result))
    
    # 返回退出码
    if result["status"] == "configured":
        return 0
    elif result["status"] == "not_configured":
        return 1
    else:  # invalid
        return 2


if __name__ == "__main__":
    sys.exit(main())
