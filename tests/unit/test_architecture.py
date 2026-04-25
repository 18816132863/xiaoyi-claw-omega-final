"""
架构测试
"""
import pytest
from pathlib import Path


class TestArchitecture:
    """架构测试"""
    
    def test_core_files_exist(self):
        """测试核心文件存在"""
        core_files = [
            "MEMORY.md",
            "ARCHITECTURE_UPGRADE_V9.md",
        ]
        for f in core_files:
            assert Path(f).exists(), f"核心文件缺失: {f}"
    
    def test_layer_directories_exist(self):
        """测试层级目录存在"""
        layers = [
            "core",
            "memory_context",
            "orchestration",
            "execution",
            "governance",
            "infrastructure",
        ]
        for layer in layers:
            assert Path(layer).is_dir(), f"层级目录缺失: {layer}"
    
    def test_scripts_directory_exists(self):
        """测试脚本目录存在"""
        assert Path("scripts").is_dir()
        assert len(list(Path("scripts").glob("*.py"))) > 0
    
    def test_skills_directory_exists(self):
        """测试技能目录存在"""
        assert Path("skills").is_dir()
        assert len(list(Path("skills").iterdir())) > 0
    
    def test_tests_directory_exists(self):
        """测试测试目录存在"""
        assert Path("tests").is_dir()
    
    def test_docs_directory_exists(self):
        """测试文档目录存在"""
        assert Path("docs").is_dir()
