#!/usr/bin/env python3
"""
File Manager 技能 - V1.0.0

入口: run(params: dict) -> dict
功能: 本地文件复制
"""

import os
import shutil
from pathlib import Path

def run(params: dict) -> dict:
    """
    执行 File Manager 技能

    Args:
        params: {
            "source_path": "...",
            "target_path": "...",
            "operation": "copy"  # 可选，默认 copy
        }

    Returns:
        {"success": bool, "data": {...}, "error": {...}}
    """
    source_path = params.get("source_path")
    target_path = params.get("target_path")
    operation = params.get("operation", "copy")

    if not source_path:
        return {
            "success": False,
            "data": None,
            "error": {"code": "MISSING_PARAM", "message": "缺少 source_path 参数"}
        }

    if not target_path:
        return {
            "success": False,
            "data": None,
            "error": {"code": "MISSING_PARAM", "message": "缺少 target_path 参数"}
        }

    source = Path(source_path)
    target = Path(target_path)

    if not source.exists():
        return {
            "success": False,
            "data": None,
            "error": {"code": "SOURCE_NOT_FOUND", "message": f"源文件不存在: {source_path}"}
        }

    if operation != "copy":
        return {
            "success": False,
            "data": None,
            "error": {"code": "UNSUPPORTED_OPERATION", "message": f"不支持的操作: {operation}"}
        }

    try:
        # 确保目标目录存在
        target.parent.mkdir(parents=True, exist_ok=True)

        # 执行复制
        shutil.copy2(source, target)

        return {
            "success": True,
            "data": {
                "source_path": str(source.absolute()),
                "target_path": str(target.absolute()),
                "operation": "copy",
                "copied": True,
                "source_size": source.stat().st_size,
                "target_size": target.stat().st_size
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": {"code": "COPY_FAILED", "message": str(e)}
        }

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    else:
        params = {
            "source_path": "tests/fixtures/integration/file_manager/source/sample.txt",
            "target_path": "tests/fixtures/integration/file_manager/target/sample.txt"
        }
    result = run(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))
