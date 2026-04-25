#!/usr/bin/env python3
"""
系统完整性检查脚本
检查工程目录结构和关键文件
"""
import os
import json
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent

# 必须存在的目录
REQUIRED_DIRS = [
    "capabilities",
    "device_capability_bus",
    "autonomous_planner",
    "visual_operation_agent",
    "safety_governor",
    "learning_loop",
    "closed_loop_verifier",
    "tests",
    "scripts",
    "infrastructure",
    "skill_asset_registry",
    "skills",
    "application",
    "domain",
    "governance",
    "core",
    "orchestration",
]

# 必须存在的文件
REQUIRED_FILES = [
    "infrastructure/route_registry.json",
    "scripts/check_route_registry.py",
    "scripts/system_integrity_check.py",
    "safety_governor/risk_levels.py",
]

# 必须存在的测试文件
REQUIRED_TESTS = [
    "tests/test_route_risk_l0_l4_blocked_mapping.py",
    "tests/test_route_l4_strong_confirm_fields.py",
    "tests/test_route_blocked_policy_fields.py",
    "tests/test_no_legacy_route_risk_levels.py",
    "tests/test_route_safety_governor_consistency.py",
]


def check_directories():
    """检查必需目录"""
    errors = []
    warnings = []
    
    for dir_name in REQUIRED_DIRS:
        dir_path = WORKSPACE / dir_name
        if not dir_path.exists():
            errors.append(f"目录缺失: {dir_name}")
        elif not dir_path.is_dir():
            errors.append(f"不是目录: {dir_name}")
        else:
            # 检查目录是否有文件
            file_count = len(list(dir_path.rglob("*.*")))
            if file_count == 0:
                warnings.append(f"目录为空: {dir_name}")
    
    return errors, warnings


def check_files():
    """检查必需文件"""
    errors = []
    warnings = []
    
    for file_name in REQUIRED_FILES:
        file_path = WORKSPACE / file_name
        if not file_path.exists():
            errors.append(f"文件缺失: {file_name}")
        elif file_path.stat().st_size == 0:
            warnings.append(f"文件为空: {file_name}")
    
    return errors, warnings


def check_tests():
    """检查测试文件"""
    errors = []
    warnings = []
    
    for test_name in REQUIRED_TESTS:
        test_path = WORKSPACE / test_name
        if not test_path.exists():
            errors.append(f"测试缺失: {test_name}")
        elif test_path.stat().st_size == 0:
            warnings.append(f"测试为空: {test_name}")
    
    return errors, warnings


def check_route_registry():
    """检查 route_registry.json"""
    errors = []
    warnings = []
    info = []
    
    route_path = WORKSPACE / "infrastructure" / "route_registry.json"
    
    if not route_path.exists():
        errors.append("route_registry.json 不存在")
        return errors, warnings, info
    
    try:
        with open(route_path) as f:
            data = json.load(f)
        
        # 检查 routes 数量
        routes = data.get("routes", {})
        route_count = len(routes)
        info.append(f"routes 数量: {route_count}")
        
        if route_count == 0:
            errors.append("routes 为空")
        elif route_count != 53:
            warnings.append(f"routes 数量不是 53: {route_count}")
        
        # 检查风险等级
        valid_levels = {"L0", "L1", "L2", "L3", "L4", "BLOCKED"}
        legacy_levels = {"LOW", "MEDIUM", "HIGH", "SYSTEM", "CRITICAL"}
        
        for route_id, route in routes.items():
            risk_level = route.get("risk_level", "")
            if risk_level in legacy_levels:
                errors.append(f"旧口径风险等级: {route_id} = {risk_level}")
            elif risk_level not in valid_levels:
                errors.append(f"无效风险等级: {route_id} = {risk_level}")
        
        # 检查 stats
        stats = data.get("stats", {})
        by_risk_level = stats.get("by_risk_level", {})
        
        for level in by_risk_level.keys():
            if level in legacy_levels:
                errors.append(f"stats 中有旧口径: {level}")
            elif level not in valid_levels:
                errors.append(f"stats 中有无效等级: {level}")
        
        info.append(f"风险等级分布: {json.dumps(by_risk_level)}")
        
    except json.JSONDecodeError as e:
        errors.append(f"JSON 解析错误: {e}")
    except Exception as e:
        errors.append(f"读取错误: {e}")
    
    return errors, warnings, info


def main():
    """主函数"""
    print("=" * 60)
    print("系统完整性检查报告")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    total_errors = 0
    total_warnings = 0
    
    # 检查目录
    print("📁 目录检查:")
    errors, warnings = check_directories()
    total_errors += len(errors)
    total_warnings += len(warnings)
    
    for e in errors:
        print(f"   ❌ {e}")
    for w in warnings:
        print(f"   ⚠️  {w}")
    
    if not errors and not warnings:
        print("   ✅ 所有必需目录存在")
    print()
    
    # 检查文件
    print("📄 文件检查:")
    errors, warnings = check_files()
    total_errors += len(errors)
    total_warnings += len(warnings)
    
    for e in errors:
        print(f"   ❌ {e}")
    for w in warnings:
        print(f"   ⚠️  {w}")
    
    if not errors and not warnings:
        print("   ✅ 所有必需文件存在")
    print()
    
    # 检查测试
    print("🧪 测试检查:")
    errors, warnings = check_tests()
    total_errors += len(errors)
    total_warnings += len(warnings)
    
    for e in errors:
        print(f"   ❌ {e}")
    for w in warnings:
        print(f"   ⚠️  {w}")
    
    if not errors and not warnings:
        print("   ✅ 所有必需测试存在")
    print()
    
    # 检查 route_registry
    print("🛣️  Route Registry 检查:")
    errors, warnings, info = check_route_registry()
    total_errors += len(errors)
    total_warnings += len(warnings)
    
    for e in errors:
        print(f"   ❌ {e}")
    for w in warnings:
        print(f"   ⚠️  {w}")
    for i in info:
        print(f"   ℹ️  {i}")
    
    if not errors and not warnings:
        print("   ✅ Route Registry 检查通过")
    print()
    
    # 总结
    print("=" * 60)
    print("📊 总结:")
    print(f"   错误: {total_errors}")
    print(f"   警告: {total_warnings}")
    
    if total_errors == 0:
        print()
        print("✅ 系统完整性检查通过")
        return 0
    else:
        print()
        print("❌ 系统完整性检查失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
