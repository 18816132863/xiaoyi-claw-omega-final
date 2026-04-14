#!/usr/bin/env python3
"""
智能压缩器 V1.0.0

功能：
- 自动识别文件类型
- 保留关键结构
- 压缩冗余内容
- 支持增量更新
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

def compress_json_smart(data: Any, max_depth: int = 3, max_items: int = 10) -> Any:
    """智能压缩 JSON"""
    if max_depth == 0:
        return "..."
    
    if isinstance(data, dict):
        result = {}
        for i, (k, v) in enumerate(data.items()):
            if i >= max_items:
                result["..."] = f"还有 {len(data) - max_items} 项"
                break
            result[k] = compress_json_smart(v, max_depth - 1, max_items)
        return result
    
    if isinstance(data, list):
        if len(data) == 0:
            return []
        if len(data) <= 2:
            return [compress_json_smart(item, max_depth - 1, max_items) for item in data]
        return [
            compress_json_smart(data[0], max_depth - 1, max_items),
            f"... 共 {len(data)} 项"
        ]
    
    if isinstance(data, str):
        if len(data) > 100:
            return data[:100] + "..."
        return data
    
    return data

def compress_markdown_smart(content: str) -> str:
    """智能压缩 Markdown"""
    lines = content.split("\n")
    result = []
    
    for line in lines:
        # 保留标题
        if line.startswith("#"):
            result.append(line)
        # 保留表格结构
        elif line.startswith("|") and ("---" in line or line.count("|") >= 2):
            result.append(line)
        # 保留关键标记
        elif any(line.strip().startswith(k) for k in ["-", "*", "1.", ">", "```"]):
            result.append(line)
        # 保留短行
        elif len(line.strip()) < 80 and line.strip():
            result.append(line)
    
    # 限制总行数
    if len(result) > 50:
        result = result[:50] + [f"\n... (已压缩，原 {len(lines)} 行)"]
    
    return "\n".join(result)

def compress_file(file_path: Path, output_path: Path = None) -> tuple:
    """压缩单个文件"""
    if not file_path.exists():
        return None, None
    
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    orig_size = len(content)
    
    if file_path.suffix == ".json":
        try:
            data = json.loads(content)
            compressed = json.dumps(compress_json_smart(data), ensure_ascii=False, indent=2)
        except:
            compressed = content
    elif file_path.suffix == ".md":
        compressed = compress_markdown_smart(content)
    else:
        compressed = content
    
    comp_size = len(compressed)
    ratio = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(compressed, encoding="utf-8")
    
    return orig_size, comp_size, ratio

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        orig, comp, ratio = compress_file(file_path)
        print(f"原始: {orig} -> 压缩: {comp} ({ratio:.1f}% 压缩)")
