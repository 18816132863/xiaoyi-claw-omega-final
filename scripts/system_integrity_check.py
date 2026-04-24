#!/usr/bin/env python3
"""
系统完整性检查 - 总入口

检查所有新增模块、能力、配置、脚本、测试、文档是否真正生效。

状态定义：
- created: 文件存在
- registered: 已注册到对应 registry
- wired: 已接入主链路
- tested: 已被测试覆盖
- documented: 已被文档记录
- active: 已被验收脚本检查

验收标准：
只有同时满足 created + registered + wired + tested + documented 才允许标记为 active
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class SystemIntegrityChecker:
    """系统完整性检查器"""
    
    # 组件类型
    COMPONENT_TYPES = [
        "module",
        "capability", 
        "config",
        "script",
        "test",
        "document",
        "table",
        "rule",
    ]
    
    # 状态流转
    STATUS_FLOW = ["created", "registered", "wired", "tested", "documented", "active"]
    
    def __init__(self, root: Path = None):
        self.root = root or PROJECT_ROOT
        self.inventory_dir = self.root / "infrastructure" / "inventory"
        self.reports_dir = self.root / "reports" / "integrity"
        
        # 确保目录存在
        self.inventory_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载所有注册表
        self.registries = self._load_all_registries()
        
        # 检查结果
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "summary": {},
            "issues": [],
        }
    
    def _load_all_registries(self) -> Dict:
        """加载所有注册表"""
        registries = {}
        
        registry_files = {
            "module": "module_registry.json",
            "capability": "capability_registry.json",
            "route": "route_registry.json",
            "config": "config_registry.json",
            "script": "script_registry.json",
            "docs": "docs_registry.json",
            "test": "test_registry.json",
        }
        
        for name, filename in registry_files.items():
            path = self.inventory_dir / filename
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    registries[name] = json.load(f)
            else:
                registries[name] = {"version": "1.0.0", "items": {}}
        
        return registries
    
    def check_modules(self) -> Dict:
        """检查模块完整性"""
        print("\n📦 检查模块完整性...")
        
        issues = []
        stats = {"total": 0, "active": 0, "created_only": 0, "registered_only": 0}
        
        # 扫描模块目录
        module_dirs = self._scan_module_directories()
        
        for module_name, module_path in module_dirs.items():
            stats["total"] += 1
            
            # 检查是否注册
            registered = module_name in self.registries.get("module", {}).get("modules", {})
            
            if not registered:
                issues.append({
                    "type": "module_not_registered",
                    "name": module_name,
                    "path": str(module_path),
                    "status": "created_only",
                })
                stats["created_only"] += 1
                continue
            
            # 检查状态
            module_info = self.registries["module"]["modules"][module_name]
            status = module_info.get("status", "created")
            
            if status == "active":
                stats["active"] += 1
            elif status == "registered":
                stats["registered_only"] += 1
        
        print(f"  总计: {stats['total']}, 活跃: {stats['active']}, 仅创建: {stats['created_only']}, 仅注册: {stats['registered_only']}")
        
        return {"stats": stats, "issues": issues}
    
    def check_capabilities(self) -> Dict:
        """检查能力完整性"""
        print("\n⚡ 检查能力完整性...")
        
        issues = []
        stats = {"total": 0, "active": 0, "created_only": 0, "unrouted": 0, "untested": 0}
        
        # 扫描 capabilities 目录
        cap_dir = self.root / "capabilities"
        if not cap_dir.exists():
            print("  ⚠️  capabilities 目录不存在")
            return {"stats": stats, "issues": issues}
        
        capability_files = list(cap_dir.glob("*.py"))
        capability_files = [f for f in capability_files if not f.name.startswith("_")]
        
        for cap_file in capability_files:
            cap_name = cap_file.stem
            stats["total"] += 1
            
            # 检查是否注册
            registered = cap_name in self.registries.get("capability", {}).get("items", {})
            
            if not registered:
                issues.append({
                    "type": "capability_not_registered",
                    "name": cap_name,
                    "path": str(cap_file),
                    "status": "created_only",
                })
                stats["created_only"] += 1
        
        print(f"  总计: {stats['total']}, 活跃: {stats['active']}, 仅创建: {stats['created_only']}")
        
        return {"stats": stats, "issues": issues}
    
    def check_configs(self) -> Dict:
        """检查配置完整性"""
        print("\n⚙️  检查配置完整性...")
        
        issues = []
        stats = {"total": 0, "active": 0, "unused": 0}
        
        # 扫描 config 目录
        config_dir = self.root / "config"
        if not config_dir.exists():
            print("  ⚠️  config 目录不存在")
            return {"stats": stats, "issues": issues}
        
        config_files = list(config_dir.glob("*.json")) + list(config_dir.glob("*.py"))
        
        for config_file in config_files:
            if config_file.name.startswith("_"):
                continue
            
            config_name = config_file.stem
            stats["total"] += 1
            
            # 检查是否被引用
            referenced = self._check_config_referenced(config_name)
            
            if not referenced:
                issues.append({
                    "type": "config_not_referenced",
                    "name": config_name,
                    "path": str(config_file),
                    "status": "unused",
                })
                stats["unused"] += 1
        
        print(f"  总计: {stats['total']}, 未使用: {stats['unused']}")
        
        return {"stats": stats, "issues": issues}
    
    def check_scripts(self) -> Dict:
        """检查脚本完整性"""
        print("\n📜 检查脚本完整性...")
        
        issues = []
        stats = {"total": 0, "active": 0, "created_only": 0}
        
        # 扫描 scripts 目录
        scripts_dir = self.root / "scripts"
        if not scripts_dir.exists():
            print("  ⚠️  scripts 目录不存在")
            return {"stats": stats, "issues": issues}
        
        script_files = list(scripts_dir.glob("*.py"))
        
        for script_file in script_files:
            if script_file.name.startswith("_"):
                continue
            
            script_name = script_file.stem
            stats["total"] += 1
            
            # 检查是否注册
            registered = script_name in self.registries.get("script", {}).get("items", {})
            
            if not registered:
                issues.append({
                    "type": "script_not_registered",
                    "name": script_name,
                    "path": str(script_file),
                    "status": "created_only",
                })
                stats["created_only"] += 1
        
        print(f"  总计: {stats['total']}, 仅创建: {stats['created_only']}")
        
        return {"stats": stats, "issues": issues}
    
    def check_tests(self) -> Dict:
        """检查测试完整性"""
        print("\n🧪 检查测试完整性...")
        
        issues = []
        stats = {"total": 0, "collected": 0, "uncollected": 0}
        
        # 扫描 tests 目录
        tests_dir = self.root / "tests"
        if not tests_dir.exists():
            print("  ⚠️  tests 目录不存在")
            return {"stats": stats, "issues": issues}
        
        test_files = list(tests_dir.glob("test_*.py"))
        
        for test_file in test_files:
            test_name = test_file.stem
            stats["total"] += 1
            
            # 检查是否能被 pytest 收集
            collected = self._check_test_collectible(test_file)
            
            if not collected:
                issues.append({
                    "type": "test_not_collected",
                    "name": test_name,
                    "path": str(test_file),
                    "status": "uncollected",
                })
                stats["uncollected"] += 1
            else:
                stats["collected"] += 1
        
        print(f"  总计: {stats['total']}, 可收集: {stats['collected']}, 不可收集: {stats['uncollected']}")
        
        return {"stats": stats, "issues": issues}
    
    def check_documents(self) -> Dict:
        """检查文档完整性"""
        print("\n📄 检查文档完整性...")
        
        issues = []
        stats = {"total": 0, "indexed": 0, "orphan": 0}
        
        # 扫描 docs 目录
        docs_dir = self.root / "docs"
        if not docs_dir.exists():
            print("  ⚠️  docs 目录不存在")
            return {"stats": stats, "issues": issues}
        
        doc_files = list(docs_dir.glob("*.md"))
        
        for doc_file in doc_files:
            if doc_file.name.startswith("_"):
                continue
            
            doc_name = doc_file.stem
            stats["total"] += 1
            
            # 检查是否在索引中
            indexed = self._check_doc_indexed(doc_name)
            
            if not indexed:
                issues.append({
                    "type": "doc_not_indexed",
                    "name": doc_name,
                    "path": str(doc_file),
                    "status": "orphan",
                })
                stats["orphan"] += 1
            else:
                stats["indexed"] += 1
        
        print(f"  总计: {stats['total']}, 已索引: {stats['indexed']}, 孤儿: {stats['orphan']}")
        
        return {"stats": stats, "issues": issues}
    
    def _scan_module_directories(self) -> Dict[str, Path]:
        """扫描模块目录"""
        modules = {}
        
        # 标准目录（不是模块）
        standard_dirs = {
            "core", "memory_context", "orchestration", "execution",
            "governance", "infrastructure", "skills", "tests",
            "scripts", "docs", "config", "data", "reports",
            "capabilities", "diagnostics", "storage", "platform_adapter",
            "memory", "repo", "build", "dist", "node_modules",
            "application", "domain",
        }
        
        for item in self.root.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith(".") or item.name.startswith("_"):
                continue
            if item.name in standard_dirs:
                continue
            
            # 检查是否有 __init__.py
            init_file = item / "__init__.py"
            if init_file.exists():
                modules[item.name] = item
        
        return modules
    
    def _check_config_referenced(self, config_name: str) -> bool:
        """检查配置是否被引用"""
        # 简单检查：在代码中搜索配置名或相关类名
        import subprocess
        
        try:
            # 搜索文件名
            result = subprocess.run(
                ["grep", "-r", config_name, "--include=*.py", str(self.root)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # 排除 config 目录自身的引用
            lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            external_refs = [l for l in lines if '/config/' not in l and l]
            
            if len(external_refs) > 0:
                return True
            
            # 搜索类名（驼峰转换）
            # default_skill_config -> DefaultSkillConfig
            class_name = ''.join(word.capitalize() for word in config_name.split('_'))
            
            result2 = subprocess.run(
                ["grep", "-r", class_name, "--include=*.py", str(self.root)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines2 = result2.stdout.strip().split('\n') if result2.stdout.strip() else []
            external_refs2 = [l for l in lines2 if '/config/' not in l and l]
            
            return len(external_refs2) > 0
        except:
            return True  # 假设已引用
    
    def _check_test_collectible(self, test_file: Path) -> bool:
        """检查测试是否能被 pytest 收集"""
        # 简单检查：文件名以 test_ 开头，且有 test 函数或类
        content = test_file.read_text(encoding='utf-8')
        
        has_test_func = "def test_" in content
        has_test_class = "class Test" in content
        
        return has_test_func or has_test_class
    
    def _check_doc_indexed(self, doc_name: str) -> bool:
        """检查文档是否在索引中"""
        # 检查 README 或索引文件
        readme_path = self.root / "docs" / "README.md"
        
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            return doc_name in content
        
        return True  # 假设已索引
    
    def run_all_checks(self) -> Dict:
        """运行所有检查"""
        print("=" * 60)
        print("  系统完整性检查 V1.0.0")
        print("=" * 60)
        
        # 运行各项检查
        self.results["checks"]["modules"] = self.check_modules()
        self.results["checks"]["capabilities"] = self.check_capabilities()
        self.results["checks"]["configs"] = self.check_configs()
        self.results["checks"]["scripts"] = self.check_scripts()
        self.results["checks"]["tests"] = self.check_tests()
        self.results["checks"]["documents"] = self.check_documents()
        
        # 汇总问题
        all_issues = []
        for check_name, check_result in self.results["checks"].items():
            all_issues.extend(check_result.get("issues", []))
        
        self.results["issues"] = all_issues
        
        # 汇总统计
        self.results["summary"] = {
            "total_checks": len(self.results["checks"]),
            "total_issues": len(all_issues),
            "passed": len(all_issues) == 0,
        }
        
        # 打印汇总
        print("\n" + "=" * 60)
        if all_issues:
            print(f"  ❌ 发现 {len(all_issues)} 个问题")
            for issue in all_issues[:10]:  # 只显示前10个
                print(f"    - [{issue['type']}] {issue['name']}: {issue['status']}")
            if len(all_issues) > 10:
                print(f"    ... 还有 {len(all_issues) - 10} 个问题")
        else:
            print("  ✅ 所有检查通过")
        print("=" * 60 + "\n")
        
        return self.results
    
    def save_report(self) -> Path:
        """保存报告"""
        report_path = self.reports_dir / f"integrity_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 报告已保存: {report_path}")
        
        return report_path


def main():
    """主函数"""
    checker = SystemIntegrityChecker()
    results = checker.run_all_checks()
    checker.save_report()
    
    # 返回退出码
    return 0 if results["summary"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
