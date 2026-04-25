#!/usr/bin/env python3
"""
投机解码模块
使用小型草稿模型 + 大型目标模型实现推理加速
"""

from .speculative_decoder import (
    SpeculativeDecoder,
    DraftModel,
    TargetModel,
    DraftToken,
    SpeculativeResult,
    VerificationResult,
    SpeculativeDecodingConfig,
    speculative_decode
)

from .nvidia_adapter import (
    NVIDIAConfig,
    NVIDIAAPIClient,
    NVIDIADraftModel,
    NVIDIATargetModel
)

__all__ = [
    # 核心类
    "SpeculativeDecoder",
    "DraftModel",
    "TargetModel",
    "DraftToken",
    "SpeculativeResult",
    "VerificationResult",
    "SpeculativeDecodingConfig",
    
    # NVIDIA 适配器
    "NVIDIAConfig",
    "NVIDIAAPIClient",
    "NVIDIADraftModel",
    "NVIDIATargetModel",
    
    # 便捷函数
    "speculative_decode"
]

__version__ = "1.0.0"
