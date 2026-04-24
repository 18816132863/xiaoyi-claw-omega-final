#!/usr/bin/env python3
"""
快速创建定时消息 V1.0.0

使用方式：
    python scripts/quick_schedule.py "消息内容" "2026-04-20 15:00:00"
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
    if len(sys.argv) < 3:
        print("用法: python scripts/quick_schedule.py <消息内容> <时间>")
        print("示例: python scripts/quick_schedule.py '开会提醒' '2026-04-20 15:00:00'")
        sys.exit(1)
    
    message = sys.argv[1]
    run_at = sys.argv[2]
    
    tm = get_task_manager()
    
    result = await tm.create_scheduled_message(
        user_id="default",
        message=message,
        run_at=run_at,
        title="⏰ 定时提醒"
    )
    
    if result.get("success"):
        print(f"✅ 任务创建成功!")
        print(f"   任务 ID: {result['task_id']}")
        print(f"   状态: {result['status']}")
        print(f"   执行时间: {run_at}")
    else:
        print(f"❌ 任务创建失败: {result.get('errors', result)}")


if __name__ == "__main__":
    asyncio.run(main())
