#!/usr/bin/env python3
"""
审计模块 - V1.0.0

记录和追踪所有关键操作。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class AuditLevel(Enum):
    """审计级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(Enum):
    """审计类别"""
    TOOL_CALL = "tool_call"
    SKILL_CALL = "skill_call"
    FILE_OPERATION = "file_operation"
    MEMORY_OPERATION = "memory_operation"
    SECURITY = "security"
    GOVERNANCE = "governance"


@dataclass
class AuditRecord:
    """审计记录"""
    timestamp: str
    category: str
    level: str
    action: str
    actor: str
    target: str
    details: Dict[str, Any]
    result: str
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AuditLog:
    """审计日志"""
    
    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_file = self._get_current_file()
    
    def _get_current_file(self) -> Path:
        """获取当前日志文件"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"audit_{date_str}.jsonl"
    
    def record(self, record: AuditRecord):
        """记录审计日志"""
        # 检查是否需要切换文件
        new_file = self._get_current_file()
        if new_file != self.current_file:
            self.current_file = new_file
        
        # 写入日志
        with open(self.current_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + '\n')
    
    def query(self, 
              category: Optional[str] = None,
              level: Optional[str] = None,
              start_time: Optional[datetime] = None,
              end_time: Optional[datetime] = None,
              limit: int = 100) -> List[AuditRecord]:
        """查询审计日志"""
        results = []
        
        for log_file in self.log_dir.glob("audit_*.jsonl"):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        record = AuditRecord(**data)
                        
                        # 过滤条件
                        if category and record.category != category:
                            continue
                        if level and record.level != level:
                            continue
                        
                        results.append(record)
                        if len(results) >= limit:
                            return results
                    except:
                        continue
        
        return results


# 全局审计实例
_audit_log: Optional[AuditLog] = None


def get_audit_log() -> AuditLog:
    """获取全局审计实例"""
    global _audit_log
    if _audit_log is None:
        _audit_log = AuditLog()
    return _audit_log


def audit_tool_call(tool_name: str, params: Dict, result: Any, duration_ms: int):
    """审计工具调用"""
    log = get_audit_log()
    record = AuditRecord(
        timestamp=datetime.now().isoformat(),
        category=AuditCategory.TOOL_CALL.value,
        level=AuditLevel.INFO.value,
        action="call",
        actor="system",
        target=tool_name,
        details={"params": params},
        result="success" if result else "failed",
        duration_ms=duration_ms
    )
    log.record(record)


def audit_skill_call(skill_name: str, params: Dict, result: Any, duration_ms: int):
    """审计技能调用"""
    log = get_audit_log()
    record = AuditRecord(
        timestamp=datetime.now().isoformat(),
        category=AuditCategory.SKILL_CALL.value,
        level=AuditLevel.INFO.value,
        action="execute",
        actor="system",
        target=skill_name,
        details={"params": params},
        result="success" if result else "failed",
        duration_ms=duration_ms
    )
    log.record(record)


def audit_file_operation(operation: str, path: str, result: str):
    """审计文件操作"""
    log = get_audit_log()
    record = AuditRecord(
        timestamp=datetime.now().isoformat(),
        category=AuditCategory.FILE_OPERATION.value,
        level=AuditLevel.INFO.value,
        action=operation,
        actor="system",
        target=path,
        details={},
        result=result
    )
    log.record(record)
