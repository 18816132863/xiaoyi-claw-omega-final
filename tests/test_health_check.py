"""
测试健康巡检脚本
"""

import pytest
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestHealthCheck:
    """测试健康巡检"""
    
    def test_health_check_runs(self):
        """测试健康巡检可以运行"""
        result = subprocess.run(
            ["python", "scripts/platform_health_check.py"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        # 应该成功运行
        assert result.returncode in [0, 1]  # 0=健康, 1=有问题
        
        # 应该有输出
        assert len(result.stdout) > 0
    
    def test_health_check_output_format(self):
        """测试输出格式"""
        result = subprocess.run(
            ["python", "scripts/platform_health_check.py"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        # 应该包含关键部分
        assert "平台健康巡检报告" in result.stdout
        assert "总体统计" in result.stdout
        assert "24 小时统计" in result.stdout
        assert "NOTIFICATION 授权状态" in result.stdout
        assert "健康评估" in result.stdout


class TestHealthCheckFunctions:
    """测试健康巡检函数"""
    
    def test_run_health_check(self):
        """测试运行健康检查"""
        from scripts.platform_health_check import run_health_check
        
        report = run_health_check()
        
        # 应该包含所有关键字段
        assert "timestamp" in report
        assert "total_invocations" in report
        assert "uncertain_count" in report
        assert "unconfirmed_uncertain_count" in report
        assert "failed_rate_24h" in report
        assert "timeout_rate_24h" in report
        assert "notification_auth_status" in report
        assert "by_status" in report
    
    def test_format_health_report(self):
        """测试格式化健康报告"""
        from scripts.platform_health_check import format_health_report
        
        report = {
            "timestamp": "2026-04-24T14:00:00",
            "total_invocations": 1000,
            "uncertain_count": 50,
            "unconfirmed_uncertain_count": 10,
            "failed_rate_24h": 2.5,
            "timeout_rate_24h": 1.8,
            "notification_auth_status": "configured",
            "notification_auth_message": "authCode 已配置",
            "by_status": {
                "completed": 900,
                "failed": 50,
                "timeout": 50,
            },
        }
        
        output = format_health_report(report)
        
        assert "平台健康巡检报告" in output
        assert "1000" in output
        assert "2.50%" in output
        assert "1.80%" in output
    
    def test_get_notification_auth_status(self):
        """测试获取 NOTIFICATION 授权状态"""
        from scripts.platform_health_check import get_notification_auth_status
        
        status = get_notification_auth_status()
        
        assert "status" in status
        assert "message" in status
        assert status["status"] in ["configured", "not_configured"]


class TestHealthCheckThresholds:
    """测试健康检查阈值"""
    
    def test_normal_thresholds(self):
        """测试正常阈值"""
        from scripts.platform_health_check import format_health_report
        
        report = {
            "timestamp": "2026-04-24T14:00:00",
            "total_invocations": 1000,
            "uncertain_count": 50,
            "unconfirmed_uncertain_count": 5,
            "failed_rate_24h": 2.0,
            "timeout_rate_24h": 1.5,
            "notification_auth_status": "configured",
            "notification_auth_message": "authCode 已配置",
            "by_status": {"completed": 900, "failed": 50, "timeout": 50},
        }
        
        output = format_health_report(report)
        
        # 应该显示正常
        assert "✅ 所有指标正常" in output
    
    def test_warning_thresholds(self):
        """测试警告阈值"""
        from scripts.platform_health_check import format_health_report
        
        report = {
            "timestamp": "2026-04-24T14:00:00",
            "total_invocations": 1000,
            "uncertain_count": 50,
            "unconfirmed_uncertain_count": 15,
            "failed_rate_24h": 6.0,
            "timeout_rate_24h": 7.0,
            "notification_auth_status": "configured",
            "notification_auth_message": "authCode 已配置",
            "by_status": {"completed": 870, "failed": 80, "timeout": 50},
        }
        
        output = format_health_report(report)
        
        # 应该显示警告
        assert "⚠️" in output
