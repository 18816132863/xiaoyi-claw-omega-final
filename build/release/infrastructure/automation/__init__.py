"""
自动化模块 - V1.0.0

提供任务自动化、事件触发和智能调度能力。
"""

from .task_automator import TaskAutomator
from .event_trigger import EventTrigger
from .smart_scheduler import SmartScheduler
from .pipeline_executor import PipelineExecutor

__all__ = ["TaskAutomator", "EventTrigger", "SmartScheduler", "PipelineExecutor"]
