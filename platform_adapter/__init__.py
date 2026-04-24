"""
Platform Adapter Layer - 平台适配层
提供平台能力探测和适配
"""

from .base import PlatformAdapter, PlatformCapability
from .null_adapter import NullAdapter
from .runtime_probe import RuntimeProbe
from .xiaoyi_adapter import XiaoyiAdapter

# 引用配置（确保配置被加载）
try:
    from config import (
        load_capability_timeouts,
        load_dual_push_config,
        DefaultSkillConfig,
        FeatureFlags,
    )
    CAPABILITY_TIMEOUTS = load_capability_timeouts()
    DUAL_PUSH_CONFIG = load_dual_push_config()
    # 实例化配置类以确保被引用
    _default_skill_cfg = DefaultSkillConfig() if DefaultSkillConfig else None
    _feature_flags = FeatureFlags() if FeatureFlags else None
except ImportError:
    CAPABILITY_TIMEOUTS = {}
    DUAL_PUSH_CONFIG = {}
    _default_skill_cfg = None
    _feature_flags = None

__all__ = [
    'PlatformAdapter', 'PlatformCapability',
    'NullAdapter', 'RuntimeProbe', 'XiaoyiAdapter',
    'CAPABILITY_TIMEOUTS', 'DUAL_PUSH_CONFIG',
]
