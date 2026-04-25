"""
统一结构化日志模块 V1.0.0

提供统一日志字段和格式，支持 JSON 输出。
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(
        self,
        service: str,
        component: str,
        log_dir: Optional[Path] = None,
        level: LogLevel = LogLevel.INFO
    ):
        self.service = service
        self.component = component
        self.level = level
        
        if log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)
            self.log_file = log_dir / f"{service}_{component}.jsonl"
        else:
            self.log_file = None
    
    def _should_log(self, level: LogLevel) -> bool:
        levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        return levels.index(level) >= levels.index(self.level)
    
    def _write(self, entry: Dict[str, Any]):
        line = json.dumps(entry, ensure_ascii=False, default=str)
        
        # 输出到 stderr
        print(line, file=sys.stderr)
        
        # 写入文件
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
    
    def log(
        self,
        level: LogLevel,
        message: str,
        task_id: Optional[str] = None,
        run_id: Optional[str] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        tool_name: Optional[str] = None,
        schedule_mode: Optional[str] = None,
        delivery_status: Optional[str] = None,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        **extra
    ):
        """记录结构化日志"""
        if not self._should_log(level):
            return
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "service": self.service,
            "component": self.component,
            "message": message,
        }
        
        if task_id:
            entry["task_id"] = task_id
        if run_id:
            entry["run_id"] = run_id
        if event_type:
            entry["event_type"] = event_type
        if status:
            entry["status"] = status
        if tool_name:
            entry["tool_name"] = tool_name
        if schedule_mode:
            entry["schedule_mode"] = schedule_mode
        if delivery_status:
            entry["delivery_status"] = delivery_status
        if error_type:
            entry["error_type"] = error_type
        if error_message:
            entry["error_message"] = error_message
        
        if extra:
            entry["extra"] = extra
        
        self._write(entry)
    
    def debug(self, message: str, **kwargs):
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self.log(LogLevel.CRITICAL, message, **kwargs)


# 全局 logger 缓存
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(
    service: str = "openclaw",
    component: str = "default",
    log_dir: Optional[Path] = None,
    level: LogLevel = LogLevel.INFO
) -> StructuredLogger:
    """获取或创建 logger"""
    key = f"{service}:{component}"
    if key not in _loggers:
        _loggers[key] = StructuredLogger(
            service=service,
            component=component,
            log_dir=log_dir,
            level=level
        )
    return _loggers[key]
