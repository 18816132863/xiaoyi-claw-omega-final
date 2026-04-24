"""
资源路径访问层 - Collaboration
统一协作资源路径访问，避免业务代码硬编码路径
"""

from pathlib import Path

# 唯一真源协作目录
COLLABORATION_DIR = Path(__file__).parent


def get_collaboration_schema_path() -> Path:
    """获取协作模式配置路径"""
    return COLLABORATION_DIR / "COLLABORATION_SCHEMA.json"


def get_domain_registry_path() -> Path:
    """获取领域代理注册表路径"""
    return COLLABORATION_DIR / "domain_agents" / "DOMAIN_REGISTRY.json"


def get_agent_registry_path() -> Path:
    """获取代理注册表路径"""
    return COLLABORATION_DIR / "multiagent" / "AGENT_REGISTRY.json"


def get_multiagent_config_path() -> Path:
    """获取多代理配置路径"""
    return COLLABORATION_DIR / "multiagent" / "MULTIAGENT_CONFIG.json"
