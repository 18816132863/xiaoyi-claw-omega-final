#!/usr/bin/env python3
"""
freeze_window_enforcer.py - 自动判断冻结期是否已满

最低职责:
- 自动判断冻结期是否已满
- 检查冻结技能状态
- 输出冻结期状态

输出: reports/freeze_window_status.json
"""

import os
import json
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def check_freeze_window(workspace_path: str) -> dict:
    """检查冻结窗口"""
    results = {
        "check_time": datetime.now().isoformat(),
        "summary": {
            "total_frozen": 0,
            "window_expired": 0,
            "window_active": 0
        },
        "frozen_items": []
    }
    
    workspace = Path(workspace_path)
    reports_dir = workspace / "reports"
    
    # 加载冻结清单
    freeze_file = reports_dir / "SKILL_FREEZE_LIST.json"
    if freeze_file.exists():
        with open(freeze_file, 'r', encoding='utf-8') as f:
            freeze_data = json.load(f)
            
            for skill in freeze_data.get("frozen_skills", []):
                skill_name = skill.get("skill_name")
                freeze_end = skill.get("freeze_end", "")
                
                item = {
                    "skill_name": skill_name,
                    "freeze_end": freeze_end,
                    "window_status": "unknown"
                }
                
                if freeze_end:
                    try:
                        end_date = datetime.strptime(freeze_end, "%Y-%m-%d")
                        if datetime.now() > end_date:
                            item["window_status"] = "expired"
                            results["summary"]["window_expired"] += 1
                        else:
                            item["window_status"] = "active"
                            results["summary"]["window_active"] += 1
                    except:
                        item["window_status"] = "unknown"
                
                results["frozen_items"].append(item)
                results["summary"]["total_frozen"] += 1
    
    return results

def main():
    workspace = str(get_project_root())
    results = check_freeze_window(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "freeze_window_status.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"冻结窗口检查完成:")
    print(f"  冻结技能: {results['summary']['total_frozen']}")
    print(f"  已过期: {results['summary']['window_expired']}")
    print(f"  进行中: {results['summary']['window_active']}")

if __name__ == "__main__":
    main()
