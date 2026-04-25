"""
测试日报/周报导出
"""

import pytest
import sys
import tempfile
import os
import subprocess
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDailyReport:
    """测试日报导出"""
    
    def setup_method(self):
        """每个测试前设置临时数据库"""
        import platform_adapter.invocation_ledger as ledger_module
        
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.temp_dir) / "test_tasks.db"
        ledger_module.DB_PATH = self.temp_db
    
    def teardown_method(self):
        """清理临时数据库"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_get_daily_stats_empty(self):
        """测试空数据的日报"""
        from scripts.export_daily_platform_report import get_daily_stats
        
        stats = get_daily_stats()
        
        assert "date" in stats
        assert "total_invocations" in stats
        assert "failed_rate" in stats
        assert stats["total_invocations"] == 0
    
    def test_get_daily_stats_with_data(self):
        """测试有数据的日报"""
        from scripts.export_daily_platform_report import get_daily_stats
        from platform_adapter.invocation_ledger import record_invocation
        
        # 插入一些记录
        for i in range(5):
            record_invocation(
                capability="MESSAGE_SENDING",
                platform_op="send_message",
                normalized_status="completed" if i < 3 else "failed",
            )
        
        stats = get_daily_stats()
        
        assert stats["total_invocations"] == 5
        assert stats["completed_count"] == 3
        assert stats["failed_count"] == 2
        assert stats["failed_rate"] == 40.0
    
    def test_format_report(self):
        """测试格式化报告"""
        from scripts.export_daily_platform_report import format_report
        
        stats = {
            "date": "2026-04-24",
            "generated_at": "2026-04-24T14:00:00",
            "total_invocations": 100,
            "completed_count": 80,
            "failed_count": 10,
            "timeout_count": 5,
            "uncertain_count": 5,
            "confirmed_count": 3,
            "failed_rate": 10.0,
            "timeout_rate": 5.0,
            "confirmation_rate": 60.0,
            "by_capability": {
                "MESSAGE_SENDING": {"total": 50, "completed": 40, "failed": 5, "timeout": 5}
            },
        }
        
        output = format_report(stats)
        
        assert "每日平台调用报告" in output
        assert "2026-04-24" in output
        assert "100" in output
    
    def test_export_json(self):
        """测试 JSON 导出"""
        from scripts.export_daily_platform_report import get_daily_stats, export_json
        
        stats = get_daily_stats()
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name
        
        try:
            export_json(stats, output_path)
            
            assert os.path.exists(output_path)
            
            import json
            with open(output_path) as f:
                loaded = json.load(f)
            
            assert "date" in loaded
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_export_csv(self):
        """测试 CSV 导出"""
        from scripts.export_daily_platform_report import get_daily_stats, export_csv
        
        stats = get_daily_stats()
        
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name
        
        try:
            export_csv(stats, output_path)
            
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestWeeklyReport:
    """测试周报导出"""
    
    def setup_method(self):
        """每个测试前设置临时数据库"""
        import platform_adapter.invocation_ledger as ledger_module
        
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.temp_dir) / "test_tasks.db"
        ledger_module.DB_PATH = self.temp_db
    
    def teardown_method(self):
        """清理临时数据库"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_get_weekly_stats_empty(self):
        """测试空数据的周报"""
        from scripts.export_weekly_platform_report import get_weekly_stats
        
        stats = get_weekly_stats()
        
        assert "week_start" in stats
        assert "week_end" in stats
        assert "total_invocations" in stats
        assert "daily_average" in stats
    
    def test_get_weekly_stats_with_data(self):
        """测试有数据的周报"""
        from scripts.export_weekly_platform_report import get_weekly_stats
        from platform_adapter.invocation_ledger import record_invocation
        
        # 插入一些记录
        for i in range(10):
            record_invocation(
                capability="MESSAGE_SENDING",
                platform_op="send_message",
                normalized_status="completed" if i < 8 else "failed",
            )
        
        stats = get_weekly_stats()
        
        assert stats["total_invocations"] == 10
        assert stats["completed_count"] == 8
        assert stats["failed_count"] == 2
    
    def test_format_report(self):
        """测试格式化报告"""
        from scripts.export_weekly_platform_report import format_report
        
        stats = {
            "week_start": "2026-04-20",
            "week_end": "2026-04-27",
            "generated_at": "2026-04-24T14:00:00",
            "total_invocations": 100,
            "daily_average": 14.3,
            "completed_count": 80,
            "failed_count": 10,
            "timeout_count": 5,
            "uncertain_count": 5,
            "confirmed_count": 3,
            "failed_rate": 10.0,
            "timeout_rate": 5.0,
            "confirmation_rate": 60.0,
            "by_day": {
                "2026-04-20": {"total": 15, "completed": 12, "failed": 2, "timeout": 1},
                "2026-04-21": {"total": 20, "completed": 16, "failed": 2, "timeout": 2},
            },
            "by_capability": {
                "MESSAGE_SENDING": {"total": 50, "completed": 40, "failed": 5, "timeout": 5}
            },
        }
        
        output = format_report(stats)
        
        assert "每周平台调用报告" in output
        assert "2026-04-20" in output
        assert "2026-04-27" in output
        assert "日均调用" in output


class TestReportScripts:
    """测试报告脚本运行"""
    
    def test_daily_report_script_runs(self):
        """测试日报脚本可以运行"""
        result = subprocess.run(
            ["python", "scripts/export_daily_platform_report.py"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0
        assert "每日平台调用报告" in result.stdout or "date" in result.stdout
    
    def test_weekly_report_script_runs(self):
        """测试周报脚本可以运行"""
        result = subprocess.run(
            ["python", "scripts/export_weekly_platform_report.py"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0
        assert "每周平台调用报告" in result.stdout or "week_start" in result.stdout
