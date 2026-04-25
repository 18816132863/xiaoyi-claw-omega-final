#!/usr/bin/env python3
"""
generate_architecture_display_v4.py - 生成架构展示页（基于执行逻辑优化）

执行逻辑：
用户请求 → 意图识别(智能层) → 技能匹配(执行层) → 执行(执行层) → 安全控制(控制层) → 结果返回(平台层)

优化说明：
1. 技能归入执行层（技能是执行的具体实现）
2. 进化层独立（负责系统自我提升，不参与日常执行）
3. 每层对应执行流程的一个环节
"""

import os
import json
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def load_config():
    config_file = Path(__file__).parent / "architecture_config.json"
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

CONFIG = load_config()
LAYER_MAPPING = CONFIG["mapping_rules"]
MAIN_LAYERS = {layer["key"]: layer for layer in CONFIG["main_architecture"]["layers"]}
INTERNAL_LAYERS = {layer["key"]: layer for layer in CONFIG["internal_detail"]["layers"]}
IGNORE_DIRS = set(CONFIG["ignore_dirs"])
IGNORE_PATTERNS = CONFIG["ignore_patterns"]

def should_ignore(path: str) -> bool:
    path_str = str(path)
    for ignore in IGNORE_DIRS:
        if ignore in path_str.split(os.sep):
            return True
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith('*') and path_str.endswith(pattern[1:]):
            return True
    return False

def count_md_files(directory: Path) -> int:
    count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        for f in files:
            if not should_ignore(os.path.join(root, f)) and f.endswith('.md'):
                count += 1
    return count

def count_skills(skills_dir: Path) -> dict:
    if not skills_dir.exists():
        return {"dir_count": 0, "md_count": 0}
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not should_ignore(str(d))]
    md_count = sum(count_md_files(d) for d in skill_dirs)
    return {"dir_count": len(skill_dirs), "md_count": md_count}

def scan_10_layers(workspace: Path) -> dict:
    return {layer_key: count_md_files(workspace / layer_key) if (workspace / layer_key).exists() else 0
            for layer_key in INTERNAL_LAYERS.keys()}

def aggregate_to_6_layers(raw_counts: dict, skills: dict) -> dict:
    aggregated = {key: 0 for key in MAIN_LAYERS.keys()}
    for layer_key, count in raw_counts.items():
        target = LAYER_MAPPING.get(layer_key, layer_key)
        if target in aggregated:
            aggregated[target] += count
    aggregated["skills_dir_count"] = skills["dir_count"]
    aggregated["skills_md_count"] = skills["md_count"]
    return aggregated

def generate_inventory(workspace: Path) -> dict:
    raw_counts_10 = scan_10_layers(workspace)
    skills = count_skills(workspace / "skills")
    aggregated_counts_6 = aggregate_to_6_layers(raw_counts_10, skills)
    root_md = len([f for f in workspace.glob("*.md") if not should_ignore(str(f))])
    
    inventory = {
        "scan_time": datetime.now().isoformat(),
        "workspace": str(workspace),
        "config_version": CONFIG["version"],
        "main_architecture": {"title": "主架构（6层聚合视图）", "layers": {}},
        "internal_detail": {"title": "统计明细（10层运行视图）", "layers": raw_counts_10},
        "skills": skills,
        "root_files": {"md_count": root_md},
        "ignore_rules": {"dirs": list(IGNORE_DIRS), "patterns": IGNORE_PATTERNS}
    }
    
    for layer_key, layer_info in MAIN_LAYERS.items():
        inventory["main_architecture"]["layers"][layer_key] = {
            "name": layer_info["name"],
            "description": layer_info["description"],
            "md_count": aggregated_counts_6.get(layer_key, 0),
            "aggregates": layer_info["aggregates"],
            "execution_role": layer_info["execution_role"],
            "rationale": layer_info["rationale"]
        }
    
    inventory["main_architecture"]["layers"]["execution"]["skills_dir_count"] = skills["dir_count"]
    inventory["main_architecture"]["layers"]["execution"]["skills_md_count"] = skills["md_count"]
    
    return inventory

def render_main_display(inventory: dict) -> str:
    scan_time = inventory["scan_time"]
    layers = inventory["main_architecture"]["layers"]
    skills = inventory["skills"]
    
    md = f"""# 鸽子王智能助手 - 主架构（基于执行逻辑）

> **最近扫描时间**: {scan_time}
> **统计口径**: Markdown 文档数（排除 backup/repo/site-packages/reports/scripts）
> **架构版本**: 6层主架构 V4.0（执行逻辑优化版）

## 📊 执行流程

```
用户请求 → 意图识别 → 技能匹配 → 执行 → 安全控制 → 结果返回
    ↓          ↓          ↓         ↓         ↓          ↓
  入口      智能层      执行层    执行层    控制层     平台层
```

## 📊 主架构概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        鸽子王智能助手 V32.0                                   │
│                    主架构（6层 - 基于执行逻辑）                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         核心层 (Core) - {layers['core']['md_count']} 文件                           │   │
│  │         系统骨架、身份定义、基础配置 [系统定义]                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         智能层 (Intelligence) - {layers['intelligence']['md_count']} 文件           │   │
│  │         记忆、理解、推理、知识 [意图识别]                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         执行层 (Execution) - {layers['execution']['md_count']} 文件 + {skills['dir_count']}技能   │   │
│  │         工作流、编排、自动化、技能执行 [任务执行]                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         控制层 (Control) - {layers['control']['md_count']} 文件                     │   │
│  │         安全、合规、审计、可靠性 [安全控制]                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         进化层 (Evolution) - {layers['evolution']['md_count']} 文件                 │   │
│  │         学习、优化、实验、升级 [系统进化]                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         平台层 (Platform) - {layers['platform']['md_count']} 文件                   │   │
│  │         API、SDK、市场、业务生态 [结果输出]                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📈 6层主架构统计

| 层级 | MD文件数 | 执行角色 | 说明 | 包含子域 |
|------|----------|----------|------|----------|
| 核心层 | {layers['core']['md_count']} | 系统定义 | 系统骨架、身份定义 | core |
| 智能层 | {layers['intelligence']['md_count']} | 意图识别 | 记忆、理解、推理 | intelligence + memory |
| 执行层 | {layers['execution']['md_count']} | 任务执行 | 工作流、编排、技能执行 | execution + skills |
| 控制层 | {layers['control']['md_count']} | 安全控制 | 安全、合规、审计、可靠性 | control + resilience |
| 进化层 | {layers['evolution']['md_count']} | 系统进化 | 学习、优化、实验、升级 | evolution_lab |
| 平台层 | {layers['platform']['md_count']} | 结果输出 | API、SDK、市场、业务 | platform + business |
| **总计** | **{sum(l['md_count'] for l in layers.values())}** | - | - | - |

## 🔧 技能统计（执行层子项）

| 指标 | 数值 |
|------|------|
| 技能目录数 | {skills['dir_count']} |
| 技能文档数 | {skills['md_count']} |

## 📐 执行逻辑说明

| 执行环节 | 对应层级 | 职责 |
|----------|----------|------|
| 系统定义 | 核心层 | 定义系统本质，不参与执行 |
| 意图识别 | 智能层 | 理解用户意图，检索相关知识 |
| 任务执行 | 执行层 | 技能匹配、工作流编排、任务执行 |
| 安全控制 | 控制层 | 贯穿全流程的安全保障 |
| 系统进化 | 进化层 | 独立于执行流程，负责自我提升 |
| 结果输出 | 平台层 | 对外输出，连接用户和系统 |

## 📦 版本信息

- **版本**: 32.0.0
- **架构版本**: V4.0（执行逻辑优化版）
- **作者**: 鸽子王
- **ClawHub**: xiaoyi-claw-omega-final
- **技能ID**: k977z2jr14tqanspkysfkk1bhh84hvqw
- **更新时间**: {scan_time}

---

## 📋 统计明细（10层运行视图）

<details>
<summary>点击展开 10 层内部明细（开发者模式）</summary>

| 内部层级 | MD文件数 | 归属主层 | 执行角色 |
|----------|----------|----------|----------|
"""
    
    internal = inventory["internal_detail"]["layers"]
    for layer_key, count in internal.items():
        main_layer = LAYER_MAPPING.get(layer_key, layer_key)
        md += f"| {layer_key}/ | {count} | {main_layer} | - |\n"
    
    md += """
</details>

## 📝 排除规则

以下目录不参与架构统计：
- full-architecture-backup（备份）
- repo（镜像）
- site-packages（依赖）
- node_modules, .git, __pycache__
- reports, scripts, _review_pending（非架构文件）
"""
    
    return md

def main():
    workspace = Path(str(get_project_root()))
    reports_dir = workspace / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    print("=== 生成架构展示（基于执行逻辑优化）===")
    print(f"工作目录: {workspace}")
    print(f"配置版本: {CONFIG['version']}")
    print()
    
    print("1. 扫描目录...")
    inventory = generate_inventory(workspace)
    
    json_file = reports_dir / "architecture_inventory.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    print(f"   库存文件: {json_file}")
    
    print("2. 渲染主架构展示页...")
    md_content = render_main_display(inventory)
    md_file = workspace / "architecture_display_live.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"   展示文件: {md_file}")
    
    print()
    print("=== 6层主架构统计（执行逻辑优化版）===")
    for layer_key, layer_data in inventory["main_architecture"]["layers"].items():
        role = layer_data.get('execution_role', '')
        print(f"  {layer_data['name']}: {layer_data['md_count']} 文件 [{role}]")
    
    print()
    print("=== 技能统计（执行层）===")
    print(f"  技能目录数: {inventory['skills']['dir_count']}")
    print(f"  技能文档数: {inventory['skills']['md_count']}")

if __name__ == "__main__":
    main()
