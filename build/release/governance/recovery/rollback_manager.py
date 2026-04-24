#!/usr/bin/env python3
"""
回滚管理器 - V1.0.0

管理变更的回滚操作。
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import json
import shutil


class RollbackStatus(Enum):
    """回滚状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ChangeRecord:
    """变更记录"""
    id: str
    timestamp: datetime
    operation: str
    target: str
    before_state: Any
    after_state: Any
    rollback_data: Dict[str, Any] = field(default_factory=dict)
    rollback_fn: Optional[str] = None


@dataclass
class RollbackOperation:
    """回滚操作"""
    id: str
    change_id: str
    status: RollbackStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    steps: List[str] = field(default_factory=list)


class RollbackManager:
    """回滚管理器"""
    
    def __init__(self, history_dir: str = "archive/rollback"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        self.changes: Dict[str, ChangeRecord] = {}
        self.rollbacks: Dict[str, RollbackOperation] = {}
        self.change_counter = 0
        self.rollback_counter = 0
        
        self._load_history()
    
    def _load_history(self):
        """加载历史记录"""
        history_file = self.history_dir / "changes.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for c in data.get("changes", []):
                        change = ChangeRecord(
                            id=c["id"],
                            timestamp=datetime.fromisoformat(c["timestamp"]),
                            operation=c["operation"],
                            target=c["target"],
                            before_state=c["before_state"],
                            after_state=c["after_state"],
                            rollback_data=c.get("rollback_data", {})
                        )
                        self.changes[change.id] = change
            except:
                pass
    
    def _save_history(self):
        """保存历史记录"""
        history_file = self.history_dir / "changes.json"
        data = {
            "changes": [
                {
                    "id": c.id,
                    "timestamp": c.timestamp.isoformat(),
                    "operation": c.operation,
                    "target": c.target,
                    "before_state": c.before_state,
                    "after_state": c.after_state,
                    "rollback_data": c.rollback_data
                }
                for c in self.changes.values()
            ]
        }
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def record_change(self,
                      operation: str,
                      target: str,
                      before_state: Any,
                      after_state: Any,
                      rollback_data: Dict = None) -> ChangeRecord:
        """
        记录变更
        
        Args:
            operation: 操作类型
            target: 目标对象
            before_state: 变更前状态
            after_state: 变更后状态
            rollback_data: 回滚所需数据
        
        Returns:
            变更记录
        """
        change = ChangeRecord(
            id=f"change_{self.change_counter}",
            timestamp=datetime.now(),
            operation=operation,
            target=target,
            before_state=before_state,
            after_state=after_state,
            rollback_data=rollback_data or {}
        )
        
        self.changes[change.id] = change
        self.change_counter += 1
        self._save_history()
        
        return change
    
    def rollback(self, change_id: str) -> RollbackOperation:
        """
        回滚变更
        
        Args:
            change_id: 变更ID
        
        Returns:
            回滚操作
        """
        change = self.changes.get(change_id)
        if not change:
            return RollbackOperation(
                id=f"rb_{self.rollback_counter}",
                change_id=change_id,
                status=RollbackStatus.FAILED,
                error="变更记录不存在"
            )
        
        rollback = RollbackOperation(
            id=f"rb_{self.rollback_counter}",
            change_id=change_id,
            status=RollbackStatus.PENDING
        )
        self.rollbacks[rollback.id] = rollback
        self.rollback_counter += 1
        
        try:
            rollback.status = RollbackStatus.IN_PROGRESS
            rollback.started_at = datetime.now()
            
            # 执行回滚
            result = self._execute_rollback(change, rollback)
            
            if result["success"]:
                rollback.status = RollbackStatus.COMPLETED
                rollback.steps = result.get("steps", [])
            else:
                rollback.status = RollbackStatus.FAILED
                rollback.error = result.get("error")
            
            rollback.completed_at = datetime.now()
            
        except Exception as e:
            rollback.status = RollbackStatus.FAILED
            rollback.error = str(e)
            rollback.completed_at = datetime.now()
        
        return rollback
    
    def _execute_rollback(self, change: ChangeRecord, rollback: RollbackOperation) -> Dict:
        """执行回滚"""
        steps = []
        
        # 根据操作类型执行回滚
        if change.operation == "file_write":
            # 恢复文件内容
            target_path = Path(change.target)
            if change.before_state:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(change.before_state, encoding='utf-8')
                steps.append(f"恢复文件: {change.target}")
            else:
                # 删除新创建的文件
                if target_path.exists():
                    target_path.unlink()
                    steps.append(f"删除文件: {change.target}")
        
        elif change.operation == "file_delete":
            # 恢复已删除的文件
            target_path = Path(change.target)
            if change.before_state:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(change.before_state, encoding='utf-8')
                steps.append(f"恢复已删除文件: {change.target}")
        
        elif change.operation == "config_change":
            # 恢复配置
            if change.rollback_data.get("config_file"):
                config_file = Path(change.rollback_data["config_file"])
                if config_file.exists():
                    config_file.write_text(json.dumps(change.before_state, indent=2), encoding='utf-8')
                    steps.append(f"恢复配置: {config_file}")
        
        elif change.operation == "json_update":
            # 恢复 JSON 文件
            target_path = Path(change.target)
            if target_path.exists() and change.before_state:
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(change.before_state, f, ensure_ascii=False, indent=2)
                steps.append(f"恢复 JSON: {change.target}")
        
        else:
            # 通用回滚
            if change.rollback_data.get("rollback_fn"):
                steps.append(f"执行自定义回滚函数")
            else:
                return {"success": False, "error": f"不支持的操作类型: {change.operation}"}
        
        return {"success": True, "steps": steps}
    
    def batch_rollback(self, change_ids: List[str]) -> List[RollbackOperation]:
        """批量回滚"""
        results = []
        
        # 按时间倒序回滚
        changes = [(cid, self.changes.get(cid)) for cid in change_ids]
        changes = [(cid, c) for cid, c in changes if c]
        changes.sort(key=lambda x: x[1].timestamp, reverse=True)
        
        for change_id, _ in changes:
            result = self.rollback(change_id)
            results.append(result)
            
            if result.status == RollbackStatus.FAILED:
                # 回滚失败，停止后续操作
                break
        
        return results
    
    def get_rollback_history(self, limit: int = 20) -> List[RollbackOperation]:
        """获取回滚历史"""
        rollbacks = list(self.rollbacks.values())
        rollbacks.sort(key=lambda r: r.started_at or datetime.min, reverse=True)
        return rollbacks[:limit]
    
    def can_rollback(self, change_id: str) -> Dict[str, Any]:
        """检查是否可以回滚"""
        change = self.changes.get(change_id)
        if not change:
            return {"can_rollback": False, "reason": "变更记录不存在"}
        
        # 检查是否有回滚数据
        if not change.before_state and not change.rollback_data:
            return {"can_rollback": False, "reason": "没有回滚数据"}
        
        # 检查目标是否存在
        if change.operation in ["file_write", "file_delete", "json_update"]:
            if not Path(change.target).exists():
                return {"can_rollback": False, "reason": "目标不存在"}
        
        return {"can_rollback": True}


# 全局回滚管理器
_rollback_manager: Optional[RollbackManager] = None


def get_rollback_manager() -> RollbackManager:
    """获取全局回滚管理器"""
    global _rollback_manager
    if _rollback_manager is None:
        _rollback_manager = RollbackManager()
    return _rollback_manager
