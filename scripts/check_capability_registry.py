#!/usr/bin/env python3
"""
能力注册表检查器

检查 capabilities/ 下的能力是否全部：
1. 已注册到 capability_registry.json
2. 已接入路由
3. 已被测试覆盖
4. 已被文档化
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class CapabilityRegistryChecker:
    """能力注册表检查器"""
    
    def __init__(self, root: Path = None):
        self.root = root or PROJECT_ROOT
        self.inventory_dir = self.root / "infrastructure" / "inventory"
        self.reports_dir = self.root / "reports" / "integrity"
        
        self.inventory_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "capabilities": {},
            "issues": [],
            "stats": {},
        }
    
    def scan_capabilities(self) -> Dict[str, Dict]:
        """扫描所有能力"""
        capabilities = {}
        
        cap_dir = self.root / "capabilities"
        if not cap_dir.exists():
            return capabilities
        
        for cap_file in cap_dir.glob("*.py"):
            if cap_file.name.startswith("_"):
                continue
            
            cap_name = cap_file.stem
            content = cap_file.read_text(encoding='utf-8')
            
            capabilities[cap_name] = {
                "name": cap_name,
                "path": str(cap_file),
                "has_class": f"class {cap_name}" in content or "class " in content,
                "has_execute": "def execute" in content or "async def execute" in content,
                "has_test": False,  # 后续检查
                "has_doc": False,   # 后续检查
                "registered": False,
                "routed": False,
            }
        
        return capabilities
    
    def check_registration(self, capabilities: Dict) -> List[Dict]:
        """检查能力是否已注册"""
        issues = []
        
        # 加载能力注册表
        registry_path = self.inventory_dir / "capability_registry.json"
        if registry_path.exists():
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            registered = set(registry.get("items", {}).keys())
        else:
            registered = set()
        
        for cap_name, cap_info in capabilities.items():
            cap_info["registered"] = cap_name in registered
            
            if not cap_info["registered"]:
                issues.append({
                    "type": "capability_not_registered",
                    "name": cap_name,
                    "path": cap_info["path"],
                })
        
        return issues
    
    def check_routing(self, capabilities: Dict) -> List[Dict]:
        """检查能力是否已接入路由"""
        issues = []
        
        # 检查路由文件
        router_paths = [
            self.root / "skill_entry" / "input_router.py",
            self.root / "infrastructure" / "skill_router.py",
        ]
        
        routed_caps = set()
        
        for router_path in router_paths:
            if router_path.exists():
                content = router_path.read_text(encoding='utf-8')
                for cap_name in capabilities.keys():
                    if cap_name in content:
                        routed_caps.add(cap_name)
        
        for cap_name, cap_info in capabilities.items():
            cap_info["routed"] = cap_name in routed_caps
            
            if not cap_info["routed"]:
                issues.append({
                    "type": "capability_not_routed",
                    "name": cap_name,
                    "path": cap_info["path"],
                })
        
        return issues
    
    def check_tests(self, capabilities: Dict) -> List[Dict]:
        """检查能力是否已被测试覆盖"""
        issues = []
        
        tests_dir = self.root / "tests"
        if not tests_dir.exists():
            return issues
        
        # 扫描测试文件
        test_files = list(tests_dir.glob("test_*.py"))
        test_content = ""
        for test_file in test_files:
            test_content += test_file.read_text(encoding='utf-8')
        
        for cap_name, cap_info in capabilities.items():
            # 检查是否有对应测试
            has_test = (
                f"test_{cap_name}" in test_content or
                cap_name in test_content
            )
            
            cap_info["has_test"] = has_test
            
            if not has_test:
                issues.append({
                    "type": "capability_not_tested",
                    "name": cap_name,
                    "path": cap_info["path"],
                })
        
        return issues
    
    def check_documentation(self, capabilities: Dict) -> List[Dict]:
        """检查能力是否已被文档化"""
        issues = []
        
        docs_dir = self.root / "docs"
        if not docs_dir.exists():
            return issues
        
        # 扫描文档文件
        doc_files = list(docs_dir.glob("*.md"))
        doc_content = ""
        for doc_file in doc_files:
            doc_content += doc_file.read_text(encoding='utf-8')
        
        for cap_name, cap_info in capabilities.items():
            has_doc = cap_name in doc_content
            cap_info["has_doc"] = has_doc
            
            if not has_doc:
                issues.append({
                    "type": "capability_not_documented",
                    "name": cap_name,
                    "path": cap_info["path"],
                })
        
        return issues
    
    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        print("=" * 60)
        print("  能力注册表检查器 V1.0.0")
        print("=" * 60)
        
        # 扫描能力
        print("\n🔍 扫描能力...")
        capabilities = self.scan_capabilities()
        print(f"  发现 {len(capabilities)} 个能力")
        
        if not capabilities:
            print("  ⚠️  没有发现能力")
            return self.results
        
        # 检查注册
        print("\n📋 检查注册状态...")
        reg_issues = self.check_registration(capabilities)
        print(f"  未注册: {len(reg_issues)} 个")
        
        # 检查路由
        print("\n🔀 检查路由状态...")
        route_issues = self.check_routing(capabilities)
        print(f"  未路由: {len(route_issues)} 个")
        
        # 检查测试
        print("\n🧪 检查测试覆盖...")
        test_issues = self.check_tests(capabilities)
        print(f"  未测试: {len(test_issues)} 个")
        
        # 检查文档
        print("\n📄 检查文档覆盖...")
        doc_issues = self.check_documentation(capabilities)
        print(f"  未文档化: {len(doc_issues)} 个")
        
        # 汇总
        all_issues = reg_issues + route_issues + test_issues + doc_issues
        
        self.results["capabilities"] = capabilities
        self.results["issues"] = all_issues
        self.results["stats"] = {
            "total": len(capabilities),
            "registered": sum(1 for c in capabilities.values() if c["registered"]),
            "routed": sum(1 for c in capabilities.values() if c["routed"]),
            "tested": sum(1 for c in capabilities.values() if c["has_test"]),
            "documented": sum(1 for c in capabilities.values() if c["has_doc"]),
            "issues": len(all_issues),
        }
        
        # 打印汇总
        print("\n" + "=" * 60)
        if all_issues:
            print(f"  ❌ 发现 {len(all_issues)} 个问题")
        else:
            print("  ✅ 所有能力检查通过")
        print("=" * 60 + "\n")
        
        return self.results
    
    def save_report(self) -> Path:
        """保存报告"""
        report_path = self.reports_dir / f"capability_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 报告已保存: {report_path}")
        
        return report_path


def main():
    """主函数"""
    checker = CapabilityRegistryChecker()
    checker.run_all_checks()
    checker.save_report()
    
    return 0 if not checker.results["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
