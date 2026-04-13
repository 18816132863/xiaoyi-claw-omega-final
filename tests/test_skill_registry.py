#!/usr/bin/env python3
"""技能注册表测试 V1.0.0"""

import unittest
import json
from pathlib import Path

class TestSkillRegistry(unittest.TestCase):
    """技能注册表测试"""
    
    def setUp(self):
        reg_path = Path('infrastructure/inventory/skill_registry.json')
        with open(reg_path) as f:
            self.registry = json.load(f)
        self.skills = self.registry.get('skills', {})
    
    def test_registry_exists(self):
        """测试注册表存在"""
        self.assertTrue(Path('infrastructure/inventory/skill_registry.json').exists())
    
    def test_skills_count(self):
        """测试技能数量 > 100"""
        self.assertGreater(len(self.skills), 100)
    
    def test_active_skills_ratio(self):
        """测试活跃技能比例 > 10%"""
        total = len(self.skills)
        active = sum(1 for s in self.skills.values() if s.get('callable', False))
        ratio = active / total * 100
        self.assertGreater(ratio, 10, f"活跃比例 {ratio:.1f}% 低于 10%")
    
    def test_core_skills_active(self):
        """测试核心技能已激活"""
        core_skills = ['docx', 'pdf', 'cron', 'file-manager', 'git']
        for skill in core_skills:
            if skill in self.skills:
                self.assertTrue(
                    self.skills[skill].get('callable', False),
                    f"核心技能 {skill} 未激活"
                )
    
    def test_skill_fields(self):
        """测试技能字段完整"""
        required_fields = ['name', 'callable', 'routable']
        for skill_name, skill_data in list(self.skills.items())[:10]:
            for field in required_fields:
                self.assertIn(field, skill_data, f"{skill_name} 缺少字段 {field}")

class TestLayerDependency(unittest.TestCase):
    """层间依赖测试"""
    
    def test_dependency_rules_exist(self):
        """测试依赖规则文件存在"""
        self.assertTrue(Path('core/LAYER_DEPENDENCY_RULES.json').exists())
    
    def test_dependency_matrix_exist(self):
        """测试依赖矩阵文件存在"""
        self.assertTrue(Path('core/LAYER_DEPENDENCY_MATRIX.md').exists())
    
    def test_io_contracts_exist(self):
        """测试 IO 契约文件存在"""
        self.assertTrue(Path('core/LAYER_IO_CONTRACTS.md').exists())

if __name__ == '__main__':
    unittest.main(verbosity=2)
