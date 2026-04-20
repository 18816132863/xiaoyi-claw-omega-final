#!/usr/bin/env python3
"""
消息队列处理器 - V1.0.0

职责：
1. 处理待发送消息队列
2. 由心跳或守护进程调用
3. 批量发送消息，避免频繁调用

使用方式：
    python scripts/message_sender.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
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
        
        # 处理消息
        processed = 0
        failed = 0
        results = []
        
        for msg in messages:
            try:
                # 这里应该调用 OpenClaw 的 message 工具
                # 但由于脚本无法直接调用工具，我们：
                # 1. 记录到已发送文件
                # 2. 输出到标准输出（会被守护进程捕获）
                
                # 记录已发送
                msg["sent_at"] = datetime.now().isoformat()
                msg["status"] = "sent"
                
                with open(self.sent_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
                
                # 输出到标准输出
                print("\n" + "=" * 60)
                print(f"📤 发送消息")
                print(f"标题: {msg.get('title')}")
                print(f"渠道: {msg.get('channel')}")
                print("=" * 60)
                print(msg.get('content'))
                print("=" * 60 + "\n")
                
                processed += 1
                results.append({
                    "title": msg.get('title'),
                    "status": "sent"
                })
            
            except Exception as e:
                failed += 1
                results.append({
                    "title": msg.get('title'),
                    "status": "failed",
                    "error": str(e)
                })
        
        # 清空队列
        self.queue_file.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "processed": processed,
            "failed": failed,
            "results": results
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
                "message": "无定时消息"
            }
        
        # 检查是否有到期的消息
        now = datetime.now()
        due_messages = []
        future_messages = []
        
        for msg in messages:
            scheduled_time = datetime.fromisoformat(msg.get('scheduled_time'))
            if scheduled_time <= now:
                due_messages.append(msg)
            else:
                future_messages.append(msg)
        
        # 处理到期消息
        processed = 0
        for msg in due_messages:
            try:
                # 记录已发送
                msg["sent_at"] = datetime.now().isoformat()
                msg["status"] = "sent"
                
                with open(self.sent_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
                
                # 输出到标准输出
                print("\n" + "=" * 60)
                print(f"📤 发送定时消息")
                print(f"标题: {msg.get('title')}")
                print(f"计划时间: {msg.get('scheduled_time')}")
                print("=" * 60)
                print(msg.get('content'))
                print("=" * 60 + "\n")
                
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


def main():
    """主函数"""
    sender = MessageSender()
    
    print("=" * 60)
    print("  消息队列处理器 V1.0.0")
    print("=" * 60)
    print()
    
    # 处理待发送队列
    print("📬 处理待发送队列...")
    queue_result = sender.process_queue()
    print(f"  处理: {queue_result['processed']} 条")
    if queue_result.get('failed'):
        print(f"  失败: {queue_result['failed']} 条")
    print()
    
    # 处理定时消息
    print("⏰ 处理定时消息...")
    scheduled_result = sender.process_scheduled()
    print(f"  处理: {scheduled_result['processed']} 条")
    print(f"  剩余: {scheduled_result['remaining']} 条")
    print()
    
    print("✅ 处理完成")


if __name__ == "__main__":
    main()
