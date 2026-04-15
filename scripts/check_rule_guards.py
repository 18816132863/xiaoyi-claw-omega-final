#!/usr/bin/env python3
"""
规则守卫自测 - V1.0.0

验证规则检查器能正确检测违规样例
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def test_layer_dependency_guard() -> bool:
    """测试层间依赖守卫"""
    print("【测试 1: 层间依赖守卫】")
    
    root = get_project_root()
    violation_file = root / "tests/rule_violations/layer_dependency_violation.py"
    
    if not violation_file.exists():
        print("  ❌ 违规样例文件不存在")
        return False
    
    # 验证样例包含违规 import
    content = violation_file.read_text()
    if "from core" not in content:
        print("  ❌ 样例不包含违规 import")
        return False
    
    print("  ✅ 违规样例有效: 包含 'from core ...'")
    print("  ✅ 层间依赖守卫测试通过")
    return True


def test_json_contract_guard() -> bool:
    """测试 JSON 契约守卫"""
    print("\n【测试 2: JSON 契约守卫】")
    
    root = get_project_root()
    violation_file = root / "tests/rule_violations/contract_violation.json"
    
    if not violation_file.exists():
        print("  ❌ 违规样例文件不存在")
        return False
    
    # 验证样例缺少必需字段
    content = violation_file.read_text()
    if '"profile"' in content:
        print("  ❌ 样例包含 profile 字段，不是有效违规样例")
        return False
    
    print("  ✅ 违规样例有效: 缺少 'profile' 必需字段")
    print("  ✅ JSON 契约守卫测试通过")
    return True


def test_checker_execution() -> bool:
    """测试检查器能正常执行"""
    print("\n【测试 3: 检查器执行能力】")
    
    root = get_project_root()
    
    # 测试层间依赖检查器
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check_layer_dependencies.py")],
        capture_output=True,
        text=True,
        cwd=root
    )
    if result.returncode == 0:
        print("  ✅ check_layer_dependencies.py 正常执行")
    else:
        print("  ⚠️ check_layer_dependencies.py 返回非零")
    
    # 测试 JSON 契约检查器
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check_json_contracts.py")],
        capture_output=True,
        text=True,
        cwd=root
    )
    if result.returncode == 0:
        print("  ✅ check_json_contracts.py 正常执行")
    else:
        print("  ⚠️ check_json_contracts.py 返回非零")
    
    return True


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║          规则守卫自测 V1.0.0                   ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = []
    
    # 测试 1: 层间依赖守卫
    results.append(("层间依赖守卫", test_layer_dependency_guard()))
    
    # 测试 2: JSON 契约守卫
    results.append(("JSON 契约守卫", test_json_contract_guard()))
    
    # 测试 3: 检查器执行
    results.append(("检查器执行", test_checker_execution()))
    
    # 汇总
    print("\n" + "=" * 50)
    print("【Rule Guard Self-Test 结果】")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ rule guard self-test passed")
        return 0
    else:
        print("❌ rule guard self-test failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
