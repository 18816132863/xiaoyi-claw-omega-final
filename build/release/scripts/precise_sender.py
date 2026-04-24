#!/usr/bin/env python3
"""
精确定时发送器 - V1.0.0

在指定时间精确发送消息到聊天界面。

使用方式：
    python scripts/precise_sender.py --time "2026-04-20 10:40:00"
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


def wait_until(target_time: datetime):
    """等待到指定时间"""
    now = datetime.now(timezone.utc)
    
    if target_time <= now:
        print(f"目标时间已过: {target_time}")
        return False
    
    diff = (target_time - now).total_seconds()
    print(f"等待 {diff:.1f} 秒到 {target_time}...")
    
    # 分段等待，最后1秒精确等待
    while diff > 1:
        time.sleep(1)
        now = datetime.now(timezone.utc)
        diff = (target_time - now).total_seconds()
        print(f"  剩余 {diff:.1f} 秒...", end='\r')
    
    # 最后精确等待
    if diff > 0:
        time.sleep(diff)
    
    print(f"\n✅ 到达目标时间: {datetime.now(timezone.utc)}")
    return True


def send_message(message: Dict[str, Any]) -> bool:
    """发送消息（写入 pending_sends.jsonl）"""
    root = get_project_root()
    pending_file = root / "reports/ops/pending_sends.jsonl"
    
    send_instruction = {
        "action": "send",
        "channel": message.get("channel", "xiaoyi-channel"),
        "target": message.get("target", "default"),
        "message": message.get("content"),
        "title": message.get("title"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    with open(pending_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(send_instruction, ensure_ascii=False) + '\n')
    
    print(f"✅ 消息已写入待发送队列: {message.get('title')}")
    return True


def main():
    root = get_project_root()
    scheduled_file = root / "reports/ops/scheduled_messages.jsonl"
    
    # 读取定时消息
    if not scheduled_file.exists():
        print("❌ 无定时消息")
        return 1
    
    messages = []
    with open(scheduled_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                messages.append(json.loads(line.strip()))
            except:
                pass
    
    if not messages:
        print("❌ 无定时消息")
        return 1
    
    # 取第一条消息
    message = messages[0]
    scheduled_time_str = message.get('scheduled_time')
    
    # 解析时间
    if scheduled_time_str.endswith('Z'):
        scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
    else:
        scheduled_time = datetime.fromisoformat(scheduled_time_str)
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
    
    print("=" * 60)
    print("  精确定时发送器 V1.0.0")
    print("=" * 60)
    print(f"  消息标题: {message.get('title')}")
    print(f"  计划时间: {scheduled_time} (UTC)")
    print(f"  北京时间: {scheduled_time.astimezone().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 等待到指定时间
    if not wait_until(scheduled_time):
        return 1
    
    # 发送消息
    send_message(message)
    
    # 清空定时消息文件
    with open(scheduled_file, 'w', encoding='utf-8') as f:
        pass
    
    print("=" * 60)
    print("  ✅ 发送完成")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
