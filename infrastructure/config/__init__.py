"""
DEPRECATED: 此模块已迁移到 config/
请使用: from config import Settings, get_settings, Environment
"""

# Shim: 仅做 re-export，真实实现已迁移到 config/
from config import Settings, get_settings, Environment

__all__ = ["Settings", "get_settings", "Environment"]
