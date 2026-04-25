from pathlib import Path
#!/usr/bin/env python3

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # tests/ 的父目录
"""测试：禁止假成功"""

import unittest
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.result_guard import ResultGuard, GuardReason
from orchestration.verify_executor import VerifyExecutor
from application.response_service.response_schema import EvidenceSchema


class TestNoFakeSuccess(unittest.TestCase):
    """测试禁止假成功"""
    
    def setUp(self):
        self.guard = ResultGuard()
        self.verify_executor = VerifyExecutor()
    
    def test_skill_success_but_evidence_empty_should_fail(self):
        """skill success 但 evidence 空 → 最终 failed"""
        result = self.guard.guard(
            has_real_execution=True,
            verify_status="success",
            evidence={},  # 空 evidence
            user_response="已完成",
            completed_items=["执行成功"]
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.reason, GuardReason.NO_EVIDENCE)
    
    def test_summarize_empty_should_fail(self):
        """summarize 为空 → 最终 failed"""
        result = self.guard.guard(
            has_real_execution=True,
            verify_status="success",
            evidence={"files": [{"path": "/tmp/test.txt", "exists": True}]},
            user_response="",  # 空 user_response
            completed_items=["执行成功"]
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.reason, GuardReason.EMPTY_USER_RESPONSE)
    
    def test_verify_failed_should_fail(self):
        """verify 失败 → 最终 failed"""
        result = self.guard.guard(
            has_real_execution=True,
            verify_status="failed",  # verify 失败
            evidence={"files": [{"path": "/tmp/test.txt", "exists": True}]},
            user_response="执行完成",
            completed_items=["执行成功"]
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.reason, GuardReason.VERIFICATION_FAILED)
    
    def test_no_real_execution_should_fail(self):
        """没有真实执行 → 最终 failed"""
        result = self.guard.guard(
            has_real_execution=False,  # 没有真实执行
            verify_status="success",
            evidence={"files": [{"path": "/tmp/test.txt", "exists": True}]},
            user_response="执行完成",
            completed_items=["执行成功"]
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.reason, GuardReason.NO_REAL_EXECUTION)
    
    def test_empty_completed_items_should_fail(self):
        """completed_items 为空 → 最终 failed"""
        result = self.guard.guard(
            has_real_execution=True,
            verify_status="success",
            evidence={"files": [{"path": "/tmp/test.txt", "exists": True}]},
            user_response="执行完成",
            completed_items=[]  # 空 completed_items
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.reason, GuardReason.EMPTY_COMPLETED_ITEMS)
    
    def test_all_conditions_met_should_pass(self):
        """所有条件满足 → 最终 success"""
        result = self.guard.guard(
            has_real_execution=True,
            verify_status="success",
            evidence={"files": [{"path": "/tmp/test.txt", "exists": True}]},
            user_response="执行完成",
            completed_items=["文件已生成"]
        )
        
        self.assertTrue(result.passed)
        self.assertEqual(result.reason, GuardReason.ALL_PASSED)


class TestVerifyExecutor(unittest.TestCase):
    """测试验证器"""
    
    def setUp(self):
        self.verify_executor = VerifyExecutor()
    
    def test_file_exists_should_success(self):
        """文件存在时 success"""
        import tempfile
        import os
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            results = {
                "task_1": {
                    "success": True,
                    "evidence": {
                        "files": [{"path": temp_path, "exists": True}]
                    }
                }
            }
            
            result = self.verify_executor.verify(results, "file")
            
            self.assertEqual(result.status, "success")
            self.assertTrue(len(result.completed_items) > 0)
        finally:
            os.unlink(temp_path)
    
    def test_file_not_exists_should_fail(self):
        """文件不存在时 failed"""
        results = {
            "task_1": {
                "success": True,
                "evidence": {
                    "files": [{"path": "/nonexistent/file.txt", "exists": False}]
                }
            }
        }
        
        result = self.verify_executor.verify(results, "file")
        
        # 文件不存在，但没有其他证据，应该失败
        self.assertEqual(result.status, "failed")
    
    def test_evidence_empty_should_fail(self):
        """evidence 为空时 failed"""
        results = {
            "task_1": {
                "success": True,
                "evidence": {}
            }
        }
        
        result = self.verify_executor.verify(results, "general")
        
        self.assertEqual(result.status, "failed")


if __name__ == '__main__':
    unittest.main(verbosity=2)
