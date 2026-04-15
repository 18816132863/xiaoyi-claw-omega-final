"""
技能注册表单元测试
"""
import json
import pytest
from pathlib import Path


class TestSkillRegistry:
    """技能注册表测试"""
    
    @pytest.fixture
    def registry(self):
        """加载技能注册表"""
        registry_path = Path("infrastructure/inventory/skill_registry.json")
        with open(registry_path) as f:
            return json.load(f)
    
    def test_registry_exists(self):
        """测试注册表文件存在"""
        registry_path = Path("infrastructure/inventory/skill_registry.json")
        assert registry_path.exists()
    
    def test_registry_has_version(self, registry):
        """测试注册表有版本号"""
        assert "version" in registry
        assert registry["version"] == "7.0.0"
    
    def test_registry_has_skills(self, registry):
        """测试注册表有技能"""
        assert "skills" in registry
        assert len(registry["skills"]) > 0
    
    def test_all_skills_have_required_fields(self, registry):
        """测试所有技能都有必要字段"""
        required = ["name", "category", "risk_level", "timeout", "layer"]
        for name, skill in registry["skills"].items():
            if isinstance(skill, dict):
                for field in required:
                    assert field in skill, f"{name} 缺少 {field}"
    
    def test_all_skills_classified(self, registry):
        """测试所有技能都已分类"""
        for name, skill in registry["skills"].items():
            if isinstance(skill, dict):
                assert skill.get("category") != "other", f"{name} 未分类"
    
    def test_all_skills_testable(self, registry):
        """测试所有技能都可测试"""
        for name, skill in registry["skills"].items():
            if isinstance(skill, dict):
                assert skill.get("testable") == True, f"{name} 不可测试"
    
    def test_timeout_range(self, registry):
        """测试超时配置范围"""
        for name, skill in registry["skills"].items():
            if isinstance(skill, dict):
                timeout = skill.get("timeout", 60)
                assert 30 <= timeout <= 180, f"{name} 超时配置异常: {timeout}"
