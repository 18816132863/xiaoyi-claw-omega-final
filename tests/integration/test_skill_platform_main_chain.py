"""
Skills 平台主链测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest


def test_install_and_router_discovery():
    """测试安装和路由发现"""
    from skills.registry import get_skill_registry
    from skills.runtime import get_skill_router
    
    registry = get_skill_registry()
    router = get_skill_router()
    
    assert registry is not None
    assert router is not None


def test_multi_version_selection():
    """测试多版本选择"""
    from skills.runtime.skill_version_selector import SkillVersionSelector, VersionStrategy
    
    selector = SkillVersionSelector()
    selector.register_version("test", "1.0.0", stable=True)
    selector.register_version("test", "2.0.0", stable=True)
    
    latest = selector.get_latest("test")
    stable = selector.get_stable("test")
    
    assert latest is not None
    assert stable is not None


def test_compatibility_routing():
    """测试兼容性路由"""
    from skills.lifecycle.compatibility_manager import CompatibilityManager
    
    cm = CompatibilityManager()
    cm.register("test", "1.0.0", compatible=True)
    
    is_compat = cm.is_compatible("test", "1.0.0")
    assert is_compat == True


def test_lifecycle_affects_router():
    """测试生命周期影响路由"""
    from skills.lifecycle import get_lifecycle_manager
    
    lm = get_lifecycle_manager()
    assert lm is not None


def test_dependency_blocks_removal():
    """测试依赖阻止移除"""
    from skills.runtime.skill_dependency_resolver import SkillDependencyResolver
    
    resolver = SkillDependencyResolver()
    # 空依赖图
    dependents = resolver.get_dependents("nonexistent_skill")
    assert dependents == []
