"""Governance Release Module"""

from governance.release.channel_manager import (
    ChannelManager,
    Channel,
    ChannelState,
    get_channel_manager
)
from governance.release.baseline_registry import (
    BaselineRegistry,
    Baseline,
    BaselineStage,
    VerificationBundle,
    get_baseline_registry
)
from governance.release.promotion_manager import (
    PromotionManager,
    PromotionRecord,
    PromotionStatus,
    get_promotion_manager
)

__all__ = [
    "ChannelManager",
    "Channel",
    "ChannelState",
    "get_channel_manager",
    "BaselineRegistry",
    "Baseline",
    "BaselineStage",
    "VerificationBundle",
    "get_baseline_registry",
    "PromotionManager",
    "PromotionRecord",
    "PromotionStatus",
    "get_promotion_manager",
]
