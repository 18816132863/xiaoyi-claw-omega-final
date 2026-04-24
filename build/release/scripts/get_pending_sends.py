#!/usr/bin/env python3
"""
获取待发送消息 - V1.0.0

供 AI 在心跳响应时调用，获取待发送消息列表。

使用方式：
    python scripts/get_pending_sends.py [--clear]

输出格式：
    JSON 数组，每条消息包含：
    - action: "send"
    - channel: 渠道
    - target: 目标
    - message: 消息内容
    - title: 标题
"""

import sys
import json
from pathlib import Path


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


def main():
    root = get_project_root()
    pending_file = root / "reports/ops/pending_sends.jsonl"
    
    if not pending_file.exists():
        print("[]")
        return
    
    messages = []
    with open(pending_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                messages.append(json.loads(line.strip()))
            except:
                pass
    
    print(json.dumps(messages, ensure_ascii=False, indent=2))
    
    # 如果指定 --clear，清空文件
    if "--clear" in sys.argv and messages:
        pending_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
