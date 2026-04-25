#!/usr/bin/env python3
"""响应 Schema - V1.0.0

定义统一的响应结构。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class ResponseStatus(Enum):
    """响应状态"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class EvidenceSchema:
    """证据结构"""
    files: List[Dict[str, Any]] = field(default_factory=list)
    db_records: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def is_empty(self) -> bool:
        """检查是否为空"""
        return not any([
            self.files,
            self.db_records,
            self.messages,
            self.tool_calls,
            self.extra
        ])
    
    def count(self) -> int:
        """统计证据数量"""
        return (
            len(self.files) +
            len(self.db_records) +
            len(self.messages) +
            len(self.tool_calls) +
            len(self.extra)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class ErrorSchema:
    """错误结构"""
    code: str
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class FinalResponse:
    """最终响应结构"""
    status: str  # success / failed
    reason: str = ""
    user_response: str = ""
    completed_items: List[str] = field(default_factory=list)
    failed_items: List[str] = field(default_factory=list)
    evidence: EvidenceSchema = field(default_factory=EvidenceSchema)
    next_action: str = ""
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    task_id: str = ""
    intent: str = ""
    total_latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "status": self.status,
            "reason": self.reason,
            "user_response": self.user_response,
            "completed_items": self.completed_items,
            "failed_items": self.failed_items,
            "evidence": self.evidence.to_dict() if isinstance(self.evidence, EvidenceSchema) else self.evidence,
            "next_action": self.next_action,
            "execution_trace": self.execution_trace,
            "task_id": self.task_id,
            "intent": self.intent,
            "total_latency_ms": self.total_latency_ms
        }
    
    def validate(self) -> bool:
        """验证响应是否合法"""
        # user_response 必须非空
        if not self.user_response or not self.user_response.strip():
            return False
        
        # success 时 evidence 必须非空
        if self.status == "success" and self.evidence.is_empty():
            return False
        
        # failed 时 failed_items 必须非空
        if self.status == "failed" and not self.failed_items:
            return False
        
        # next_action 必须非空
        if not self.next_action:
            return False
        
        return True


@dataclass
class SkillResultSchema:
    """技能返回结构"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[ErrorSchema] = None
    evidence: EvidenceSchema = field(default_factory=EvidenceSchema)
    user_summary: str = ""
    machine_summary: str = ""
    artifacts: List[str] = field(default_factory=list)
    verification_hint: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error.to_dict() if self.error else None,
            "evidence": self.evidence.to_dict(),
            "user_summary": self.user_summary,
            "machine_summary": self.machine_summary,
            "artifacts": self.artifacts,
            "verification_hint": self.verification_hint
        }
