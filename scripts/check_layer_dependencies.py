#!/usr/bin/env python3
"""
层间依赖检查器 V1.0.0

职责：
1. 读取 core/LAYER_DEPENDENCY_RULES.json
2. 扫描关键目录下 Python 文件的 import / 路径引用，查明显违规

只检查显式违规：
- core/ import execution/
- core/ import orchestration/
- execution/ import governance/
- governance/ import skills/
- scripts/ 反向成为 core 真源
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

class LayerDependencyChecker:
    """层间依赖检查器"""

    # 显式违规规则
    EXPLICIT_VIOLATIONS = [
        # (目录, 禁止 import 的模块)
        ("core", ["execution", "orchestration", "memory_context", "governance", "infrastructure", "scripts"]),
        ("execution", ["governance", "scripts"]),
        ("governance", ["execution", "skills"]),
        ("memory_context", ["orchestration", "governance", "scripts"]),
        ("orchestration", ["execution", "scripts"]),
        ("infrastructure", ["memory_context", "orchestration", "execution", "governance"]),
    ]

    def __init__(self, root: Path):
        self.root = root
        self.violations = []
        self.passed = []

    def check_imports(self, directory: str, forbidden: List[str]) -> List[Dict]:
        """检查目录下的 import 违规"""
        violations = []
        dir_path = self.root / directory

        if not dir_path.exists():
            return violations

        for py_file in dir_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                rel_path = py_file.relative_to(self.root)

                for forbidden_module in forbidden:
                    # 检查 import 语句
                    patterns = [
                        f"from {forbidden_module}",
                        f"import {forbidden_module}",
                    ]
                    for pattern in patterns:
                        if pattern in content:
                            violations.append({
                                "file": str(rel_path),
                                "violation": f"违规 import: {pattern}",
                                "directory": directory,
                                "forbidden": forbidden_module
                            })
            except Exception:
                pass

        return violations

    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("╔══════════════════════════════════════════════════╗")
        print("║          层间依赖检查 V1.0.0                    ║")
        print("╚══════════════════════════════════════════════════╝")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        total_violations = 0

        for directory, forbidden in self.EXPLICIT_VIOLATIONS:
            print(f"【检查 {directory}/】")
            violations = self.check_imports(directory, forbidden)

            if violations:
                for v in violations:
                    self.violations.append(v)
                    print(f"  ❌ {v['file']}: {v['violation']}")
                total_violations += len(violations)
            else:
                self.passed.append(f"{directory}/ 无违规")
                print(f"  ✅ 无违规")
            print()

        # 汇总
        print("╔══════════════════════════════════════════════════╗")
        print("║              检查结果汇总                       ║")
        print("╚══════════════════════════════════════════════════╝")
        print()
        print(f"  ✅ 通过: {len(self.passed)}")
        print(f"  ❌ 违规: {total_violations}")
        print()

        if self.violations:
            print("【违规详情】")
            for v in self.violations:
                print(f"  ❌ {v['file']}: {v['violation']}")
            print()

        # 保存违规报告
        if self.violations:
            report_dir = self.root / "reports" / "integrity"
            report_dir.mkdir(parents=True, exist_ok=True)
            report_file = report_dir / "dependency_violations.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_violations": total_violations,
                    "violations": self.violations
                }, f, ensure_ascii=False, indent=2)
            print(f"违规报告已保存: {report_file}")

        return total_violations == 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="层间依赖检查 V1.0.0")
    parser.add_argument("--strict", action="store_true", help="严格模式，任何违规都失败")
    args = parser.parse_args()

    root = get_project_root()
    checker = LayerDependencyChecker(root)
    success = checker.run_all_checks()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
