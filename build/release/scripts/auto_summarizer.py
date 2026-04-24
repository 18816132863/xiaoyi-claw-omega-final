#!/usr/bin/env python3
"""
自动摘要生成器 V1.0.0

功能：
- 自动生成文件摘要
- 提取关键信息
- 支持多种格式
"""

import json
import re
from pathlib import Path

def extract_summary(content: str, file_type: str) -> str:
    """提取文件摘要"""
    if file_type == "md":
        # 提取标题和第一段
        lines = content.split("\n")
        title = ""
        first_para = ""
        
        for line in lines:
            if line.startswith("#") and not title:
                title = line.strip("# ")
            elif line.strip() and not line.startswith("#") and not first_para:
                first_para = line.strip()[:200]
                break
        
        return f"{title}: {first_para}" if title else first_para
    
    elif file_type == "json":
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                return f"JSON 对象，包含: {', '.join(keys)}"
            elif isinstance(data, list):
                return f"JSON 数组，{len(data)} 项"
        except:
            pass
    
    return content[:200]

def generate_summary_file(source: Path, target: Path):
    """生成摘要文件"""
    content = source.read_text(encoding="utf-8", errors="ignore")
    file_type = source.suffix[1:]
    summary = extract_summary(content, file_type)
    
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(summary)
    
    return len(content), len(summary)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        source = Path(sys.argv[1])
        orig, comp = generate_summary_file(source, Path("summary.txt"))
        print(f"原始: {orig} -> 摘要: {comp}")
