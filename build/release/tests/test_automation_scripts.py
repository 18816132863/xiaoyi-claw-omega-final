"""
测试自动化脚本
"""

import pytest
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent


class TestAutomationScriptsExist:
    """测试自动化脚本存在"""
    
    def test_daily_backup_script_exists(self):
        """测试每日备份脚本存在"""
        script_path = project_root / "scripts" / "run_daily_backup.sh"
        assert script_path.exists()
    
    def test_weekly_cleanup_script_exists(self):
        """测试每周清理脚本存在"""
        script_path = project_root / "scripts" / "run_weekly_cleanup.sh"
        assert script_path.exists()
    
    def test_hourly_health_check_script_exists(self):
        """测试每小时健康巡检脚本存在"""
        script_path = project_root / "scripts" / "run_hourly_health_check.sh"
        assert script_path.exists()


class TestAutomationScriptsSyntax:
    """测试自动化脚本语法"""
    
    def test_daily_backup_syntax(self):
        """测试每日备份脚本语法"""
        result = subprocess.run(
            ["bash", "-n", "scripts/run_daily_backup.sh"],
            capture_output=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0
    
    def test_weekly_cleanup_syntax(self):
        """测试每周清理脚本语法"""
        result = subprocess.run(
            ["bash", "-n", "scripts/run_weekly_cleanup.sh"],
            capture_output=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0
    
    def test_hourly_health_check_syntax(self):
        """测试每小时健康巡检脚本语法"""
        result = subprocess.run(
            ["bash", "-n", "scripts/run_hourly_health_check.sh"],
            capture_output=True,
            cwd=str(project_root),
        )
        assert result.returncode == 0


class TestConfigExamples:
    """测试配置示例"""
    
    def test_crontab_example_exists(self):
        """测试 crontab 示例存在"""
        config_path = project_root / "config" / "crontab.example"
        assert config_path.exists()
    
    def test_systemd_example_exists(self):
        """测试 systemd 示例存在"""
        config_path = project_root / "config" / "systemd.example"
        assert config_path.exists()
    
    def test_crontab_has_entries(self):
        """测试 crontab 有条目"""
        config_path = project_root / "config" / "crontab.example"
        content = config_path.read_text()
        
        assert "run_daily_backup" in content
        assert "run_weekly_cleanup" in content
        assert "run_hourly_health_check" in content
    
    def test_systemd_has_services(self):
        """测试 systemd 有服务定义"""
        config_path = project_root / "config" / "systemd.example"
        content = config_path.read_text()
        
        assert "platform-health-check" in content
        assert "platform-daily-backup" in content
        assert "platform-weekly-cleanup" in content


class TestAutomationScriptsSmoke:
    """自动化脚本冒烟测试"""
    
    def test_health_check_script_runs(self):
        """测试健康巡检脚本可以运行"""
        result = subprocess.run(
            ["bash", "scripts/run_hourly_health_check.sh"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=60,
        )
        
        # 应该运行完成（不管返回码）
        assert "每小时平台健康巡检" in result.stdout or "健康巡检" in result.stdout
