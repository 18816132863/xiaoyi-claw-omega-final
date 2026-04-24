"""
Runtime Modes - 运行时模式
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class RuntimeMode(Enum):
    """运行时模式"""
    SKILL_DEFAULT = "skill_default"
    PLATFORM_ENHANCED = "platform_enhanced"
    SELF_HOSTED_ENHANCED = "self_hosted_enhanced"


@dataclass
class ModeCapabilities:
    """模式能力"""
    mode: RuntimeMode
    description: str
    features: Dict[str, bool]
    requirements: list
    limitations: list


class RuntimeModes:
    """运行时模式管理"""
    
    MODE_DEFINITIONS = {
        RuntimeMode.SKILL_DEFAULT: ModeCapabilities(
            mode=RuntimeMode.SKILL_DEFAULT,
            description="默认模式，零配置可用",
            features={
                "sqlite_storage": True,
                "single_process": True,
                "request_driven": True,
                "basic_scheduling": True,
                "diagnostics": True,
                "export": True,
                "replay": True
            },
            requirements=[],
            limitations=[
                "No distributed execution",
                "No Redis caching",
                "Single instance only"
            ]
        ),
        RuntimeMode.PLATFORM_ENHANCED: ModeCapabilities(
            mode=RuntimeMode.PLATFORM_ENHANCED,
            description="平台增强模式，利用平台能力",
            features={
                "sqlite_storage": True,
                "platform_scheduling": True,
                "platform_messaging": True,
                "platform_notifications": True,
                "diagnostics": True,
                "export": True,
                "replay": True
            },
            requirements=["Xiaoyi or HarmonyOS platform"],
            limitations=[
                "Platform availability dependent"
            ]
        ),
        RuntimeMode.SELF_HOSTED_ENHANCED: ModeCapabilities(
            mode=RuntimeMode.SELF_HOSTED_ENHANCED,
            description="自托管增强模式，完整功能",
            features={
                "postgresql_storage": True,
                "redis_caching": True,
                "distributed_execution": True,
                "advanced_scheduling": True,
                "diagnostics": True,
                "export": True,
                "replay": True,
                "self_repair": True
            },
            requirements=["PostgreSQL", "Redis", "Docker (optional)"],
            limitations=[]
        )
    }
    
    @classmethod
    def get_current_mode(cls) -> RuntimeMode:
        """获取当前运行模式"""
        from platform_adapter.runtime_probe import RuntimeProbe
        env = RuntimeProbe.detect_environment()
        
        mode_str = env.get("runtime_mode", "skill_default")
        
        return {
            "skill_default": RuntimeMode.SKILL_DEFAULT,
            "platform_enhanced": RuntimeMode.PLATFORM_ENHANCED,
            "self_hosted_enhanced": RuntimeMode.SELF_HOSTED_ENHANCED
        }.get(mode_str, RuntimeMode.SKILL_DEFAULT)
    
    @classmethod
    def get_capabilities(cls, mode: Optional[RuntimeMode] = None) -> ModeCapabilities:
        """获取模式能力"""
        if mode is None:
            mode = cls.get_current_mode()
        return cls.MODE_DEFINITIONS.get(mode)
    
    @classmethod
    def is_feature_available(cls, feature: str, mode: Optional[RuntimeMode] = None) -> bool:
        """检查功能是否可用"""
        caps = cls.get_capabilities(mode)
        return caps.features.get(feature, False) if caps else False
