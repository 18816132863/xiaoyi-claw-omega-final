"""
资源路径访问层 - Config
统一配置资源路径访问，避免业务代码硬编码路径
"""

from pathlib import Path

# 唯一真源配置目录
CONFIG_DIR = Path(__file__).parent


def get_config_path(filename: str) -> Path:
    """获取配置文件路径"""
    return CONFIG_DIR / filename


def get_settings_path() -> Path:
    """获取 settings.py 路径"""
    return CONFIG_DIR / "settings.py"


def get_injection_config_path(mode: str = "default") -> Path:
    """获取注入配置路径
    
    Args:
        mode: 配置模式 (default, minimal, smart)
    """
    config_map = {
        "default": "injection_config.json",
        "minimal": "injection_config.json",
        "ultra_minimal": "injection_config_minimal.json",
        "smart": "injection_config_smart.json"
    }
    return CONFIG_DIR / config_map.get(mode, "injection_config.json")


def get_component_classification_path() -> Path:
    """获取组件分类配置路径"""
    return CONFIG_DIR / "component_classification.json"


def get_dependency_manifest_path() -> Path:
    """获取依赖清单路径"""
    return CONFIG_DIR / "dependency_manifest.json"


def get_permanent_keepers_path() -> Path:
    """获取永久守护配置路径"""
    return CONFIG_DIR / "permanent_keepers.json"


def get_unified_config_path() -> Path:
    """获取统一配置路径"""
    return CONFIG_DIR / "unified.json"
