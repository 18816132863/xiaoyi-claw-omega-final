"""
测试预热脚本
"""

import pytest
import sys
import tempfile
import os
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSeedInvocations:
    """测试预热脚本"""
    
    def setup_method(self):
        """每个测试前设置临时数据库"""
        import scripts.seed_platform_invocations as seed_module
        
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.temp_dir) / "test_tasks.db"
        seed_module.DB_PATH = self.temp_db
    
    def teardown_method(self):
        """清理临时数据库"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_seed_creates_records(self):
        """测试预热创建记录"""
        from scripts.seed_platform_invocations import seed_demo_standard
        
        # 预热
        seed_demo_standard()
        
        # 验证
        import sqlite3
        conn = sqlite3.connect(str(self.temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM platform_invocations")
        total = cursor.fetchone()[0]
        conn.close()
        
        # 应该有记录
        assert total > 0
    
    def test_seed_creates_confirmed_records(self):
        """测试预热创建已确认记录"""
        from scripts.seed_platform_invocations import seed_demo_standard
        
        # 预热
        seed_demo_standard()
        
        # 验证
        import sqlite3
        conn = sqlite3.connect(str(self.temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM platform_invocations WHERE confirmed_status IS NOT NULL")
        confirmed = cursor.fetchone()[0]
        conn.close()
        
        # 应该有已确认的记录
        assert confirmed > 0
    
    def test_seed_sample_data_types(self):
        """测试样例数据包含所有类型"""
        from scripts.seed_platform_invocations import seed_demo_standard
        
        # 预热
        seed_demo_standard()
        
        # 验证
        import sqlite3
        conn = sqlite3.connect(str(self.temp_db))
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT normalized_status FROM platform_invocations")
        statuses = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # 应该有 completed, failed, timeout
        assert "completed" in statuses
        assert "failed" in statuses
        assert "timeout" in statuses


class TestSeedScriptMain:
    """测试预热脚本主函数"""
    
    def test_main_runs(self):
        """测试主函数可以运行"""
        result = subprocess.run(
            ["python", "scripts/seed_platform_invocations.py", "--preset", "demo_standard"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        # 应该成功运行
        assert result.returncode == 0
        assert "预热完成" in result.stdout or "预热" in result.stdout
    
    def test_reset_flag(self):
        """测试重置标志"""
        result = subprocess.run(
            ["python", "scripts/seed_platform_invocations.py", "--preset", "demo_standard", "--reset-before-seed"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        # 应该成功运行
        assert result.returncode == 0
