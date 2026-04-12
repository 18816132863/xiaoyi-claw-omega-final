#!/usr/bin/env python3
"""
generate_architecture_display.py - 生成实时架构展示页

职责:
1. 读取 workspace 目录
2. 应用 ignore 规则（排除 backup/repo/site-packages 等）
3. 生成 architecture_inventory.json
4. 渲染 architecture_display_live.md

统计口径:
- md_only: 仅统计 Markdown 文档数（面向用户展示）
- all_files: 统计所有文件数（技术排查用）
"""

import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from infrastructure.path_resolver import get_project_root

# 排除规则 - 这些目录不参与架构展示统计
IGNORE_DIRS = {
    'node_modules',
    '.git',
    '__pycache__',
    '.pytest_cache',
    '*.egg-info',
    'full-architecture-backup',  # 备份目录
    'repo',                       # 镜像/仓库
    'venv',
    '.venv',
    'site-packages',
    'include',
    'bin',
    'cache',
    '.cache',
    'dist',
    'build',
    '*.pyc',
    '*.log',
    '*.tmp',
}

# 展示域 - 只统计这些目录
DISPLAY_DOMAINS = [
    'core',
    'intelligence',
    'execution',
    'control',
    'evolution_lab',
    'platform',
    'resilience',
    'business',
    'skills',
    'memory',
]

def should_ignore(path: str) -> bool:
    """检查路径是否应该被忽略"""
    path_str = str(path)
    for ignore in IGNORE_DIRS:
        if ignore.startswith('*'):
            # 通配符匹配
            if path_str.endswith(ignore[1:]):
                return True
        elif ignore in path_str.split(os.sep):
            return True
    return False

def count_files(directory: Path, extension: str = None) -> int:
    """统计目录中的文件数"""
    count = 0
    for root, dirs, files in os.walk(directory):
        # 过滤忽略目录
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        
        for f in files:
            if should_ignore(os.path.join(root, f)):
                continue
            if extension is None or f.endswith(extension):
                count += 1
    return count

def count_md_files(directory: Path) -> int:
    """统计 Markdown 文件数"""
    return count_files(directory, '.md')

def count_all_files(directory: Path) -> int:
    """统计所有文件数"""
    return count_files(directory)

def count_skills(skills_dir: Path) -> dict:
    """统计技能目录"""
    if not skills_dir.exists():
        return {"dirs": 0, "md_files": 0}
    
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not should_ignore(str(d))]
    
    md_count = 0
    for skill_dir in skill_dirs:
        md_count += count_md_files(skill_dir)
    
    return {
        "dirs": len(skill_dirs),
        "md_files": md_count
    }

def generate_inventory(workspace: Path) -> dict:
    """生成库存快照"""
    inventory = {
        "scan_time": datetime.now().isoformat(),
        "workspace": str(workspace),
        "ignore_rules": list(IGNORE_DIRS),
        "statistics": {
            "md_only": {},
            "all_files": {}
        },
        "domains": {},
        "skills": {},
        "root_files": {}
    }
    
    # 统计根目录 MD 文件
    root_md = len([f for f in workspace.glob("*.md") if not should_ignore(str(f))])
    inventory["root_files"]["md_count"] = root_md
    
    # 统计各展示域
    for domain in DISPLAY_DOMAINS:
        domain_path = workspace / domain
        if domain_path.exists():
            md_count = count_md_files(domain_path)
            all_count = count_all_files(domain_path)
            
            inventory["domains"][domain] = {
                "md_count": md_count,
                "all_count": all_count
            }
            inventory["statistics"]["md_only"][domain] = md_count
            inventory["statistics"]["all_files"][domain] = all_count
    
    # 统计技能
    skills_dir = workspace / "skills"
    if skills_dir.exists():
        inventory["skills"] = count_skills(skills_dir)
    
    # 计算总计
    inventory["statistics"]["md_only"]["total"] = sum(inventory["statistics"]["md_only"].values())
    inventory["statistics"]["all_files"]["total"] = sum(inventory["statistics"]["all_files"].values())
    
    return inventory

def render_display_md(inventory: dict) -> str:
    """渲染架构展示 Markdown"""
    scan_time = inventory["scan_time"]
    total_md = inventory["statistics"]["md_only"]["total"]
    skills = inventory.get("skills", {})
    
    md = f"""# 鸽子王智能助手 - 实时架构展示

> **最近扫描时间**: {scan_time}
> **统计口径**: Markdown 文档数（排除 backup/repo/site-packages）
> **排除规则**: full-architecture-backup, repo, site-packages, node_modules, .git

## 📊 架构概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        鸽子王智能助手 V32.0                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    核心层 (Core) - {inventory['domains'].get('core', {}).get('md_count', 0)} 文件                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                智能层 (Intelligence) - {inventory['domains'].get('intelligence', {}).get('md_count', 0)} 文件              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  执行层 (Execution) - {inventory['domains'].get('execution', {}).get('md_count', 0)} 文件                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   控制层 (Control) - {inventory['domains'].get('control', {}).get('md_count', 0)} 文件                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │               进化层 (Evolution Lab) - {inventory['domains'].get('evolution_lab', {}).get('md_count', 0)} 文件             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  平台层 (Platform) - {inventory['domains'].get('platform', {}).get('md_count', 0)} 文件                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                可靠性层 (Resilience) - {inventory['domains'].get('resilience', {}).get('md_count', 0)} 文件                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  业务层 (Business) - {inventory['domains'].get('business', {}).get('md_count', 0)} 文件                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │            技能层 (Skills) - {skills.get('dirs', 0)} 技能 / {skills.get('md_files', 0)} 文件              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📈 统计数据

| 模块 | MD文件数 | 说明 |
|------|----------|------|
| 根目录 | {inventory['root_files']['md_count']} | 核心配置和报告 |
"""
    
    for domain in DISPLAY_DOMAINS:
        if domain in inventory['domains']:
            md_count = inventory['domains'][domain]['md_count']
            md += f"| {domain}/ | {md_count} | 架构模块 |\n"
    
    md += f"| **总计** | **{total_md}** | **全部MD文件** |\n"
    
    md += f"""
## 🔧 技能统计

| 指标 | 数值 |
|------|------|
| 技能目录数 | {skills.get('dirs', 0)} |
| 技能文档数 | {skills.get('md_files', 0)} |

## 📦 版本信息

- **版本**: 32.0.0
- **作者**: 鸽子王
- **ClawHub**: xiaoyi-claw-omega-final
- **技能ID**: k977z2jr14tqanspkysfkk1bhh84hvqw
- **更新时间**: {scan_time}
"""
    
    return md

def main():
    workspace = Path(str(get_project_root()))
    reports_dir = workspace / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    print("=== 生成架构展示 ===")
    print(f"工作目录: {workspace}")
    print(f"排除规则: {len(IGNORE_DIRS)} 项")
    print()
    
    # 生成库存
    print("1. 扫描目录...")
    inventory = generate_inventory(workspace)
    
    # 保存 JSON
    json_file = reports_dir / "architecture_inventory.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    print(f"   库存文件: {json_file}")
    
    # 渲染 MD
    print("2. 渲染展示页...")
    md_content = render_display_md(inventory)
    md_file = workspace / "architecture_display_live.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"   展示文件: {md_file}")
    
    # 输出统计
    print()
    print("=== 统计结果 ===")
    print(f"扫描时间: {inventory['scan_time']}")
    print(f"MD文件总数: {inventory['statistics']['md_only']['total']}")
    print(f"技能目录数: {inventory['skills'].get('dirs', 0)}")
    print(f"技能文档数: {inventory['skills'].get('md_files', 0)}")
    print()
    print("各模块MD文件数:")
    for domain, stats in inventory['domains'].items():
        print(f"  {domain}: {stats['md_count']}")

if __name__ == "__main__":
    main()
