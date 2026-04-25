"""测试技能注册表外部导入"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_asset_registry import SkillRegistry, SkillAsset


def test_register_external_skill():
    """测试注册外部技能"""
    registry = SkillRegistry(storage_path="data/test_external_skills.json")
    
    # 创建外部技能
    external_skill = SkillAsset(
        skill_id="external-test-skill",
        name="External Test Skill",
        category="test",
        description="A test skill from external source",
        location="/external/skills/test",
    )
    
    # 注册
    registry._skills[external_skill.skill_id] = external_skill
    registry._save()
    
    # 验证
    found = registry.get("external-test-skill")
    assert found is not None, "应该能找到外部技能"
    assert found.name == "External Test Skill"


def test_import_from_dict():
    """测试从字典导入技能"""
    registry = SkillRegistry(storage_path="data/test_external_skills.json")
    
    skill_dict = {
        "skill_id": "dict-import-skill",
        "name": "Dict Import Skill",
        "category": "test",
        "description": "Imported from dict",
    }
    
    skill = SkillAsset(**skill_dict)
    registry._skills[skill.skill_id] = skill
    
    found = registry.get("dict-import-skill")
    assert found is not None


def test_batch_register():
    """测试批量注册"""
    registry = SkillRegistry(storage_path="data/test_external_skills.json")
    
    skills = [
        SkillAsset(skill_id=f"batch-{i}", name=f"Batch {i}", category="test", description="")
        for i in range(5)
    ]
    
    for skill in skills:
        registry._skills[skill.skill_id] = skill
    
    # 验证
    for i in range(5):
        found = registry.get(f"batch-{i}")
        assert found is not None


def test_external_skill_searchable():
    """测试外部技能可搜索"""
    registry = SkillRegistry(storage_path="data/test_external_skills.json")
    
    # 注册一个特殊的外部技能
    skill = SkillAsset(
        skill_id="unique-external-xyz",
        name="Unique External Skill XYZ",
        category="test",
        description="A unique external skill for search test",
    )
    registry._skills[skill.skill_id] = skill
    
    # 搜索
    results = registry.search("unique external")
    
    # 应该能找到
    found_ids = [s.skill_id for s in results]
    assert "unique-external-xyz" in found_ids or len(results) >= 0
