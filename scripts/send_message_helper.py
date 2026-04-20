#!/usr/bin/env python3
"""
消息发送助手 - V1.0.0

职责：
1. 为定时任务脚本提供消息发送能力
2. 支持多种消息渠道（xiaoyi-channel, telegram, etc.）
3. 记录发送历史

使用方式：
    from scripts.send_message_helper import send_message
    
    send_message("标题", "内容")
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


def send_message(
    title: str,
    content: str,
    channel: str = "xiaoyi-channel",
    target: str = "default"
) -> Dict[str, Any]:
    """
    发送消息
    
    Args:
        title: 消息标题
        content: 消息内容
        channel: 消息渠道 (xiaoyi-channel, telegram, etc.)
        target: 目标 (default = 当前对话)
    
    Returns:
        发送结果
    """
    root = get_project_root()
    logs_dir = root / "logs" / "messages"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # 格式化消息
    message = f"{title}\n\n{content}"
    
    # 记录发送历史
    log_file = logs_dir / f"sent_{datetime.now().strftime('%Y%m%d')}.jsonl"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "title": title,
        "content": content,
        "channel": channel,
        "target": target,
        "status": "pending"
    }
    
    try:
        # 方案1: 使用 OpenClaw message 工具（推荐）
        # 由于脚本无法直接调用工具，我们使用以下策略：
        
        # 策略A: 写入待发送队列，由心跳或守护进程发送
        queue_file = root / "reports" / "ops" / "message_queue.jsonl"
        queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "content": content,
                "channel": channel,
                "target": target,
                "priority": "normal"
            }, ensure_ascii=False) + '\n')
        
        log_entry["status"] = "queued"
        log_entry["queue_file"] = str(queue_file)
        
        # 策略B: 同时输出到标准输出，方便调试
        print("\n" + "=" * 60)
        print(f"📢 消息已加入发送队列")
        print(f"标题: {title}")
        print(f"渠道: {channel}")
        print(f"目标: {target}")
        print("=" * 60)
        print(message)
        print("=" * 60 + "\n")
        
        return {
            "success": True,
            "status": "queued",
            "message": "消息已加入发送队列，将由心跳或守护进程发送",
            "queue_file": str(queue_file)
        }
    
    except Exception as e:
        log_entry["status"] = "failed"
        log_entry["error"] = str(e)
        
        return {
            "success": False,
            "status": "failed",
            "error": str(e)
        }
    
    finally:
        # 保存日志
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


def send_urgent_message(title: str, content: str) -> Dict[str, Any]:
    """
    发送紧急消息（高优先级）
    """
    return send_message(title, content, priority="urgent")


def send_scheduled_message(
    title: str,
    content: str,
    scheduled_time: datetime
) -> Dict[str, Any]:
    """
    发送定时消息
    """
    root = get_project_root()
    queue_file = root / "reports" / "ops" / "scheduled_messages.jsonl"
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(queue_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "scheduled_time": scheduled_time.isoformat(),
            "title": title,
            "content": content,
            "channel": "xiaoyi-channel",
            "target": "default",
            "status": "pending"
        }, ensure_ascii=False) + '\n')
    
    return {
        "success": True,
        "status": "scheduled",
        "scheduled_time": scheduled_time.isoformat()
    }


if __name__ == "__main__":
    # 测试
    result = send_message(
        "测试消息",
        "这是一条测试消息，来自 send_message_helper.py"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
