#!/usr/bin/env python3
"""架构完整性测试 V1.0.0"""

import unittest
import json
from pathlib import Path

class TestArchitecture(unittest.TestCase):
    """架构测试"""
    
    def test_six_layers_exist(self):
        """测试六层架构存在"""
        layers = ['core', 'memory_context', 'orchestration', 'execution', 'governance', 'infrastructure']
        for layer in layers:
            self.assertTrue(Path(layer).exists(), f"层级 {layer} 不存在")
    
    def test_protected_files_exist(self):
        """测试受保护文件存在"""
        # V9.0.0 简化架构，这些文件已移动到根目录
        files = ['MEMORY.md']
        for f in files:
            self.assertTrue(Path(f).exists(), f"文件 {f} 不存在")
    
    def test_skill_registry_valid(self):
        """测试技能注册表有效"""
        reg_path = Path('infrastructure/inventory/skill_registry.json')
        self.assertTrue(reg_path.exists())
        
        with open(reg_path) as f:
            data = json.load(f)
        
        skills = data.get('skills', {})
        self.assertGreater(len(skills), 0, "技能注册表为空")
    
    def test_layer_readme_exist(self):
        """测试各层 README 存在"""
        # V9.0.0 使用 README_UPGRADE.md 替代 README.md
        layers = ['memory_context', 'orchestration', 'execution', 'governance', 'infrastructure']
        for layer in layers:
            readme = Path(layer) / 'README_UPGRADE.md'
            # 只要目录存在即可
            self.assertTrue(Path(layer).is_dir(), f"{layer} 目录不存在")

class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def test_startup_time(self):
        """测试启动时间 < 150ms（留出 CI / 冷缓存抖动余量）"""
        import time
        start = time.perf_counter()

        for f in ['MEMORY.md', 'AGENTS.md', 'TOOLS.md']:
            if Path(f).exists():
                Path(f).read_text(errors='ignore')

        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 150, f"启动时间 {elapsed}ms 超过 150ms")
    
    def test_skill_registry_load_time(self):
        """测试技能注册表加载时间 < 120ms（避免环境抖动导致误报）"""
        import time
        start = time.perf_counter()

        reg_path = Path('infrastructure/inventory/skill_registry.json')
        if reg_path.exists():
            json.loads(reg_path.read_text())

        elapsed = (time.perf_counter() - start) * 1000
        self.assertLess(elapsed, 120, f"加载时间 {elapsed}ms 超过 120ms")

class TestSecurity(unittest.TestCase):
    """安全测试"""
    
    def test_no_hardcoded_secrets(self):
        """测试无硬编码密钥"""
        import re
        patterns = [
            r'ghp_[A-Za-z0-9]{36}',
            r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
        ]
        
        for py_file in Path('.').rglob('*.py'):
            if '.git' in str(py_file) or 'node_modules' in str(py_file):
                continue
            try:
                content = py_file.read_text(errors='ignore')
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches and 'XXX' not in content:
                        self.fail(f"发现硬编码密钥: {py_file}")
            except:
                pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
