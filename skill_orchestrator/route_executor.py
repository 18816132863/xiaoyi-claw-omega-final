"""
Route Executor

Orchestrator 执行 route
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.route_audit import RouteAuditLog, ExecutionStatus, get_route_audit_log


@dataclass
class RouteExecutionResult:
    """Route 执行结果"""
    success: bool
    route_id: str
    capability: str
    handler: str
    risk_level: str
    policy: str
    execution_status: str
    result: Optional[dict]
    error: Optional[str]
    fallback_used: Optional[str]
    audit_id: str
    duration_ms: int
    
    def to_dict(self) -> dict:
        return asdict(self)


class SafetyGovernor:
    """安全治理器"""
    
    def evaluate(self, route: dict, params: dict) -> dict:
        """评估 route 执行安全性"""
        risk = route.get("risk_level", "L3")
        policy = route.get("policy", "confirm_once")
        
        # L4 必须强确认
        if risk == "L4":
            return {
                "allowed": False,
                "reason": "L4 route requires strong confirmation",
                "action": "strong_confirm_required"
            }
        
        # BLOCKED 禁止执行
        if risk == "BLOCKED" or route.get("blocked"):
            return {
                "allowed": False,
                "reason": "Route is blocked",
                "action": "blocked"
            }
        
        # 根据策略决定
        if policy == "auto_execute":
            return {"allowed": True, "action": "execute"}
        elif policy == "rate_limited":
            return {"allowed": True, "action": "execute_rate_limited"}
        elif policy == "confirm_once":
            return {"allowed": True, "action": "confirm_required"}
        elif policy == "strong_confirm":
            return {"allowed": False, "reason": "Strong confirmation required", "action": "strong_confirm_required"}
        
        return {"allowed": True, "action": "execute"}


class FakeHandlerExecutor:
    """Fake Handler 执行器"""
    
    def execute(self, handler: str, params: dict, dry_run: bool = True) -> dict:
        """执行 handler"""
        if dry_run:
            return {
                "success": True,
                "result": f"[DRY_RUN] Would execute {handler}",
                "params": params
            }
        
        # 模拟执行
        return {
            "success": True,
            "result": f"[FAKE] Executed {handler}",
            "params": params
        }


class RouteExecutor:
    """Route 执行器"""
    
    def __init__(
        self,
        registry_path: str = "infrastructure/route_registry.json",
        dry_run: bool = True
    ):
        self.registry_path = Path(registry_path)
        self.dry_run = dry_run
        self.registry = self._load_registry()
        self.audit_log = get_route_audit_log()
        self.safety_governor = SafetyGovernor()
        self.handler_executor = FakeHandlerExecutor()
    
    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text())
        return {"routes": {}}
    
    def execute_route(
        self,
        route_id: str,
        params: dict,
        dry_run: bool = None,
        user_message: str = None
    ) -> RouteExecutionResult:
        """执行 route"""
        dry_run = dry_run if dry_run is not None else self.dry_run
        
        route = self.registry["routes"].get(route_id)
        if not route:
            return RouteExecutionResult(
                success=False,
                route_id=route_id,
                capability="unknown",
                handler="unknown",
                risk_level="unknown",
                policy="unknown",
                execution_status="failed",
                result=None,
                error=f"Route {route_id} not found",
                fallback_used=None,
                audit_id="",
                duration_ms=0
            )
        
        capability = route.get("capability", "")
        handler = route.get("handler", "")
        risk_level = route.get("risk_level", "L3")
        policy = route.get("policy", "confirm_once")
        
        # 创建审计记录
        audit_record = self.audit_log.start_execution(
            route_id=route_id,
            capability=capability,
            handler=handler,
            risk_level=risk_level,
            policy=policy,
            params=params,
            dry_run=dry_run,
            user_message=user_message
        )
        
        # 安全治理检查
        safety_result = self.safety_governor.evaluate(route, params)
        
        if not safety_result.get("allowed"):
            self.audit_log.finish_execution(
                audit_record,
                ExecutionStatus.CANCELLED,
                error_code=safety_result.get("action", "safety_check_failed"),
                error_message=safety_result.get("reason", "Safety check failed")
            )
            
            return RouteExecutionResult(
                success=False,
                route_id=route_id,
                capability=capability,
                handler=handler,
                risk_level=risk_level,
                policy=policy,
                execution_status="cancelled",
                result=None,
                error=safety_result.get("reason"),
                fallback_used=None,
                audit_id=audit_record.audit_id,
                duration_ms=0
            )
        
        # 执行 handler
        start_time = datetime.now()
        
        try:
            result = self.handler_executor.execute(handler, params, dry_run)
            
            finish_time = datetime.now()
            duration_ms = int((finish_time - start_time).total_seconds() * 1000)
            
            self.audit_log.finish_execution(
                audit_record,
                ExecutionStatus.DRY_RUN if dry_run else ExecutionStatus.SUCCESS
            )
            
            return RouteExecutionResult(
                success=True,
                route_id=route_id,
                capability=capability,
                handler=handler,
                risk_level=risk_level,
                policy=policy,
                execution_status="dry_run" if dry_run else "success",
                result=result,
                error=None,
                fallback_used=None,
                audit_id=audit_record.audit_id,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            finish_time = datetime.now()
            duration_ms = int((finish_time - start_time).total_seconds() * 1000)
            
            self.audit_log.finish_execution(
                audit_record,
                ExecutionStatus.FAILED,
                error_code="EXECUTION_ERROR",
                error_message=str(e)
            )
            
            # 尝试 fallback
            fallback_result = self._try_fallback(route, params, dry_run, str(e))
            
            return RouteExecutionResult(
                success=fallback_result.get("success", False) if fallback_result else False,
                route_id=route_id,
                capability=capability,
                handler=handler,
                risk_level=risk_level,
                policy=policy,
                execution_status="fallback_used" if fallback_result else "failed",
                result=fallback_result,
                error=str(e),
                fallback_used=fallback_result.get("route_id") if fallback_result else None,
                audit_id=audit_record.audit_id,
                duration_ms=duration_ms
            )
    
    def _try_fallback(
        self,
        route: dict,
        params: dict,
        dry_run: bool,
        error: str
    ) -> Optional[dict]:
        """尝试执行 fallback"""
        fallbacks = route.get("fallback_routes", [])
        
        if not fallbacks:
            return None
        
        for fb in fallbacks:
            fb_route_id = f"route.{fb}" if not fb.startswith("route.") else fb
            fb_route = self.registry["routes"].get(fb_route_id)
            
            if fb_route:
                result = self.execute_route(fb_route_id, params, dry_run)
                if result.success:
                    return {
                        "success": True,
                        "route_id": fb_route_id,
                        "fallback_reason": error
                    }
        
        return None


def get_route_executor(registry_path: str = None, dry_run: bool = True) -> RouteExecutor:
    """获取 Route 执行器实例"""
    if registry_path:
        return RouteExecutor(registry_path, dry_run)
    return RouteExecutor(dry_run=dry_run)
