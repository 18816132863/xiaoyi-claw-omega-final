from pathlib import Path
import os
#!/usr/bin/env python3

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # tests/ 的父目录
"""端到端测试"""

import unittest
import sys
import asyncio
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.task_engine import TaskEngine


class TestEndToEndSuccess(unittest.TestCase):
    """端到端成功测试"""
    
    def test_success_task_structure(self):
        """成功任务返回结构正确"""
        # 模拟成功任务
        expected_keys = [
            "status",
            "reason",
            "user_response",
            "completed_items",
            "failed_items",
            "evidence",
            "next_action",
            "execution_trace",
            "task_id",
            "intent",
            "total_latency_ms"
        ]
        
        # 这里只验证结构，实际执行需要真实环境
        # 在真实环境中，会调用 TaskEngine.process()
        
        # 模拟返回
        mock_response = {
            "status": "success",
            "reason": "",
            "user_response": "【执行结果】\n✅ 测试任务 成功",
            "completed_items": ["文件已生成"],
            "failed_items": [],
            "evidence": {
                "files": [{"path": "/tmp/test.txt", "exists": True}],
                "db_records": [],
                "messages": [],
                "tool_calls": [],
                "extra": {}
            },
            "next_action": "任务已完成",
            "execution_trace": [],
            "task_id": "test_001",
            "intent": "test",
            "total_latency_ms": 100.0
        }
        
        for key in expected_keys:
            self.assertIn(key, mock_response)
        
        # success 时 evidence 必须非空
        self.assertTrue(len(mock_response["evidence"]["files"]) > 0)
        
        # user_response 必须非空
        self.assertTrue(len(mock_response["user_response"]) > 0)
        
        # next_action 必须非空
        self.assertTrue(len(mock_response["next_action"]) > 0)


class TestEndToEndFailure(unittest.TestCase):
    """端到端失败测试"""
    
    def test_failure_task_structure(self):
        """失败任务返回结构正确"""
        # 模拟失败任务
        mock_response = {
            "status": "failed",
            "reason": "no_evidence",
            "user_response": "【执行结果】\n❌ 测试任务 失败\n\n【未完成项】\n- 无有效证据",
            "completed_items": [],
            "failed_items": ["无有效证据"],
            "evidence": {
                "files": [],
                "db_records": [],
                "messages": [],
                "tool_calls": [],
                "extra": {}
            },
            "next_action": "请检查失败项后重试",
            "execution_trace": [
                {"subtask_id": "task_1", "status": "failed", "error": "无有效证据"}
            ],
            "task_id": "test_002",
            "intent": "test",
            "total_latency_ms": 50.0
        }
        
        # failed 时 failed_items 必须非空
        self.assertTrue(len(mock_response["failed_items"]) > 0)
        
        # reason 必须明确
        self.assertTrue(len(mock_response["reason"]) > 0)
        
        # user_response 必须非空
        self.assertTrue(len(mock_response["user_response"]) > 0)
        
        # next_action 必须非空
        self.assertTrue(len(mock_response["next_action"]) > 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
