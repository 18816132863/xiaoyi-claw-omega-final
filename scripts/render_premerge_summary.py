#!/usr/bin/env python3
"""渲染 premerge summary"""

import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent

    print("## 🔍 Premerge Summary")
    print()

    # Runtime integrity
    runtime_path = root / "reports/runtime_integrity.json"
    if runtime_path.exists():
        try:
            data = json.load(open(runtime_path, encoding='utf-8'))
            passed = data.get("overall_passed", False)
            status = "✅" if passed else "❌"
            print(f"**Runtime Gate**: {status}")
            print(f"- P0: {data.get('p0_count', 0)}")
            print(f"- P1: {data.get('p1_count', 0)}")
            print(f"- P2: {data.get('p2_count', 0)}")
            print()
        except:
            print("**Runtime Gate**: ⚠️ 无法读取")
            print()

    # Quality gate
    quality_path = root / "reports/quality_gate.json"
    if quality_path.exists():
        try:
            data = json.load(open(quality_path, encoding='utf-8'))
            passed = data.get("overall_passed", False)
            status = "✅" if passed else "❌"
            print(f"**Quality Gate**: {status}")
            print(f"- Protected files: {data.get('protected_files', {}).get('message', 'N/A')}")
            print(f"- Skill registry: {data.get('skill_registry', {}).get('message', 'N/A')}")
            print()
        except:
            print("**Quality Gate**: ⚠️ 无法读取")
            print()

if __name__ == "__main__":
    main()
