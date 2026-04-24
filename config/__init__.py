"""
配置加载器

统一加载所有配置文件
"""

from pathlib import Path
import json

# 配置目录
CONFIG_DIR = Path(__file__).parent

# 导入所有配置
try:
    from .default_skill_config import DefaultSkillConfig
except ImportError:
    DefaultSkillConfig = None

try:
    from .feature_flags import FeatureFlags
except ImportError:
    FeatureFlags = None


def load_capability_timeouts():
    """加载能力超时配置"""
    config_path = CONFIG_DIR / "capability_timeouts.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_dual_push_config():
    """加载双通道推送配置"""
    config_path = CONFIG_DIR / "dual_push_config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


# 预加载配置
CAPABILITY_TIMEOUTS = load_capability_timeouts()
DUAL_PUSH_CONFIG = load_dual_push_config()

# 导出
__all__ = [
    'CONFIG_DIR',
    'DefaultSkillConfig',
    'FeatureFlags',
    'load_capability_timeouts',
    'load_dual_push_config',
    'CAPABILITY_TIMEOUTS',
    'DUAL_PUSH_CONFIG',
]
