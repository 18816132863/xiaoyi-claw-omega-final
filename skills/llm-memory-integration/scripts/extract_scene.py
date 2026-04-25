#!/usr/bin/env python3
"""
LLM Memory Integration - 场景提取脚本
使用 LLM_GLM5 分析对话，提取场景并记录
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"

def get_daily_note_path():
    """获取今日记录文件路径"""
    today = datetime.now().strftime("%Y-%m-%d")
    return MEMORY_DIR / f"{today}.md"

def read_file(filepath):
    """读取文件内容"""
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return ""

def write_file(filepath, content):
    """写入文件"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")

def append_to_daily_note(scene_name, scene_content):
    """追加场景到每日记录"""
    daily_note = get_daily_note_path()
    existing = read_file(daily_note)
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # 构建场景块
    scene_block = f"""

---

## 场景: {scene_name}
**时间**: {timestamp}

{scene_content}
"""
    
    # 如果文件不存在，创建头部
    if not existing:
        today = datetime.now().strftime("%Y-%m-%d")
        header = f"# {today} 每日记录\n\n> 自动记录的场景和事件\n"
        existing = header
    
    write_file(daily_note, existing + scene_block)
    print(f"✅ 已记录场景到 {daily_note.name}")

def record_to_git_notes(scene_name, scene_content):
    """记录到 git-notes-memory"""
    import subprocess
    
    git_notes_script = WORKSPACE / "skills" / "git-notes-memory" / "memory.py"
    
    if git_notes_script.exists():
        try:
            # 构建记忆内容
            memory_content = json.dumps({
                "scene": scene_name,
                "content": scene_content,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False)
            
            # 调用 git-notes-memory
            result = subprocess.run([
                "python3", str(git_notes_script),
                "-p", str(WORKSPACE),
                "remember", memory_content,
                "-t", f"scene,{scene_name}",
                "-i", "n"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ 已记录到 git-notes-memory: {result.stdout.strip()}")
            else:
                print(f"⚠️ git-notes-memory 记录失败: {result.stderr}")
        except Exception as e:
            print(f"⚠️ git-notes-memory 调用失败: {e}")
    else:
        print("⚠️ git-notes-memory 脚本不存在")

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 extract_scene.py '<场景名称>' '<场景内容>'")
        sys.exit(1)
    
    scene_name = sys.argv[1]
    scene_content = sys.argv[2]
    
    # 追加到每日记录
    append_to_daily_note(scene_name, scene_content)
    
    # 记录到 git-notes-memory
    record_to_git_notes(scene_name, scene_content)
    
    print("场景提取完成")

if __name__ == "__main__":
    main()
