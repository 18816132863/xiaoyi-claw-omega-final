#!/usr/bin/env python3
"""
仓库完整性检查 - V3.0.0

检查：
1. 必需文件和目录存在
2. Makefile 目标完整
3. Workflow 完整性
4. 脚本依赖完整
5. 审批历史与 remediation history 一致性
6. 调用 layer dependency 检查（新增）
7. 调用 json contract 检查（新增）
8. 检查唯一真源文件是否存在（新增）
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

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
        "core/ARCHITECTURE.md",
        "core/LAYER_DEPENDENCY_MATRIX.md",
        "core/LAYER_DEPENDENCY_RULES.json",
        "core/LAYER_IO_CONTRACTS.md",
        "core/CHANGE_IMPACT_MATRIX.md",
        "core/SINGLE_SOURCE_OF_TRUTH.md",
        "infrastructure/verify_runtime_integrity.py",
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
        "scripts/approval_manager.py",
        "scripts/control_plane.py",
        "scripts/control_plane_audit.py",
        "scripts/check_repo_integrity.py",
        "scripts/check_layer_dependencies.py",
        "scripts/check_json_contracts.py",
        "execution/skill_adapter_gateway.py",
        "execution/skill_gateway.py",
    ]

    # 必须存在的目录
    REQUIRED_DIRS = [
        "core",
        "core/contracts",
        "governance",
        "infrastructure",
        "infrastructure/inventory",
        "scripts",
        ".github/workflows",
        "reports",
        "reports/alerts",
        "reports/bundles",
        "reports/dashboard",
        "reports/ops",
        "reports/remediation",
        "reports/remediation/history",
        "reports/trends",
        "reports/history",
        "skills",
        "execution",
        "orchestration",
        "memory_context",
    ]

    # 唯一真源文件
    SINGLE_SOURCE_FILES = [
        "core/LAYER_DEPENDENCY_MATRIX.md",
        "core/LAYER_DEPENDENCY_RULES.json",
        "core/LAYER_IO_CONTRACTS.md",
        "core/CHANGE_IMPACT_MATRIX.md",
        "core/SINGLE_SOURCE_OF_TRUTH.md",
    ]

    # Schema 文件与对应的 contract
    SCHEMA_CONTRACTS = {
        "core/contracts/gate_report.schema.json": ["reports/runtime_integrity.json", "reports/quality_gate.json", "reports/release_gate.json"],
        "core/contracts/alert.schema.json": ["reports/alerts/latest_alerts.json"],
        "core/contracts/incident.schema.json": ["governance/ops/incident_tracker.json"],
        "core/contracts/remediation.schema.json": ["reports/remediation/latest_remediation.json"],
        "core/contracts/approval.schema.json": ["reports/remediation/approval_history.json"],
        "core/contracts/control_plane_state.schema.json": ["reports/ops/control_plane_state.json"],
        "core/contracts/control_plane_audit.schema.json": ["reports/ops/control_plane_audit.json"],
    }

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
        return full_path.exists()

    def check_dir_exists(self, rel_path: str) -> bool:
        """检查目录是否存在"""
        full_path = self.root / rel_path
        return full_path.is_dir()

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

    def check_single_source_files(self):
        """检查唯一真源文件"""
        print("【检查唯一真源文件】")
        for f in self.SINGLE_SOURCE_FILES:
            if self.check_file_exists(f):
                self.passed.append(f"真源文件存在: {f}")
                print(f"  ✅ {f}")
            else:
                self.errors.append(f"真源文件缺失: {f}")
                print(f"  ❌ {f} (缺失)")
        print()

    def check_schema_contracts(self):
        """检查 Schema 与 Contract 对应关系"""
        print("【检查 Schema 与 Contract 对应】")
        for schema_file, contract_files in self.SCHEMA_CONTRACTS.items():
            # 检查 schema 文件存在
            if not self.check_file_exists(schema_file):
                self.errors.append(f"Schema 文件缺失: {schema_file}")
                print(f"  ❌ Schema 缺失: {schema_file}")
                continue
            
            # 检查对应的 contract 文件
            for contract_file in contract_files:
                if self.check_file_exists(contract_file):
                    self.passed.append(f"Contract 存在: {contract_file}")
                    print(f"  ✅ {contract_file} -> {schema_file}")
                else:
                    self.errors.append(f"Contract 文件缺失: {contract_file} (对应 {schema_file})")
                    print(f"  ❌ Contract 缺失: {contract_file}")
        print()

    def check_rules_self_consistency(self):
        """检查规则层自洽性"""
        print("【检查规则层自洽性】")
        
        # 1. 检查 LAYER_DEPENDENCY_RULES.json 与 check_layer_dependencies.py 一致性
        rules_file = self.root / "core/LAYER_DEPENDENCY_RULES.json"
        checker_file = self.root / "scripts/check_layer_dependencies.py"
        
        if rules_file.exists() and checker_file.exists():
            try:
                rules = json.load(open(rules_file, encoding='utf-8'))
                layers = rules.get("layers", {})
                
                # 检查 checker 是否读取了规则文件
                checker_content = checker_file.read_text()
                if "LAYER_DEPENDENCY_RULES.json" in checker_content:
                    self.passed.append("check_layer_dependencies.py 使用规则文件")
                    print(f"  ✅ check_layer_dependencies.py 正确引用规则文件")
                else:
                    self.warnings.append("check_layer_dependencies.py 未引用规则文件")
                    print(f"  ⚠️ check_layer_dependencies.py 未引用 LAYER_DEPENDENCY_RULES.json")
            except Exception as e:
                self.warnings.append(f"无法检查规则一致性: {e}")
                print(f"  ⚠️ 无法检查: {e}")
        
        # 2. 检查 skill_registry.json 与 skill_inverted_index.json 的真源/派生关系
        registry_file = self.root / "infrastructure/inventory/skill_registry.json"
        index_file = self.root / "infrastructure/inventory/skill_inverted_index.json"
        
        if registry_file.exists() and index_file.exists():
            try:
                index_data = json.load(open(index_file, encoding='utf-8'))
                
                # 检查 index 是否标注为派生物
                if index_data.get("derived") == True:
                    self.passed.append("skill_inverted_index.json 正确标注为派生物")
                    print(f"  ✅ skill_inverted_index.json 正确标注为派生物")
                else:
                    self.warnings.append("skill_inverted_index.json 未标注为派生物")
                    print(f"  ⚠️ skill_inverted_index.json 未标注 derived=true")
                
                # 检查 source 字段是否指向 registry
                source = index_data.get("source", "")
                if "skill_registry.json" in source:
                    self.passed.append("skill_inverted_index.json source 指向正确")
                    print(f"  ✅ skill_inverted_index.json source 指向 skill_registry.json")
                else:
                    self.warnings.append("skill_inverted_index.json source 未指向 skill_registry.json")
                    print(f"  ⚠️ skill_inverted_index.json source 应指向 skill_registry.json")
                    
            except Exception as e:
                self.warnings.append(f"无法检查 skill index: {e}")
                print(f"  ⚠️ 无法检查: {e}")
        
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

    def check_approval_history_consistency(self):
        """检查审批历史与 remediation history 一致性"""
        print("【检查审批历史一致性】")
        approval_history_path = self.root / "reports/remediation/approval_history.json"
        remediation_history_dir = self.root / "reports/remediation/history"

        if not approval_history_path.exists():
            print("  ⚠️ approval_history.json 不存在，跳过")
            print()
            return

        try:
            data = json.load(open(approval_history_path, encoding='utf-8'))
            approvals = data.get("approvals", [])

            checked = 0
            for approval in approvals:
                if approval.get("status") != "executed":
                    continue

                execute_record_id = approval.get("execute_record_id")
                if execute_record_id:
                    history_file = remediation_history_dir / f"{execute_record_id}.json"
                    if not history_file.exists():
                        self.errors.append(f"executed 审批缺少 remediation history: {execute_record_id}")
                        print(f"  ❌ 缺失 remediation history: {execute_record_id}")
                    else:
                        checked += 1

            if checked > 0:
                self.passed.append(f"{checked} 条 executed 审批有对应的 remediation history")
                print(f"  ✅ {checked} 条 executed 审批有对应的 remediation history")
        except Exception as e:
            self.warnings.append(f"无法检查审批历史一致性: {e}")
            print(f"  ⚠️ 无法检查: {e}")

        print()

    def run_layer_dependency_check(self) -> bool:
        """调用层间依赖检查"""
        print("【调用层间依赖检查】")
        script_path = self.root / "scripts/check_layer_dependencies.py"

        if not script_path.exists():
            self.warnings.append("check_layer_dependencies.py 不存在，跳过")
            print("  ⚠️ check_layer_dependencies.py 不存在，跳过")
            print()
            return True

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.passed.append("层间依赖检查通过")
                print("  ✅ 层间依赖检查通过")
            else:
                self.errors.append("层间依赖检查失败")
                print("  ❌ 层间依赖检查失败")
                if result.stdout:
                    print(result.stdout[-500:])

        except Exception as e:
            self.warnings.append(f"无法运行层间依赖检查: {e}")
            print(f"  ⚠️ 无法运行: {e}")

        print()
        return True

    def run_json_contract_check(self) -> bool:
        """调用 JSON 契约检查"""
        print("【调用 JSON 契约检查】")
        script_path = self.root / "scripts/check_json_contracts.py"

        if not script_path.exists():
            self.warnings.append("check_json_contracts.py 不存在，跳过")
            print("  ⚠️ check_json_contracts.py 不存在，跳过")
            print()
            return True

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.passed.append("JSON 契约检查通过")
                print("  ✅ JSON 契约检查通过")
            else:
                self.errors.append("JSON 契约检查失败")
                print("  ❌ JSON 契约检查失败")
                if result.stdout:
                    print(result.stdout[-500:])

        except Exception as e:
            self.warnings.append(f"无法运行 JSON 契约检查: {e}")
            print(f"  ⚠️ 无法运行: {e}")

        print()
        return True

    def run_rule_guards_self_test(self) -> bool:
        """调用规则守卫自测"""
        print("【调用规则守卫自测】")
        script_path = self.root / "scripts/check_rule_guards.py"

        if not script_path.exists():
            self.warnings.append("check_rule_guards.py 不存在，跳过")
            print("  ⚠️ check_rule_guards.py 不存在，跳过")
            print()
            return True

        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.passed.append("规则守卫自测通过")
                print("  ✅ 规则守卫自测通过")
            else:
                self.errors.append("规则守卫自测失败")
                print("  ❌ 规则守卫自测失败")
                if result.stdout:
                    print(result.stdout[-500:])

        except Exception as e:
            self.warnings.append(f"无法运行规则守卫自测: {e}")
            print(f"  ⚠️ 无法运行: {e}")

        print()
        return True

    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("╔══════════════════════════════════════════════════╗")
        print("║          仓库完整性检查 V3.0.0                  ║")
        print("╚══════════════════════════════════════════════════╝")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        self.check_required_dirs()
        self.check_required_files()
        self.check_single_source_files()
        self.check_schema_contracts()
        self.check_rules_self_consistency()
        self.check_makefile_targets()
        self.check_approval_history_consistency()

        # 新增：调用两个检查脚本
        self.run_layer_dependency_check()
        self.run_json_contract_check()
        
        # 新增：规则守卫自测
        self.run_rule_guards_self_test()

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
    parser = argparse.ArgumentParser(description="仓库完整性检查 V3.0.0")
    parser.add_argument("--strict", action="store_true", help="严格模式，任何错误都失败")
    args = parser.parse_args()

    root = get_project_root()
    checker = RepoIntegrityChecker(root, args.strict)
    success = checker.run_all_checks()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
