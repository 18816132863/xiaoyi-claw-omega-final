"""测试技能扫描覆盖率"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_asset_registry import SkillScanner, SkillRegistry


def test_skill_scanner_finds_skills():
    """测试技能扫描器能找到技能"""
    scanner = SkillScanner()
    assets = scanner.scan_all()
    
    assert len(assets) > 0, "应该扫描到技能"
    assert len(assets) >= 100, "应该扫描到至少 100 个技能"


def test_skill_scanner_coverage():
    """测试扫描覆盖率"""
    scanner = SkillScanner()
    stats = scanner.get_stats()
    
    # 检查覆盖率
    skills_dir = Path(__file__).parent.parent / "skills"
    actual_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    
    coverage = stats["total"] / len(actual_dirs) if actual_dirs else 0
    
    assert coverage >= 0.9, f"扫描覆盖率应该 >= 90%，实际 {coverage*100:.1f}%"


def test_skill_categories():
    """测试技能分类"""
    scanner = SkillScanner()
    stats = scanner.get_stats()
    
    # 应该有多种分类
    assert len(stats["categories"]) > 1, "应该有多种分类"
    
    # 常见分类应该存在
    common_categories = ["ai", "search", "document", "other"]
    found = [c for c in common_categories if c in stats["categories"]]
    assert len(found) > 0, "应该有常见分类"


def test_skill_registry_loads():
    """测试技能注册表能加载"""
    registry = SkillRegistry()
    skills = registry.list_all()
    
    assert len(skills) > 0, "注册表应该有技能"


def test_skill_search():
    """测试技能搜索"""
    registry = SkillRegistry()
    results = registry.search("image")
    
    assert isinstance(results, list), "搜索应该返回列表"


def test_skill_by_category():
    """测试按分类获取技能"""
    registry = SkillRegistry()
    skills = registry.list_by_category("ai")
    
    assert isinstance(skills, list), "应该返回列表"
