#!/usr/bin/env python3
"""
skill_maturity_review.py - 刷新每个技能的成熟度阶段

最低职责:
- 刷新每个技能的成熟度阶段
- 根据使用数据更新成熟度
- 输出评审结果

输出: reports/skill_maturity_review.json
"""

import os
import json
from datetime import datetime
from pathlib import Path

def review_maturity(workspace_path: str) -> dict:
    """评审技能成熟度"""
    results = {
        "review_time": datetime.now().isoformat(),
        "summary": {
            "total_skills": 0,
            "core": 0,
            "ga": 0,
            "beta": 0,
            "candidate": 0,
            "incubating": 0,
            "deprecated": 0,
            "frozen": 0
        },
        "skills": []
    }
    
    workspace = Path(workspace_path)
    skills_dir = workspace / "skills"
    
    # 加载决策日志
    reports_dir = workspace / "reports"
    decision_file = reports_dir / "SKILL_DECISION_LOG.csv"
    decisions = {}
    
    if decision_file.exists():
        with open(decision_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                header = lines[0].strip().split(',')
                for line in lines[1:]:
                    values = line.strip().split(',')
                    if len(values) >= 5:
                        skill_name = values[1]
                        decision = values[4]
                        decisions[skill_name] = decision
    
    # 遍历技能目录
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_name = skill_dir.name
            
            # 跳过特殊目录
            if skill_name.startswith('_'):
                if skill_name == "_frozen":
                    results["summary"]["frozen"] = len(list(skill_dir.iterdir()))
                continue
            
            results["summary"]["total_skills"] += 1
            
            # 确定成熟度
            maturity = "ga"  # 默认
            
            if skill_name in decisions:
                decision = decisions[skill_name]
                if decision == "keep_core":
                    maturity = "core"
                elif decision == "freeze":
                    maturity = "frozen"
                elif decision == "deprecate":
                    maturity = "deprecated"
            
            # 检查是否有 SKILL.md
            has_skill_md = (skill_dir / "SKILL.md").exists()
            
            skill_info = {
                "skill_name": skill_name,
                "maturity": maturity,
                "has_skill_md": has_skill_md,
                "file_count": len(list(skill_dir.rglob("*.*"))),
                "decision": decisions.get(skill_name, "unknown")
            }
            
            results["skills"].append(skill_info)
            results["summary"][maturity] = results["summary"].get(maturity, 0) + 1
    
    return results

def main():
    from infrastructure.path_resolver import get_project_root
    workspace = get_project_root()
    results = review_maturity(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "skill_maturity_review.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"技能成熟度评审完成:")
    print(f"  总技能数: {results['summary']['total_skills']}")
    print(f"  核心: {results['summary']['core']}")
    print(f"  正式: {results['summary']['ga']}")
    print(f"  冻结: {results['summary']['frozen']}")

if __name__ == "__main__":
    main()
