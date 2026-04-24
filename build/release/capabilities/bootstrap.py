"""
Capabilities Bootstrap - 能力自动注册
在启动时自动注册所有能力到注册表
"""

from typing import Optional
import logging

from .registry import get_registry, CapabilityStatus
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

logger = logging.getLogger(__name__)

# 能力实例缓存
_capability_instances = {}


def get_capability_instance(name: str):
    """获取能力实例"""
    return _capability_instances.get(name)


def register_default_capabilities() -> None:
    """注册所有默认能力"""
    registry = get_registry()
    
    # 创建能力实例
    capabilities = [
        ("send_message", SendMessageCapability()),
        ("schedule_task", ScheduleTaskCapability()),
        ("retry_task", RetryTaskCapability()),
        ("pause_task", PauseTaskCapability()),
        ("resume_task", ResumeTaskCapability()),
        ("cancel_task", CancelTaskCapability()),
        ("diagnostics", DiagnosticsCapability()),
        ("export_history", ExportHistoryCapability()),
        ("replay_run", ReplayRunCapability()),
        ("self_repair", SelfRepairCapability()),
    ]
    
    for name, instance in capabilities:
        _capability_instances[name] = instance
        
        registry.register(
            name=name,
            description=instance.description,
            handler=instance.execute,
            category="task_management" if name in [
                "schedule_task", "retry_task", "pause_task", 
                "resume_task", "cancel_task"
            ] else "system" if name in [
                "diagnostics", "self_repair"
            ] else "messaging" if name == "send_message" else "data"
        )
        
        logger.info(f"Registered capability: {name}")
    
    logger.info(f"Total capabilities registered: {len(capabilities)}")


def bootstrap_capabilities() -> None:
    """
    启动能力系统
    - 注册所有能力
    - 设置初始状态
    """
    # 注册能力
    register_default_capabilities()
    
    # 设置能力状态为可用
    registry = get_registry()
    for name in _capability_instances.keys():
        registry.update_status(name, CapabilityStatus.AVAILABLE)
    
    logger.info("Capabilities bootstrap completed")


# 自动执行 bootstrap（可选）
_auto_bootstrap_done = False


def ensure_bootstrap():
    """确保 bootstrap 已执行"""
    global _auto_bootstrap_done
    if not _auto_bootstrap_done:
        bootstrap_capabilities()
        _auto_bootstrap_done = True
