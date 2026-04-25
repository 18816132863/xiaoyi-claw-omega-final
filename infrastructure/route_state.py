"""
Route State Machine

状态流转: generated → verified → active → deprecated/failed
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum


class RouteStatus(str, Enum):
    GENERATED = "generated"
    VERIFIED = "verified"
    ACTIVE = "active"
    FAILED = "failed"
    DEPRECATED = "deprecated"


class RouteStateMachine:
    """Route 状态机"""
    
    VALID_TRANSITIONS = {
        RouteStatus.GENERATED: [RouteStatus.VERIFIED, RouteStatus.FAILED],
        RouteStatus.VERIFIED: [RouteStatus.ACTIVE, RouteStatus.FAILED, RouteStatus.DEPRECATED],
        RouteStatus.ACTIVE: [RouteStatus.FAILED, RouteStatus.DEPRECATED],
        RouteStatus.FAILED: [RouteStatus.VERIFIED],  # 可重试
        RouteStatus.DEPRECATED: [],  # 终态
    }
    
    def __init__(self, registry_path: str = "infrastructure/route_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text())
        return {"version": "2.2.0", "routes": {}}
    
    def _save_registry(self):
        self.registry["updated"] = datetime.now().isoformat()
        self.registry_path.write_text(json.dumps(self.registry, indent=2, ensure_ascii=False))
    
    def can_transition(self, route_id: str, target_status: RouteStatus) -> bool:
        """检查是否可以转换到目标状态"""
        route = self.registry["routes"].get(route_id)
        if not route:
            return False
        
        current = RouteStatus(route.get("status", "generated"))
        return target_status in self.VALID_TRANSITIONS.get(current, [])
    
    def transition_to_verified(self, route_id: str, verification: dict) -> bool:
        """转换到 verified 状态"""
        if not self.can_transition(route_id, RouteStatus.VERIFIED):
            return False
        
        route = self.registry["routes"][route_id]
        route["status"] = RouteStatus.VERIFIED.value
        route["verification"] = {
            "static_verified": verification.get("static_verified", True),
            "handler_importable": verification.get("handler_importable", False),
            "schema_valid": verification.get("schema_valid", True),
            "risk_policy_valid": verification.get("risk_policy_valid", True),
            "tested": verification.get("tested", False),
            "last_verified_at": datetime.now().isoformat()
        }
        
        self._save_registry()
        return True
    
    def transition_to_active(self, route_id: str, activation: dict) -> bool:
        """转换到 active 状态 - 必须有 smoke + audit 证据"""
        if not self.can_transition(route_id, RouteStatus.ACTIVE):
            return False
        
        # 必须有 smoke 执行和 audit 写入证据
        if not activation.get("smoke_executed"):
            return False
        if not activation.get("audit_written"):
            return False
        
        route = self.registry["routes"][route_id]
        
        # 初始化 activation 字段
        if "activation" not in route:
            route["activation"] = {
                "smoke_executed": False,
                "audit_written": False,
                "fallback_tested": False,
                "last_activated_at": None,
                "activation_count": 0
            }
        
        route["status"] = RouteStatus.ACTIVE.value
        route["activation"]["smoke_executed"] = activation.get("smoke_executed", True)
        route["activation"]["audit_written"] = activation.get("audit_written", True)
        route["activation"]["fallback_tested"] = activation.get("fallback_tested", False)
        route["activation"]["last_activated_at"] = datetime.now().isoformat()
        route["activation"]["activation_count"] = route["activation"].get("activation_count", 0) + 1
        
        self._save_registry()
        return True
    
    def transition_to_failed(self, route_id: str, reason: str) -> bool:
        """转换到 failed 状态"""
        if not self.can_transition(route_id, RouteStatus.FAILED):
            return False
        
        route = self.registry["routes"][route_id]
        route["status"] = RouteStatus.FAILED.value
        route["failure_reason"] = reason
        route["failed_at"] = datetime.now().isoformat()
        
        self._save_registry()
        return True
    
    def transition_to_deprecated(self, route_id: str, reason: str) -> bool:
        """转换到 deprecated 状态"""
        if not self.can_transition(route_id, RouteStatus.DEPRECATED):
            return False
        
        route = self.registry["routes"][route_id]
        route["status"] = RouteStatus.DEPRECATED.value
        route["deprecation_reason"] = reason
        route["deprecated_at"] = datetime.now().isoformat()
        
        self._save_registry()
        return True
    
    def get_route_status(self, route_id: str) -> Optional[RouteStatus]:
        """获取 route 状态"""
        route = self.registry["routes"].get(route_id)
        if route:
            return RouteStatus(route.get("status", "generated"))
        return None
    
    def get_status_counts(self) -> dict:
        """获取各状态统计"""
        counts = {s.value: 0 for s in RouteStatus}
        for route in self.registry["routes"].values():
            status = route.get("status", "generated")
            counts[status] = counts.get(status, 0) + 1
        return counts
    
    def get_verified_routes(self) -> list:
        """获取所有 verified route"""
        return [
            rid for rid, r in self.registry["routes"].items()
            if r.get("status") in ["verified", "active"]
        ]
    
    def get_active_routes(self) -> list:
        """获取所有 active route"""
        return [
            rid for rid, r in self.registry["routes"].items()
            if r.get("status") == "active"
        ]


def get_route_state_machine(registry_path: str = None) -> RouteStateMachine:
    """获取 Route 状态机实例"""
    if registry_path:
        return RouteStateMachine(registry_path)
    return RouteStateMachine()
