"""
恢复性模块 - V1.0.0

提供系统恢复、故障恢复和状态回滚能力。
"""

from .state_recovery import StateRecovery
from .fault_recovery import FaultRecovery
from .rollback_manager import RollbackManager

__all__ = ["StateRecovery", "FaultRecovery", "RollbackManager"]
