# infrastructure/tool_adapters/__init__.py
"""
工具适配器模块

职责：
- 封装外部工具
- 提供统一接口
- 幂等控制
"""

from .message_adapter import MessageAdapter, MessageSendResult

# 工具注册表
TOOL_REGISTRY = {}

# 创建消息适配器实例
_message_adapter = MessageAdapter()

async def send_message_tool(inputs: dict, context: dict) -> dict:
    """发送消息工具"""
    user_id = inputs.get("user_id", "default")
    message = inputs.get("message", "")

    task_obj = context.get("task")
    task_id = getattr(task_obj, "task_id", None) if task_obj else context.get("task_id")
    run_id = context.get("run_id")

    result = await _message_adapter.send_message(
        user_id,
        message,
        task_id=task_id,
        run_id=run_id,
        source="task_executor",
    )
    return result

# 注册工具
TOOL_REGISTRY["send_message"] = send_message_tool

# 兼容旧名称
MessageSenderAdapter = MessageAdapter

# 兼容 flaky_tool
try:
    from .flaky_tool import flaky_sender, reset_flaky_counter
    TOOL_REGISTRY["flaky_sender"] = flaky_sender
except ImportError:
    flaky_sender = None
    reset_flaky_counter = lambda: None

__all__ = [
    "MessageAdapter",
    "MessageSenderAdapter",  # 兼容别名
    "MessageSendResult",
    "send_message_tool",
    "TOOL_REGISTRY",
    "flaky_sender",
    "reset_flaky_counter",
]
