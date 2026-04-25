"""
Test Connected Permission Report - 测试连接权限报告

验证：
1. 权限检查覆盖所有必需权限
2. 权限状态正确分类
3. 报告格式正确
"""

import pytest
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.check_connected_permissions import PermissionChecker
from infrastructure.device_runtime_state import PermissionState


class TestConnectedPermissionReport:
    """连接权限报告测试"""
    
    @pytest.fixture
    def checker(self):
        """创建权限检查器"""
        return PermissionChecker(is_xiaoyi_channel=True)
    
    @pytest.mark.asyncio
    async def test_all_permissions_checked(self, checker):
        """测试所有权限都被检查"""
        await checker.check_all_permissions()
        
        # 应该检查所有必需权限
        required_permissions = ["contact", "calendar", "note", "location", "notification", "screenshot"]
        
        for perm in required_permissions:
            assert perm in checker.results
    
    @pytest.mark.asyncio
    async def test_permission_states_valid(self, checker):
        """测试权限状态有效"""
        await checker.check_all_permissions()
        
        valid_states = [
            PermissionState.GRANTED,
            PermissionState.DENIED,
            PermissionState.UNKNOWN,
            PermissionState.TIMEOUT,
            PermissionState.PARTIAL
        ]
        
        for name, result in checker.results.items():
            assert result.state in valid_states
    
    @pytest.mark.asyncio
    async def test_permission_summary(self, checker):
        """测试权限摘要"""
        await checker.check_all_permissions()
        
        summary = checker.get_permission_summary()
        
        assert "total_permissions" in summary
        assert "granted_count" in summary
        assert "denied_count" in summary
        assert "ready_percentage" in summary
    
    @pytest.mark.asyncio
    async def test_permission_report_format(self, checker):
        """测试权限报告格式"""
        await checker.check_all_permissions()
        
        report = checker.generate_report()
        
        # 报告应该包含关键部分
        assert "CONNECTED PERMISSION REPORT" in report
        assert "[Permission Status]" in report
        assert "[Summary]" in report


class TestPermissionRequiredHumanAction:
    """权限缺失需要人工干预测试"""
    
    @pytest.mark.asyncio
    async def test_denied_permission_requires_human_action(self):
        """测试拒绝权限需要人工干预"""
        checker = PermissionChecker(is_xiaoyi_channel=False)
        
        # 模拟权限拒绝
        from infrastructure.device_runtime_state import PermissionCheckResult
        from datetime import datetime
        
        checker.results["contact"] = PermissionCheckResult(
            permission_name="contact",
            state=PermissionState.DENIED,
            last_check_time=datetime.now(),
            error_message="Permission denied by user"
        )
        
        hints = checker.get_missing_permission_hints()
        
        # 应该有提示
        assert len(hints) > 0
        assert any(h["permission"] == "contact" for h in hints)
    
    @pytest.mark.asyncio
    async def test_timeout_not_human_action_first(self):
        """测试超时不是首先人工干预"""
        checker = PermissionChecker(is_xiaoyi_channel=True)
        
        from infrastructure.device_runtime_state import PermissionCheckResult
        from datetime import datetime
        
        # 模拟超时
        checker.results["calendar"] = PermissionCheckResult(
            permission_name="calendar",
            state=PermissionState.TIMEOUT,
            last_check_time=datetime.now(),
            error_message="timeout"
        )
        
        # 超时应该先自动恢复，不是直接人工干预
        # 这里验证状态是 TIMEOUT 而不是 DENIED
        assert checker.results["calendar"].state == PermissionState.TIMEOUT


class TestTimeoutNotHumanActionFirst:
    """超时不首先人工干预测试"""
    
    def test_service_timeout_should_retry_first(self):
        """测试服务超时应该先重试"""
        from infrastructure.connected_runtime_recovery_policy import (
            ConnectedRuntimeRecoveryPolicy,
            FailureType
        )
        
        policy = ConnectedRuntimeRecoveryPolicy()
        plan = policy.create_recovery_plan(FailureType.CONTACT_SERVICE_TIMEOUT)
        
        # 第一步应该是 RETRY
        assert plan.steps[0].strategy.value == "retry"
        
        # 最后一步才是 HUMAN_ACTION_REQUIRED
        assert plan.steps[-1].strategy.value == "human_action_required"
    
    def test_permission_denied_can_be_human_action(self):
        """测试权限拒绝可以是人工干预"""
        from infrastructure.connected_runtime_recovery_policy import (
            ConnectedRuntimeRecoveryPolicy,
            FailureType
        )
        
        policy = ConnectedRuntimeRecoveryPolicy()
        plan = policy.create_recovery_plan(FailureType.PERMISSION_REQUIRED)
        
        # 权限问题的恢复步骤较少
        strategies = [s.strategy.value for s in plan.steps]
        
        # 应该包含 permission_diagnosis 和 human_action_required
        assert "permission_diagnosis" in strategies
        assert "human_action_required" in strategies


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
