"""
Platform Adapter Layer - 平台适配层
提供平台能力探测和适配
"""

from .base import PlatformAdapter, PlatformCapability
from .null_adapter import NullAdapter
from .runtime_probe import RuntimeProbe
from .xiaoyi_adapter import XiaoyiAdapter

__all__ = [
    'PlatformAdapter', 'PlatformCapability',
    'NullAdapter', 'RuntimeProbe', 'XiaoyiAdapter'
]
