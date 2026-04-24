"""
测试审计 CLI
"""

import pytest
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestAuditCLI:
    """测试审计 CLI"""
    
    def test_cli_help(self):
        """测试 CLI 帮助"""
        result = subprocess.run(
            ["python", "scripts/invocation_audit_cli.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0
        assert "query-recent" in result.stdout
        assert "query-uncertain" in result.stdout
        assert "confirm" in result.stdout
        assert "stats" in result.stdout
    
    def test_cli_stats(self):
        """测试统计命令"""
        result = subprocess.run(
            ["python", "scripts/invocation_audit_cli.py", "stats"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0
        assert "总调用数" in result.stdout or "total" in result.stdout.lower()
    
    def test_cli_query_recent_json(self):
        """测试查询最近记录 JSON 格式"""
        result = subprocess.run(
            ["python", "scripts/invocation_audit_cli.py", "query-recent", "--format", "json", "--limit", "5"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0
        # 应该输出 JSON 数组
        assert result.stdout.strip().startswith("[") or result.stdout.strip() == "[]"
    
    def test_cli_query_uncertain(self):
        """测试查询 uncertain 记录"""
        result = subprocess.run(
            ["python", "scripts/invocation_audit_cli.py", "query-uncertain", "--limit", "5"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0
    
    def test_cli_query_failed(self):
        """测试查询 failed 记录"""
        result = subprocess.run(
            ["python", "scripts/invocation_audit_cli.py", "query-failed", "--limit", "5"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0
    
    def test_cli_query_timeout(self):
        """测试查询 timeout 记录"""
        result = subprocess.run(
            ["python", "scripts/invocation_audit_cli.py", "query-timeout", "--limit", "5"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0


class TestAuditCLIRedact:
    """测试脱敏功能"""
    
    def test_redact_flag_works(self):
        """测试脱敏标志"""
        result = subprocess.run(
            ["python", "scripts/invocation_audit_cli.py", "query-recent", "--redact", "--format", "json", "--limit", "5"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
        )
        
        assert result.returncode == 0
        # 如果有记录，检查是否脱敏
        if result.stdout.strip() != "[]":
            # 不应该有完整的手机号
            assert "13800138000" not in result.stdout


class TestAuditCLIExport:
    """测试导出功能"""
    
    def test_export_json(self):
        """测试 JSON 导出"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            output_path = f.name
        
        try:
            result = subprocess.run(
                ["python", "scripts/invocation_audit_cli.py", "export", "--format", "json", "--output", output_path],
                capture_output=True,
                text=True,
                cwd=str(project_root),
            )
            
            assert result.returncode == 0
            assert "已导出" in result.stdout
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_export_csv(self):
        """测试 CSV 导出"""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            output_path = f.name
        
        try:
            result = subprocess.run(
                ["python", "scripts/invocation_audit_cli.py", "export", "--format", "csv", "--output", output_path],
                capture_output=True,
                text=True,
                cwd=str(project_root),
            )
            
            assert result.returncode == 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
