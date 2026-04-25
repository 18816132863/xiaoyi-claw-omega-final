"""
Null Adapter - 空适配器
当平台能力不可用时使用
"""

from typing import Dict, Any, Optional, List
from .base import PlatformAdapter, PlatformCapability, PlatformCapabilityState


class NullAdapter(PlatformAdapter):
    """空适配器 - 所有能力都不可用"""
    
    name = "null"
    description = "Null adapter for degraded mode"
    
    async def probe(self) -> Dict[str, Any]:
        return {
            "adapter": self.name,
            "available": False,
            "capabilities": {},
            "message": "No platform capabilities available, using skill default mode"
        }
    
    async def get_capability(self, capability: PlatformCapability) -> Optional[PlatformCapabilityState]:
        return PlatformCapabilityState(
            capability=capability,
            available=False,
            description=f"{capability.value} not available in null adapter"
        )
    
    async def invoke(self, capability: PlatformCapability, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": False,
            "error": f"Platform capability {capability.value} not available",
            "error_code": "CAPABILITY_NOT_AVAILABLE",
            "fallback_available": True
        }
    
    async def is_available(self) -> bool:
        return False
