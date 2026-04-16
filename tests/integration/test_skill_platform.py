"""
Phase3 Group3 验证示例
Skills 正式插件平台化验证
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import tempfile
from datetime import datetime


def create_test_skill_package(skill_id: str, version: str, **kwargs) -> dict:
    """创建测试技能包"""
    return {
        "skill_id": skill_id,
        "name": kwargs.get("name", f"Test Skill {skill_id}"),
        "version": version,
        "description": kwargs.get("description", "A test skill"),
        "entry_point": kwargs.get("entry_point", f"skills.{skill_id}.main"),
        "input_schema": kwargs.get("input_schema", {"type": "object"}),
        "output_schema": kwargs.get("output_schema", {"type": "object"}),
        "dependencies": kwargs.get("dependencies", []),
        "compatible_profiles": kwargs.get("compatible_profiles", ["default"]),
        "compatible_runtime_versions": kwargs.get("compatible_runtime_versions", []),
        "status": kwargs.get("status", "active"),
        "health_status": kwargs.get("health_status", "unknown"),
        "timeout_ms": kwargs.get("timeout_ms", 30000)
    }


def test_skill_package():
    """测试 1: 正式 skill package 示例"""
    print("\n" + "=" * 60)
    print("测试 1: 正式 Skill Package 示例")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建技能包
        skill_dir = os.path.join(tmpdir, "test_skill")
        os.makedirs(skill_dir)

        package = create_test_skill_package(
            "test_skill",
            "1.0.0",
            name="测试技能",
            description="用于验证的测试技能",
            dependencies=[
                {"skill_id": "dep_skill", "version_range": "^1.0.0", "optional": False}
            ],
            compatible_profiles=["default", "production"],
            compatible_runtime_versions=["32.0.0"]
        )

        with open(os.path.join(skill_dir, "package.json"), 'w') as f:
            json.dump(package, f, indent=2)

        # 加载技能包
        loader = SkillPackageLoader()
        result = loader.load(skill_dir)

        print(f"\n加载结果:")
        print(f"  - 成功: {result.success}")
        print(f"  - 技能 ID: {result.package.skill_id if result.package else 'N/A'}")
        print(f"  - 版本: {result.package.version if result.package else 'N/A'}")
        print(f"  - 名称: {result.package.name if result.package else 'N/A'}")
        print(f"  - 状态: {result.package.status if result.package else 'N/A'}")
        print(f"  - 依赖: {result.package.dependencies if result.package else []}")

        if result.warnings:
            print(f"  - 警告: {result.warnings}")

        return result.success


def test_dependency_resolution():
    """测试 2: Dependency Resolution 示例"""
    print("\n" + "=" * 60)
    print("测试 2: Dependency Resolution 示例")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.runtime.skill_dependency_resolver import SkillDependencyResolver

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建依赖技能
        dep_dir = os.path.join(tmpdir, "dep_skill")
        os.makedirs(dep_dir)
        dep_package = create_test_skill_package("dep_skill", "1.2.0")
        with open(os.path.join(dep_dir, "package.json"), 'w') as f:
            json.dump(dep_package, f)

        # 创建主技能
        main_dir = os.path.join(tmpdir, "main_skill")
        os.makedirs(main_dir)
        main_package = create_test_skill_package(
            "main_skill",
            "2.0.0",
            dependencies=[
                {"skill_id": "dep_skill", "version_range": "^1.0.0", "optional": False}
            ]
        )
        with open(os.path.join(main_dir, "package.json"), 'w') as f:
            json.dump(main_package, f)

        # 加载技能包
        loader = SkillPackageLoader()
        loader.load(dep_dir)
        loader.load(main_dir)

        # 解析依赖
        resolver = SkillDependencyResolver(package_loader=loader)
        result = resolver.resolve("main_skill", "2.0.0")

        print(f"\n解析结果:")
        print(f"  - 成功: {result.success}")
        print(f"  - 技能: {result.skill_id}@{result.version}")
        print(f"  - 依赖数量: {len(result.dependencies)}")

        for dep in result.dependencies:
            print(f"    - {dep.skill_id}: {'✅ 满足' if dep.satisfied else '❌ 不满足'}")
            if dep.installed_version:
                print(f"      已安装版本: {dep.installed_version}")

        print(f"  - 解析顺序: {result.resolution_order}")

        if result.errors:
            print(f"  - 错误: {result.errors}")

        return result.success


def test_version_selection():
    """测试 3: Version Selection 示例"""
    print("\n" + "=" * 60)
    print("测试 3: Version Selection 示例")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.runtime.skill_version_selector import SkillVersionSelector, SelectionCriteria

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建多个版本
        versions = ["1.0.0", "1.1.0", "2.0.0", "2.0.1-beta"]
        for v in versions:
            skill_dir = os.path.join(tmpdir, f"multi_skill_{v}")
            os.makedirs(skill_dir)
            package = create_test_skill_package(
                "multi_skill",
                v,
                status="active" if "beta" not in v else "draft",
                health_status="healthy" if v == "2.0.0" else "unknown"
            )
            with open(os.path.join(skill_dir, "package.json"), 'w') as f:
                json.dump(package, f)

        # 加载所有版本
        loader = SkillPackageLoader()
        for v in versions:
            loader.load(os.path.join(tmpdir, f"multi_skill_{v}"))

        # 选择版本
        selector = SkillVersionSelector(package_loader=loader)

        # 测试 1: 选择最新稳定版本
        criteria = SelectionCriteria(
            prefer_stable=True,
            exclude_deprecated=True
        )
        result = selector.select("multi_skill", criteria)

        print(f"\n选择最新稳定版本:")
        print(f"  - 选中版本: {result.selected_version}")
        print(f"  - 候选版本: {[c.version for c in result.candidates]}")
        print(f"  - 拒绝版本: {result.rejected}")

        # 测试 2: 选择特定版本范围
        criteria2 = SelectionCriteria(
            version_range="^1.0.0",
            prefer_stable=True
        )
        result2 = selector.select("multi_skill", criteria2)

        print(f"\n选择 1.x 版本:")
        print(f"  - 选中版本: {result2.selected_version}")
        print(f"  - 候选版本: {[c.version for c in result2.candidates]}")

        return result.success and result2.success


def test_compatibility_check():
    """测试 4: Compatibility Check 示例"""
    print("\n" + "=" * 60)
    print("测试 4: Compatibility Check 示例")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.lifecycle.compatibility_manager import CompatibilityManager

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建技能
        skill_dir = os.path.join(tmpdir, "compat_skill")
        os.makedirs(skill_dir)
        package = create_test_skill_package(
            "compat_skill",
            "1.0.0",
            compatible_profiles=["default", "production"],
            compatible_runtime_versions=["32.0.0", "32.1.0"]
        )
        with open(os.path.join(skill_dir, "package.json"), 'w') as f:
            json.dump(package, f)

        # 加载
        loader = SkillPackageLoader()
        loader.load(skill_dir)

        # 检查兼容性
        compat_manager = CompatibilityManager()

        # 测试 1: 兼容的配置
        result1 = compat_manager.check_compatibility(
            "compat_skill",
            profile="production",
            runtime_version="32.0.0",
            package_loader=loader
        )

        print(f"\n检查 production/32.0.0:")
        print(f"  - 兼容: {result1.compatible}")
        print(f"  - 配置匹配: {result1.matched_profile}")
        print(f"  - 运行时匹配: {result1.matched_runtime}")

        # 测试 2: 不兼容的配置
        result2 = compat_manager.check_compatibility(
            "compat_skill",
            profile="development",
            runtime_version="33.0.0",
            package_loader=loader
        )

        print(f"\n检查 development/33.0.0:")
        print(f"  - 兼容: {result2.compatible}")
        print(f"  - 原因: {result2.reasons}")

        return result1.compatible and not result2.compatible


def test_health_routing():
    """测试 5: Health Routing 示例"""
    print("\n" + "=" * 60)
    print("测试 5: Health Routing 示例")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.runtime.skill_health_monitor import SkillHealthMonitor
    from skills.runtime.skill_version_selector import SkillVersionSelector, SelectionCriteria

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建两个版本的技能
        for version, health in [("1.0.0", "healthy"), ("2.0.0", "unhealthy")]:
            skill_dir = os.path.join(tmpdir, f"health_skill_{version}")
            os.makedirs(skill_dir)
            package = create_test_skill_package(
                "health_skill",
                version,
                health_status=health
            )
            with open(os.path.join(skill_dir, "package.json"), 'w') as f:
                json.dump(package, f)

        # 加载
        loader = SkillPackageLoader()
        for version in ["1.0.0", "2.0.0"]:
            loader.load(os.path.join(tmpdir, f"health_skill_{version}"))

        # 模拟执行记录
        health_monitor = SkillHealthMonitor()

        # 1.0.0 版本：成功率高
        for _ in range(10):
            health_monitor.record_execution("health_skill", "1.0.0", success=True, latency_ms=100)

        # 2.0.0 版本：失败率高
        for _ in range(8):
            health_monitor.record_execution("health_skill", "2.0.0", success=False, error="timeout")
        for _ in range(2):
            health_monitor.record_execution("health_skill", "2.0.0", success=True, latency_ms=5000)

        # 获取健康指标
        metrics1 = health_monitor.get_metrics("health_skill", "1.0.0")
        metrics2 = health_monitor.get_metrics("health_skill", "2.0.0")

        print(f"\n健康指标:")
        print(f"  1.0.0:")
        print(f"    - 成功率: {metrics1.success_rate:.1%}")
        print(f"    - 健康状态: {metrics1.health_status}")
        print(f"    - 健康分数: {metrics1.health_score:.2f}")

        print(f"  2.0.0:")
        print(f"    - 成功率: {metrics2.success_rate:.1%}")
        print(f"    - 健康状态: {metrics2.health_status}")
        print(f"    - 健康分数: {metrics2.health_score:.2f}")

        # 选择健康版本
        selector = SkillVersionSelector(
            package_loader=loader,
            health_monitor=health_monitor
        )

        criteria = SelectionCriteria(
            prefer_healthy=True,
            exclude_unhealthy=True
        )
        result = selector.select("health_skill", criteria)

        print(f"\n健康路由选择:")
        print(f"  - 选中版本: {result.selected_version}")
        print(f"  - 原因: {result.reason}")

        # 验证选择了健康版本
        return result.selected_version == "1.0.0"


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Phase3 Group3 验证")
    print("Skills 正式插件平台化")
    print("=" * 60)

    results = []

    results.append(("Skill Package 示例", test_skill_package()))
    results.append(("Dependency Resolution 示例", test_dependency_resolution()))
    results.append(("Version Selection 示例", test_version_selection()))
    results.append(("Compatibility Check 示例", test_compatibility_check()))
    results.append(("Health Routing 示例", test_health_routing()))

    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 Phase3 Group3 Skills 平台化验证通过！")
    else:
        print("❌ 需要继续修复")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
