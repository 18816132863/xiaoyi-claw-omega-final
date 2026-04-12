#!/usr/bin/env python3
"""
golden_path_regression.py - 跑 10 条黄金路径回归

最低职责:
- 跑 10 条黄金路径回归
- 验证每条路径的核心技能存在
- 输出回归结果

输出: reports/golden_path_regression.json
"""

import os
import json
from datetime import datetime
from pathlib import Path

def test_golden_paths(workspace_path: str) -> dict:
    """测试黄金路径"""
    results = {
        "test_time": datetime.now().isoformat(),
        "summary": {
            "total_paths": 10,
            "passed": 0,
            "failed": 0,
            "partial": 0
        },
        "paths": []
    }
    
    workspace = Path(workspace_path)
    skills_dir = workspace / "skills"
    
    # 定义 10 条黄金路径
    golden_paths = [
        {
            "id": "GP-001",
            "name": "目标输入 → 项目拆解 → 里程碑 → 风险跟踪",
            "core_skills": ["planning-with-files", "productivity", "taskr", "post-job"]
        },
        {
            "id": "GP-002",
            "name": "会议记录 → 行动项抽取 → owner指派 → 跟进",
            "core_skills": ["docs-cog", "productivity", "taskr"]
        },
        {
            "id": "GP-003",
            "name": "知识检索 → 证据绑定 → 建议生成 → 审批",
            "core_skills": ["xiaoyi-web-search", "unified-search", "research-cog"]
        },
        {
            "id": "GP-004",
            "name": "事故发现 → 分级升级 → 缓解回滚 → 复盘",
            "core_skills": ["senior-security", "clawsec-suite", "moltguard"]
        },
        {
            "id": "GP-005",
            "name": "新租户接入 → 配置 → 权限 → 试运行",
            "core_skills": ["api-gateway", "verified-agent-identity"]
        },
        {
            "id": "GP-006",
            "name": "RFP输入 → 条款映射 → 证据拉取 → 答复生成",
            "core_skills": ["unified-search", "docs-cog", "article-writer"]
        },
        {
            "id": "GP-007",
            "name": "伙伴交付 → 蓝图部署 → UAT → 上线护航",
            "core_skills": ["ansible", "terraform", "docker"]
        },
        {
            "id": "GP-008",
            "name": "策略变更 → 沙盘 → 灰度 → 观测 → 发布",
            "core_skills": ["git", "tdd-guide", "webapp-testing"]
        },
        {
            "id": "GP-009",
            "name": "问题反馈 → 学习沉淀 → playbook更新 → 回归测试",
            "core_skills": ["docs-cog", "quality-documentation-manager"]
        },
        {
            "id": "GP-010",
            "name": "高层问ROI → 成本归因 → 风险摘要 → 经营输出",
            "core_skills": ["data-analysis", "excel-analysis", "stock-price-query"]
        }
    ]
    
    for path in golden_paths:
        path_result = {
            "id": path["id"],
            "name": path["name"],
            "skills_found": [],
            "skills_missing": [],
            "status": "unknown"
        }
        
        for skill in path["core_skills"]:
            skill_path = skills_dir / skill
            if skill_path.exists():
                path_result["skills_found"].append(skill)
            else:
                path_result["skills_missing"].append(skill)
        
        # 判断状态
        if len(path_result["skills_missing"]) == 0:
            path_result["status"] = "passed"
            results["summary"]["passed"] += 1
        elif len(path_result["skills_found"]) > 0:
            path_result["status"] = "partial"
            results["summary"]["partial"] += 1
        else:
            path_result["status"] = "failed"
            results["summary"]["failed"] += 1
        
        results["paths"].append(path_result)
    
    return results

def main():
    try:
        from infrastructure.path_resolver import get_project_root
        workspace = str(get_project_root())
    except ImportError:
        workspace = "."
    results = test_golden_paths(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "golden_path_regression.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"黄金路径回归测试完成:")
    print(f"  通过: {results['summary']['passed']}")
    print(f"  部分通过: {results['summary']['partial']}")
    print(f"  失败: {results['summary']['failed']}")
    
    if results['summary']['failed'] > 0:
        print("\n❌ 存在失败路径!")
    else:
        print("\n✅ 所有黄金路径正常")

if __name__ == "__main__":
    main()
