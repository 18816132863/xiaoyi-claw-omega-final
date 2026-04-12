#!/usr/bin/env python3
"""
PDF 技能 - V1.0.0

入口: run(params: dict) -> dict
功能: 校验 PDF 文件存在并返回基本信息
"""

import os
from pathlib import Path

def run(params: dict) -> dict:
    """
    执行 PDF 技能

    Args:
        params: {"file_path": "..."}

    Returns:
        {"success": bool, "data": {...}, "error": {...}}
    """
    file_path = params.get("file_path")

    if not file_path:
        return {
            "success": False,
            "data": None,
            "error": {"code": "MISSING_PARAM", "message": "缺少 file_path 参数"}
        }

    path = Path(file_path)

    if not path.exists():
        return {
            "success": False,
            "data": None,
            "error": {"code": "FILE_NOT_FOUND", "message": f"文件不存在: {file_path}"}
        }

    if path.suffix.lower() != ".pdf":
        return {
            "success": False,
            "data": None,
            "error": {"code": "INVALID_EXTENSION", "message": f"文件扩展名不是 .pdf: {path.suffix}"}
        }

    stat = path.stat()

    return {
        "success": True,
        "data": {
            "file_name": path.name,
            "file_path": str(path.absolute()),
            "file_size": stat.st_size,
            "extension": path.suffix.lower()
        },
        "error": None
    }

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        params = json.loads(sys.argv[1])
    else:
        params = {"file_path": "tests/fixtures/smoke/blank.pdf"}
    result = run(params)
    print(json.dumps(result, indent=2, ensure_ascii=False))
