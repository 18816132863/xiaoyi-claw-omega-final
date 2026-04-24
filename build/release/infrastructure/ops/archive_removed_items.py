#!/usr/bin/env python3
"""
archive_removed_items.py - 把被删技能、旧映射、旧证据归档

最低职责:
- 把被删技能、旧映射、旧证据归档
- 创建归档目录
- 输出归档清单

输出: reports/archive_manifest.json
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def archive_removed_items(workspace_path: str) -> dict:
    """归档删除项"""
    results = {
        "archive_time": datetime.now().isoformat(),
        "summary": {
            "archived_skills": 0,
            "archived_mappings": 0,
            "archived_reports": 0
        },
        "archives": []
    }
    
    workspace = Path(workspace_path)
    archive_dir = workspace / "archive" / datetime.now().strftime("%Y%m%d")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    reports_dir = workspace / "reports"
    
    # 归档删除清单
    removed_file = reports_dir / "SKILL_REMOVED_MANIFEST.json"
    if removed_file.exists():
        archive_path = archive_dir / "SKILL_REMOVED_MANIFEST.json"
        shutil.copy2(removed_file, archive_path)
        results["archives"].append({
            "type": "removed_manifest",
            "source": str(removed_file),
            "archive": str(archive_path)
        })
        results["summary"]["archived_reports"] += 1
    
    # 归档合并映射
    merge_file = reports_dir / "MERGE_MAPPING.json"
    if merge_file.exists():
        archive_path = archive_dir / "MERGE_MAPPING.json"
        shutil.copy2(merge_file, archive_path)
        results["archives"].append({
            "type": "merge_mapping",
            "source": str(merge_file),
            "archive": str(archive_path)
        })
        results["summary"]["archived_mappings"] += 1
    
    # 归档差异报告
    diff_file = reports_dir / "BEFORE_AFTER_DIFF.md"
    if diff_file.exists():
        archive_path = archive_dir / "BEFORE_AFTER_DIFF.md"
        shutil.copy2(diff_file, archive_path)
        results["archives"].append({
            "type": "diff_report",
            "source": str(diff_file),
            "archive": str(archive_path)
        })
        results["summary"]["archived_reports"] += 1
    
    return results

def main():
    workspace = str(get_project_root())
    results = archive_removed_items(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "archive_manifest.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"归档完成:")
    print(f"  归档映射: {results['summary']['archived_mappings']}")
    print(f"  归档报告: {results['summary']['archived_reports']}")

if __name__ == "__main__":
    main()
