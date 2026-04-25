#!/usr/bin/env python3
"""
路径解析器 - V1.0.0

统一路径解析入口，所有模块都应使用此模块。
"""

import os
from pathlib import Path
from typing import Union

def get_project_root() -> Path:
    """
    获取项目根目录。

    优先级：
    1. OPENCLAW_WORKSPACE 环境变量（如果存在且有效）
    2. 基于 __file__ 向上查找包含 core/ARCHITECTURE.md 的目录
    """
    # 检查环境变量
    env_workspace = os.environ.get('OPENCLAW_WORKSPACE')
    if env_workspace:
        env_path = Path(env_workspace)
        if (env_path / 'core' / 'ARCHITECTURE.md').exists():
            return env_path

    # 基于 __file__ 向上查找
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent

    # 回退到当前文件的上两级
    return Path(__file__).resolve().parent.parent

def resolve_path(relative_path: str) -> Path:
    """
    解析相对路径为绝对路径。

    Args:
        relative_path: 相对于项目根的路径

    Returns:
        绝对路径
    """
    return get_project_root() / relative_path

def ensure_dir(relative_path: str) -> Path:
    """
    确保目录存在，不存在则创建。

    Args:
        relative_path: 相对于项目根的目录路径

    Returns:
        创建后的绝对路径
    """
    path = resolve_path(relative_path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_reports_dir() -> Path:
    """获取 reports 目录"""
    return resolve_path("reports")

def get_governance_dir() -> Path:
    """获取 governance 目录"""
    return resolve_path("governance")

def get_infrastructure_dir() -> Path:
    """获取 infrastructure 目录"""
    return resolve_path("infrastructure")
