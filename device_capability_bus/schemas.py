"""设备能力请求和响应模式"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class DeviceCapabilityRequest:
    """设备能力请求"""
    capability: str
    params: Dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False
    approval_required: bool = False
    idempotency_key: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    timeout_ms: int = 30000
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "params": self.params,
            "dry_run": self.dry_run,
            "approval_required": self.approval_required,
            "idempotency_key": self.idempotency_key,
            "user_id": self.user_id,
            "timeout_ms": self.timeout_ms,
        }


@dataclass
class DeviceCapabilityResult:
    """设备能力结果"""
    success: bool
    status: str  # completed, failed, timeout, result_uncertain, requires_confirmation
    raw_result: Dict[str, Any] = field(default_factory=dict)
    user_message: str = ""
    audit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error: Optional[str] = None
    elapsed_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "status": self.status,
            "raw_result": self.raw_result,
            "user_message": self.user_message,
            "audit_id": self.audit_id,
            "error": self.error,
            "elapsed_ms": self.elapsed_ms,
            "timestamp": self.timestamp,
        }
