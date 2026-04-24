#!/usr/bin/env python3
"""
skill_removed_manifest.py - 生成当天删除留痕文件

最低职责:
- 生成当天删除留痕文件
- 记录删除详情
- 输出 manifest

输出: reports/skill_removed_manifest_daily.json
"""

import os
import json
from datetime import datetime
from pathlib import Path

def generate_removed_manifest(workspace_path: str) -> dict:
    """生成删除清单"""
    results = {
        "manifest_time": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "summary": {
            "total_removed": 0
        },
        "removed_items": []
    }
    
    workspace = Path(workspace_path)
    reports_dir = workspace / "reports"
    
    # 加载删除清单
    removed_file = reports_dir / "SKILL_REMOVED_MANIFEST.json"
    if removed_file.exists():
        with open(removed_file, 'r', encoding='utf-8') as f:
            removed_data = json.load(f)
            results["removed_items"] = removed_data.get("removed_skills", [])
            results["summary"]["total_removed"] = len(results["removed_items"])
    
    return results

def main():
    # 使用 path_resolver 获取路径
    from infrastructure.path_resolver import get_project_root
    workspace = get_project_root()
    results = generate_removed_manifest(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = output_dir / f"skill_removed_manifest_{date_str}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"删除清单已生成:")
    print(f"  删除技能数: {results['summary']['total_removed']}")
    print(f"  输出: {output_file}")

if __name__ == "__main__":
    main()
