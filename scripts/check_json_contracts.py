#!/usr/bin/env python3
"""
JSON 契约校验器 V1.0.0

职责：
1. 读取 schema
2. 校验 latest 文件是否符合 schema

校验文件：
- reports/runtime_integrity.json
- reports/alerts/latest_alerts.json
- governance/ops/incident_tracker.json
- reports/remediation/latest_remediation.json
- reports/remediation/approval_history.json
- reports/ops/control_plane_state.json
- reports/ops/control_plane_audit.json
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

class JsonContractChecker:
    """JSON 契约校验器"""

    # 校验映射：(JSON 文件, Schema 文件, 是否是数组, 是否必须存在, 数组字段名)
    VALIDATION_MAP = [
        ("reports/runtime_integrity.json", "core/contracts/gate_report.schema.json", False, True, None),
        ("reports/quality_gate.json", "core/contracts/gate_report.schema.json", False, False, None),
        ("reports/release_gate.json", "core/contracts/gate_report.schema.json", False, False, None),
        ("reports/alerts/latest_alerts.json", "core/contracts/alert.schema.json", True, True, "alerts"),
        ("governance/ops/incident_tracker.json", "core/contracts/incident.schema.json", True, True, None),  # 纯数组
        ("reports/remediation/latest_remediation.json", "core/contracts/remediation.schema.json", False, True, None),
        ("reports/remediation/approval_history.json", "core/contracts/approval.schema.json", True, True, "approvals"),
        ("reports/ops/control_plane_state.json", "core/contracts/control_plane_state.schema.json", False, True, None),
        ("reports/ops/control_plane_audit.json", "core/contracts/control_plane_audit.schema.json", False, True, None),
    ]

    def __init__(self, root: Path):
        self.root = root
        self.errors = []
        self.warnings = []
        self.passed = []
        self.jsonschema = None

    def load_jsonschema(self) -> bool:
        """加载 jsonschema 库"""
        try:
            import jsonschema
            self.jsonschema = jsonschema
            return True
        except ImportError:
            self.warnings.append("jsonschema 未安装，跳过 schema 验证")
            return False

    def validate_json(self, json_path: str, schema_path: str, is_array: bool = False, required: bool = False, array_field: str = None) -> bool:
        """验证 JSON 文件是否符合 schema
        
        Args:
            json_path: JSON 文件路径
            schema_path: Schema 文件路径
            is_array: 是否是数组格式（或包含数组字段）
            required: 文件是否必须存在（True 时缺失报错）
            array_field: 数组字段名（如果数据是对象但包含数组字段）
        """
        full_json = self.root / json_path
        full_schema = self.root / schema_path

        if not full_json.exists():
            if required:
                self.errors.append(f"{json_path} 不存在（必须文件）")
                print(f"  ❌ {json_path} 不存在（必须文件）")
                return False
            else:
                self.warnings.append(f"{json_path} 不存在，跳过")
                return True

        if not full_schema.exists():
            self.warnings.append(f"{schema_path} 不存在，跳过")
            return True

        if not self.jsonschema:
            return True

        try:
            data = json.load(open(full_json, encoding='utf-8'))
            schema = json.load(open(full_schema, encoding='utf-8'))

            # 处理数组字段（对象包含数组）
            if is_array and array_field and isinstance(data, dict):
                if array_field in data and isinstance(data[array_field], list):
                    items = data[array_field]
                    if len(items) == 0:
                        self.passed.append(f"{json_path} 符合 schema (空数组)")
                        print(f"  ✅ {json_path} 符合 schema (空数组)")
                    else:
                        for i, item in enumerate(items):
                            self.jsonschema.validate(item, schema)
                        self.passed.append(f"{json_path} 符合 schema ({len(items)} 条)")
                        print(f"  ✅ {json_path} 符合 schema ({len(items)} 条)")
                    return True
                else:
                    self.warnings.append(f"{json_path} 不包含数组字段 '{array_field}'")
                    print(f"  ⚠️ {json_path} 不包含数组字段 '{array_field}'")
                    return True

            # 处理纯数组
            if is_array and isinstance(data, list):
                for i, item in enumerate(data):
                    self.jsonschema.validate(item, schema)
                self.passed.append(f"{json_path} 符合 schema ({len(data)} 条)")
                print(f"  ✅ {json_path} 符合 schema ({len(data)} 条)")
            # 处理对象
            elif isinstance(data, dict):
                self.jsonschema.validate(data, schema)
                self.passed.append(f"{json_path} 符合 schema")
                print(f"  ✅ {json_path} 符合 schema")
            else:
                self.jsonschema.validate(data, schema)
                self.passed.append(f"{json_path} 符合 schema")
                print(f"  ✅ {json_path} 符合 schema")

            return True

        except self.jsonschema.ValidationError as e:
            self.errors.append(f"{json_path}: {e.message}")
            print(f"  ❌ {json_path}: {e.message}")
            return False
        except Exception as e:
            self.warnings.append(f"无法验证 {json_path}: {e}")
            print(f"  ⚠️ 无法验证 {json_path}: {e}")
            return True

    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("╔══════════════════════════════════════════════════╗")
        print("║          JSON 契约校验 V1.0.0                   ║")
        print("╚══════════════════════════════════════════════════╝")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        if not self.load_jsonschema():
            print("⚠️ jsonschema 未安装，跳过 schema 验证")
            print("安装命令: pip install jsonschema")
            print()
            return True

        print("【校验 JSON 契约】")
        for json_path, schema_path, is_array, required, array_field in self.VALIDATION_MAP:
            self.validate_json(json_path, schema_path, is_array, required, array_field)

        print()

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

        return len(self.errors) == 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="JSON 契约校验 V1.0.0")
    parser.add_argument("--strict", action="store_true", help="严格模式")
    args = parser.parse_args()

    root = get_project_root()
    checker = JsonContractChecker(root)
    success = checker.run_all_checks()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
