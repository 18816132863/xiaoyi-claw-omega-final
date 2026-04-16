"""
Degradation - 降级模块
"""

from .profile_degradation_strategy import (
    ProfileDegradationStrategy,
    DegradationReason,
    DegradationRule,
    get_profile_degradation_strategy
)
from .capability_degradation_strategy import (
    CapabilityDegradationStrategy,
    CapabilityDegradationRule,
    DegradationMode,
    get_capability_degradation_strategy
)

__all__ = [
    "ProfileDegradationStrategy",
    "DegradationReason",
    "DegradationRule",
    "get_profile_degradation_strategy",
    "CapabilityDegradationStrategy",
    "CapabilityDegradationRule",
    "DegradationMode",
    "get_capability_degradation_strategy"
]
