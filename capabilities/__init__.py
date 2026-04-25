"""
Capabilities Layer - 能力层
提供统一的能力注册与执行
"""

from .registry import CapabilityRegistry, register_capability, get_registry, CapabilityStatus
from .bootstrap import (
    register_default_capabilities,
    bootstrap_capabilities,
    ensure_bootstrap,
    get_capability_instance
)
from .send_message import SendMessageCapability
from .schedule_task import ScheduleTaskCapability
from .retry_task import RetryTaskCapability
from .pause_task import PauseTaskCapability
from .resume_task import ResumeTaskCapability
from .cancel_task import CancelTaskCapability
from .diagnostics import DiagnosticsCapability
from .export_history import ExportHistoryCapability
from .replay_run import ReplayRunCapability
from .self_repair import SelfRepairCapability

__all__ = [
    # 注册表
    'CapabilityRegistry', 'register_capability', 'get_registry', 'CapabilityStatus',
    
    # Bootstrap
    'register_default_capabilities', 'bootstrap_capabilities', 'ensure_bootstrap',
    'get_capability_instance',
    
    # 能力类
    'SendMessageCapability',
    'ScheduleTaskCapability',
    'RetryTaskCapability',
    'PauseTaskCapability',
    'ResumeTaskCapability',
    'CancelTaskCapability',
    'DiagnosticsCapability',
    'ExportHistoryCapability',
    'ReplayRunCapability',
    'SelfRepairCapability'
]
