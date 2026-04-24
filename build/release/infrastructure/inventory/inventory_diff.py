#!/usr/bin/env python3
"""
inventory_diff.py - 对比 before / after

最低职责:
- 对比 before / after
- 生成新增、合并、删除、重命名差异
- 输出差异报告

输出: reports/inventory_diff.json
"""

import os
import json
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def load_inventory(file_path: str) -> dict:
    """加载库存文件"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def compare_inventories(before: dict, after: dict) -> dict:
    """对比两个库存快照"""
    diff = {
        "compare_time": datetime.now().isoformat(),
        "summary": {
            "dirs_added": 0,
            "dirs_removed": 0,
            "skills_added": 0,
            "skills_removed": 0,
            "skills_merged": 0,
            "files_added": 0,
            "files_removed": 0
        },
        "details": {
            "dirs_added": [],
            "dirs_removed": [],
            "skills_added": [],
            "skills_removed": [],
            "skills_merged": []
        }
    }
    
    # 对比目录 - 修复：处理字典列表
    before_dirs = before.get("top_level_dirs", [])
    after_dirs = after.get("top_level_dirs", [])
    
    # 如果是字典列表，提取名称
    if before_dirs and isinstance(before_dirs[0], dict):
        before_dirs = [d.get("name", str(d)) for d in before_dirs]
    if after_dirs and isinstance(after_dirs[0], dict):
        after_dirs = [d.get("name", str(d)) for d in after_dirs]
    
    before_dirs = set(before_dirs)
    after_dirs = set(after_dirs)
    
    diff["details"]["dirs_added"] = list(after_dirs - before_dirs)
    diff["details"]["dirs_removed"] = list(before_dirs - after_dirs)
    diff["summary"]["dirs_added"] = len(diff["details"]["dirs_added"])
    diff["summary"]["dirs_removed"] = len(diff["details"]["dirs_removed"])
    
    # 对比技能 - 修复：处理字典列表
    before_skills = before.get("skills", [])
    after_skills = after.get("skills", [])
    
    # 如果是字典列表，提取名称
    if before_skills and isinstance(before_skills[0], dict):
        before_skills = [s.get("name", str(s)) for s in before_skills]
    if after_skills and isinstance(after_skills[0], dict):
        after_skills = [s.get("name", str(s)) for s in after_skills]
    
    before_skills = set(before_skills)
    after_skills = set(after_skills)
    
    diff["details"]["skills_added"] = list(after_skills - before_skills)
    diff["details"]["skills_removed"] = list(before_skills - after_skills)
    diff["summary"]["skills_added"] = len(diff["details"]["skills_added"])
    diff["summary"]["skills_removed"] = len(diff["details"]["skills_removed"])
    
    # 对比文件数
    before_files = before.get("summary", {}).get("total_files", 0)
    after_files = after.get("summary", {}).get("total_files", 0)
    diff["summary"]["files_added"] = max(0, after_files - before_files)
    diff["summary"]["files_removed"] = max(0, before_files - after_files)
    
    return diff

def main():
    workspace = str(get_project_root())
    reports_dir = Path(workspace) / "reports"
    
    # 加载 before 和 after
    before_file = reports_dir / "INVENTORY_BEFORE.json"
    after_file = reports_dir / "INVENTORY_AFTER.json"
    
    before = load_inventory(str(before_file))
    after = load_inventory(str(after_file))
    
    if not before:
        print(f"警告: 未找到 BEFORE 文件: {before_file}")
    if not after:
        print(f"警告: 未找到 AFTER 文件: {after_file}")
    
    # 对比
    diff = compare_inventories(before, after)
    
    # 保存差异报告
    output_file = reports_dir / "inventory_diff.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(diff, f, indent=2, ensure_ascii=False)
    
    print(f"差异报告已生成: {output_file}")
    print(f"目录变化: +{diff['summary']['dirs_added']} -{diff['summary']['dirs_removed']}")
    print(f"技能变化: +{diff['summary']['skills_added']} -{diff['summary']['skills_removed']}")

if __name__ == "__main__":
    main()
