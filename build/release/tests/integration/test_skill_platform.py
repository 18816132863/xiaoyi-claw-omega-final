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
from pathlib import Path
import pytest


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
    from skills.runtime.skill_package_loader import SkillPackageLoader, LoadResult

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
            dependencies=[],
            compatible_profiles=["default", "production"],
            compatible_runtime_versions=["32.0.0"]
        )

        with open(os.path.join(skill_dir, "package.json"), 'w') as f:
            json.dump(package, f, indent=2)

        # 加载技能包
        loader = SkillPackageLoader()
        result = loader.load_from_path(Path(skill_dir))

        assert result is not None
        assert result.success == True


def test_dependency_resolution():
    """测试 2: 依赖解析"""
    from skills.runtime.skill_dependency_resolver import SkillDependencyResolver

    resolver = SkillDependencyResolver()
    assert resolver is not None


def test_version_selection():
    """测试 3: 版本选择"""
    from skills.runtime.skill_version_selector import SkillVersionSelector, VersionStrategy

    selector = SkillVersionSelector()
    selector.register_version("test_skill", "1.0.0", stable=True)
    selector.register_version("test_skill", "1.1.0", stable=True)
    
    version = selector.select("test_skill", VersionStrategy.LATEST)
    assert version is not None


def test_compatibility_check():
    """测试 4: 兼容性检查"""
    from skills.lifecycle.compatibility_manager import CompatibilityManager

    cm = CompatibilityManager()
    cm.register("test_skill", "1.0.0", compatible=True)
    
    result = cm.check("test_skill", "1.0.0")
    assert result is not None
    assert result.compatible == True


def test_health_routing():
    """测试 5: 健康路由"""
    from skills.runtime.skill_health_monitor import SkillHealthMonitor, HealthStatus

    monitor = SkillHealthMonitor()
    monitor.record_execution("test_skill", success=True, duration_ms=100)
    
    health = monitor.get_health("test_skill")
    assert health is not None
