#!/usr/bin/env python3
"""
Visual Probe Smoke - 视觉探测冒烟测试

测试视觉相关能力：
- 截图能力
- 读屏能力
- 图像理解能力
- GUI Agent 能力

基于新的设备状态判断逻辑
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
    DeviceRuntimeStateChecker,
    CapabilityState,
    PermissionState
)
from infrastructure.connected_runtime_recovery_policy import (
    ConnectedRuntimeRecoveryPolicy,
    TaskProgressTracker,
    ProbeMode
)


class VisualProbeSmokeTest:
    """视觉探测冒烟测试"""
    
    # 视觉能力列表
    VISUAL_CAPABILITIES = [
        {
            "name": "screenshot",
            "display_name": "截图能力",
            "permission": "screenshot",
            "tool": "get_photo_tool_schema",
            "risk_level": "L2"
        },
        {
            "name": "screen_reader",
            "display_name": "读屏能力",
            "permission": "screenshot",
            "tool": "image_reading",
            "risk_level": "L2"
        },
        {
            "name": "image_understanding",
            "display_name": "图像理解能力",
            "permission": "screenshot",
            "tool": "image_reading",
            "risk_level": "L1"
        },
        {
            "name": "gui_agent",
            "display_name": "GUI Agent 能力",
            "permission": "screenshot",
            "tool": "xiaoyi_gui_agent",
            "risk_level": "L3"
        }
    ]
    
    def __init__(self, is_xiaoyi_channel: bool = True):
        self.is_xiaoyi_channel = is_xiaoyi_channel
        self.state_checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=is_xiaoyi_channel)
        self.recovery_policy = ConnectedRuntimeRecoveryPolicy()
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.progress_tracker: Optional[TaskProgressTracker] = None
    
    async def setup(self):
        """初始化"""
        self.progress_tracker = TaskProgressTracker("visual_probe_smoke", timeout_seconds=180.0)
        self.progress_tracker.update_progress("init", "Starting visual probe smoke test")
    
    async def check_visual_permissions(self) -> Dict[str, Any]:
        """检查视觉相关权限"""
        self.progress_tracker.update_progress("permission_check", "Checking visual permissions")
        
        results = {}
        for cap in self.VISUAL_CAPABILITIES:
            perm_name = cap["permission"]
            
            # 检查权限
            perm_result = await self.state_checker.check_permission(perm_name)
            
            results[cap["name"]] = {
                "permission": perm_name,
                "state": perm_result.state.value,
                "is_granted": perm_result.state == PermissionState.GRANTED
            }
        
        self.test_results["permissions"] = results
        return results
    
    async def test_visual_capabilities(self) -> Dict[str, Any]:
        """测试视觉能力"""
        self.progress_tracker.update_progress("capability_test", "Testing visual capabilities")
        
        results = {}
        for cap in self.VISUAL_CAPABILITIES:
            result = await self._test_single_capability(cap)
            results[cap["name"]] = result
            
            # 记录到恢复策略
            self.recovery_policy.l0_adjustment.record_result(result["success"])
        
        self.test_results["capabilities"] = results
        return results
    
    async def _test_single_capability(self, cap: Dict[str, Any]) -> Dict[str, Any]:
        """测试单个视觉能力"""
        result = {
            "name": cap["name"],
            "display_name": cap["display_name"],
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "status": "unknown",
            "response_time_ms": 0,
            "error_type": None,
            "error_message": None,
            "risk_level": cap["risk_level"]
        }
        
        import time
        start = time.time()
        
        try:
            # 检查超时状态
            timeout_status = self.progress_tracker.check_timeout()
            if timeout_status["action"] != "continue":
                result["status"] = f"timeout_{timeout_status['action']}"
                result["error_type"] = "progress_timeout"
                return result
            
            # 检查权限
            perm_result = await self.state_checker.check_permission(cap["permission"])
            if perm_result.state != PermissionState.GRANTED:
                result["status"] = "permission_required"
                result["error_type"] = "permission_denied"
                result["error_message"] = f"Permission {cap['permission']} not granted"
                return result
            
            # 检查能力服务
            cap_result = await self.state_checker.check_capability(cap["name"])
            
            if cap_result.state == CapabilityState.READY:
                result["success"] = True
                result["status"] = "ready"
            elif cap_result.state == CapabilityState.TIMEOUT:
                result["status"] = "timeout"
                result["error_type"] = "service_timeout"
                result["error_message"] = cap_result.error_message
            else:
                result["status"] = cap_result.state.value
                result["error_message"] = cap_result.error_message
        
        except asyncio.TimeoutError:
            result["status"] = "timeout"
            result["error_type"] = "service_timeout"
            result["error_message"] = f"Capability {cap['name']} timed out"
        
        except Exception as e:
            error_msg = str(e)
            result["error_message"] = error_msg
            
            if "permission" in error_msg.lower():
                result["status"] = "permission_required"
                result["error_type"] = "permission_denied"
            elif "timeout" in error_msg.lower():
                result["status"] = "timeout"
                result["error_type"] = "service_timeout"
            else:
                result["status"] = "error"
                result["error_type"] = "unknown_error"
        
        result["response_time_ms"] = (time.time() - start) * 1000
        return result
    
    def generate_report(self) -> str:
        """生成报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("VISUAL PROBE SMOKE TEST REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        # 环境
        lines.append("[Environment]")
        lines.append(f"  is_xiaoyi_channel: {self.is_xiaoyi_channel}")
        lines.append(f"  probe_mode: {self.recovery_policy.get_current_probe_mode().value}")
        lines.append(f"  l0_success_rate: {self.recovery_policy.get_success_rate():.1%}")
        lines.append("")
        
        # 权限状态
        if "permissions" in self.test_results:
            lines.append("[Visual Permissions]")
            for name, perm in self.test_results["permissions"].items():
                icon = "✓" if perm["is_granted"] else "✗"
                lines.append(f"  {icon} {name}: {perm['state']}")
            lines.append("")
        
        # 能力状态
        if "capabilities" in self.test_results:
            lines.append("[Visual Capabilities]")
            for name, cap in self.test_results["capabilities"].items():
                icon = "✓" if cap["success"] else "✗"
                status = cap["status"]
                rt = cap.get("response_time_ms", 0)
                risk = cap.get("risk_level", "?")
                lines.append(f"  {icon} {name} ({risk}): {status} ({rt:.1f}ms)")
                if cap.get("error_message"):
                    lines.append(f"      Error: {cap['error_message']}")
            lines.append("")
        
        # 统计
        lines.append("[Statistics]")
        total = len(self.VISUAL_CAPABILITIES)
        passed = sum(1 for c in self.test_results.get("capabilities", {}).values() if c["success"])
        lines.append(f"  total_capabilities: {total}")
        lines.append(f"  passed: {passed}")
        lines.append(f"  failed: {total - passed}")
        lines.append(f"  pass_rate: {passed / total * 100:.1f}%" if total > 0 else "  pass_rate: N/A")
        lines.append("")
        
        # 进度
        if self.progress_tracker:
            timeout_status = self.progress_tracker.check_timeout()
            lines.append("[Progress]")
            lines.append(f"  elapsed_seconds: {timeout_status['elapsed_seconds']:.1f}")
            lines.append(f"  current_stage: {self.progress_tracker.current_stage}")
            lines.append("")
        
        return "\n".join(lines)


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visual probe smoke test")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-xiaoyi", action="store_true", help="Not in Xiaoyi channel")
    args = parser.parse_args()
    
    is_xiaoyi = not args.no_xiaoyi
    tester = VisualProbeSmokeTest(is_xiaoyi_channel=is_xiaoyi)
    
    # 执行测试
    await tester.setup()
    await tester.check_visual_permissions()
    await tester.test_visual_capabilities()
    
    # 输出结果
    if args.json:
        print(json.dumps(tester.test_results, indent=2, ensure_ascii=False))
    else:
        print(tester.generate_report())
    
    # 返回码
    passed = sum(1 for c in tester.test_results.get("capabilities", {}).values() if c["success"])
    if passed >= len(tester.VISUAL_CAPABILITIES) * 0.75:
        return 0
    elif passed > 0:
        return 1
    else:
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
