"""
Route Audit System

记录所有 route 执行的审计日志
"""

import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DRY_RUN = "dry_run"
    FALLBACK_USED = "fallback_used"


@dataclass
class RouteAuditRecord:
    """Route 执行审计记录"""
    audit_id: str
    route_id: str
    capability: str
    handler: str
    risk_level: str
    policy: str
    params_redacted: dict
    dry_run: bool
    status: str
    fallback_used: Optional[str]
    fallback_reason: Optional[str]
    started_at: str
    finished_at: Optional[str]
    duration_ms: Optional[int]
    error_code: Optional[str]
    error_message: Optional[str]
    user_message: Optional[str]
    
    def to_dict(self) -> dict:
        return asdict(self)


class RouteAuditLog:
    """Route 审计日志"""
    
    def __init__(self, audit_path: str = "data/route_audit.jsonl"):
        self.audit_path = Path(audit_path)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _generate_audit_id(self) -> str:
        return f"audit_{uuid.uuid4().hex[:12]}"
    
    def _redact_params(self, params: dict) -> dict:
        """脱敏参数"""
        if not params:
            return {}
        
        redacted = {}
        sensitive_keys = ["password", "token", "secret", "key", "auth", "credential"]
        
        for k, v in params.items():
            if any(sk in k.lower() for sk in sensitive_keys):
                redacted[k] = "***REDACTED***"
            elif isinstance(v, str) and len(v) > 100:
                redacted[k] = v[:100] + "...[truncated]"
            else:
                redacted[k] = v
        
        return redacted
    
    def start_execution(
        self,
        route_id: str,
        capability: str,
        handler: str,
        risk_level: str,
        policy: str,
        params: dict,
        dry_run: bool = False,
        user_message: Optional[str] = None
    ) -> RouteAuditRecord:
        """开始执行，创建审计记录"""
        record = RouteAuditRecord(
            audit_id=self._generate_audit_id(),
            route_id=route_id,
            capability=capability,
            handler=handler,
            risk_level=risk_level,
            policy=policy,
            params_redacted=self._redact_params(params),
            dry_run=dry_run,
            status="started",
            fallback_used=None,
            fallback_reason=None,
            started_at=datetime.now().isoformat(),
            finished_at=None,
            duration_ms=None,
            error_code=None,
            error_message=None,
            user_message=user_message
        )
        
        return record
    
    def finish_execution(
        self,
        record: RouteAuditRecord,
        status: ExecutionStatus,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        fallback_used: Optional[str] = None,
        fallback_reason: Optional[str] = None
    ) -> RouteAuditRecord:
        """完成执行，更新审计记录"""
        record.finished_at = datetime.now().isoformat()
        
        start = datetime.fromisoformat(record.started_at)
        finish = datetime.fromisoformat(record.finished_at)
        record.duration_ms = int((finish - start).total_seconds() * 1000)
        
        record.status = status.value
        record.error_code = error_code
        record.error_message = error_message
        record.fallback_used = fallback_used
        record.fallback_reason = fallback_reason
        
        # 写入审计日志
        self._append_record(record)
        
        return record
    
    def _append_record(self, record: RouteAuditRecord):
        """追加审计记录到文件"""
        with open(self.audit_path, "a") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
    
    def get_recent_records(self, limit: int = 20) -> list:
        """获取最近的审计记录"""
        if not self.audit_path.exists():
            return []
        
        records = []
        with open(self.audit_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        
        return records[-limit:]
    
    def get_records_by_route(self, route_id: str, limit: int = 10) -> list:
        """获取指定 route 的审计记录"""
        if not self.audit_path.exists():
            return []
        
        records = []
        with open(self.audit_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    if record.get("route_id") == route_id:
                        records.append(record)
        
        return records[-limit:]
    
    def get_statistics(self) -> dict:
        """获取审计统计"""
        if not self.audit_path.exists():
            return {"total": 0, "by_status": {}, "by_route": {}}
        
        stats = {
            "total": 0,
            "by_status": {},
            "by_route": {},
            "by_risk_level": {}
        }
        
        with open(self.audit_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    record = json.loads(line)
                    stats["total"] += 1
                    
                    status = record.get("status", "unknown")
                    stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                    
                    route_id = record.get("route_id", "unknown")
                    stats["by_route"][route_id] = stats["by_route"].get(route_id, 0) + 1
                    
                    risk = record.get("risk_level", "unknown")
                    stats["by_risk_level"][risk] = stats["by_risk_level"].get(risk, 0) + 1
        
        return stats


def get_route_audit_log(audit_path: str = None) -> RouteAuditLog:
    """获取 Route 审计日志实例"""
    if audit_path:
        return RouteAuditLog(audit_path)
    return RouteAuditLog()
