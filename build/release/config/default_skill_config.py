"""
Default Skill Config - 默认技能配置
"""

from typing import Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StorageConfig:
    """存储配置"""
    type: str = "sqlite"
    database_url: str = "data/tasks.db"
    pool_size: int = 5
    timeout_seconds: int = 30


@dataclass
class ExecutionConfig:
    """执行配置"""
    max_concurrent_tasks: int = 10
    default_timeout_seconds: int = 300
    max_retry_attempts: int = 3
    retry_backoff_seconds: int = 60


@dataclass
class SchedulerConfig:
    """调度配置"""
    enabled: bool = True
    check_interval_seconds: int = 60
    max_scheduled_tasks: int = 1000


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/skill.log"


@dataclass
class DefaultSkillConfig:
    """默认技能配置"""
    
    storage: StorageConfig = field(default_factory=StorageConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # 运行时模式
    runtime_mode: str = "skill_default"
    
    # 功能开关
    enable_diagnostics: bool = True
    enable_export: bool = True
    enable_replay: bool = True
    enable_self_repair: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DefaultSkillConfig':
        """从字典创建配置"""
        config = cls()
        
        if "storage" in data:
            config.storage = StorageConfig(**data["storage"])
        if "execution" in data:
            config.execution = ExecutionConfig(**data["execution"])
        if "scheduler" in data:
            config.scheduler = SchedulerConfig(**data["scheduler"])
        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])
        
        config.runtime_mode = data.get("runtime_mode", "skill_default")
        config.enable_diagnostics = data.get("enable_diagnostics", True)
        config.enable_export = data.get("enable_export", True)
        config.enable_replay = data.get("enable_replay", True)
        config.enable_self_repair = data.get("enable_self_repair", True)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "storage": {
                "type": self.storage.type,
                "database_url": self.storage.database_url,
                "pool_size": self.storage.pool_size,
                "timeout_seconds": self.storage.timeout_seconds
            },
            "execution": {
                "max_concurrent_tasks": self.execution.max_concurrent_tasks,
                "default_timeout_seconds": self.execution.default_timeout_seconds,
                "max_retry_attempts": self.execution.max_retry_attempts,
                "retry_backoff_seconds": self.execution.retry_backoff_seconds
            },
            "scheduler": {
                "enabled": self.scheduler.enabled,
                "check_interval_seconds": self.scheduler.check_interval_seconds,
                "max_scheduled_tasks": self.scheduler.max_scheduled_tasks
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file
            },
            "runtime_mode": self.runtime_mode,
            "enable_diagnostics": self.enable_diagnostics,
            "enable_export": self.enable_export,
            "enable_replay": self.enable_replay,
            "enable_self_repair": self.enable_self_repair
        }
