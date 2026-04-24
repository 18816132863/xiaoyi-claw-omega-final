"""
Input Router - 输入路由器
负责将请求路由到正确的处理器
支持自动连接能力注册表
"""

from typing import Dict, Any, Optional, Callable, Awaitable
from enum import Enum
import logging
import asyncio
import inspect

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """请求类型枚举"""
    SEND_MESSAGE = "send_message"
    SCHEDULE_TASK = "schedule_task"
    RETRY_TASK = "retry_task"
    PAUSE_TASK = "pause_task"
    RESUME_TASK = "resume_task"
    CANCEL_TASK = "cancel_task"
    DIAGNOSTICS = "diagnostics"
    EXPORT_HISTORY = "export_history"
    REPLAY_RUN = "replay_run"
    SELF_REPAIR = "self_repair"
    BATCH_TASK = "batch_task"
    WORKFLOW = "workflow"


# 请求类型到能力名称的映射
REQUEST_TO_CAPABILITY = {
    RequestType.SEND_MESSAGE: "send_message",
    RequestType.SCHEDULE_TASK: "schedule_task",
    RequestType.RETRY_TASK: "retry_task",
    RequestType.PAUSE_TASK: "pause_task",
    RequestType.RESUME_TASK: "resume_task",
    RequestType.CANCEL_TASK: "cancel_task",
    RequestType.DIAGNOSTICS: "diagnostics",
    RequestType.EXPORT_HISTORY: "export_history",
    RequestType.REPLAY_RUN: "replay_run",
    RequestType.SELF_REPAIR: "self_repair",
}


class InputRouter:
    """
    输入路由器
    根据请求类型将请求路由到对应的处理器
    支持自动连接能力注册表
    """
    
    def __init__(self, auto_wire: bool = True):
        self._handlers: Dict[RequestType, Callable] = {}
        self._middleware: list = []
        self._wired = False
        
        if auto_wire:
            self._wire_default_handlers()
    
    def _wire_default_handlers(self) -> None:
        """自动连接能力注册表"""
        if self._wired:
            return
        
        try:
            # 确保 bootstrap 已执行
            from capabilities import ensure_bootstrap, get_registry
            ensure_bootstrap()
            
            registry = get_registry()
            
            # 为每个请求类型创建处理器
            for request_type, capability_name in REQUEST_TO_CAPABILITY.items():
                cap_info = registry.get(capability_name)
                if cap_info and cap_info.handler:
                    self._handlers[request_type] = cap_info.handler
                    logger.debug(f"Wired {request_type.value} -> {capability_name}")
            
            self._wired = True
            logger.info(f"Auto-wired {len(self._handlers)} handlers from capability registry")
            
        except Exception as e:
            logger.warning(f"Failed to wire default handlers: {e}")
    
    def register_handler(self, request_type: RequestType, handler: Callable) -> None:
        """注册请求处理器"""
        self._handlers[request_type] = handler
        logger.info(f"Registered handler for {request_type.value}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """添加中间件"""
        self._middleware.append(middleware)
    
    async def _run_middleware(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行中间件链"""
        processed_request = request
        for middleware in self._middleware:
            if inspect.iscoroutinefunction(middleware):
                processed_request = await middleware(processed_request)
            else:
                processed_request = middleware(processed_request)
            
            if processed_request is None:
                return None
        return processed_request
    
    async def route(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        路由请求到对应处理器
        
        Args:
            request: 包含 type 和 data 的请求字典
            
        Returns:
            处理结果
        """
        request_type_str = request.get("type", "")
        
        try:
            request_type = RequestType(request_type_str)
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown request type: {request_type_str}",
                "error_code": "UNKNOWN_REQUEST_TYPE"
            }
        
        # 执行中间件
        processed_request = await self._run_middleware(request)
        if processed_request is None:
            return {
                "success": False,
                "error": "Request blocked by middleware",
                "error_code": "MIDDLEWARE_BLOCK"
            }
        
        # 获取处理器
        handler = self._handlers.get(request_type)
        if handler is None:
            return {
                "success": False,
                "error": f"No handler registered for {request_type_str}",
                "error_code": "NO_HANDLER"
            }
        
        # 执行处理器
        try:
            data = processed_request.get("data", {})
            
            if inspect.iscoroutinefunction(handler):
                result = await handler(data)
            else:
                result = handler(data)
            
            return result
            
        except Exception as e:
            logger.exception(f"Handler error for {request_type_str}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "HANDLER_ERROR"
            }
    
    def get_registered_types(self) -> list:
        """获取已注册的请求类型"""
        return [rt.value for rt in self._handlers.keys()]


# 默认路由器实例
_default_router: Optional[InputRouter] = None


def get_router() -> InputRouter:
    """获取默认路由器实例（自动连接能力注册表）"""
    global _default_router
    if _default_router is None:
        _default_router = InputRouter(auto_wire=True)
    return _default_router


async def route_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """便捷函数：路由请求"""
    return await get_router().route(request)
