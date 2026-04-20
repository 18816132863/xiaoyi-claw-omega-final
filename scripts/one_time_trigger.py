#!/usr/bin/env python3
"""
一次性定时任务触发器 - V1.0.0

职责：
1. 检查 scheduled_messages.jsonl
2. 发送到期的消息
3. 清理已发送的消息

使用方式：
    python scripts/one_time_trigger.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


def check_scheduled_messages() -> Dict[str, Any]:
    """检查并发送到期的定时消息"""
    root = get_project_root()
    scheduled_file = root / "reports" / "ops" / "scheduled_messages.jsonl"
    sent_file = root / "reports" / "ops" / "sent_messages.jsonl"
    
    if not scheduled_file.exists():
        return {
            "status": "success",
            "processed": 0,
            "remaining": 0,
            "message": "无定时消息"
        }
    
    # 读取定时消息
    messages = []
    with open(scheduled_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                messages.append(json.loads(line.strip()))
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
        scheduled_time = datetime.fromisoformat(msg.get('scheduled_time'))
        if scheduled_time <= now:
            due_messages.append(msg)
        else:
            future_messages.append(msg)
    
    # 发送到期的消息
    processed = 0
    for msg in due_messages:
        try:
            # 输出到标准输出（供心跳执行器捕获）
            print("\n" + "=" * 60)
            print(f"📤 发送定时消息")
            print(f"标题: {msg.get('title')}")
            print(f"计划时间: {msg.get('scheduled_time')}")
            print("=" * 60)
            print(msg.get('content'))
            print("=" * 60 + "\n")
            
            # 生成消息发送指令文件（供心跳执行器读取并调用 message 工具）
            send_instruction = {
                "action": "send_message",
                "channel": msg.get("channel", "xiaoyi-channel"),
                "target": msg.get("target", "default"),
                "message": msg.get("content"),
                "timestamp": datetime.now().isoformat()
            }
            
            instruction_file = root / "reports" / "ops" / "pending_sends.jsonl"
            with open(instruction_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(send_instruction, ensure_ascii=False) + '\n')
            
            # 记录已发送
            msg["sent_at"] = datetime.now().isoformat()
            msg["status"] = "sent"
            
            with open(sent_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
            
            processed += 1
        
        except Exception as e:
            print(f"❌ 发送失败: {e}")
    
    # 更新定时消息文件（只保留未来的消息）
    with open(scheduled_file, 'w', encoding='utf-8') as f:
        for msg in future_messages:
            f.write(json.dumps(msg, ensure_ascii=False) + '\n')
    
    return {
        "status": "success",
        "processed": processed,
        "remaining": len(future_messages)
    }


def main():
    """主函数"""
    print("=" * 60)
    print("  一次性定时任务触发器 V1.0.0")
    print("=" * 60)
    print()
    
    result = check_scheduled_messages()
    
    print(f"✅ 处理完成")
    print(f"  发送: {result['processed']} 条")
    print(f"  剩余: {result['remaining']} 条")
    print()


if __name__ == "__main__":
    main()
