#!/usr/bin/env python3
"""回归测试基线 - V4.3.2

固定测试用例，验证搜索、路由、执行、任务编排的一致性
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

class RegressionTest:
    """回归测试"""
    
    def __init__(self):
        self.results: List[Dict] = []
    
    def run_all(self) -> Dict:
        """运行所有回归测试"""
        self.results = []
        
        # 1. 搜索回归
        self._test_search()
        
        # 2. 路由回归
        self._test_route()
        
        # 3. 执行回归
        self._test_execute()
        
        # 4. 任务编排回归
        asyncio.run(self._test_task())
        
        # 汇总
        passed = sum(1 for r in self.results if r["status"] == "pass")
        failed = sum(1 for r in self.results if r["status"] == "fail")
        
        return {
            "status": "pass" if failed == 0 else "fail",
            "tests": self.results,
            "summary": {
                "passed": passed,
                "failed": failed,
                "total": len(self.results)
            }
        }
    
    def _test_search(self):
        """搜索回归测试"""
        from memory_context.unified_search import get_unified_search
        
        search = get_unified_search()
        
        # 固定查询
        test_queries = ["skill", "pdf", "docx"]
        
        for query in test_queries:
            start = __import__("time").time()
            result = search.search(query, mode="fast", limit=5)
            elapsed = int((__import__("time").time() - start) * 1000)
            
            self.results.append({
                "name": f"search_{query}",
                "status": "pass" if result["total"] > 0 else "fail",
                "hits": result["total"],
                "time_ms": elapsed,
                "details": {
                    "has_snippet": any(r.get("snippet") for r in result["results"])
                }
            })
    
    def _test_route(self):
        """路由回归测试"""
        from infrastructure.shared.router import get_router
        
        router = get_router()
        
        # 固定路由测试
        test_routes = [
            ("docx", "docx"),
            ("pdf", "pdf"),
            ("find skill", "find-skills"),
        ]
        
        for query, expected in test_routes:
            result = router.route(query)
            
            if result and result.target == expected:
                self.results.append({
                    "name": f"route_{query}",
                    "status": "pass",
                    "target": result.target,
                    "callable": result.is_callable
                })
            else:
                self.results.append({
                    "name": f"route_{query}",
                    "status": "fail",
                    "expected": expected,
                    "actual": result.target if result else None
                })
    
    def _test_execute(self):
        """执行回归测试"""
        from execution.skill_adapter_gateway import get_skill_gateway
        from pathlib import Path
        from docx import Document
        
        gateway = get_skill_gateway()
        
        # 测试 find-skills
        result = gateway.execute("find-skills", {"query": "pdf"})
        self.results.append({
            "name": "execute_find-skills",
            "status": "pass" if result.success else "fail",
            "success": result.success,
            "error_code": result.error_code
        })
        
        # 测试 docx
        doc = Document()
        doc.add_paragraph("Test")
        test_docx = Path("/tmp/test_regression.docx")
        doc.save(str(test_docx))
        
        result = gateway.execute("docx", {
            "input_file": str(test_docx),
            "output_directory": "/tmp/test_output"
        })
        self.results.append({
            "name": "execute_docx",
            "status": "pass" if result.success else "fail",
            "success": result.success,
            "error_code": result.error_code
        })
    
    async def _test_task(self):
        """任务编排回归测试"""
        from orchestration.task_engine import get_engine
        
        engine = get_engine()
        
        # 固定任务测试
        test_tasks = [
            ("搜索 pdf", "success"),
            ("查询 git 状态", "failed"),
            ("创建一个文档", "failed"),
        ]
        
        for user_input, expected_status in test_tasks:
            result = await engine.process(user_input)
            actual_status = result["result"].get("status", "unknown")
            
            self.results.append({
                "name": f"task_{user_input[:10]}",
                "status": "pass" if actual_status == expected_status else "fail",
                "expected": expected_status,
                "actual": actual_status,
                "has_real_execution": any(
                    t.get("skill") and t.get("status") == "success"
                    for t in result["subtasks"]
                )
            })

def main():
    print("=" * 70)
    print("回归测试基线")
    print("=" * 70)
    
    test = RegressionTest()
    result = test.run_all()
    
    for t in result["tests"]:
        status_icon = "✅" if t["status"] == "pass" else "❌"
        print(f"{status_icon} {t['name']}: {t.get('details', {})}")
    
    print("\n" + "=" * 70)
    print(f"汇总: 通过 {result['summary']['passed']}, 失败 {result['summary']['failed']}")
    print("=" * 70)
    
    return 0 if result["status"] == "pass" else 1

if __name__ == "__main__":
    exit(main())
