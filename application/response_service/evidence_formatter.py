#!/usr/bin/env python3
"""证据格式化器 - 将执行结果转换为可读证据"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class EvidenceType(Enum):
    """证据类型"""
    FILE = "file"
    DB_RECORD = "db_record"
    MESSAGE = "message"
    CONTENT = "content"
    TRACE = "trace"
    NONE = "none"


@dataclass
class Evidence:
    """证据"""
    type: EvidenceType
    description: str
    value: Any
    verified: bool = False


class EvidenceFormatter:
    """证据格式化器"""
    
    def __init__(self):
        self.evidences: List[Evidence] = []
    
    def add_file_evidence(self, path: str, exists: bool, size: int = 0) -> Evidence:
        """添加文件证据"""
        evidence = Evidence(
            type=EvidenceType.FILE,
            description=f"文件: {path}",
            value={"path": path, "exists": exists, "size": size},
            verified=exists
        )
        self.evidences.append(evidence)
        return evidence
    
    def add_db_evidence(self, table: str, record_id: str, fields: Dict[str, Any]) -> Evidence:
        """添加数据库记录证据"""
        evidence = Evidence(
            type=EvidenceType.DB_RECORD,
            description=f"数据库记录: {table}.{record_id}",
            value={"table": table, "id": record_id, "fields": fields},
            verified=True
        )
        self.evidences.append(evidence)
        return evidence
    
    def add_message_evidence(self, channel: str, message_id: str, content_preview: str) -> Evidence:
        """添加消息证据"""
        evidence = Evidence(
            type=EvidenceType.MESSAGE,
            description=f"消息: {channel}/{message_id}",
            value={"channel": channel, "id": message_id, "preview": content_preview},
            verified=bool(message_id)
        )
        self.evidences.append(evidence)
        return evidence
    
    def add_content_evidence(self, content_type: str, content: str, length: int) -> Evidence:
        """添加内容证据"""
        evidence = Evidence(
            type=EvidenceType.CONTENT,
            description=f"生成内容: {content_type} ({length}字)",
            value={"type": content_type, "content": content[:500], "length": length},
            verified=length > 0
        )
        self.evidences.append(evidence)
        return evidence
    
    def add_trace_evidence(self, steps: List[Dict[str, Any]]) -> Evidence:
        """添加执行轨迹证据"""
        evidence = Evidence(
            type=EvidenceType.TRACE,
            description=f"执行轨迹: {len(steps)}步",
            value={"steps": steps},
            verified=len(steps) > 0
        )
        self.evidences.append(evidence)
        return evidence
    
    def has_verified_evidence(self) -> bool:
        """是否有已验证的证据"""
        return any(e.verified for e in self.evidences)
    
    def format_evidences(self) -> List[Dict[str, Any]]:
        """格式化证据列表"""
        return [
            {
                "type": e.type.value,
                "description": e.description,
                "verified": e.verified,
                "value": e.value if e.verified else None
            }
            for e in self.evidences
        ]
    
    def format_summary(self) -> str:
        """格式化证据摘要"""
        if not self.evidences:
            return "无证据"
        
        verified = [e for e in self.evidences if e.verified]
        unverified = [e for e in self.evidences if not e.verified]
        
        lines = []
        if verified:
            lines.append(f"✅ 已验证证据 ({len(verified)}):")
            for e in verified:
                lines.append(f"  - {e.description}")
        
        if unverified:
            lines.append(f"⚠️ 未验证证据 ({len(unverified)}):")
            for e in unverified:
                lines.append(f"  - {e.description}")
        
        return "\n".join(lines)
    
    def clear(self):
        """清空证据"""
        self.evidences.clear()
