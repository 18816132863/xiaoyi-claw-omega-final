"""测试闲置技能激活建议"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_asset_registry import SkillRegistry, SkillAsset
from datetime import datetime, timedelta


def test_identify_unused_skills():
    """测试识别未使用的技能"""
    registry = SkillRegistry()
    skills = registry.list_all()
    
    # 找出从未使用的技能
    unused = [s for s in skills if s.last_used_at is None]
    
    # 应该有一些未使用的技能
    assert len(unused) > 0, "应该有未使用的技能"


def test_identify_low_usage_skills():
    """测试识别低频使用的技能"""
    registry = SkillRegistry()
    skills = registry.list_all()
    
    # 找出成功率低的技能
    low_success = [s for s in skills if s.success_rate < 0.5]
    
    # 这是一个有效的查询
    assert isinstance(low_success, list)


def test_get_top_skills():
    """测试获取热门技能"""
    registry = SkillRegistry()
    top_skills = registry.get_top_skills(limit=10)
    
    assert len(top_skills) <= 10, "应该返回最多 10 个"
    assert isinstance(top_skills, list)


def test_skill_usage_stats():
    """测试技能使用统计"""
    registry = SkillRegistry()
    skills = registry.list_all()
    
    # 统计
    total = len(skills)
    with_usage = sum(1 for s in skills if s.last_used_at is not None)
    never_used = total - with_usage
    
    # 输出统计
    stats = {
        "total": total,
        "with_usage": with_usage,
        "never_used": never_used,
        "usage_rate": with_usage / total if total > 0 else 0,
    }
    
    assert stats["total"] > 0
    assert stats["never_used"] >= 0


def test_activation_suggestions():
    """测试激活建议"""
    registry = SkillRegistry()
    skills = registry.list_all()
    
    # 找出可以激活的技能
    suggestions = []
    for skill in skills:
        if skill.last_used_at is None:
            suggestions.append({
                "skill_id": skill.skill_id,
                "name": skill.name,
                "suggestion": "从未使用，考虑激活或删除",
            })
    
    # 应该有建议
    assert len(suggestions) > 0, "应该有激活建议"


def test_category_distribution():
    """测试分类分布"""
    registry = SkillRegistry()
    skills = registry.list_all()
    
    # 按分类统计
    categories = {}
    for skill in skills:
        categories[skill.category] = categories.get(skill.category, 0) + 1
    
    # 应该有多种分类
    assert len(categories) > 1, "应该有多种分类"
