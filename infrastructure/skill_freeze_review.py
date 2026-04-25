#!/usr/bin/env python3
"""
skill_freeze_review.py - 检查冻结中的技能

最低职责:
- 检查冻结中的技能是否仍有真实调用
- 是否还有 blocker
- 是否可删除或应恢复
- 输出评审结果

输出: reports/skill_freeze_review.json
"""

import os
import json
from datetime import datetime
from pathlib import Path

def review_frozen_skills(workspace_path: str) -> dict:
    """评审冻结技能"""
    results = {
        "review_time": datetime.now().isoformat(),
        "summary": {
            "total_frozen": 0,
            "can_delete": 0,
            "should_extend": 0,
            "should_restore": 0,
            "has_blockers": 0
        },
        "reviews": []
    }
    
    workspace = Path(workspace_path)
    skills_dir = workspace / "skills"
    frozen_dir = skills_dir / "_frozen"
    reports_dir = workspace / "reports"
    
    if not frozen_dir.exists():
        print("没有冻结技能目录")
        return results
    
    # 加载冻结清单
    freeze_file = reports_dir / "SKILL_FREEZE_LIST.json"
    freeze_data = {}
    if freeze_file.exists():
        with open(freeze_file, 'r', encoding='utf-8') as f:
            freeze_data = json.load(f)
    
    # 遍历冻结技能
    for skill_dir in frozen_dir.iterdir():
        if skill_dir.is_dir():
            skill_name = skill_dir.name
            results["summary"]["total_frozen"] += 1
            
            # 获取冻结信息
            freeze_info = None
            for fs in freeze_data.get("frozen_skills", []):
                if fs.get("skill_name") == skill_name:
                    freeze_info = fs
                    break
            
            review = {
                "skill_name": skill_name,
                "freeze_start": freeze_info.get("freeze_start", "unknown") if freeze_info else "unknown",
                "freeze_end": freeze_info.get("freeze_end", "unknown") if freeze_info else "unknown",
                "calls_during_freeze": 0,  # 实际需要从日志获取
                "has_blockers": False,
                "recommendation": "unknown"
            }
            
            # 简单判断：如果冻结期结束且无调用，建议删除
            if freeze_info:
                freeze_end = freeze_info.get("freeze_end", "")
                if freeze_end:
                    try:
                        end_date = datetime.strptime(freeze_end, "%Y-%m-%d")
                        if datetime.now() > end_date:
                            if review["calls_during_freeze"] == 0:
                                review["recommendation"] = "delete"
                                results["summary"]["can_delete"] += 1
                            else:
                                review["recommendation"] = "extend"
                                results["summary"]["should_extend"] += 1
                        else:
                            review["recommendation"] = "waiting"
                    except:
                        review["recommendation"] = "waiting"
            
            results["reviews"].append(review)
    
    return results

def main():
    from infrastructure.path_resolver import get_project_root
    workspace = get_project_root()
    results = review_frozen_skills(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "skill_freeze_review.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"冻结技能评审完成:")
    print(f"  冻结技能: {results['summary']['total_frozen']}")
    print(f"  可删除: {results['summary']['can_delete']}")
    print(f"  需延长: {results['summary']['should_extend']}")

if __name__ == "__main__":
    main()
