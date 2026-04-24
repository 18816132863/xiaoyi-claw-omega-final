"""
技能审计

记录技能执行日志和审计信息
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import json


class SkillAudit:
    """技能审计"""
    
    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or Path("logs/skill_audit")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log: List[Dict[str, Any]] = []
    
    def log_execution(self, skill_id: str, action: str, details: Dict[str, Any] = None):
        """记录技能执行"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "skill_id": skill_id,
            "action": action,
            "details": details or {},
        }
        
        self.audit_log.append(entry)
        self._persist(entry)
    
    def log_success(self, skill_id: str, result: Any = None):
        """记录成功执行"""
        self.log_execution(skill_id, "success", {"result": str(result)[:500]})
    
    def log_failure(self, skill_id: str, error: str):
        """记录失败执行"""
        self.log_execution(skill_id, "failure", {"error": error})
    
    def log_permission_denied(self, skill_id: str, reason: str):
        """记录权限拒绝"""
        self.log_execution(skill_id, "permission_denied", {"reason": reason})
    
    def _persist(self, entry: Dict[str, Any]):
        """持久化审计日志"""
        log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_skill_history(self, skill_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取技能执行历史"""
        return [
            entry for entry in self.audit_log
            if entry.get("skill_id") == skill_id
        ][-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.audit_log)
        
        by_action = {}
        for entry in self.audit_log:
            action = entry.get("action", "unknown")
            by_action[action] = by_action.get(action, 0) + 1
        
        return {
            "total": total,
            "by_action": by_action,
        }


__all__ = ["SkillAudit"]
