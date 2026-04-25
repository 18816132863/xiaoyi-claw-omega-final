"""
发送消息能力 - 真实实现
接入 MessageAdapter 和任务内核
"""

from typing import Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.tool_adapters.message_adapter import MessageAdapter


class SendMessageCapability:
    """发送消息能力"""
    
    name = "send_message"
    description = "发送消息到指定渠道"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行消息发送
        
        Args:
            params: {
                "user_id": 用户ID,
                "message": 消息内容,
                "task_id": 关联任务ID（可选）,
                "run_id": 关联运行ID（可选）,
                "channel": 渠道（可选，默认default）
            }
        
        Returns:
            {
                "success": bool,
                "status": "delivered" | "queued_for_delivery" | "failed",
                "task_id": str,
                "run_id": str,
                "message_id": str,
                "sent_at": str
            }
        """
        user_id = params.get("user_id", "default")
        message = params.get("message", "")
        task_id = params.get("task_id")
        run_id = params.get("run_id")
        channel = params.get("channel", "default")
        
        if not message:
            return {
                "success": False,
                "error": "消息内容不能为空",
                "error_code": "EMPTY_MESSAGE"
            }
        
        try:
            # 使用真实的 MessageAdapter
            adapter = MessageAdapter()
            result = await adapter.send_message(
                user_id=user_id,
                message=message,
                task_id=task_id,
                run_id=run_id
            )
            
            return {
                "success": result.get("success", False),
                "status": result.get("delivery_status", "unknown"),
                "task_id": task_id,
                "run_id": run_id,
                "message_id": result.get("message_id"),
                "sent_at": datetime.now().isoformat(),
                "channel": channel
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SEND_FAILED",
                "task_id": task_id,
                "run_id": run_id
            }
