"""审计写入器"""

from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path


class AuditWriter:
    """审计写入器"""
    
    def __init__(self, storage_path: str = "data/audit_log.jsonl"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def write(self, event: Dict[str, Any]):
        """写入审计事件"""
        event["timestamp"] = datetime.now().isoformat()
        
        with open(self.storage_path, "a") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    
    def write_execution_start(self, goal: str, plan: Dict[str, Any]):
        """写入执行开始"""
        self.write({
            "event": "execution_start",
            "goal": goal,
            "plan": plan,
        })
    
    def write_step_start(self, step_id: int, capability: str, params: Dict[str, Any]):
        """写入步骤开始"""
        self.write({
            "event": "step_start",
            "step_id": step_id,
            "capability": capability,
            "params": params,
        })
    
    def write_step_complete(self, step_id: int, result: Dict[str, Any]):
        """写入步骤完成"""
        self.write({
            "event": "step_complete",
            "step_id": step_id,
            "result": result,
        })
    
    def write_step_failed(self, step_id: int, error: str):
        """写入步骤失败"""
        self.write({
            "event": "step_failed",
            "step_id": step_id,
            "error": error,
        })
    
    def write_confirmation(self, step_id: int, approved: bool, approver: str = "user"):
        """写入确认"""
        self.write({
            "event": "confirmation",
            "step_id": step_id,
            "approved": approved,
            "approver": approver,
        })
    
    def write_execution_complete(self, goal: str, success: bool, summary: str):
        """写入执行完成"""
        self.write({
            "event": "execution_complete",
            "goal": goal,
            "success": success,
            "summary": summary,
        })
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近记录"""
        if not self.storage_path.exists():
            return []
        
        events = []
        with open(self.storage_path, "r") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        return events[-limit:]
