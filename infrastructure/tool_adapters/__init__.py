# infrastructure/tool_adapters/__init__.py
"""
工具适配器模块

职责：
- 封装外部工具
- 提供统一接口
- 幂等控制
"""

from .message_adapter import MessageSenderAdapter, send_message_tool, TOOL_REGISTRY
from .flaky_tool import flaky_sender, reset_flaky_counter

# 添加 flaky_sender 到工具注册表
TOOL_REGISTRY["flaky_sender"] = flaky_sender

__all__ = [
    "MessageSenderAdapter",
    "send_message_tool",
    "TOOL_REGISTRY",
    "flaky_sender",
    "reset_flaky_counter",
]
