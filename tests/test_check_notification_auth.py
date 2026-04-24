"""
测试 NOTIFICATION 授权检查脚本
"""

import pytest
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestCheckNotificationAuth:
    """测试授权检查脚本"""
    
    def test_check_function_exists(self):
        """测试检查函数存在"""
        from scripts.check_notification_auth import check_notification_auth
        
        result = check_notification_auth()
        
        # 应该返回正确的结构
        assert "status" in result
        assert "message" in result
        assert "details" in result
        
        # 状态应该是三种之一
        assert result["status"] in ["configured", "not_configured", "invalid"]
    
    def test_format_report(self):
        """测试格式化报告"""
        from scripts.check_notification_auth import format_report
        
        result = {
            "status": "not_configured",
            "message": "authCode 未配置",
            "details": {
                "auth_code_found": False,
                "config_source": None,
                "hint": "请配置 authCode",
            }
        }
        
        output = format_report(result)
        
        assert "NOTIFICATION 授权状态检查" in output
        assert "not_configured" in output
        assert "authCode 未配置" in output
    
    def test_script_runs(self):
        """测试脚本可以运行"""
        result = subprocess.run(
            ["python", "scripts/check_notification_auth.py"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        # 应该成功运行（返回 0, 1, 或 2）
        assert result.returncode in [0, 1, 2]
        
        # 应该有输出
        assert "NOTIFICATION 授权状态检查" in result.stdout


class TestAuthStatusValues:
    """测试授权状态值"""
    
    def test_configured_status_structure(self):
        """测试 configured 状态结构"""
        from scripts.check_notification_auth import check_notification_auth
        
        result = check_notification_auth()
        
        if result["status"] == "configured":
            assert result["details"]["auth_code_found"] == True
            assert result["details"]["capability_available"] == True
    
    def test_not_configured_status_structure(self):
        """测试 not_configured 状态结构"""
        from scripts.check_notification_auth import check_notification_auth
        
        result = check_notification_auth()
        
        if result["status"] == "not_configured":
            assert result["details"]["auth_code_found"] == False
            assert "hint" in result["details"]
    
    def test_invalid_status_structure(self):
        """测试 invalid 状态结构"""
        from scripts.check_notification_auth import check_notification_auth
        
        result = check_notification_auth()
        
        if result["status"] == "invalid":
            assert result["details"]["auth_code_found"] == True
            assert result["details"]["capability_available"] == False
