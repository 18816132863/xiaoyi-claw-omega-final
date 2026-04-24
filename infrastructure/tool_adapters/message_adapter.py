"""
消息发送适配器 V3.0.0

职责：
- 发送消息到用户
- 记录发送状态
- 携带 task_id/run_id 供后续确认

语义说明：
- SUCCESS: 消息已真实送达用户
- QUEUED: 消息已加入待发送队列，等待真实网关处理
- FAILED: 发送失败
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class MessageSendResult:
    """发送结果状态"""
    SUCCESS = "success"              # 真实送达
    QUEUED = "queued_for_delivery"   # 已生成发送请求，等待处理
    FAILED = "failed"                # 发送失败


class MessageAdapter:
    """消息发送适配器"""
    
    def __init__(self):
        self.root = get_project_root()
        self.pending_file = self.root / "reports" / "ops" / "pending_sends.jsonl"
        self.sent_file = self.root / "reports" / "ops" / "sent_messages.jsonl"
    
    async def send_message(
        self,
        user_id: str,
        message: str,
        task_id: Optional[str] = None,
        run_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送消息
        
        Returns:
            success: True/False (操作是否成功)
            status: success / queued_for_delivery / failed
            task_id: 任务ID
            run_id: 运行ID
        """
        try:
            return await self._fallback_send(
                user_id,
                message,
                task_id=task_id,
                run_id=run_id,
                **kwargs
            )
        except Exception as e:
            return {
                "success": False,
                "status": MessageSendResult.FAILED,
                "task_id": task_id,
                "run_id": run_id,
                "error": str(e)
            }
    
    async def _fallback_send(
        self,
        user_id: str,
        message: str,
        task_id: Optional[str] = None,
        run_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fallback 发送 - 写入待发送队列
        
        重要：这不是真正的发送成功！
        状态是 queued_for_delivery，表示"已生成发送请求"
        """
        self.pending_file.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "task_id": task_id,
            "run_id": run_id,
            "user_id": user_id,
            "message": message,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "source": kwargs.get("source", "message_adapter")
        }
        
        with open(self.pending_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        return {
            "success": True,
            "status": MessageSendResult.QUEUED,
            "task_id": task_id,
            "run_id": run_id,
            "message": "已生成发送请求，等待真实网关处理",
            "queued_at": datetime.now().isoformat()
        }
    
    async def get_pending_count(self) -> int:
        """获取待发送消息数量"""
        if not self.pending_file.exists():
            return 0
        
        count = 0
        with open(self.pending_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("status") == "pending":
                        count += 1
                except:
                    pass
        
        return count
