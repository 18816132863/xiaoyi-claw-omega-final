"""
Decision Audit Log - 决策审计日志
记录所有控制平面决策，支持审计和追溯
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os


@dataclass
class DecisionAuditRecord:
    """决策审计记录"""
    decision_id: str
    task_id: str
    profile: str
    decision: str
    risk_level: str
    requires_review: bool
    degradation_mode: Optional[str]
    allowed_capabilities: List[str]
    blocked_capabilities: List[str]
    reasons: List[str]
    timestamp: str
    policy_snapshot_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "task_id": self.task_id,
            "profile": self.profile,
            "decision": self.decision,
            "risk_level": self.risk_level,
            "requires_review": self.requires_review,
            "degradation_mode": self.degradation_mode,
            "allowed_capabilities": self.allowed_capabilities,
            "blocked_capabilities": self.blocked_capabilities,
            "reasons": self.reasons,
            "timestamp": self.timestamp,
            "policy_snapshot_id": self.policy_snapshot_id
        }


class DecisionAuditLog:
    """
    决策审计日志
    
    记录所有控制平面决策：
    - decision_id: 决策唯一标识
    - task_id: 任务 ID
    - profile: 配置文件名
    - decision: 决策类型 (allow/deny/degrade/review)
    - risk_level: 风险等级
    - requires_review: 是否需要 review
    - degradation_mode: 降级模式
    - allowed_capabilities: 允许的能力
    - blocked_capabilities: 阻止的能力
    - reasons: 原因列表
    - timestamp: 时间戳
    - policy_snapshot_id: 策略快照 ID
    """
    
    def __init__(self, log_dir: str = "reports/audit"):
        self._records: Dict[str, DecisionAuditRecord] = {}
        self._task_index: Dict[str, List[str]] = {}  # task_id -> decision_ids
        self._profile_index: Dict[str, List[str]] = {}  # profile -> decision_ids
        self._decision_index: Dict[str, List[str]] = {  # decision_type -> decision_ids
            "allow": [],
            "deny": [],
            "degrade": [],
            "review": []
        }
        self._log_dir = log_dir
        self._ensure_log_dir()
    
    def record(self, decision: Any) -> DecisionAuditRecord:
        """
        记录决策
        
        Args:
            decision: ControlDecision 对象
            
        Returns:
            审计记录
        """
        # 从 ControlDecision 提取数据
        record = DecisionAuditRecord(
            decision_id=decision.decision_id,
            task_id=decision.task_id,
            profile=decision.profile,
            decision=decision.decision.value if hasattr(decision.decision, 'value') else str(decision.decision),
            risk_level=decision.risk_level.value if hasattr(decision.risk_level, 'value') else str(decision.risk_level),
            requires_review=decision.requires_review,
            degradation_mode=decision.degradation_mode,
            allowed_capabilities=decision.allowed_capabilities,
            blocked_capabilities=decision.blocked_capabilities,
            reasons=decision.reasons,
            timestamp=decision.timestamp,
            policy_snapshot_id=decision.policy_snapshot_id
        )
        
        # 存储记录
        self._records[record.decision_id] = record
        
        # 更新索引
        self._update_indices(record)
        
        # 持久化
        self._persist(record)
        
        return record
    
    def query(
        self,
        decision_id: Optional[str] = None,
        task_id: Optional[str] = None,
        profile: Optional[str] = None,
        decision_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        查询审计记录
        
        Args:
            decision_id: 决策 ID
            task_id: 任务 ID
            profile: 配置文件名
            decision_type: 决策类型
            limit: 返回数量限制
            
        Returns:
            审计记录列表
        """
        results = []
        
        # 按 decision_id 查询
        if decision_id:
            if decision_id in self._records:
                results = [self._records[decision_id].to_dict()]
            return results
        
        # 按 task_id 查询
        if task_id:
            if task_id in self._task_index:
                results = [
                    self._records[did].to_dict()
                    for did in self._task_index[task_id]
                    if did in self._records
                ]
            return results[:limit]
        
        # 按 profile 查询
        if profile:
            if profile in self._profile_index:
                results = [
                    self._records[did].to_dict()
                    for did in self._profile_index[profile]
                    if did in self._records
                ]
            return results[:limit]
        
        # 按 decision_type 查询
        if decision_type:
            if decision_type in self._decision_index:
                results = [
                    self._records[did].to_dict()
                    for did in self._decision_index[decision_type]
                    if did in self._records
                ]
            return results[:limit]
        
        # 返回所有记录
        results = [r.to_dict() for r in self._records.values()]
        return results[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        total = len(self._records)
        
        if total == 0:
            return {
                "total": 0,
                "by_decision": {},
                "by_profile": {},
                "by_risk_level": {}
            }
        
        # 按决策类型统计
        by_decision = {
            dtype: len(dids)
            for dtype, dids in self._decision_index.items()
        }
        
        # 按配置文件统计
        by_profile = {
            profile: len(dids)
            for profile, dids in self._profile_index.items()
        }
        
        # 按风险等级统计
        by_risk_level: Dict[str, int] = {}
        for record in self._records.values():
            level = record.risk_level
            by_risk_level[level] = by_risk_level.get(level, 0) + 1
        
        return {
            "total": total,
            "by_decision": by_decision,
            "by_profile": by_profile,
            "by_risk_level": by_risk_level,
            "review_required": sum(1 for r in self._records.values() if r.requires_review),
            "degraded": sum(1 for r in self._records.values() if r.degradation_mode)
        }
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近的记录
        
        Args:
            limit: 返回数量
            
        Returns:
            审计记录列表
        """
        records = list(self._records.values())
        records.sort(key=lambda r: r.timestamp, reverse=True)
        return [r.to_dict() for r in records[:limit]]
    
    def _update_indices(self, record: DecisionAuditRecord):
        """
        更新索引
        
        Args:
            record: 审计记录
        """
        # task_id 索引
        if record.task_id not in self._task_index:
            self._task_index[record.task_id] = []
        self._task_index[record.task_id].append(record.decision_id)
        
        # profile 索引
        if record.profile not in self._profile_index:
            self._profile_index[record.profile] = []
        self._profile_index[record.profile].append(record.decision_id)
        
        # decision_type 索引
        decision_type = record.decision
        if decision_type not in self._decision_index:
            self._decision_index[decision_type] = []
        self._decision_index[decision_type].append(record.decision_id)
    
    def _ensure_log_dir(self):
        """确保日志目录存在"""
        if self._log_dir:
            os.makedirs(self._log_dir, exist_ok=True)
    
    def _persist(self, record: DecisionAuditRecord):
        """
        持久化记录
        
        Args:
            record: 审计记录
        """
        if not self._log_dir:
            return
        
        try:
            log_file = os.path.join(self._log_dir, f"decision_{record.decision_id}.json")
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # 静默失败，不影响主流程
    
    def export(self, format: str = "json") -> str:
        """
        导出审计日志
        
        Args:
            format: 导出格式 (json)
            
        Returns:
            导出内容
        """
        if format == "json":
            data = [r.to_dict() for r in self._records.values()]
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


# 全局单例
_decision_audit_log = None

def get_decision_audit_log() -> DecisionAuditLog:
    """获取决策审计日志单例"""
    global _decision_audit_log
    if _decision_audit_log is None:
        _decision_audit_log = DecisionAuditLog()
    return _decision_audit_log
