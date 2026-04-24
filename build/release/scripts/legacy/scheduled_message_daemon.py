#!/usr/bin/env python3
"""
定时消息守护进程 - V1.0.0

职责：
1. 持续监控 scheduled_messages.jsonl
2. 到期时写入 pending_sends.jsonl 并触发通知
3. 支持精确到秒的定时发送

使用方式：
    python scripts/scheduled_message_daemon.py &
"""

import sys
import json
import time
import signal
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class ScheduledMessageDaemon:
    """定时消息守护进程"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.scheduled_file = self.root / "reports" / "ops" / "scheduled_messages.jsonl"
        self.pending_file = self.root / "reports" / "ops" / "pending_sends.jsonl"
        self.notify_file = self.root / "reports" / "ops" / "notify_send.txt"
        self.sent_file = self.root / "reports" / "ops" / "sent_messages.jsonl"
        
        self.running = True
        self.check_interval = 1.0  # 1秒检查一次
        
        # 确保目录存在
        self.scheduled_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """处理终止信号"""
        print(f"\n收到信号 {signum}，正在停止...")
        self.running = False
    
    def parse_time(self, time_str: str) -> datetime:
        """解析时间字符串"""
        if time_str.endswith('Z'):
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        elif '+' in time_str or time_str.count('-') > 2:
            return datetime.fromisoformat(time_str)
        else:
            dt = datetime.fromisoformat(time_str)
            return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    
    def check_scheduled_messages(self) -> List[Dict[str, Any]]:
        """检查定时消息"""
        if not self.scheduled_file.exists():
            return []
        
        messages = []
        with open(self.scheduled_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    messages.append(json.loads(line.strip()))
                except:
                    pass
        
        return messages
    
    def process_due_messages(self) -> int:
        """处理到期消息"""
        messages = self.check_scheduled_messages()
        if not messages:
            return 0
        
        now = datetime.now(timezone.utc)
        due_messages = []
        future_messages = []
        
        for msg in messages:
            scheduled_time = self.parse_time(msg.get('scheduled_time'))
            if scheduled_time <= now:
                due_messages.append(msg)
            else:
                future_messages.append(msg)
        
        if not due_messages:
            return 0
        
        # 处理到期消息
        processed = 0
        for msg in due_messages:
            try:
                # 写入待发送队列
                send_instruction = {
                    "action": "send",
                    "channel": msg.get("channel", "xiaoyi-channel"),
                    "target": msg.get("target", "default"),
                    "message": msg.get("content"),
                    "title": msg.get("title"),
                    "scheduled_time": msg.get("scheduled_time"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                with open(self.pending_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(send_instruction, ensure_ascii=False) + '\n')
                
                # 触发通知（写入通知文件）
                with open(self.notify_file, 'w', encoding='utf-8') as f:
                    f.write(f"PENDING_SEND:{msg.get('title', '无标题')}\n")
                
                # 记录已发送
                msg["sent_at"] = datetime.now(timezone.utc).isoformat()
                msg["status"] = "sent"
                with open(self.sent_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(msg, ensure_ascii=False) + '\n')
                
                print(f"✅ 处理到期消息: {msg.get('title')}")
                processed += 1
                
            except Exception as e:
                print(f"❌ 处理失败: {e}")
        
        # 更新定时消息文件（只保留未来的消息）
        with open(self.scheduled_file, 'w', encoding='utf-8') as f:
            for msg in future_messages:
                f.write(json.dumps(msg, ensure_ascii=False) + '\n')
        
        return processed
    
    def run(self):
        """运行守护进程"""
        print("=" * 60)
        print("  定时消息守护进程 V1.0.0")
        print("=" * 60)
        print(f"  检查间隔: {self.check_interval} 秒")
        print(f"  定时消息: {self.scheduled_file}")
        print(f"  待发送队列: {self.pending_file}")
        print("=" * 60)
        print("  按 Ctrl+C 停止")
        print("=" * 60)
        print()
        
        while self.running:
            try:
                processed = self.process_due_messages()
                if processed > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 处理了 {processed} 条到期消息")
                
            except Exception as e:
                print(f"❌ 错误: {e}")
            
            time.sleep(self.check_interval)
        
        print("\n守护进程已停止")


def main():
    root = get_project_root()
    daemon = ScheduledMessageDaemon(root)
    daemon.run()


if __name__ == "__main__":
    main()
