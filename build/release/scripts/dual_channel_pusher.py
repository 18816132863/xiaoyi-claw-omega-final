import os
#!/usr/bin/env python3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
"""
双渠道推送器 - 负一屏 + 小艺界面

所有定时任务完成后，同时推送到：
1. 负一屏（通过 today-task 技能）
2. 小艺界面（通过 message 工具）
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 路径配置
WORKSPACE = Path(str(PROJECT_ROOT))
TODAY_TASK_SKILL = WORKSPACE / "skills/today-task/scripts/task_push.py"


def push_to_negative_screen(task_data: dict) -> dict:
    """推送到负一屏"""
    # 创建临时 JSON 文件
    temp_file = f"/tmp/push_{int(time.time())}.json"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(task_data, f, ensure_ascii=False, indent=2)

    # 调用 today-task 技能
    result = subprocess.run(
        ["python", str(TODAY_TASK_SKILL), "--data", temp_file],
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr
    }


def push_to_xiaoyi(task_data: dict) -> dict:
    """推送到小艺界面（通过 message 工具）"""
    # 这里需要通过 OpenClaw 的 message 工具
    # 由于我们在脚本中，需要通过其他方式触发
    # 方案：写入待发送队列，由心跳执行器处理

    pending_file = WORKSPACE / "reports/ops/pending_sends.jsonl"
    pending_file.parent.mkdir(parents=True, exist_ok=True)

    message = {
        "channel": "xiaoyi-channel",
        "message": task_data.get("task_content", ""),
        "scheduled_time": datetime.now().isoformat(),
        "task_name": task_data.get("task_name", "定时任务")
    }

    with open(pending_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(message, ensure_ascii=False) + "\n")

    return {
        "success": True,
        "queued": True,
        "file": str(pending_file)
    }


def dual_push(task_name: str, task_content: str, task_result: str = "已完成") -> dict:
    """
    双渠道推送

    Args:
        task_name: 任务名称
        task_content: 任务内容（Markdown格式）
        task_result: 执行结果

    Returns:
        推送结果
    """
    task_data = {
        "task_name": task_name,
        "task_content": task_content,
        "task_result": task_result,
        "schedule_task_id": f"{task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

    # 1. 推送到负一屏
    neg_screen_result = push_to_negative_screen(task_data)

    # 2. 推送到小艺界面
    xiaoyi_result = push_to_xiaoyi(task_data)

    return {
        "task_name": task_name,
        "negative_screen": neg_screen_result,
        "xiaoyi": xiaoyi_result,
        "success": neg_screen_result["success"] and xiaoyi_result["success"]
    }


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: python dual_channel_pusher.py <任务名称> <内容文件> [结果]")
        print("示例: python dual_channel_pusher.py 天气提醒 weather.md 已完成")
        sys.exit(1)

    task_name = sys.argv[1]
    content_file = sys.argv[2]
    task_result = sys.argv[3] if len(sys.argv) > 3 else "已完成"

    # 读取内容
    with open(content_file, "r", encoding="utf-8") as f:
        task_content = f.read()

    # 执行双渠道推送
    result = dual_push(task_name, task_content, task_result)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
