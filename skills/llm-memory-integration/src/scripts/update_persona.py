#!/usr/bin/env python3
"""
LLM Memory Integration - 用户画像更新脚本
使用 LLM_GLM5 分析对话历史，更新用户画像
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
PERSONA_FILE = MEMORY_DIR / "persona.md"
MEMORY_FILE = WORKSPACE / "MEMORY.md"
SESSION_STATE = WORKSPACE / "SESSION-STATE.md"

def read_file(filepath):
    """读取文件内容"""
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return ""

def write_file(filepath, content):
    """写入文件"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")

def append_to_persona(preferences):
    """追加用户偏好到 persona.md"""
    existing = read_file(PERSONA_FILE)
    
    # 添加时间戳
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 构建新内容
    new_section = f"""

---

## 更新记录 ({timestamp})

{preferences}
"""
    
    # 追加到文件末尾
    write_file(PERSONA_FILE, existing + new_section)
    print(f"✅ 已更新 persona.md")

def update_memory_md(preferences):
    """更新 MEMORY.md 用户画像部分"""
    existing = read_file(MEMORY_FILE)
    
    # 查找用户画像部分
    if "## 用户画像" in existing:
        # 在用户画像部分后追加
        lines = existing.split("\n")
        new_lines = []
        in_persona = False
        added = False
        
        for line in lines:
            new_lines.append(line)
            if "## 用户画像" in line:
                in_persona = True
            elif in_persona and line.startswith("## ") and not added:
                # 在下一个章节前插入
                new_lines.insert(-1, f"\n### 更新 {datetime.now().strftime('%Y-%m-%d')}\n{preferences}\n")
                added = True
        
        if not added:
            new_lines.append(f"\n### 更新 {datetime.now().strftime('%Y-%m-%d')}\n{preferences}\n")
        
        write_file(MEMORY_FILE, "\n".join(new_lines))
    else:
        # 添加用户画像部分
        persona_section = f"""

## 用户画像

### 更新 {datetime.now().strftime('%Y-%m-%d')}
{preferences}
"""
        write_file(MEMORY_FILE, existing + persona_section)
    
    print(f"✅ 已更新 MEMORY.md")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 update_persona.py '<偏好内容>'")
        sys.exit(1)
    
    preferences = sys.argv[1]
    
    # 更新 persona.md
    append_to_persona(preferences)
    
    # 更新 MEMORY.md
    update_memory_md(preferences)
    
    print("用户画像更新完成")

if __name__ == "__main__":
    main()
