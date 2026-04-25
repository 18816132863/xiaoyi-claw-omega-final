#!/usr/bin/env python3
"""
skill_merge_mapping.py - 记录"谁并到谁"

最低职责:
- 记录"谁并到谁"
- 验证合并是否完成
- 输出合并映射

输出: reports/skill_merge_mapping_daily.json
"""

import os
import json
from datetime import datetime
from pathlib import Path

def generate_merge_mapping(workspace_path: str) -> dict:
    """生成合并映射"""
    results = {
        "mapping_time": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "summary": {
            "total_merges": 0,
            "verified": 0,
            "pending": 0
        },
        "merges": []
    }
    
    workspace = Path(workspace_path)
    reports_dir = workspace / "reports"
    skills_dir = workspace / "skills"
    
    # 加载合并映射
    merge_file = reports_dir / "MERGE_MAPPING.json"
    if merge_file.exists():
        with open(merge_file, 'r', encoding='utf-8') as f:
            merge_data = json.load(f)
            
            for merge in merge_data.get("merges", []):
                source = merge.get("source")
                target = merge.get("target")
                
                # 验证合并是否完成
                source_exists = (skills_dir / source).exists()
                target_exists = (skills_dir / target).exists()
                
                merge_info = {
                    "source": source,
                    "target": target,
                    "reason": merge.get("reason", ""),
                    "source_exists": source_exists,
                    "target_exists": target_exists,
                    "status": "verified" if (not source_exists and target_exists) else "pending"
                }
                
                results["merges"].append(merge_info)
                results["summary"]["total_merges"] += 1
                if merge_info["status"] == "verified":
                    results["summary"]["verified"] += 1
                else:
                    results["summary"]["pending"] += 1
    
    return results

def main():
    from infrastructure.path_resolver import get_project_root
    workspace = get_project_root()
    results = generate_merge_mapping(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    output_file = output_dir / f"skill_merge_mapping_{date_str}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"合并映射已生成:")
    print(f"  总合并数: {results['summary']['total_merges']}")
    print(f"  已验证: {results['summary']['verified']}")
    print(f"  待处理: {results['summary']['pending']}")

if __name__ == "__main__":
    main()
