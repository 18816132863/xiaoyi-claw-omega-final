#!/usr/bin/env python3
"""
route_impact_analysis.py - 分析路由影响

最低职责:
- 当技能冻结、删除、合并后，分析影响哪些路由
- 生成影响报告
- 输出分析结果

输出: reports/route_impact_analysis.json
"""

import os
import json
from datetime import datetime
from pathlib import Path

def analyze_impact(workspace_path: str) -> dict:
    """分析路由影响"""
    results = {
        "analysis_time": datetime.now().isoformat(),
        "summary": {
            "frozen_skills": 0,
            "deleted_skills": 0,
            "merged_skills": 0,
            "affected_golden_paths": 0
        },
        "impacts": []
    }
    
    workspace = Path(workspace_path)
    reports_dir = workspace / "reports"
    
    # 加载冻结清单
    freeze_file = reports_dir / "SKILL_FREEZE_LIST.json"
    if freeze_file.exists():
        with open(freeze_file, 'r', encoding='utf-8') as f:
            freeze_data = json.load(f)
            results["summary"]["frozen_skills"] = len(freeze_data.get("frozen_skills", []))
    
    # 加载删除清单
    removed_file = reports_dir / "SKILL_REMOVED_MANIFEST.json"
    if removed_file.exists():
        with open(removed_file, 'r', encoding='utf-8') as f:
            removed_data = json.load(f)
            results["summary"]["deleted_skills"] = len(removed_data.get("removed_skills", []))
    
    # 加载合并映射
    merge_file = reports_dir / "MERGE_MAPPING.json"
    if merge_file.exists():
        with open(merge_file, 'r', encoding='utf-8') as f:
            merge_data = json.load(f)
            results["summary"]["merged_skills"] = len(merge_data.get("merges", []))
    
    # 加载黄金路径绑定
    gp_file = reports_dir / "GOLDEN_PATH_BINDING.json"
    if gp_file.exists():
        with open(gp_file, 'r', encoding='utf-8') as f:
            gp_data = json.load(f)
            
            # 检查受影响的黄金路径
            frozen_skills = []
            if freeze_file.exists():
                with open(freeze_file, 'r', encoding='utf-8') as ff:
                    fd = json.load(ff)
                    frozen_skills = [s["skill_name"] for s in fd.get("frozen_skills", [])]
            
            skill_to_gp = gp_data.get("skill_to_golden_path", {})
            for skill in frozen_skills:
                if skill in skill_to_gp:
                    affected_paths = skill_to_gp[skill]
                    results["impacts"].append({
                        "skill": skill,
                        "type": "frozen",
                        "affected_paths": affected_paths
                    })
                    results["summary"]["affected_golden_paths"] += len(affected_paths)
    
    return results

def main():
    try:
        from infrastructure.path_resolver import get_project_root
        workspace = str(get_project_root())
    except ImportError:
        workspace = "."
    results = analyze_impact(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "route_impact_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"路由影响分析完成:")
    print(f"  冻结技能: {results['summary']['frozen_skills']}")
    print(f"  删除技能: {results['summary']['deleted_skills']}")
    print(f"  合并技能: {results['summary']['merged_skills']}")
    print(f"  受影响黄金路径: {results['summary']['affected_golden_paths']}")

if __name__ == "__main__":
    main()
