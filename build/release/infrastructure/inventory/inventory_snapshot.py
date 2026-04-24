#!/usr/bin/env python3
"""
inventory_snapshot.py - 导出当前目录、模块、文件、技能总量快照

最低职责:
- 导出当前目录、模块、文件、技能总量快照
- 生成 JSON 格式的快照文件
- 支持与历史快照对比

输出: reports/snapshots/inventory_snapshot_YYYYMMDD.json
"""

import os
import json
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def get_inventory_snapshot(workspace_path: str) -> dict:
    """生成库存快照"""
    snapshot = {
        "snapshot_time": datetime.now().isoformat(),
        "version": "V28.0",
        "summary": {
            "top_level_dirs": 0,
            "total_files": 0,
            "md_files": 0,
            "json_files": 0,
            "py_files": 0,
            "skill_dirs": 0
        },
        "top_level_dirs": [],
        "skill_count": 0,
        "skills": []
    }
    
    workspace = Path(workspace_path)
    
    # 统计顶层目录
    for item in workspace.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            snapshot["summary"]["top_level_dirs"] += 1
            file_count = len(list(item.rglob("*.*")))
            snapshot["top_level_dirs"].append({
                "name": item.name,
                "file_count": file_count
            })
    
    # 统计文件
    snapshot["summary"]["total_files"] = len(list(workspace.rglob("*.*")))
    snapshot["summary"]["md_files"] = len(list(workspace.rglob("*.md")))
    snapshot["summary"]["json_files"] = len(list(workspace.rglob("*.json")))
    snapshot["summary"]["py_files"] = len(list(workspace.rglob("*.py")))
    
    # 统计技能
    skills_dir = workspace / "skills"
    if skills_dir.exists():
        for skill in skills_dir.iterdir():
            if skill.is_dir() and not skill.name.startswith('_'):
                snapshot["summary"]["skill_dirs"] += 1
                snapshot["skills"].append(skill.name)
    
    snapshot["skill_count"] = snapshot["summary"]["skill_dirs"]
    
    return snapshot

def main():
    workspace = str(get_project_root())
    snapshot = get_inventory_snapshot(workspace)
    
    # 保存快照
    output_dir = Path(workspace) / "reports" / "snapshots"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = output_dir / f"inventory_snapshot_{date_str}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    print(f"快照已生成: {output_file}")
    print(f"顶层目录: {snapshot['summary']['top_level_dirs']}")
    print(f"技能数量: {snapshot['skill_count']}")
    print(f"总文件数: {snapshot['summary']['total_files']}")

if __name__ == "__main__":
    main()
