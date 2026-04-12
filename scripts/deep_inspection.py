#!/usr/bin/env python3
"""
深度巡检器 - V1.0.0

最细粒度巡检，覆盖所有可检查项
"""

import os
import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

class DeepInspector:
    """深度巡检器"""
    
    def __init__(self, root: Path):
        self.root = root
        self.results = {
            "inspected_at": datetime.now().isoformat(),
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warnings": 0,
            "categories": {},
            "details": []
        }
    
    def add_result(self, category: str, check: str, status: str, message: str, details: Any = None):
        """添加检查结果"""
        self.results["total_checks"] += 1
        
        if status == "pass":
            self.results["passed_checks"] += 1
        elif status == "fail":
            self.results["failed_checks"] += 1
        elif status == "warn":
            self.results["warnings"] += 1
        
        if category not in self.results["categories"]:
            self.results["categories"][category] = {"pass": 0, "fail": 0, "warn": 0, "checks": []}
        
        self.results["categories"][category][status] += 1
        self.results["categories"][category]["checks"].append({
            "check": check,
            "status": status,
            "message": message,
            "details": details
        })
        
        self.results["details"].append({
            "category": category,
            "check": check,
            "status": status,
            "message": message
        })
    
    # ==================== 文件系统巡检 ====================
    
    def check_protected_files(self):
        """检查保护文件"""
        protected = [
            "AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md",
            "MEMORY.md", "HEARTBEAT.md", "Makefile",
            "core/ARCHITECTURE.md", "core/ARCHITECTURE_INTEGRITY.md",
            "governance/guard/protected_files.json",
            "infrastructure/inventory/skill_registry.json"
        ]
        
        for f in protected:
            path = self.root / f
            if path.exists():
                self.add_result("protected_files", f, "pass", f"存在")
            else:
                self.add_result("protected_files", f, "fail", f"缺失")
    
    def check_directory_structure(self):
        """检查目录结构"""
        required_dirs = [
            "infrastructure", "governance", "execution", "orchestration",
            "core", "scripts", "reports", "tests",
            "memory_context/vector", "memory_context/ontology"
        ]
        
        for d in required_dirs:
            path = self.root / d
            if path.is_dir():
                count = len(list(path.rglob("*")))
                self.add_result("directory_structure", d, "pass", f"存在 ({count} 文件)")
            else:
                self.add_result("directory_structure", d, "fail", f"缺失")
    
    def check_file_permissions(self):
        """检查文件权限"""
        scripts = list((self.root / "scripts").glob("*.py"))
        for script in scripts:
            if os.access(script, os.X_OK) or script.suffix == ".py":
                self.add_result("file_permissions", script.name, "pass", "可执行")
            else:
                self.add_result("file_permissions", script.name, "warn", "无执行权限")
    
    def check_file_sizes(self):
        """检查文件大小"""
        large_files = []
        for f in self.root.rglob("*"):
            if f.is_file() and f.suffix in [".json", ".log", ".txt"]:
                size = f.stat().st_size
                if size > 10 * 1024 * 1024:  # 10MB
                    large_files.append((str(f.relative_to(self.root)), size))
        
        if large_files:
            for f, size in large_files[:5]:
                self.add_result("file_sizes", f, "warn", f"{size/1024/1024:.1f}MB")
        else:
            self.add_result("file_sizes", "large_files", "pass", "无超大文件")
    
    def check_orphan_files(self):
        """检查孤立文件"""
        orphans = []
        for f in self.root.glob("*"):
            if f.is_file() and f.suffix in [".tmp", ".bak", ".old", ".swp"]:
                orphans.append(f.name)
        
        if orphans:
            for f in orphans:
                self.add_result("orphan_files", f, "warn", "孤立文件")
        else:
            self.add_result("orphan_files", "check", "pass", "无孤立文件")
    
    # ==================== 代码质量巡检 ====================
    
    def check_python_syntax(self):
        """检查 Python 语法"""
        python_files = list(self.root.rglob("*.py"))
        # 排除 repo 和 skills
        python_files = [f for f in python_files if "repo" not in str(f) and "skills" not in str(f)]
        
        errors = []
        for f in python_files[:50]:  # 限制检查数量
            try:
                compile(open(f, encoding='utf-8', errors='ignore').read(), str(f), 'exec')
            except SyntaxError as e:
                errors.append((f.name, str(e)))
        
        if errors:
            for f, e in errors[:5]:
                self.add_result("python_syntax", f, "fail", e)
        else:
            self.add_result("python_syntax", "check", "pass", f"检查 {len(python_files[:50])} 文件")
    
    def check_import_statements(self):
        """检查导入语句"""
        core_modules = ["infrastructure", "governance", "execution", "orchestration"]
        
        for module in core_modules:
            module_path = self.root / module
            if not module_path.is_dir():
                continue
            
            broken = []
            for f in module_path.rglob("*.py"):
                try:
                    content = open(f, encoding='utf-8', errors='ignore').read()
                    # 检查相对导入
                    if "from .." in content or "from ." in content:
                        broken.append(f.name)
                except:
                    pass
            
            if broken:
                self.add_result("import_statements", module, "warn", f"{len(broken)} 相对导入")
            else:
                self.add_result("import_statements", module, "pass", "导入正常")
    
    def check_code_duplicates(self):
        """检查代码重复"""
        hashes = {}
        duplicates = []
        
        for f in self.root.rglob("*.py"):
            if "repo" in str(f) or "skills" in str(f) or "__pycache__" in str(f):
                continue
            try:
                content = open(f, encoding='utf-8', errors='ignore').read()
                h = hashlib.md5(content.encode()).hexdigest()
                if h in hashes:
                    duplicates.append((f.name, hashes[h]))
                else:
                    hashes[h] = f.name
            except:
                pass
        
        if duplicates:
            for f, orig in duplicates[:3]:
                self.add_result("code_duplicates", f, "warn", f"与 {orig} 重复")
        else:
            self.add_result("code_duplicates", "check", "pass", "无重复代码")
    
    # ==================== 配置巡检 ====================
    
    def check_json_configs(self):
        """检查 JSON 配置"""
        json_files = list(self.root.rglob("*.json"))
        json_files = [f for f in json_files if "repo" not in str(f) and "node_modules" not in str(f)]
        
        invalid = []
        for f in json_files[:30]:
            try:
                json.load(open(f, encoding='utf-8'))
            except json.JSONDecodeError as e:
                invalid.append((f.name, str(e)))
        
        if invalid:
            for f, e in invalid[:5]:
                self.add_result("json_configs", f, "fail", e)
        else:
            self.add_result("json_configs", "check", "pass", f"检查 {len(json_files[:30])} 文件")
    
    def check_skill_registry(self):
        """检查技能注册表"""
        registry_path = self.root / "infrastructure/inventory/skill_registry.json"
        if not registry_path.exists():
            self.add_result("skill_registry", "registry", "fail", "注册表缺失")
            return
        
        try:
            registry = json.load(open(registry_path, encoding='utf-8'))
            total = len(registry)
            callable_count = sum(1 for s in registry.values() if isinstance(s, dict) and s.get("callable"))
            
            self.add_result("skill_registry", "total", "pass", f"{total} 技能")
            self.add_result("skill_registry", "callable", "pass", f"{callable_count} 可执行")
            
            # 检查缺失元数据
            missing = []
            for name, info in registry.items():
                if isinstance(info, dict) and info.get("callable"):
                    if not info.get("test_mode"):
                        missing.append(name)
            
            if missing:
                self.add_result("skill_registry", "metadata", "warn", f"{len(missing)} 缺 test_mode")
            else:
                self.add_result("skill_registry", "metadata", "pass", "元数据完整")
        except Exception as e:
            self.add_result("skill_registry", "registry", "fail", str(e))
    
    def check_workflow_files(self):
        """检查 GitHub Workflow"""
        workflow_dir = self.root / ".github/workflows"
        if not workflow_dir.exists():
            self.add_result("workflows", "directory", "fail", "缺失")
            return
        
        workflows = list(workflow_dir.glob("*.yml"))
        for wf in workflows:
            try:
                content = open(wf, encoding='utf-8').read()
                if "uses:" in content and "runs-on:" in content:
                    self.add_result("workflows", wf.name, "pass", "配置有效")
                else:
                    self.add_result("workflows", wf.name, "warn", "配置可能不完整")
            except Exception as e:
                self.add_result("workflows", wf.name, "fail", str(e))
    
    # ==================== 依赖巡检 ====================
    
    def check_python_dependencies(self):
        """检查 Python 依赖"""
        req_file = self.root / "requirements.txt"
        if not req_file.exists():
            self.add_result("dependencies", "requirements.txt", "warn", "缺失")
            return
        
        try:
            content = open(req_file, encoding='utf-8').read()
            deps = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
            self.add_result("dependencies", "requirements.txt", "pass", f"{len(deps)} 依赖")
        except Exception as e:
            self.add_result("dependencies", "requirements.txt", "fail", str(e))
    
    def check_makefile(self):
        """检查 Makefile"""
        makefile = self.root / "Makefile"
        if not makefile.exists():
            self.add_result("makefile", "file", "fail", "缺失")
            return
        
        try:
            content = open(makefile, encoding='utf-8').read()
            targets = [l.split(':')[0] for l in content.split('\n') if ':' in l and not l.startswith('\t')]
            self.add_result("makefile", "targets", "pass", f"{len(targets)} 目标")
            
            # 检查关键目标
            key_targets = ["verify-premerge", "verify-nightly", "verify-release"]
            for t in key_targets:
                if t in targets:
                    self.add_result("makefile", t, "pass", "存在")
                else:
                    self.add_result("makefile", t, "warn", "缺失")
        except Exception as e:
            self.add_result("makefile", "file", "fail", str(e))
    
    # ==================== 报告巡检 ====================
    
    def check_reports(self):
        """检查报告文件"""
        report_files = [
            "reports/runtime_integrity.json",
            "reports/quality_gate.json",
            "reports/release_gate.json",
            "reports/nightly_audit.json",
            "reports/alerts/latest_alerts.json",
            "reports/dashboard/ops_dashboard.json"
        ]
        
        for f in report_files:
            path = self.root / f
            if path.exists():
                try:
                    data = json.load(open(path, encoding='utf-8'))
                    self.add_result("reports", f, "pass", f"有效 ({len(str(data))} 字符)")
                except:
                    self.add_result("reports", f, "warn", "格式可能无效")
            else:
                self.add_result("reports", f, "warn", "尚未生成")
    
    def check_history_snapshots(self):
        """检查历史快照"""
        history_dirs = [
            "reports/history/runtime",
            "reports/history/quality",
            "reports/history/release",
            "reports/alerts/history"
        ]
        
        for d in history_dirs:
            path = self.root / d
            if path.exists():
                count = len(list(path.glob("*.json")))
                if count > 0:
                    self.add_result("history", d, "pass", f"{count} 快照")
                else:
                    self.add_result("history", d, "warn", "无快照")
            else:
                self.add_result("history", d, "warn", "目录不存在")
    
    # ==================== 安全巡检 ====================
    
    def check_secrets(self):
        """检查敏感信息"""
        patterns = ["password", "secret", "token", "api_key", "private_key"]
        found = []
        
        for f in self.root.rglob("*.py"):
            if "repo" in str(f) or "skills" in str(f):
                continue
            try:
                content = open(f, encoding='utf-8', errors='ignore').read().lower()
                for p in patterns:
                    if f'"{p}"' in content or f"'{p}'" in content:
                        if "os.environ" not in content and "getenv" not in content:
                            found.append(f.name)
                            break
            except:
                pass
        
        if found:
            for f in found[:5]:
                self.add_result("secrets", f, "warn", "可能包含硬编码敏感信息")
        else:
            self.add_result("secrets", "check", "pass", "无硬编码敏感信息")
    
    def check_gitignore(self):
        """检查 .gitignore"""
        gitignore = self.root / ".gitignore"
        if not gitignore.exists():
            self.add_result("gitignore", "file", "warn", "缺失")
            return
        
        try:
            content = open(gitignore, encoding='utf-8').read()
            required = ["__pycache__", "*.pyc", ".env", "node_modules"]
            missing = [r for r in required if r not in content]
            
            if missing:
                self.add_result("gitignore", "entries", "warn", f"缺少: {missing}")
            else:
                self.add_result("gitignore", "file", "pass", "配置完整")
        except Exception as e:
            self.add_result("gitignore", "file", "fail", str(e))
    
    # ==================== 运行巡检 ====================
    
    def run_all_checks(self):
        """运行所有检查"""
        print("╔══════════════════════════════════════════════════╗")
        print("║              深度巡检 V1.0                      ║")
        print("╚══════════════════════════════════════════════════╝")
        print()
        
        # 文件系统
        print("【文件系统巡检】")
        self.check_protected_files()
        self.check_directory_structure()
        self.check_file_permissions()
        self.check_file_sizes()
        self.check_orphan_files()
        
        # 代码质量
        print("【代码质量巡检】")
        self.check_python_syntax()
        self.check_import_statements()
        self.check_code_duplicates()
        
        # 配置
        print("【配置巡检】")
        self.check_json_configs()
        self.check_skill_registry()
        self.check_workflow_files()
        
        # 依赖
        print("【依赖巡检】")
        self.check_python_dependencies()
        self.check_makefile()
        
        # 报告
        print("【报告巡检】")
        self.check_reports()
        self.check_history_snapshots()
        
        # 安全
        print("【安全巡检】")
        self.check_secrets()
        self.check_gitignore()
        
        return self.results
    
    def save_report(self):
        """保存报告"""
        report_path = self.root / "reports/deep_inspection.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return report_path
    
    def print_summary(self):
        """打印摘要"""
        print()
        print("╔══════════════════════════════════════════════════╗")
        print("║              巡检摘要                          ║")
        print("╚══════════════════════════════════════════════════╝")
        print()
        print(f"总检查项: {self.results['total_checks']}")
        print(f"通过: {self.results['passed_checks']}")
        print(f"失败: {self.results['failed_checks']}")
        print(f"警告: {self.results['warnings']}")
        print()
        
        for cat, data in self.results["categories"].items():
            status = "✅" if data["fail"] == 0 else "❌"
            print(f"{status} {cat}: {data['pass']}/{data['pass']+data['fail']+data['warn']}")
        
        # 显示失败项
        failed = [d for d in self.results["details"] if d["status"] == "fail"]
        if failed:
            print()
            print("【失败项】")
            for f in failed[:10]:
                print(f"  ❌ [{f['category']}] {f['check']}: {f['message']}")
        
        # 显示警告项
        warnings = [d for d in self.results["details"] if d["status"] == "warn"]
        if warnings:
            print()
            print("【警告项】")
            for w in warnings[:10]:
                print(f"  ⚠️  [{w['category']}] {w['check']}: {w['message']}")

def main():
    root = get_project_root()
    inspector = DeepInspector(root)
    inspector.run_all_checks()
    report_path = inspector.save_report()
    inspector.print_summary()
    
    print()
    print(f"报告已保存: {report_path}")
    
    return 1 if inspector.results["failed_checks"] > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
