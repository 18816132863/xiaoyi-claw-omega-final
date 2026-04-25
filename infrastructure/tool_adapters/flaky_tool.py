import os
"""

PROJECT_ROOT = Path(__file__).resolve().parents[2]
模拟临时失败的工具 V1.0.0

用于测试重试机制。
"""

import random
from typing import Dict, Any

# 全局计数器
_call_count = 0


async def flaky_sender(inputs: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    模拟临时失败的消息发送工具
    
    前两次调用失败，第三次成功
    """
    global _call_count
    _call_count += 1
    
    print(f"  [FlakySender] 第 {_call_count} 次调用")
    
    if _call_count < 3:
        # 模拟临时失败
        print(f"  [FlakySender] 模拟失败")
        raise Exception(f"临时网络错误 (第 {_call_count} 次尝试)")
    
    # 第三次成功
    print(f"  [FlakySender] 成功!")
    
    from pathlib import Path
    import json
    from datetime import datetime
    
    root = Path(str(PROJECT_ROOT))
    pending_file = root / "reports" / "ops" / "pending_sends.jsonl"
    pending_file.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "action": "send",
        "channel": inputs.get("channel", "xiaoyi-channel"),
        "target": inputs.get("target", "default"),
        "message": inputs.get("message", ""),
        "timestamp": datetime.now().isoformat()
    }
    
    with open(pending_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    return {"success": True, "message": "发送成功"}


# 重置计数器
def reset_flaky_counter():
    global _call_count
    _call_count = 0
