"""
资源路径访问层 - Workflows
统一工作流资源路径访问，避免业务代码硬编码路径
"""

from pathlib import Path

# 唯一真源工作流目录
WORKFLOWS_DIR = Path(__file__).parent


def get_workflow_config_path() -> Path:
    """获取工作流配置路径"""
    return WORKFLOWS_DIR / "WORKFLOW_CONFIG.json"


def get_workflow_registry_path() -> Path:
    """获取工作流注册表路径"""
    return WORKFLOWS_DIR / "WORKFLOW_REGISTRY.json"


def get_integration_registry_path() -> Path:
    """获取集成注册表路径"""
    return WORKFLOWS_DIR / "INTEGRATION_REGISTRY.json"
