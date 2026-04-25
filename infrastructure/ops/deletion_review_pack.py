#!/usr/bin/env python3
"""
deletion_review_pack.py - 汇总删除评审会需要看的材料

最低职责:
- 汇总删除评审会需要看的材料
- 整合冻结状态、删除候选、影响分析
- 输出评审包

输出: reports/deletion_review_pack.json
"""

import os
import json
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def generate_review_pack(workspace_path: str) -> dict:
    """生成评审包"""
    results = {
        "pack_time": datetime.now().isoformat(),
        "summary": {
            "frozen_skills": 0,
            "delete_candidates": 0,
            "affected_paths": 0
        },
        "materials": {
            "frozen_skills": [],
            "delete_candidates": [],
            "affected_golden_paths": []
        }
    }
    
    workspace = Path(workspace_path)
    reports_dir = workspace / "reports"
    
    # 加载冻结清单
    freeze_file = reports_dir / "SKILL_FREEZE_LIST.json"
    if freeze_file.exists():
        with open(freeze_file, 'r', encoding='utf-8') as f:
            freeze_data = json.load(f)
            results["materials"]["frozen_skills"] = freeze_data.get("frozen_skills", [])
            results["summary"]["frozen_skills"] = len(results["materials"]["frozen_skills"])
    
    # 加载删除候选
    candidates_file = reports_dir / "SKILL_DELETE_CANDIDATES.json"
    if candidates_file.exists():
        with open(candidates_file, 'r', encoding='utf-8') as f:
            candidates_data = json.load(f)
            results["materials"]["delete_candidates"] = candidates_data.get("candidates", [])
            results["summary"]["delete_candidates"] = len(results["materials"]["delete_candidates"])
    
    # 加载路由影响
    impact_file = reports_dir / "route_impact_analysis.json"
    if impact_file.exists():
        with open(impact_file, 'r', encoding='utf-8') as f:
            impact_data = json.load(f)
            results["materials"]["affected_golden_paths"] = impact_data.get("impacts", [])
            results["summary"]["affected_paths"] = len(results["materials"]["affected_golden_paths"])
    
    return results

def main():
    workspace = str(get_project_root())
    results = generate_review_pack(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "deletion_review_pack.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"删除评审包已生成:")
    print(f"  冻结技能: {results['summary']['frozen_skills']}")
    print(f"  删除候选: {results['summary']['delete_candidates']}")
    print(f"  受影响路径: {results['summary']['affected_paths']}")

if __name__ == "__main__":
    main()
