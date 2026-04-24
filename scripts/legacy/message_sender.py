#!/usr/bin/env python3
"""
消息队列处理器 - V2.0.0

职责：
1. 处理待发送消息队列
2. 生成消息发送指令文件
3. 由心跳执行器读取并返回给 AI

V2.0.0 改进：
- 不再只是打印到控制台
- 生成 pending_sends.jsonl 供 AI 读取
- AI 在心跳响应时调用 message 工具发送

使用方式：
    python scripts/message_sender.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class MessageSender:
    """消息队列处理器"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.queue_file = self.root / "reports" / "ops" / "message_queue.jsonl"
        self.scheduled_file = self.root / "reports" / "ops" / "scheduled_messages.jsonl"
        self.pending_sends_file = self.root / "reports" / "ops" / "pending_sends.jsonl"
        self.sent_file = self.root / "reports" / "ops" / "sent_messages.jsonl"
        
        # 确保目录存在
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
    
    def process_queue(self) -> Dict[str, Any]:
        """处理待发送消息队列"""
        if not self.queue_file.exists():
            return {
                "status": "success",
                "processed": 0,
                "message": "队列为空"
            }
        
        # 读取队列
        messages = []
        with open(self.queue_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    messages.append(msg)
                except:
                    pass
        
        if not messages:
            return {
                "status": "success",
                "processed": 0,
                "message": "队列为空"
            }
        
        # 处理消息：写入 pending_sends.jsonl
        processed = 0
        for msg in messages:
            try:
                # 生成发送指令
                send_instruction = {
                    "action": "send",
                    "channel": msg.get("channel", "xiaoyi-channel"),
                    "target": msg.get("target", "default"),
                    "message": msg.get("content"),
                    "title": msg.get("title"),
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(self.pending_sends_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(send_instruction, ensure_ascii=False) + '\n')
                
                processed += 1
            
            except Exception as e:
                print(f"❌ 处理失败: {e}")
        
        # 清空队列
        self.queue_file.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "processed": processed
        }
    
    def process_scheduled(self) -> Dict[str, Any]:
        """处理定时消息"""
        if not self.scheduled_file.exists():
            return {
                "status": "success",
                "processed": 0,
                "remaining": 0,
                "message": "无定时消息"
            }
        
        # 读取定时消息
        messages = []
        with open(self.scheduled_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    messages.append(msg)
                except:
                    pass
        
        if not messages:
            return {
                "status": "success",
                "processed": 0,
                "remaining": 0,
                "message": "无定时消息"
            }
        
        # 检查是否有到期的消息
        now = datetime.now()
        due_messages = []
        future_messages = []
        
        for msg in messages:
            scheduled_time_str = msg.get('scheduled_time')
            # 解析时间，处理有无时区的情况
            if scheduled_time_str.endswith('Z'):
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            elif '+' in scheduled_time_str or scheduled_time_str.count('-') > 2:
                scheduled_time = datetime.fromisoformat(scheduled_time_str)
            else:
                scheduled_time = datetime.fromisoformat(scheduled_time_str).replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            
            if scheduled_time <= now:
                due_messages.append(msg)
            else:
                future_messages.append(msg)
        
        # 处理到期消息：写入 pending_sends.jsonl
        processed = 0
        for msg in due_messages:
            try:
                # 生成发送指令
                send_instruction = {
                    "action": "send",
                    "channel": msg.get("channel", "xiaoyi-channel"),
                    "target": msg.get("target", "default"),
                    "message": msg.get("content"),
                    "title": msg.get("title"),
                    "scheduled_time": msg.get("scheduled_time"),
                    "timestamp": datetime.now().isoformat()
                }
                
                with open(self.pending_sends_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(send_instruction, ensure_ascii=False) + '\n')
                
                # 记录已发送
                msg["sent_at"] = datetime.now().isoformat()
                msg["status"] = "sent"
                
                with open(self.sent_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
                
                processed += 1
            
            except Exception as e:
                print(f"❌ 发送失败: {e}")
        
        # 更新定时消息文件（只保留未来的消息）
        with open(self.scheduled_file, 'w', encoding='utf-8') as f:
            for msg in future_messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        
        return {
            "status": "success",
            "processed": processed,
            "remaining": len(future_messages)
        }
    
    def get_pending_sends(self) -> List[Dict[str, Any]]:
        """获取待发送消息（不清空）"""
        if not self.pending_sends_file.exists():
            return []
        
        messages = []
        with open(self.pending_sends_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    messages.append(json.loads(line.strip()))
                except:
                    pass
        
        return messages
    
    def clear_pending_sends(self):
        """清空待发送消息"""
        self.pending_sends_file.unlink(missing_ok=True)
    
    def mark_sent(self, messages: List[Dict[str, Any]]):
        """标记消息为已发送"""
        for msg in messages:
            msg["sent_at"] = datetime.now().isoformat()
            msg["status"] = "sent"
            with open(self.sent_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')


def main():
    """主函数"""
    sender = MessageSender()
    
    print("=" * 60)
    print("  消息队列处理器 V2.0.0")
    print("=" * 60)
    print()
    
    # 处理待发送队列
    print("📬 处理待发送队列...")
    queue_result = sender.process_queue()
    print(f"  处理: {queue_result['processed']} 条")
    print()
    
    # 处理定时消息
    print("⏰ 处理定时消息...")
    scheduled_result = sender.process_scheduled()
    print(f"  处理: {scheduled_result['processed']} 条")
    print(f"  剩余: {scheduled_result['remaining']} 条")
    print()
    
    # 输出待发送消息（供 AI 读取）
    pending = sender.get_pending_sends()
    if pending:
        print("=" * 60)
        print("📤 待发送消息:")
        print("=" * 60)
        for msg in pending:
            print(json.dumps(msg, ensure_ascii=False))
        print("=" * 60)
    
    print("✅ 处理完成")


if __name__ == "__main__":
    main()
