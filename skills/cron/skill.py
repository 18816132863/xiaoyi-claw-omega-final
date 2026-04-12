#!/usr/bin/env python3
"""
Cron 技能 - V1.0.0

入口: run(params: dict) -> dict
功能: 校验 cron 表达式合法性
"""

import re

def run(params: dict) -> dict:
    """
    执行 Cron 技能

    Args:
        params: {"expression": "*/5 * * * *"}

    Returns:
        {"success": bool, "data": {...}, "error": {...}}
    """
    expression = params.get("expression")

    if not expression:
        return {
            "success": False,
            "data": None,
            "error": {"code": "MISSING_PARAM", "message": "缺少 expression 参数"}
        }

    parts = expression.strip().split()

    # 标准 cron 是 5 段，有些扩展支持 6 段（带秒）
    if len(parts) not in [5, 6]:
        return {
            "success": False,
            "data": None,
            "error": {
                "code": "INVALID_FORMAT",
                "message": f"cron 表达式应为 5 或 6 段，实际 {len(parts)} 段: {expression}"
            }
        }

    # 基本格式校验（每段允许: *, 数字, 范围, 步进）
    # 支持: *, 数字, 数字-数字, */数字, 数字/数字, 数字-数字/数字
    valid_pattern = re.compile(r'^(\*|(\d{1,2})(-(\d{1,2}))?)(/(\d{1,2}))?$')

    for i, part in enumerate(parts):
        if not valid_pattern.match(part):
            return {
                "success": False,
                "data": None,
                "error": {
                    "code": "INVALID_SEGMENT",
                    "message": f"第 {i+1} 段格式无效: {part}"
                }
            }

    return {
        "success": True,
        "data": {
            "expression": expression,
            "segments": len(parts),
            "valid": True
        },
        "error": None
    }

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    else:
        params = {"expression": "*/5 * * * *"}
    result = run(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))
