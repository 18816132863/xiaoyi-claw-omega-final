"""Skill Audit - 技能审计日志"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os


@dataclass
class AuditEntry:
    """审计条目"""
    timestamp: datetime
    skill_id: str
    action: str  # register, execute, enable, disable, deprecate
    profile: str
    success: bool
    duration_ms: int = 0
    error: Optional[str] = None
    input_summary: str = ""
    output_summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "skill_id": self.skill_id,
            "action": self.action,
            "profile": self.profile,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "metadata": self.metadata
        }


class SkillAudit:
    """
    技能审计日志
    
    职责：
    - 记录所有技能操作
    - 支持审计查询
    - 持久化审计日志
    """
    
    def __init__(self, audit_path: str = "skills/audit/skill_audit.json"):
        self.audit_path = audit_path
        self._entries: List[AuditEntry] = []
        self._load()
    
    def _load(self):
        """加载审计日志"""
        if os.path.exists(self.audit_path):
            try:
                with open(self.audit_path, 'r') as f:
                    data = json.load(f)
                    for entry_data in data.get("entries", []):
                        self._entries.append(AuditEntry(
                            timestamp=datetime.fromisoformat(entry_data["timestamp"]),
                            skill_id=entry_data.get("skill_id", ""),
                            action=entry_data.get("action", ""),
                            profile=entry_data.get("profile", "default"),
                            success=entry_data.get("success", False),
                            duration_ms=entry_data.get("duration_ms", 0),
                            error=entry_data.get("error"),
                            input_summary=entry_data.get("input_summary", ""),
                            output_summary=entry_data.get("output_summary", ""),
                            metadata=entry_data.get("metadata", {})
                        ))
            except:
                pass
    
    def _save(self):
        """保存审计日志"""
        os.makedirs(os.path.dirname(self.audit_path) or ".", exist_ok=True)
        data = {
            "entries": [e.to_dict() for e in self._entries[-1000:]]  # 保留最近 1000 条
        }
        with open(self.audit_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def log(
        self,
        skill_id: str,
        action: str,
        profile: str,
        success: bool,
        duration_ms: int = 0,
        error: str = None,
        input_data: Dict = None,
        output_data: Dict = None,
        metadata: Dict = None
    ):
        """记录审计日志"""
        # 生成摘要
        input_summary = self._summarize(input_data)
        output_summary = self._summarize(output_data)
        
        entry = AuditEntry(
            timestamp=datetime.now(),
            skill_id=skill_id,
            action=action,
            profile=profile,
            success=success,
            duration_ms=duration_ms,
            error=error,
            input_summary=input_summary,
            output_summary=output_summary,
            metadata=metadata or {}
        )
        
        self._entries.append(entry)
        self._save()
    
    def _summarize(self, data: Dict, max_length: int = 100) -> str:
        """生成数据摘要"""
        if not data:
            return ""
        
        try:
            s = json.dumps(data, ensure_ascii=False)
            if len(s) <= max_length:
                return s
            return s[:max_length] + "..."
        except:
            return str(data)[:max_length]
    
    def query(
        self,
        skill_id: str = None,
        action: str = None,
        profile: str = None,
        success: bool = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """查询审计日志"""
        results = self._entries
        
        if skill_id:
            results = [e for e in results if e.skill_id == skill_id]
        
        if action:
            results = [e for e in results if e.action == action]
        
        if profile:
            results = [e for e in results if e.profile == profile]
        
        if success is not None:
            results = [e for e in results if e.success == success]
        
        return results[-limit:]
    
    def get_skill_history(self, skill_id: str) -> List[AuditEntry]:
        """获取技能历史"""
        return [e for e in self._entries if e.skill_id == skill_id]
    
    def get_failed_executions(self, limit: int = 50) -> List[AuditEntry]:
        """获取失败的执行"""
        return [
            e for e in self._entries
            if e.action == "execute" and not e.success
        ][-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self._entries)
        successful = sum(1 for e in self._entries if e.success)
        failed = total - successful
        
        by_action = {}
        for e in self._entries:
            by_action[e.action] = by_action.get(e.action, 0) + 1
        
        by_skill = {}
        for e in self._entries:
            by_skill[e.skill_id] = by_skill.get(e.skill_id, 0) + 1
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "by_action": by_action,
            "by_skill": by_skill
        }
    
    def clear(self):
        """清空审计日志"""
        self._entries.clear()
        self._save()
