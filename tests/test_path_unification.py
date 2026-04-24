"""
路径统一测试
验证旧路径不再包含真实实现文件
"""

import pytest
from pathlib import Path


class TestPathUnification:
    """测试路径统一"""
    
    def test_infrastructure_config_no_real_files(self):
        """infrastructure/config/ 不应包含真实实现文件"""
        infra_config = Path(__file__).parent.parent / "infrastructure" / "config"
        
        if not infra_config.exists():
            pytest.skip("infrastructure/config/ 不存在")
        
        # 允许的文件
        allowed_files = {"__init__.py", "README_DEPRECATED.md", "__pycache__"}
        
        # 检查是否有不允许的真实文件
        real_files = []
        for f in infra_config.iterdir():
            if f.name not in allowed_files:
                real_files.append(f.name)
        
        assert len(real_files) == 0, f"infrastructure/config/ 包含真实文件: {real_files}"
    
    def test_execution_workflows_no_real_files(self):
        """execution/workflows/ 不应包含真实资源文件"""
        exec_workflows = Path(__file__).parent.parent / "execution" / "workflows"
        
        if not exec_workflows.exists():
            pytest.skip("execution/workflows/ 不存在")
        
        # 允许的文件
        allowed_files = {"__init__.py", "README_DEPRECATED.md", "__pycache__"}
        
        # 检查是否有不允许的真实文件
        real_files = []
        for f in exec_workflows.iterdir():
            if f.name not in allowed_files:
                real_files.append(f.name)
        
        assert len(real_files) == 0, f"execution/workflows/ 包含真实文件: {real_files}"
    
    def test_execution_collaboration_no_real_files(self):
        """execution/collaboration/ 不应包含真实资源文件"""
        exec_collab = Path(__file__).parent.parent / "execution" / "collaboration"
        
        if not exec_collab.exists():
            pytest.skip("execution/collaboration/ 不存在")
        
        # 允许的文件
        allowed_files = {"__init__.py", "README_DEPRECATED.md", "__pycache__"}
        
        # 检查是否有不允许的真实文件
        real_files = []
        for f in exec_collab.iterdir():
            if f.name not in allowed_files:
                real_files.append(f.name)
        
        assert len(real_files) == 0, f"execution/collaboration/ 包含真实文件: {real_files}"
    
    def test_config_is_true_source(self):
        """config/ 应该是唯一真源配置目录"""
        config_dir = Path(__file__).parent.parent / "config"
        
        assert config_dir.exists(), "config/ 目录不存在"
        assert (config_dir / "settings.py").exists(), "config/settings.py 不存在"
        assert (config_dir / "__init__.py").exists(), "config/__init__.py 不存在"
    
    def test_orchestration_workflows_is_true_source(self):
        """orchestration/workflows/ 应该是唯一真源工作流目录"""
        workflows_dir = Path(__file__).parent.parent / "orchestration" / "workflows"
        
        assert workflows_dir.exists(), "orchestration/workflows/ 目录不存在"
        assert (workflows_dir / "WORKFLOW_REGISTRY.json").exists(), "WORKFLOW_REGISTRY.json 不存在"
    
    def test_orchestration_collaboration_is_true_source(self):
        """orchestration/collaboration/ 应该是唯一真源协作目录"""
        collab_dir = Path(__file__).parent.parent / "orchestration" / "collaboration"
        
        assert collab_dir.exists(), "orchestration/collaboration/ 目录不存在"
        assert (collab_dir / "COLLABORATION_SCHEMA.json").exists(), "COLLABORATION_SCHEMA.json 不存在"
    
    def test_resource_paths_exist(self):
        """资源路径访问层应该存在"""
        config_resource = Path(__file__).parent.parent / "config" / "resource_paths.py"
        workflows_resource = Path(__file__).parent.parent / "orchestration" / "workflows" / "resource_paths.py"
        collab_resource = Path(__file__).parent.parent / "orchestration" / "collaboration" / "resource_paths.py"
        
        assert config_resource.exists(), "config/resource_paths.py 不存在"
        assert workflows_resource.exists(), "orchestration/workflows/resource_paths.py 不存在"
        assert collab_resource.exists(), "orchestration/collaboration/resource_paths.py 不存在"
