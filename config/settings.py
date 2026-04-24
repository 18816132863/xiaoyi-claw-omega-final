"""
配置中心 V1.0.0

支持多环境配置：local / test / prod
"""

import os
from pathlib import Path
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


class Environment(str, Enum):
    """运行环境"""
    LOCAL = "local"
    TEST = "test"
    PROD = "prod"


class DatabaseConfig(BaseModel):
    """数据库配置"""
    type: str = "sqlite"
    url: Optional[str] = None
    host: str = "localhost"
    port: int = 5432
    name: str = "openclaw"
    user: str = "openclaw"
    password: str = ""


class RedisConfig(BaseModel):
    """Redis 配置"""
    enabled: bool = False
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None


class MessageServerConfig(BaseModel):
    """消息服务配置"""
    host: str = "localhost"
    port: int = 18790
    timeout: int = 5


class DaemonConfig(BaseModel):
    """守护进程配置"""
    check_interval: float = 5.0
    max_concurrent_tasks: int = 10
    log_level: str = "INFO"


class ObservabilityConfig(BaseModel):
    """可观测性配置"""
    log_dir: str = "logs"
    metrics_dir: str = "reports/metrics"
    enable_tracing: bool = True
    enable_metrics: bool = True


class Settings(BaseModel):
    """全局配置"""
    env: Environment = Environment.LOCAL
    debug: bool = False
    
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    message_server: MessageServerConfig = Field(default_factory=MessageServerConfig)
    daemon: DaemonConfig = Field(default_factory=DaemonConfig)
    observability: ObservabilityConfig = Field(default_factory=ObservabilityConfig)
    
    @classmethod
    def from_env(cls) -> "Settings":
        """从环境变量加载配置"""
        env_str = os.getenv("OPENCLAW_ENV", "local").lower()
        env = Environment(env_str) if env_str in [e.value for e in Environment] else Environment.LOCAL
        
        settings = cls(env=env)
        
        # 数据库配置
        if db_url := os.getenv("DATABASE_URL"):
            settings.database.url = db_url
        if db_host := os.getenv("DB_HOST"):
            settings.database.host = db_host
        if db_port := os.getenv("DB_PORT"):
            settings.database.port = int(db_port)
        if db_name := os.getenv("DB_NAME"):
            settings.database.name = db_name
        if db_user := os.getenv("DB_USER"):
            settings.database.user = db_user
        if db_pass := os.getenv("DB_PASSWORD"):
            settings.database.password = db_pass
        
        # Redis 配置
        if redis_host := os.getenv("REDIS_HOST"):
            settings.redis.host = redis_host
            settings.redis.enabled = True
        if redis_port := os.getenv("REDIS_PORT"):
            settings.redis.port = int(redis_port)
        
        # 消息服务配置
        if msg_port := os.getenv("MESSAGE_SERVER_PORT"):
            settings.message_server.port = int(msg_port)
        
        # 守护进程配置
        if interval := os.getenv("DAEMON_CHECK_INTERVAL"):
            settings.daemon.check_interval = float(interval)
        
        # Debug 模式
        settings.debug = os.getenv("OPENCLAW_DEBUG", "").lower() in ("true", "1", "yes")
        
        return settings
    
    def get_database_url(self) -> str:
        """获取数据库 URL"""
        if self.database.url:
            return self.database.url
        
        if self.database.type == "sqlite":
            return "sqlite:///data/tasks.db"
        
        return f"postgresql://{self.database.user}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.name}"
    
    def get_redis_url(self) -> Optional[str]:
        """获取 Redis URL"""
        if not self.redis.enabled:
            return None
        
        auth = f":{self.redis.password}@" if self.redis.password else ""
        return f"redis://{auth}{self.redis.host}:{self.redis.port}/{self.redis.db}"


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取全局配置"""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
