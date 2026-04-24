"""
Capability Registry - 能力注册表
统一管理所有能力的注册、发现和执行
"""

from typing import Dict, Any, List, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import logging
import inspect

logger = logging.getLogger(__name__)


class CapabilityStatus(Enum):
    """能力状态"""
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass
class CapabilityInfo:
    """能力信息"""
    name: str
    description: str
    version: str = "1.0.0"
    status: CapabilityStatus = CapabilityStatus.AVAILABLE
    dependencies: List[str] = field(default_factory=list)
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    handler: Optional[Callable] = None
    fallback_handler: Optional[Callable] = None
    deprecation_message: Optional[str] = None


class CapabilityRegistry:
    """
    能力注册表
    管理所有能力的注册、发现和执行
    """
    
    def __init__(self):
        self._capabilities: Dict[str, CapabilityInfo] = {}
        self._categories: Dict[str, List[str]] = {}
    
    def register(
        self,
        name: str,
        description: str,
        handler: Callable,
        version: str = "1.0.0",
        dependencies: List[str] = None,
        input_schema: Dict[str, Any] = None,
        output_schema: Dict[str, Any] = None,
        fallback_handler: Callable = None,
        category: str = "general"
    ) -> None:
        """注册能力"""
        cap_info = CapabilityInfo(
            name=name,
            description=description,
            version=version,
            dependencies=dependencies or [],
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            handler=handler,
            fallback_handler=fallback_handler
        )
        
        self._capabilities[name] = cap_info
        
        # 添加到分类
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)
        
        logger.info(f"Registered capability: {name} v{version}")
    
    def get(self, name: str) -> Optional[CapabilityInfo]:
        """获取能力信息"""
        return self._capabilities.get(name)
    
    def list_all(self) -> List[str]:
        """列出所有能力"""
        return list(self._capabilities.keys())
    
    def list_by_category(self, category: str) -> List[str]:
        """按分类列出能力"""
        return self._categories.get(category, [])
    
    def list_available(self) -> List[str]:
        """列出可用能力"""
        return [
            name for name, info in self._capabilities.items()
            if info.status != CapabilityStatus.UNAVAILABLE
        ]
    
    async def execute(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行能力"""
        cap_info = self._capabilities.get(name)
        
        if not cap_info:
            return {
                "success": False,
                "error": f"Capability not found: {name}",
                "error_code": "CAPABILITY_NOT_FOUND"
            }
        
        if cap_info.status == CapabilityStatus.UNAVAILABLE:
            # 尝试使用降级处理器
            if cap_info.fallback_handler:
                logger.warning(f"Using fallback for unavailable capability: {name}")
                return await self._call_handler(cap_info.fallback_handler, params)
            
            return {
                "success": False,
                "error": f"Capability unavailable: {name}",
                "error_code": "CAPABILITY_UNAVAILABLE"
            }
        
        if cap_info.status == CapabilityStatus.DEGRADED and cap_info.fallback_handler:
            logger.info(f"Using fallback for degraded capability: {name}")
            return await self._call_handler(cap_info.fallback_handler, params)
        
        return await self._call_handler(cap_info.handler, params)
    
    async def _call_handler(self, handler: Callable, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用处理器"""
        try:
            if inspect.iscoroutinefunction(handler):
                return await handler(params)
            else:
                return handler(params)
        except Exception as e:
            logger.exception(f"Handler execution failed")
            return {
                "success": False,
                "error": str(e),
                "error_code": "HANDLER_ERROR"
            }
    
    def update_status(self, name: str, status: CapabilityStatus) -> None:
        """更新能力状态"""
        if name in self._capabilities:
            self._capabilities[name].status = status
            logger.info(f"Updated capability {name} status to {status.value}")
    
    def get_capabilities_report(self) -> Dict[str, Any]:
        """获取能力报告"""
        available = sum(1 for c in self._capabilities.values() if c.status == CapabilityStatus.AVAILABLE)
        degraded = sum(1 for c in self._capabilities.values() if c.status == CapabilityStatus.DEGRADED)
        unavailable = sum(1 for c in self._capabilities.values() if c.status == CapabilityStatus.UNAVAILABLE)
        
        return {
            "total": len(self._capabilities),
            "available": available,
            "degraded": degraded,
            "unavailable": unavailable,
            "categories": {
                cat: caps for cat, caps in self._categories.items()
            },
            "capabilities": {
                name: {
                    "status": info.status.value,
                    "version": info.version,
                    "description": info.description
                }
                for name, info in self._capabilities.items()
            }
        }


# 全局注册表实例
_global_registry: Optional[CapabilityRegistry] = None


def get_registry() -> CapabilityRegistry:
    """获取全局注册表"""
    global _global_registry
    if _global_registry is None:
        _global_registry = CapabilityRegistry()
    return _global_registry


def register_capability(
    name: str,
    description: str,
    **kwargs
) -> Callable:
    """装饰器：注册能力"""
    def decorator(func: Callable) -> Callable:
        get_registry().register(
            name=name,
            description=description,
            handler=func,
            **kwargs
        )
        return func
    return decorator
