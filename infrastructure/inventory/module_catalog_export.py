#!/usr/bin/env python3
"""
module_catalog_export.py - 导出所有模块清单

最低职责:
- 导出所有模块清单
- 包含 owner、domain、purpose
- 生成 CSV 和 JSON 两种格式

输出: reports/module_catalog.csv, reports/module_catalog.json
"""

import os
import json
import csv
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def get_module_catalog(workspace_path: str) -> list:
    """生成模块目录"""
    modules = []
    workspace = Path(workspace_path)
    
    # 定义域映射
    domain_map = {
        "core": "核心层",
        "execution": "执行层",
        "control": "控制层",
        "resilience": "韧性层",
        "intelligence": "智能层",
        "platform": "平台层",
        "business": "商业层",
        "evolution_lab": "进化实验室",
        "skills": "技能库",
        "reports": "报告目录"
    }
    
    for domain_dir in workspace.iterdir():
        if domain_dir.is_dir() and not domain_dir.name.startswith('_'):
            domain = domain_map.get(domain_dir.name, "其他")
            
            # 遍历子目录
            for module_dir in domain_dir.iterdir():
                if module_dir.is_dir():
                    module_info = {
                        "module_name": module_dir.name,
                        "domain": domain,
                        "path": str(module_dir.relative_to(workspace)),
                        "owner": "待分配",
                        "purpose": "",
                        "file_count": len(list(module_dir.rglob("*.*"))),
                        "last_modified": datetime.fromtimestamp(module_dir.stat().st_mtime).isoformat()
                    }
                    
                    # 尝试读取 README 或 SKILL.md 获取 purpose
                    readme = module_dir / "README.md"
                    skill_md = module_dir / "SKILL.md"
                    
                    if readme.exists():
                        with open(readme, 'r', encoding='utf-8') as f:
                            first_line = f.readline()
                            module_info["purpose"] = first_line.strip("# \n")[:100]
                    elif skill_md.exists():
                        with open(skill_md, 'r', encoding='utf-8') as f:
                            first_line = f.readline()
                            module_info["purpose"] = first_line.strip("# \n")[:100]
                    
                    modules.append(module_info)
    
    return modules

def main():
    workspace = str(get_project_root())
    modules = get_module_catalog(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存 JSON
    json_file = output_dir / "module_catalog.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            "export_time": datetime.now().isoformat(),
            "total_modules": len(modules),
            "modules": modules
        }, f, indent=2, ensure_ascii=False)
    
    # 保存 CSV
    csv_file = output_dir / "module_catalog.csv"
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["module_name", "domain", "path", "owner", "purpose", "file_count"])
        writer.writeheader()
        writer.writerows(modules)
    
    print(f"模块目录已导出: {len(modules)} 个模块")
    print(f"JSON: {json_file}")
    print(f"CSV: {csv_file}")

if __name__ == "__main__":
    main()
