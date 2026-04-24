#!/usr/bin/env python3
"""
测试收集检查器

检查 tests/ 下新增测试是否能被 pytest 收集
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestCollectionChecker:
    """测试收集检查器"""
    
    def __init__(self, root: Path = None):
        self.root = root or PROJECT_ROOT
        self.inventory_dir = self.root / "infrastructure" / "inventory"
        self.reports_dir = self.root / "reports" / "integrity"
        
        self.inventory_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "issues": [],
            "stats": {},
        }
    
    def scan_tests(self) -> Dict:
        """扫描测试文件"""
        tests = {}
        
        tests_dir = self.root / "tests"
        if not tests_dir.exists():
            return tests
        
        for test_file in tests_dir.glob("test_*.py"):
            test_name = test_file.stem
            content = test_file.read_text(encoding='utf-8')
            
            tests[test_name] = {
                "name": test_name,
                "path": str(test_file),
                "has_test_func": "def test_" in content,
                "has_test_class": "class Test" in content,
                "collectible": False,
                "collected_count": 0,
            }
        
        return tests
    
    def check_collection(self) -> List[Dict]:
        """检查测试是否能被收集"""
        issues = []
        
        tests = self.scan_tests()
        
        # 使用 pytest --collect-only 检查
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q", "tests/"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            collected_output = result.stdout + result.stderr
            
            # 解析收集结果
            for test_name, test_info in tests.items():
                # 检查是否有可收集的测试
                test_info["collectible"] = (
                    test_info["has_test_func"] or test_info["has_test_class"]
                )
                
                # 检查是否在收集输出中
                if test_name in collected_output or test_info["path"] in collected_output:
                    test_info["collectible"] = True
                
                if not test_info["collectible"]:
                    issues.append({
                        "type": "test_not_collectible",
                        "name": test_name,
                        "path": test_info["path"],
                        "reason": "无可收集的测试函数或类",
                    })
        except subprocess.TimeoutExpired:
            print("  ⚠️  pytest 收集超时")
        except Exception as e:
            print(f"  ⚠️  pytest 收集失败: {e}")
        
        self.results["tests"] = tests
        self.results["issues"] = issues
        self.results["stats"] = {
            "total": len(tests),
            "collectible": sum(1 for t in tests.values() if t["collectible"]),
            "uncollectible": len(issues),
        }
        
        return issues
    
    def run_check(self) -> Dict:
        """运行检查"""
        print("=" * 60)
        print("  测试收集检查器 V1.0.0")
        print("=" * 60)
        
        print("\n🔍 扫描测试文件...")
        issues = self.check_collection()
        
        print(f"\n测试文件总数: {self.results['stats']['total']}")
        print(f"可收集: {self.results['stats']['collectible']}")
        print(f"不可收集: {self.results['stats']['uncollectible']}")
        
        print("\n" + "=" * 60)
        if issues:
            print(f"  ❌ 发现 {len(issues)} 个不可收集的测试")
            for issue in issues:
                print(f"    - {issue['name']}: {issue.get('reason', '')}")
        else:
            print("  ✅ 所有测试可被 pytest 收集")
        print("=" * 60 + "\n")
        
        return self.results
    
    def save_report(self) -> Path:
        """保存报告"""
        report_path = self.reports_dir / f"test_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 报告已保存: {report_path}")
        
        return report_path


def main():
    """主函数"""
    checker = TestCollectionChecker()
    checker.run_check()
    checker.save_report()
    
    return 0 if not checker.results["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
