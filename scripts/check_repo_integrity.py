#!/usr/bin/env python3
"""
仓库完整性检查 - V1.0.0

检查：
1. workflow 引用的命令入口是否真实存在
2. 主链脚本引用的文件是否真实存在
3. governance / infrastructure / scripts 之间的关键入口是否断链
4. Makefile 目标是否和 workflow 保持一致
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

class RepoIntegrityChecker:
    """仓库完整性检查器"""

    # 必须存在的关键文件
    REQUIRED_FILES = [
        "Makefile",
        "infrastructure/verify_runtime_integrity.py",
        "infrastructure/release/release_manager.py",
        "infrastructure/path_resolver.py",
        "infrastructure/inventory/skill_registry.json",
        "infrastructure/inventory/skill_inverted_index.json",
        "governance/quality_gate.py",
        "governance/guard/protected_files.json",
        "scripts/run_release_gate.py",
        "scripts/run_nightly_audit.py",
        "scripts/generate_alerts.py",
        "scripts/build_ops_dashboard.py",
        "scripts/ops_center.py",
        "scripts/remediation_center.py",
        "execution/skill_adapter_gateway.py",
        "execution/skill_gateway.py",
        "skills/docx/skill.py",
        "skills/pdf/skill.py",
        "skills/cron/skill.py",
        "skills/file-manager/skill.py",
        "tests/fixtures/smoke/blank.pdf",
        "tests/fixtures/smoke/sample.docx",
        "tests/fixtures/integration/file_manager/source/sample.txt",
    ]

    # 必须存在的目录
    REQUIRED_DIRS = [
        "core",
        "governance",
        "infrastructure",
        "scripts",
        ".github/workflows",
        "reports",
        "reports/alerts",
        "reports/bundles",
        "reports/dashboard",
        "reports/ops",
        "reports/remediation",
        "reports/trends",
        "reports/history",
    ]

    # Makefile 必须支持的目标
    REQUIRED_MAKE_TARGETS = [
        "verify-premerge",
        "verify-nightly",
        "verify-release",
    ]

    def __init__(self, root: Path, strict: bool = False):
        self.root = root
        self.strict = strict
        self.errors = []
        self.warnings = []
        self.passed = []

    def check_file_exists(self, rel_path: str) -> bool:
        """检查文件是否存在"""
        full_path = self.root / rel_path
        if full_path.exists():
            return True
        return False

    def check_dir_exists(self, rel_path: str) -> bool:
        """检查目录是否存在"""
        full_path = self.root / rel_path
        if full_path.is_dir():
            return True
        return False

    def check_required_files(self):
        """检查必需文件"""
        print("【检查必需文件】")
        for f in self.REQUIRED_FILES:
            if self.check_file_exists(f):
                self.passed.append(f"文件存在: {f}")
                print(f"  ✅ {f}")
            else:
                self.errors.append(f"文件缺失: {f}")
                print(f"  ❌ {f} (缺失)")
        print()

    def check_required_dirs(self):
        """检查必需目录"""
        print("【检查必需目录】")
        for d in self.REQUIRED_DIRS:
            if self.check_dir_exists(d):
                self.passed.append(f"目录存在: {d}")
                print(f"  ✅ {d}")
            else:
                self.errors.append(f"目录缺失: {d}")
                print(f"  ❌ {d} (缺失)")
        print()

    def check_makefile_targets(self):
        """检查 Makefile 目标"""
        print("【检查 Makefile 目标】")
        makefile_path = self.root / "Makefile"

        if not makefile_path.exists():
            self.errors.append("Makefile 缺失")
            print("  ❌ Makefile 缺失")
            print()
            return

        content = makefile_path.read_text()

        for target in self.REQUIRED_MAKE_TARGETS:
            if f"{target}:" in content:
                self.passed.append(f"Makefile 目标存在: {target}")
                print(f"  ✅ {target}")
            else:
                self.errors.append(f"Makefile 目标缺失: {target}")
                print(f"  ❌ {target} (缺失)")
        print()

    def check_workflow_integrity(self):
        """检查 workflow 完整性"""
        print("【检查 Workflow 完整性】")
        workflows_dir = self.root / ".github" / "workflows"

        if not workflows_dir.exists():
            self.errors.append(".github/workflows 目录缺失")
            print("  ❌ .github/workflows 目录缺失")
            print()
            return

        workflow_files = list(workflows_dir.glob("*.yml"))

        for wf in workflow_files:
            print(f"  检查 {wf.name}...")
            try:
                content = yaml.safe_load(wf.read_text())
                self.passed.append(f"Workflow 解析成功: {wf.name}")
                print(f"    ✅ 解析成功")
                self._check_workflow_commands(wf.name, content)
            except yaml.YAMLError as e:
                # 严格模式下，YAML 解析失败是错误
                self.errors.append(f"Workflow YAML 解析失败: {wf.name}: {str(e)[:100]}")
                print(f"    ❌ YAML 解析失败: {str(e)[:50]}")
            except Exception as e:
                self.warnings.append(f"无法解析 {wf.name}: {e}")
                print(f"    ⚠️ 无法解析: {e}")

        print()

    def _check_workflow_commands(self, wf_name: str, content: dict):
        """检查 workflow 中的命令"""
        jobs = content.get("jobs", {})

        for job_name, job in jobs.items():
            steps = job.get("steps", [])
            for step in steps:
                run_cmd = step.get("run", "")
                if not run_cmd:
                    continue

                # 检查 python scripts/ 调用
                if "python scripts/" in run_cmd:
                    lines = run_cmd.split("\n")
                    for line in lines:
                        if "python scripts/" in line:
                            # 提取脚本名
                            parts = line.split("python scripts/")
                            if len(parts) > 1:
                                script_part = parts[1].split()[0]
                                script_path = f"scripts/{script_part}"
                                if not self.check_file_exists(script_path):
                                    self.errors.append(f"{wf_name} 引用不存在的脚本: {script_path}")
                                    print(f"    ❌ 引用不存在: {script_path}")

                # 检查 make 调用
                if "make " in run_cmd:
                    lines = run_cmd.split("\n")
                    for line in lines:
                        if "make " in line:
                            parts = line.split("make ")
                            if len(parts) > 1:
                                target = parts[1].split()[0]
                                # 检查 Makefile 是否有这个目标
                                makefile = self.root / "Makefile"
                                if makefile.exists():
                                    if f"{target}:" not in makefile.read_text():
                                        self.errors.append(f"{wf_name} 引用不存在的 make 目标: {target}")
                                        print(f"    ❌ Make 目标不存在: {target}")

    def check_script_dependencies(self):
        """检查脚本依赖"""
        print("【检查脚本依赖】")

        # run_release_gate.py 依赖
        deps = [
            ("scripts/run_release_gate.py", "infrastructure/verify_runtime_integrity.py"),
            ("scripts/run_release_gate.py", "governance/quality_gate.py"),
            ("scripts/run_nightly_audit.py", "infrastructure/verify_runtime_integrity.py"),
            ("scripts/build_ops_dashboard.py", "reports/"),
            ("scripts/ops_center.py", "reports/"),
            ("scripts/remediation_center.py", "infrastructure/remediation/"),
        ]

        for script, dep in deps:
            script_path = self.root / script
            dep_path = self.root / dep

            if not script_path.exists():
                self.warnings.append(f"脚本不存在，跳过依赖检查: {script}")
                continue

            if dep.endswith("/"):
                # 目录依赖
                if dep_path.is_dir():
                    self.passed.append(f"{script} -> {dep}")
                    print(f"  ✅ {script} -> {dep}/")
                else:
                    self.errors.append(f"{script} 依赖目录不存在: {dep}")
                    print(f"  ❌ {script} -> {dep}/ (缺失)")
            else:
                # 文件依赖
                if dep_path.exists():
                    self.passed.append(f"{script} -> {dep}")
                    print(f"  ✅ {script} -> {dep}")
                else:
                    self.errors.append(f"{script} 依赖文件不存在: {dep}")
                    print(f"  ❌ {script} -> {dep} (缺失)")

        print()

    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("╔══════════════════════════════════════════════════╗")
        print("║          仓库完整性检查                         ║")
        print("╚══════════════════════════════════════════════════╝")
        print()

        self.check_required_dirs()
        self.check_required_files()
        self.check_makefile_targets()
        self.check_workflow_integrity()
        self.check_script_dependencies()

        # 汇总
        print("╔══════════════════════════════════════════════════╗")
        print("║              检查结果汇总                       ║")
        print("╚══════════════════════════════════════════════════╝")
        print()
        print(f"  ✅ 通过: {len(self.passed)}")
        print(f"  ⚠️ 警告: {len(self.warnings)}")
        print(f"  ❌ 错误: {len(self.errors)}")
        print()

        if self.errors:
            print("【错误详情】")
            for e in self.errors:
                print(f"  ❌ {e}")
            print()

        if self.warnings:
            print("【警告详情】")
            for w in self.warnings:
                print(f"  ⚠️ {w}")
            print()

        # 严格模式下，任何错误都失败
        if self.strict and self.errors:
            print("❌ 严格模式：检查失败")
            return False

        if self.errors:
            print("⚠️ 存在错误，请修复")
            return False

        print("✅ 所有检查通过")
        return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="仓库完整性检查")
    parser.add_argument("--strict", action="store_true", help="严格模式，任何错误都失败")
    args = parser.parse_args()

    root = get_project_root()
    checker = RepoIntegrityChecker(root, args.strict)
    success = checker.run_all_checks()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
