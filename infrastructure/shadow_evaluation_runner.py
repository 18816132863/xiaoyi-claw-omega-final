#!/usr/bin/env python3
"""
shadow_evaluation_runner.py - 让 candidate/beta 技能跑 shadow 模式

最低职责:
- 让 candidate / beta 技能跑 shadow 模式
- 收集评估数据
- 输出评估结果

输出: reports/shadow_evaluation_results.json
"""

import os
import json
from datetime import datetime
from pathlib import Path

def run_shadow_evaluation(workspace_path: str) -> dict:
    """运行影子评估"""
    results = {
        "evaluation_time": datetime.now().isoformat(),
        "summary": {
            "total_evaluated": 0,
            "passed": 0,
            "failed": 0,
            "pending": 0
        },
        "evaluations": []
    }
    
    workspace = Path(workspace_path)
    skills_dir = workspace / "skills"
    
    # 查找需要 shadow 评估的技能
    # 这里简化处理，实际需要根据成熟度判断
    candidate_skills = []
    
    # 遍历技能目录
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith('_'):
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    # 检查是否标记为 candidate 或 beta
                    if "candidate" in content.lower() or "beta" in content.lower():
                        candidate_skills.append(skill_dir.name)
    
    # 模拟评估
    for skill_name in candidate_skills:
        evaluation = {
            "skill_name": skill_name,
            "mode": "shadow",
            "runs": 0,
            "success_rate": 0,
            "status": "pending"
        }
        
        # 实际需要运行 shadow 测试
        # 这里简化处理
        evaluation["status"] = "pending"
        results["summary"]["pending"] += 1
        
        results["evaluations"].append(evaluation)
        results["summary"]["total_evaluated"] += 1
    
    return results

def main():
    from infrastructure.path_resolver import get_project_root
    workspace = get_project_root()
    results = run_shadow_evaluation(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "shadow_evaluation_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"影子评估完成:")
    print(f"  评估技能数: {results['summary']['total_evaluated']}")
    print(f"  通过: {results['summary']['passed']}")
    print(f"  待定: {results['summary']['pending']}")

if __name__ == "__main__":
    main()
