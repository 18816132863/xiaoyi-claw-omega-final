#!/usr/bin/env python3
"""
定时消息创建工具 V1.0.0

使用方式：
    python scripts/create_scheduled_message.py --message "提醒内容" --time "2026-04-20 15:00:00"
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from infrastructure.task_manager import get_task_manager


async def main():
    parser = argparse.ArgumentParser(description="创建定时消息任务")
    parser.add_argument("--message", "-m", required=True, help="消息内容")
    parser.add_argument("--time", "-t", required=True, help="执行时间 (格式: YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--user", "-u", default="default", help="用户 ID")
    parser.add_argument("--channel", "-c", default="xiaoyi-channel", help="消息渠道")
    parser.add_argument("--title", default=None, help="消息标题")
    
    args = parser.parse_args()
    
    tm = get_task_manager()
    
    print(f"创建定时消息任务...")
    print(f"  消息: {args.message[:50]}...")
    print(f"  时间: {args.time}")
    print(f"  渠道: {args.channel}")
    
    result = await tm.create_scheduled_message(
        user_id=args.user,
        message=args.message,
        run_at=args.time,
        channel=args.channel,
        title=args.title
    )
    
    if result.get("success"):
        print(f"\n✅ 任务创建成功!")
        print(f"  任务 ID: {result['task_id']}")
        print(f"  状态: {result['status']}")
        
        # 查询任务详情
        task = await tm.get_task(result['task_id'])
        if task:
            print(f"\n任务详情:")
            print(f"  类型: {task.task_type}")
            print(f"  目标: {task.goal}")
            print(f"  触发模式: {task.trigger_mode.value}")
    else:
        print(f"\n❌ 任务创建失败!")
        print(f"  错误: {result.get('errors', result)}")


if __name__ == "__main__":
    asyncio.run(main())
