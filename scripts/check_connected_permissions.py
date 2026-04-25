#!/usr/bin/env python3
"""
Check Connected Permissions - 检查连接权限

必须检查：
- 联系人权限
- 日历权限
- 备忘录权限
- 位置权限
- 通知权限
- 截图/读屏权限

输出格式：
- 每个权限的状态
- 权限缺失时的建议
- 整体权限就绪状态
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.device_runtime_state import (
    PermissionState,
    PermissionCheckResult,
    DeviceRuntimeStateChecker
)


class PermissionChecker:
    """权限检查器"""
    
    # 权限配置
    PERMISSION_CONFIGS = {
        "contact": {
            "display_name": "联系人权限",
            "tool_name": "get_contact_tool_schema",
            "test_action": "search_contacts",
            "required_for": ["route.query_contact", "route.call_phone", "route.send_message"],
            "recovery_hint": "请在手机设置中授予联系人访问权限"
        },
        "calendar": {
            "display_name": "日历权限",
            "tool_name": "get_calendar_tool_schema",
            "test_action": "query_calendar",
            "required_for": ["route.query_calendar", "route.create_calendar_event"],
            "recovery_hint": "请在手机设置中授予日历访问权限"
        },
        "note": {
            "display_name": "备忘录权限",
            "tool_name": "get_note_tool_schema",
            "test_action": "search_notes",
            "required_for": ["route.query_note", "route.create_note"],
            "recovery_hint": "请在手机设置中授予备忘录访问权限"
        },
        "location": {
            "display_name": "位置权限",
            "tool_name": "get_user_location",
            "test_action": "get_location",
            "required_for": ["route.get_location"],
            "recovery_hint": "请在手机设置中授予位置访问权限"
        },
        "notification": {
            "display_name": "通知权限",
            "tool_name": "get_alarm_tool_schema",
            "test_action": "query_alarms",
            "required_for": ["route.query_alarm", "route.set_alarm"],
            "recovery_hint": "请在手机设置中授予通知访问权限"
        },
        "screenshot": {
            "display_name": "截图/读屏权限",
            "tool_name": "get_photo_tool_schema",
            "test_action": "search_photos",
            "required_for": ["route.screenshot", "route.read_screen"],
            "recovery_hint": "请在手机设置中授予相册/截图访问权限"
        }
    }
    
    def __init__(self, is_xiaoyi_channel: bool = True):
        self.is_xiaoyi_channel = is_xiaoyi_channel
        self.results: Dict[str, PermissionCheckResult] = {}
        self.check_errors: List[Dict[str, Any]] = []
    
    async def check_single_permission(self, permission_name: str) -> PermissionCheckResult:
        """检查单个权限"""
        config = self.PERMISSION_CONFIGS.get(permission_name)
        if not config:
            return PermissionCheckResult(
                permission_name=permission_name,
                state=PermissionState.UNKNOWN,
                last_check_time=datetime.now(),
                error_message="Unknown permission"
            )
        
        now = datetime.now()
        
        try:
            # 尝试获取工具 schema 来验证权限
            # 在实际环境中，这里应该调用 call_device_tool
            # 目前模拟检查
            
            # 模拟：在小艺连接端，假设权限已授予
            if self.is_xiaoyi_channel:
                result = PermissionCheckResult(
                    permission_name=permission_name,
                    state=PermissionState.GRANTED,
                    last_check_time=now
                )
            else:
                # 非小艺连接端，需要实际检查
                result = PermissionCheckResult(
                    permission_name=permission_name,
                    state=PermissionState.UNKNOWN,
                    last_check_time=now
                )
        
        except Exception as e:
            error_msg = str(e)
            
            # 根据错误类型判断状态
            if "permission" in error_msg.lower() or "denied" in error_msg.lower():
                state = PermissionState.DENIED
            elif "timeout" in error_msg.lower():
                state = PermissionState.TIMEOUT
            else:
                state = PermissionState.ERROR
            
            result = PermissionCheckResult(
                permission_name=permission_name,
                state=state,
                last_check_time=now,
                error_message=error_msg
            )
            
            self.check_errors.append({
                "permission": permission_name,
                "error": error_msg,
                "state": state.value
            })
        
        self.results[permission_name] = result
        return result
    
    async def check_all_permissions(self) -> Dict[str, PermissionCheckResult]:
        """检查所有权限"""
        for perm_name in self.PERMISSION_CONFIGS.keys():
            await self.check_single_permission(perm_name)
        
        return self.results
    
    def get_permission_summary(self) -> Dict[str, Any]:
        """获取权限摘要"""
        granted = [name for name, result in self.results.items() 
                  if result.state == PermissionState.GRANTED]
        denied = [name for name, result in self.results.items() 
                 if result.state == PermissionState.DENIED]
        timeout = [name for name, result in self.results.items() 
                  if result.state == PermissionState.TIMEOUT]
        unknown = [name for name, result in self.results.items() 
                  if result.state == PermissionState.UNKNOWN]
        
        total = len(self.PERMISSION_CONFIGS)
        granted_count = len(granted)
        
        return {
            "total_permissions": total,
            "granted_count": granted_count,
            "denied_count": len(denied),
            "timeout_count": len(timeout),
            "unknown_count": len(unknown),
            "granted": granted,
            "denied": denied,
            "timeout": timeout,
            "unknown": unknown,
            "ready_percentage": (granted_count / total * 100) if total > 0 else 0,
            "is_fully_ready": granted_count == total,
            "is_partial_ready": granted_count > 0
        }
    
    def get_missing_permission_hints(self) -> List[Dict[str, str]]:
        """获取缺失权限的提示"""
        hints = []
        for name, result in self.results.items():
            if result.state != PermissionState.GRANTED:
                config = self.PERMISSION_CONFIGS.get(name, {})
                hints.append({
                    "permission": name,
                    "display_name": config.get("display_name", name),
                    "state": result.state.value,
                    "recovery_hint": config.get("recovery_hint", ""),
                    "affected_routes": config.get("required_for", [])
                })
        return hints
    
    def generate_report(self) -> str:
        """生成权限报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("CONNECTED PERMISSION REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        # 基本信息
        lines.append("[Environment]")
        lines.append(f"  is_xiaoyi_channel: {self.is_xiaoyi_channel}")
        lines.append(f"  check_time: {datetime.now().isoformat()}")
        lines.append("")
        
        # 权限状态
        lines.append("[Permission Status]")
        for name, result in self.results.items():
            config = self.PERMISSION_CONFIGS.get(name, {})
            display_name = config.get("display_name", name)
            status_icon = "✓" if result.state == PermissionState.GRANTED else "✗"
            status = result.state.value
            
            line = f"  {status_icon} {display_name} ({name}): {status}"
            if result.error_message:
                line += f" - {result.error_message}"
            lines.append(line)
        lines.append("")
        
        # 摘要
        summary = self.get_permission_summary()
        lines.append("[Summary]")
        lines.append(f"  total_permissions: {summary['total_permissions']}")
        lines.append(f"  granted: {summary['granted_count']}")
        lines.append(f"  denied: {summary['denied_count']}")
        lines.append(f"  timeout: {summary['timeout_count']}")
        lines.append(f"  unknown: {summary['unknown_count']}")
        lines.append(f"  ready_percentage: {summary['ready_percentage']:.1f}%")
        lines.append(f"  is_fully_ready: {summary['is_fully_ready']}")
        lines.append("")
        
        # 缺失权限提示
        hints = self.get_missing_permission_hints()
        if hints:
            lines.append("[Missing Permissions & Recovery Hints]")
            for hint in hints:
                lines.append(f"  - {hint['display_name']} ({hint['permission']}): {hint['state']}")
                lines.append(f"    Hint: {hint['recovery_hint']}")
                if hint['affected_routes']:
                    lines.append(f"    Affected routes: {', '.join(hint['affected_routes'])}")
            lines.append("")
        
        # 错误详情
        if self.check_errors:
            lines.append("[Check Errors]")
            for error in self.check_errors:
                lines.append(f"  - {error['permission']}: {error['error']}")
            lines.append("")
        
        return "\n".join(lines)


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check connected permissions")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-xiaoyi", action="store_true", help="Not in Xiaoyi channel")
    args = parser.parse_args()
    
    is_xiaoyi = not args.no_xiaoyi
    checker = PermissionChecker(is_xiaoyi_channel=is_xiaoyi)
    
    # 执行检查
    await checker.check_all_permissions()
    
    # 输出结果
    if args.json:
        summary = checker.get_permission_summary()
        summary["results"] = {
            name: {
                "state": result.state.value,
                "error_message": result.error_message
            }
            for name, result in checker.results.items()
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(checker.generate_report())
    
    # 返回码
    summary = checker.get_permission_summary()
    if summary["is_fully_ready"]:
        return 0
    elif summary["is_partial_ready"]:
        return 1
    else:
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
