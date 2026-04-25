"""
Test Connected Route Smoke - 测试连接路由冒烟测试
"""

import pytest
import asyncio

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.connected_route_smoke import ConnectedRouteSmokeTest


class TestConnectedRouteSmokeTest:
    """测试连接路由冒烟测试"""
    
    @pytest.mark.asyncio
    async def test_setup(self):
        """测试初始化"""
        tester = ConnectedRouteSmokeTest(is_xiaoyi_channel=True)
        await tester.setup()
        
        assert tester.progress_tracker is not None
        assert tester.progress_tracker.current_stage == "init"
    
    @pytest.mark.asyncio
    async def test_check_device_state(self):
        """测试设备状态检查"""
        tester = ConnectedRouteSmokeTest(is_xiaoyi_channel=True)
        await tester.setup()
        
        state = await tester.check_device_state()
        
        # 小艺连接端应该显示 session_connected
        assert "device_state" in tester.test_results
        assert "session_connected=true" in tester.test_results["device_state"]["summary"]
    
    @pytest.mark.asyncio
    async def test_safe_routes(self):
        """测试安全路由"""
        tester = ConnectedRouteSmokeTest(is_xiaoyi_channel=True)
        await tester.setup()
        await tester.check_device_state()
        
        results = await tester.test_safe_routes()
        
        assert "safe_routes" in tester.test_results
        assert len(results) == len(tester.SAFE_ROUTES)
    
    @pytest.mark.asyncio
    async def test_full_smoke_test(self):
        """测试完整冒烟测试"""
        tester = ConnectedRouteSmokeTest(is_xiaoyi_channel=True)
        
        await tester.setup()
        await tester.check_device_state()
        await tester.test_safe_routes()
        await tester.test_confirm_routes()
        await tester.test_strong_confirm_routes()
        
        # 应该有所有测试结果
        assert "device_state" in tester.test_results
        assert "safe_routes" in tester.test_results
        assert "confirm_routes" in tester.test_results
        assert "strong_confirm_routes" in tester.test_results
    
    def test_generate_report(self):
        """测试生成报告"""
        tester = ConnectedRouteSmokeTest(is_xiaoyi_channel=True)
        tester.test_results = {
            "device_state": {
                "summary": "session_connected=true, connected_runtime=partial",
                "is_fully_ready": False,
                "is_partial_ready": True,
                "failure_breakdown": {"session_issues": [], "bridge_issues": []}
            },
            "safe_routes": {
                "route.query_note": {"success": True, "status": "reachable"}
            }
        }
        
        report = tester.generate_report()
        
        assert "CONNECTED ROUTE SMOKE TEST REPORT" in report
        assert "session_connected=true" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
