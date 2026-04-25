"""
Platform Adapter Base - 平台适配器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass


class PlatformCapability(Enum):
    """平台能力枚举"""
    TASK_SCHEDULING = "task_scheduling"
    MESSAGE_SENDING = "message_sending"
    STORAGE = "storage"
    NOTIFICATION = "notification"
    INTENT_HANDLING = "intent_handling"
    COLLABORATION = "collaboration"


@dataclass
class PlatformCapabilityState:
    """平台能力状态（与 capabilities.registry.CapabilityStatus 不同）"""
    capability: PlatformCapability
    available: bool
    version: str = "1.0.0"
    description: str = ""
    limitations: List[str] = None
    
    def __post_init__(self):
        if self.limitations is None:
            self.limitations = []


class PlatformAdapter(ABC):
    """平台适配器基类"""
    
    name: str = "base"
    description: str = "Base platform adapter"
    
    @abstractmethod
    async def probe(self) -> Dict[str, Any]:
        """探测平台能力"""
        pass
    
    @abstractmethod
    async def get_capability(self, capability: PlatformCapability) -> Optional[PlatformCapabilityState]:
        """获取特定能力状态"""
        pass
    
    @abstractmethod
    async def invoke(self, capability: PlatformCapability, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用平台能力"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """检查平台是否可用"""
        pass
    
    def get_fallback_adapter(self) -> Optional['PlatformAdapter']:
        """获取降级适配器"""
        return None
