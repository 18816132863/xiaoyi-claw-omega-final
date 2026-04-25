#!/usr/bin/env python3
"""
快速创建定时任务 V2.0.0

使用方式：
    python scripts/quick_task.py "消息内容" "2026-04-20 22:30:00"
    python scripts/quick_task.py --recurring "消息内容" --cron "0 9 * * *"
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.task_manager import get_task_manager


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="创建定时任务")
    parser.add_argument("message", help="消息内容")
    parser.add_argument("time", nargs="?", help="执行时间 (格式: YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--cron", "-c", help="Cron 表达式 (重复任务)")
    parser.add_argument("--title", "-t", default="⏰ 定时提醒", help="消息标题")
    
    args = parser.parse_args()
    
    tm = get_task_manager()
    
    if args.cron:
        # 重复任务
        result = await tm.create_recurring_message(
            user_id="default",
            message=args.message,
            cron_expr=args.cron,
            title=args.title
        )
    elif args.time:
        # 一次性任务
        result = await tm.create_scheduled_message(
            user_id="default",
            message=args.message,
            run_at=args.time,
            title=args.title
        )
    else:
        print("错误: 必须提供时间或 cron 表达式")
        sys.exit(1)
    
    if result.get("success"):
        print(f"✅ 任务创建成功!")
        print(f"   任务 ID: {result['task_id']}")
        print(f"   状态: {result['status']}")
    else:
        print(f"❌ 任务创建失败: {result.get('errors', result)}")


if __name__ == "__main__":
    asyncio.run(main())
