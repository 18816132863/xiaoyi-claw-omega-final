"""
Phase3 Group3 主链生效验证
证明平台主链真正生效，不是单个模块能跑
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import tempfile
from datetime import datetime


def create_skill_package(skill_id: str, version: str, **kwargs) -> dict:
    """创建技能包"""
    return {
        "skill_id": skill_id,
        "name": kwargs.get("name", f"Skill {skill_id}"),
        "version": version,
        "description": kwargs.get("description", "Test skill"),
        "entry_point": f"skills.{skill_id}.main",
        "input_schema": {"type": "object"},
        "output_schema": {"type": "object"},
        "dependencies": kwargs.get("dependencies", []),
        "compatible_profiles": kwargs.get("compatible_profiles", ["default"]),
        "compatible_runtime_versions": kwargs.get("compatible_runtime_versions", ["32.0.0"]),
        "status": kwargs.get("status", "active"),
        "health_status": kwargs.get("health_status", "unknown"),
        "timeout_ms": 30000
    }


def test_install_and_router_discovery():
    """测试 1: install 一个 skill package，router 立刻可发现"""
    print("\n" + "=" * 60)
    print("测试 1: Install Skill Package，Router 立刻可发现")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.runtime.skill_router import SkillRouter

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建技能包
        skill_dir = os.path.join(tmpdir, "new_skill")
        os.makedirs(skill_dir)

        package = create_skill_package("new_skill", "1.0.0", name="新技能")
        with open(os.path.join(skill_dir, "package.json"), 'w') as f:
            json.dump(package, f)

        # 加载技能包
        loader = SkillPackageLoader()
        result = loader.load(skill_dir)

        print(f"\n安装结果: {'成功' if result.success else '失败'}")
        print(f"技能 ID: {result.package.skill_id if result.package else 'N/A'}")

        # 创建 router 并搜索
        router = SkillRouter(package_loader=loader)

        # 使用 select_skill
        selection = router.select_skill("new_skill", "default")

        print(f"\nRouter 发现结果:")
        print(f"  - 成功: {selection['success']}")
        print(f"  - 技能 ID: {selection.get('skill_id')}")
        print(f"  - 版本: {selection.get('version')}")
        print(f"  - 选择链: {selection.get('selection_chain', [])}")

        return selection['success'] and selection.get('skill_id') == 'new_skill'


def test_multi_version_selection():
    """测试 2: 同 skill 有多个 version，router 正确选择"""
    print("\n" + "=" * 60)
    print("测试 2: 多版本选择")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.runtime.skill_router import SkillRouter
    from skills.runtime.skill_health_monitor import SkillHealthMonitor

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建两个版本
        for version, health in [("1.0.0", "healthy"), ("2.0.0", "unhealthy")]:
            skill_dir = os.path.join(tmpdir, f"multi_v_{version}")
            os.makedirs(skill_dir)
            package = create_skill_package("multi_v_skill", version, health_status=health)
            with open(os.path.join(skill_dir, "package.json"), 'w') as f:
                json.dump(package, f)

        # 加载
        loader = SkillPackageLoader()
        for version in ["1.0.0", "2.0.0"]:
            loader.load(os.path.join(tmpdir, f"multi_v_{version}"))

        # 模拟健康数据
        health_monitor = SkillHealthMonitor()
        for _ in range(10):
            health_monitor.record_execution("multi_v_skill", "1.0.0", True, 100)
        for _ in range(8):
            health_monitor.record_execution("multi_v_skill", "2.0.0", False, 5000, "error")

        # 创建 router
        router = SkillRouter(
            package_loader=loader,
            health_monitor=health_monitor
        )
        
        # 确保 version_selector 使用正确的 loader
        from skills.runtime.skill_version_selector import SkillVersionSelector
        router._version_selector = SkillVersionSelector(
            package_loader=loader,
            health_monitor=health_monitor
        )

        # 选择
        selection = router.select_skill("multi_v_skill", "default")

        print(f"\n选择结果:")
        print(f"  - 选中版本: {selection.get('version')}")
        print(f"  - 健康状态: {selection.get('health_status')}")
        print(f"  - 健康分数: {selection.get('health_score')}")

        # 应该选择健康的 1.0.0 版本
        return selection.get('version') == '1.0.0'


def test_compatibility_routing():
    """测试 3: router 经过 compatibility 检查"""
    print("\n" + "=" * 60)
    print("测试 3: Compatibility 路由")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.runtime.skill_router import SkillRouter

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建兼容和不兼容的技能
        for skill_id, profiles in [
            ("compatible_skill", ["default", "production"]),
            ("incompatible_skill", ["admin"])  # 只兼容 admin
        ]:
            skill_dir = os.path.join(tmpdir, skill_id)
            os.makedirs(skill_dir)
            package = create_skill_package(skill_id, "1.0.0", compatible_profiles=profiles)
            with open(os.path.join(skill_dir, "package.json"), 'w') as f:
                json.dump(package, f)

        # 加载
        loader = SkillPackageLoader()
        loader.load(os.path.join(tmpdir, "compatible_skill"))
        loader.load(os.path.join(tmpdir, "incompatible_skill"))

        # 创建 router
        router = SkillRouter(package_loader=loader)

        # 用 default profile 选择
        selection = router.select_skill("skill", "default")

        print(f"\n选择结果 (profile=default):")
        print(f"  - 成功: {selection['success']}")
        print(f"  - 技能 ID: {selection.get('skill_id')}")
        print(f"  - 兼容性检查: {selection.get('compatibility_checked')}")

        # 应该选择 compatible_skill
        return selection.get('skill_id') == 'compatible_skill'


def test_lifecycle_affects_router():
    """测试 4: upgrade/deprecate 后，router 结果跟着变化"""
    print("\n" + "=" * 60)
    print("测试 4: Lifecycle 影响 Router")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.runtime.skill_router import SkillRouter

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建技能
        skill_dir = os.path.join(tmpdir, "lifecycle_skill")
        os.makedirs(skill_dir)
        package = create_skill_package("lifecycle_skill", "1.0.0", status="active")
        with open(os.path.join(skill_dir, "package.json"), 'w') as f:
            json.dump(package, f)

        # 加载
        loader = SkillPackageLoader()
        loader.load(skill_dir)

        # 创建 router
        router = SkillRouter(package_loader=loader)

        # 第一次选择（active）
        selection1 = router.select_skill("lifecycle_skill", "default")
        print(f"\n第一次选择 (status=active):")
        print(f"  - 成功: {selection1['success']}")
        print(f"  - 技能 ID: {selection1.get('skill_id')}")

        # 模拟 deprecate（修改 package 状态）
        pkg = loader.get("lifecycle_skill", "1.0.0")
        if pkg:
            pkg.status = "deprecated"

        # 第二次选择（deprecated）
        selection2 = router.select_skill("lifecycle_skill", "default")
        print(f"\n第二次选择 (status=deprecated):")
        print(f"  - 成功: {selection2['success']}")
        print(f"  - 原因: {selection2.get('reason')}")

        # 第一次应该成功，第二次应该失败
        return selection1['success'] and not selection2['success']


def test_dependency_blocks_removal():
    """测试 5: remove 被依赖的 skill 时被阻止"""
    print("\n" + "=" * 60)
    print("测试 5: 依赖阻止移除")
    print("=" * 60)

    from skills.runtime.skill_package_loader import SkillPackageLoader
    from skills.lifecycle.remove_manager import RemoveManager

    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建依赖技能
        dep_dir = os.path.join(tmpdir, "dep_skill")
        os.makedirs(dep_dir)
        dep_package = create_skill_package("dep_skill", "1.0.0")
        with open(os.path.join(dep_dir, "package.json"), 'w') as f:
            json.dump(dep_package, f)

        # 创建主技能（依赖 dep_skill）
        main_dir = os.path.join(tmpdir, "main_skill")
        os.makedirs(main_dir)
        main_package = create_skill_package(
            "main_skill",
            "1.0.0",
            dependencies=[
                {"skill_id": "dep_skill", "version_range": "^1.0.0", "optional": False}
            ]
        )
        with open(os.path.join(main_dir, "package.json"), 'w') as f:
            json.dump(main_package, f)

        # 加载
        loader = SkillPackageLoader()
        loader.load(dep_dir)
        loader.load(main_dir)

        # 创建注册表文件
        registry_path = os.path.join(tmpdir, "registry.json")
        registry_data = {
            "skills": {
                "dep_skill": {"version": "1.0.0", "status": "active"},
                "main_skill": {"version": "1.0.0", "status": "active", "dependencies": [
                    {"skill_id": "dep_skill", "version_range": "^1.0.0", "optional": False}
                ]}
            }
        }
        with open(registry_path, 'w') as f:
            json.dump(registry_data, f)

        # 尝试移除被依赖的技能
        remove_manager = RemoveManager(
            registry_path=registry_path,
            history_path=os.path.join(tmpdir, "remove_history.json"),
            backup_dir=os.path.join(tmpdir, "backups")
        )

        # 规划移除
        plan = remove_manager.plan_remove("dep_skill")

        print(f"\n移除规划:")
        print(f"  - 有依赖者: {plan.has_dependents}")
        print(f"  - 依赖者列表: {[d.skill_id for d in plan.dependents]}")
        print(f"  - 警告: {plan.warnings}")

        # 尝试强制移除（不强制应该失败）
        result = remove_manager.remove("dep_skill", force=False)

        print(f"\n移除结果 (不强制):")
        print(f"  - 成功: {result.success}")
        print(f"  - 错误: {result.errors}")

        # 应该被阻止
        return plan.has_dependents and not result.success


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Phase3 Group3 主链生效验证")
    print("=" * 60)

    results = []

    results.append(("Install + Router 发现", test_install_and_router_discovery()))
    results.append(("多版本选择", test_multi_version_selection()))
    results.append(("Compatibility 路由", test_compatibility_routing()))
    results.append(("Lifecycle 影响 Router", test_lifecycle_affects_router()))
    results.append(("依赖阻止移除", test_dependency_blocks_removal()))

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
        print("🎉 Phase3 Group3 平台主链验证通过！")
    else:
        print("❌ 需要继续修复")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
