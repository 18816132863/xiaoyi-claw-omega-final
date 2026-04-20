"""
消息发送工具适配器 V1.0.0

职责：
- 封装消息发送接口
- 支持多种渠道
- 幂等控制
- 结果记录
"""

import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class MessageSenderAdapter:
    """消息发送适配器"""
    
    def __init__(self):
        self.root = get_project_root()
        self.sent_log = self.root / "data" / "sent_messages.jsonl"
        self.sent_log.parent.mkdir(parents=True, exist_ok=True)
    
    async def send(
        self,
        channel: str,
        target: str,
        message: str,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送消息
        
        Args:
            channel: 渠道 (xiaoyi-channel, telegram, etc.)
            target: 目标 (default, user_id, chat_id)
            message: 消息内容
            idempotency_key: 幂等键
        
        Returns:
            发送结果
        """
        # 生成幂等键
        if not idempotency_key:
            content = f"{channel}:{target}:{message}"
            idempotency_key = hashlib.sha256(content.encode()).hexdigest()[:32]
        
        # 检查幂等
        if await self._check_sent(idempotency_key):
            return {
                "success": True,
                "idempotent": True,
                "message": "消息已发送过（幂等）"
            }
        
        # 尝试调用消息服务
        result = await self._call_message_service(channel, target, message, idempotency_key)
        
        if result.get("success"):
            # 记录已发送
            await self._record_sent(idempotency_key, channel, target, message)
            return result
        
        # 备用方案：写入待发送队列
        result = await self._write_to_pending_sends({
            "action": "send",
            "channel": channel,
            "target": target,
            "message": message,
            "idempotency_key": idempotency_key,
            "timestamp": datetime.now().isoformat()
        })
        
        # 记录已发送
        await self._record_sent(idempotency_key, channel, target, message)
        
        return result
    
    async def _call_message_service(
        self,
        channel: str,
        target: str,
        message: str,
        idempotency_key: str
    ) -> Dict[str, Any]:
        """调用消息服务"""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:18790/send",
                    json={
                        "channel": channel,
                        "target": target,
                        "message": message,
                        "idempotency_key": idempotency_key
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return {"success": False, "error": f"HTTP {resp.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _write_to_pending_sends(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """写入待发送队列"""
        pending_file = self.root / "reports" / "ops" / "pending_sends.jsonl"
        pending_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(pending_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        # 写入通知文件，让 AI 知道有消息待发送
        notify_file = self.root / "reports" / "ops" / "notify_send.txt"
        with open(notify_file, 'w', encoding='utf-8') as f:
            f.write(f"PENDING_SEND:{entry.get('message', '')[:50]}...\n")
        
        return {
            "success": True,
            "idempotent": False,
            "message": "消息已写入发送队列"
        }
    
    async def _check_sent(self, idempotency_key: str) -> bool:
        """检查是否已发送"""
        if not self.sent_log.exists():
            return False
        
        with open(self.sent_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("idempotency_key") == idempotency_key:
                        return True
                except:
                    pass
        
        return False
    
    async def _record_sent(
        self,
        idempotency_key: str,
        channel: str,
        target: str,
        message: str
    ):
        """记录已发送"""
        entry = {
            "idempotency_key": idempotency_key,
            "channel": channel,
            "target": target,
            "message_hash": hashlib.sha256(message.encode()).hexdigest()[:16],
            "sent_at": datetime.now().isoformat()
        }
        
        with open(self.sent_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# 工具函数（供 TaskExecutor 调用）
async def send_message_tool(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    发送消息工具
    
    Inputs:
        channel: 渠道
        target: 目标
        message: 消息内容
    
    Returns:
        发送结果
    """
    adapter = MessageSenderAdapter()
    
    return await adapter.send(
        channel=inputs.get("channel", "xiaoyi-channel"),
        target=inputs.get("target", "default"),
        message=inputs.get("message", ""),
        idempotency_key=inputs.get("idempotency_key")
    )


async def system_validator_tool(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    系统校验工具
    
    校验任务参数是否完整
    """
    task = context.get("task")
    
    if not task:
        return {"success": False, "error": "任务不存在"}
    
    # 校验必要参数
    if task.task_type == "scheduled_message":
        if not task.inputs.get("message"):
            return {"success": False, "error": "消息内容不能为空"}
        if not task.inputs.get("channel"):
            return {"success": False, "error": "消息渠道不能为空"}
    
    return {"success": True, "message": "校验通过"}


# 工具注册表
TOOL_REGISTRY = {
    "message_sender": send_message_tool,
    "system_validator": system_validator_tool,
}
