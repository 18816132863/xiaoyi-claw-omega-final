"""审批门控"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from .risk_levels import RiskLevel, RiskPolicy


@dataclass
class ApprovalRequest:
    """审批请求"""
    approval_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action: str = ""
    risk_level: RiskLevel = RiskLevel.L0
    preview_data: Dict[str, Any] = field(default_factory=dict)
    confirmation_prompt: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected, expired


@dataclass
class ApprovalResult:
    """审批结果"""
    approval_id: str
    approved: bool
    approved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approver: Optional[str] = None
    note: Optional[str] = None


class ApprovalGate:
    """审批门控"""
    
    def __init__(self):
        self._pending_approvals: Dict[str, ApprovalRequest] = {}
        self._approval_history: list = []
    
    def create_approval_request(
        self,
        action: str,
        risk_level: RiskLevel,
        preview_data: Dict[str, Any],
        confirmation_prompt: str,
    ) -> ApprovalRequest:
        """创建审批请求"""
        request = ApprovalRequest(
            action=action,
            risk_level=risk_level,
            preview_data=preview_data,
            confirmation_prompt=confirmation_prompt,
        )
        
        # L4 审批请求 5 分钟过期
        if risk_level == RiskLevel.L4:
            from datetime import timedelta
            request.expires_at = (datetime.now() + timedelta(minutes=5)).isoformat()
        
        self._pending_approvals[request.approval_id] = request
        return request
    
    def approve(self, approval_id: str, approver: Optional[str] = None, note: Optional[str] = None) -> ApprovalResult:
        """批准请求"""
        request = self._pending_approvals.get(approval_id)
        if not request:
            return ApprovalResult(approval_id=approval_id, approved=False, note="审批请求不存在")
        
        # 检查是否过期
        if request.expires_at and datetime.now().isoformat() > request.expires_at:
            request.status = "expired"
            return ApprovalResult(approval_id=approval_id, approved=False, note="审批请求已过期")
        
        request.status = "approved"
        result = ApprovalResult(
            approval_id=approval_id,
            approved=True,
            approver=approver,
            note=note,
        )
        
        self._approval_history.append({
            "approval_id": approval_id,
            "action": request.action,
            "risk_level": request.risk_level.value,
            "result": "approved",
            "timestamp": result.approved_at,
        })
        
        del self._pending_approvals[approval_id]
        return result
    
    def reject(self, approval_id: str, reason: Optional[str] = None) -> ApprovalResult:
        """拒绝请求"""
        request = self._pending_approvals.get(approval_id)
        if not request:
            return ApprovalResult(approval_id=approval_id, approved=False, note="审批请求不存在")
        
        request.status = "rejected"
        result = ApprovalResult(
            approval_id=approval_id,
            approved=False,
            note=reason,
        )
        
        self._approval_history.append({
            "approval_id": approval_id,
            "action": request.action,
            "risk_level": request.risk_level.value,
            "result": "rejected",
            "timestamp": result.approved_at,
        })
        
        del self._pending_approvals[approval_id]
        return result
    
    def get_pending(self) -> list:
        """获取待审批列表"""
        return [
            {
                "approval_id": r.approval_id,
                "action": r.action,
                "risk_level": r.risk_level.value,
                "created_at": r.created_at,
            }
            for r in self._pending_approvals.values()
        ]
    
    def get_history(self, limit: int = 100) -> list:
        """获取审批历史"""
        return self._approval_history[-limit:]
