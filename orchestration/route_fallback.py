"""
Route Fallback Executor

处理 route 执行失败后的 fallback
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.route_audit import RouteAuditLog, ExecutionStatus, get_route_audit_log


@dataclass
class FallbackExecutionResult:
    """Fallback 执行结果"""
    primary_route: str
    primary_error: str
    fallback_route: Optional[str]
    fallback_success: bool
    fallback_result: Optional[dict]
    audit_id: str
    
    def to_dict(self) -> dict:
        return asdict(self)


class RouteFallbackExecutor:
    """Route Fallback 执行器"""
    
    # 预定义的 fallback 映射
    FALLBACK_MAPPING = {
        "MESSAGE_SENDING_FAILED": ["query_message_status", "list_recent_messages"],
        "NOTIFICATION_AUTH_FAILED": ["explain_notification_auth_state", "send_message"],
        "STORAGE_FAILED": ["create_note", "query_note"],
        "TASK_SCHEDULING_FAILED": ["create_alarm", "create_note"],
        "CALL_FAILED": ["send_message", "query_contact"],
        "LOCATION_FAILED": ["query_contact", "get_last_known_location"],
    }
    
    def __init__(
        self,
        registry_path: str = "infrastructure/route_registry.json"
    ):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
        self.audit_log = get_route_audit_log()
    
    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text())
        return {"routes": {}}
    
    def get_fallback_routes(self, route_id: str, error_type: str = None) -> List[str]:
        """获取 fallback routes"""
        route = self.registry["routes"].get(route_id)
        
        if not route:
            return []
        
        # 优先使用 route 定义的 fallback
        fallbacks = route.get("fallback_routes", [])
        
        # 如果有错误类型映射，补充额外的 fallback
        if error_type and error_type in self.FALLBACK_MAPPING:
            mapped = self.FALLBACK_MAPPING[error_type]
            for fb in mapped:
                fb_id = f"route.{fb}" if not fb.startswith("route.") else fb
                if fb_id not in fallbacks:
                    fallbacks.append(fb_id)
        
        return fallbacks
    
    def execute_fallback(
        self,
        primary_route: str,
        error: str,
        params: dict,
        error_type: str = None,
        dry_run: bool = True
    ) -> FallbackExecutionResult:
        """执行 fallback"""
        # 创建审计记录
        audit_record = self.audit_log.start_execution(
            route_id=f"fallback:{primary_route}",
            capability="fallback",
            handler="orchestration.route_fallback",
            risk_level="L2",
            policy="auto_execute",
            params={"primary_route": primary_route, "error": error},
            dry_run=dry_run,
            user_message=f"Fallback for {primary_route}"
        )
        
        # 获取 fallback routes
        fallbacks = self.get_fallback_routes(primary_route, error_type)
        
        if not fallbacks:
            self.audit_log.finish_execution(
                audit_record,
                ExecutionStatus.FAILED,
                error_code="NO_FALLBACK_AVAILABLE",
                error_message=f"No fallback routes for {primary_route}"
            )
            
            return FallbackExecutionResult(
                primary_route=primary_route,
                primary_error=error,
                fallback_route=None,
                fallback_success=False,
                fallback_result={"error": "No fallback available"},
                audit_id=audit_record.audit_id
            )
        
        # 尝试执行 fallback
        for fb_route_id in fallbacks:
            fb_route = self.registry["routes"].get(fb_route_id)
            
            if not fb_route:
                continue
            
            # 模拟执行
            if dry_run:
                self.audit_log.finish_execution(
                    audit_record,
                    ExecutionStatus.DRY_RUN,
                    fallback_used=fb_route_id,
                    fallback_reason=error
                )
                
                return FallbackExecutionResult(
                    primary_route=primary_route,
                    primary_error=error,
                    fallback_route=fb_route_id,
                    fallback_success=True,
                    fallback_result={"dry_run": True, "message": f"Would execute {fb_route_id}"},
                    audit_id=audit_record.audit_id
                )
        
        # 所有 fallback 都失败
        self.audit_log.finish_execution(
            audit_record,
            ExecutionStatus.FAILED,
            error_code="ALL_FALLBACKS_FAILED",
            error_message="All fallback routes failed"
        )
        
        return FallbackExecutionResult(
            primary_route=primary_route,
            primary_error=error,
            fallback_route=None,
            fallback_success=False,
            fallback_result={"error": "All fallbacks failed"},
            audit_id=audit_record.audit_id
        )


def get_route_fallback_executor(registry_path: str = None) -> RouteFallbackExecutor:
    """获取 Route Fallback 执行器实例"""
    if registry_path:
        return RouteFallbackExecutor(registry_path)
    return RouteFallbackExecutor()
