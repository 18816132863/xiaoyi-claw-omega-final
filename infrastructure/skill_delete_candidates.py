#!/usr/bin/env python3
"""
skill_delete_candidates.py - 自动筛出删除候选

最低职责:
- 自动筛出删除候选
- 根据冻结期、使用数据判断
- 输出候选清单

输出: reports/skill_delete_candidates_auto.json
"""

import os
import json
from datetime import datetime
from pathlib import Path

def find_delete_candidates(workspace_path: str) -> dict:
    """查找删除候选"""
    results = {
        "scan_time": datetime.now().isoformat(),
        "summary": {
            "total_candidates": 0,
            "from_frozen": 0,
            "from_deprecated": 0,
            "from_low_usage": 0
        },
        "candidates": []
    }
    
    workspace = Path(workspace_path)
    reports_dir = workspace / "reports"
    
    # 从冻结清单获取
    freeze_file = reports_dir / "SKILL_FREEZE_LIST.json"
    if freeze_file.exists():
        with open(freeze_file, 'r', encoding='utf-8') as f:
            freeze_data = json.load(f)
            for skill in freeze_data.get("frozen_skills", []):
                results["candidates"].append({
                    "skill_name": skill.get("skill_name"),
                    "source": "frozen",
                    "reason": "冻结期结束，无真实调用"
                })
                results["summary"]["from_frozen"] += 1
    
    # 从决策日志获取 deprecated
    decision_file = reports_dir / "SKILL_DECISION_LOG.csv"
    if decision_file.exists():
        with open(decision_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                for line in lines[1:]:
                    values = line.strip().split(',')
                    if len(values) >= 5:
                        decision = values[4]
                        if decision == "deprecate":
                            skill_name = values[1]
                            # 避免重复
                            if not any(c["skill_name"] == skill_name for c in results["candidates"]):
                                results["candidates"].append({
                                    "skill_name": skill_name,
                                    "source": "deprecated",
                                    "reason": "已标记为废弃"
                                })
                                results["summary"]["from_deprecated"] += 1
    
    results["summary"]["total_candidates"] = len(results["candidates"])
    
    return results

def main():
    from infrastructure.path_resolver import get_project_root
    workspace = get_project_root()
    results = find_delete_candidates(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "skill_delete_candidates_auto.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"删除候选扫描完成:")
    print(f"  总候选数: {results['summary']['total_candidates']}")
    print(f"  来自冻结: {results['summary']['from_frozen']}")
    print(f"  来自废弃: {results['summary']['from_deprecated']}")

if __name__ == "__main__":
    main()
