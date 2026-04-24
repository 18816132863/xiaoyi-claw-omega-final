#!/usr/bin/env python3
"""
skill_catalog_export.py - 导出所有技能清单

最低职责:
- 导出所有技能清单
- 包含 maturity、owner、decision
- 生成 CSV 和 JSON 两种格式

输出: reports/skill_catalog.csv, reports/skill_catalog.json
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def get_skill_catalog(workspace_path: str) -> list:
    """生成技能目录"""
    skills = []
    workspace = Path(workspace_path)
    skills_dir = workspace / "skills"
    
    if not skills_dir.exists():
        return skills
    
    # 分类定义
    categories = {
        "search": "搜索类",
        "analysis": "分析类",
        "generation": "生成类",
        "automation": "自动化类",
        "adapter": "适配器",
        "processor": "处理器",
        "persona": "人格",
        "meta_tool": "元工具"
    }
    
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith('_'):
            skill_info = {
                "skill_name": skill_dir.name,
                "category": "unknown",
                "maturity": "ga",
                "owner": "待分配",
                "decision": "keep",
                "golden_path": "",
                "file_count": len(list(skill_dir.rglob("*.*"))),
                "has_skill_md": (skill_dir / "SKILL.md").exists(),
                "last_modified": datetime.fromtimestamp(skill_dir.stat().st_mtime).isoformat()
            }
            
            # 尝试读取 SKILL.md 获取更多信息
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                with open(skill_md, 'r', encoding='utf-8') as f:
                    content = f.read(500)
                    # 简单提取描述
                    for line in content.split('\n')[:10]:
                        if line.startswith('#') and not line.startswith('##'):
                            skill_info["description"] = line.strip("# \n")[:100]
                            break
            
            # 根据名称推断分类
            name_lower = skill_dir.name.lower()
            if any(x in name_lower for x in ['search', 'find', 'query']):
                skill_info["category"] = "search"
            elif any(x in name_lower for x in ['analysis', 'analyze', 'excel', 'stock', 'data']):
                skill_info["category"] = "analysis"
            elif any(x in name_lower for x in ['writer', 'generator', 'gen', 'create']):
                skill_info["category"] = "generation"
            elif any(x in name_lower for x in ['ansible', 'terraform', 'docker', 'git', 'cron']):
                skill_info["category"] = "automation"
            elif any(x in name_lower for x in ['api', 'imap', 'discord', 'spotify', 'maps']):
                skill_info["category"] = "adapter"
            elif any(x in name_lower for x in ['pdf', 'docx', 'pptx', 'ocr', 'image', 'video']):
                skill_info["category"] = "processor"
            elif any(x in name_lower for x in ['architect', 'advisor', 'scientist', 'security', 'minds']):
                skill_info["category"] = "persona"
            elif any(x in name_lower for x in ['skill', 'memory', 'command', 'install', 'creator']):
                skill_info["category"] = "meta_tool"
            
            skills.append(skill_info)
    
    return skills

def main():
    workspace = str(get_project_root())
    skills = get_skill_catalog(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存 JSON
    json_file = output_dir / "skill_catalog.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "export_time": datetime.now().isoformat(),
            "total_skills": len(skills),
            "skills": skills
        }, f, indent=2, ensure_ascii=False)
    
    # 保存 CSV
    csv_file = output_dir / "skill_catalog.csv"
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["skill_name", "category", "maturity", "owner", "decision", "golden_path"])
        writer.writeheader()
        writer.writerows(skills)
    
    print(f"技能目录已导出: {len(skills)} 个技能")
    print(f"JSON: {json_file}")
    print(f"CSV: {csv_file}")

if __name__ == "__main__":
    main()
