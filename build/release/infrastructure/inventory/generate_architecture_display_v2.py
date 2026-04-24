#!/usr/bin/env python3
"""
generate_architecture_display_v2.py - 生成架构展示页（6层主架构 + 10层明细）

最高指令：
- 主架构固定为 6 层
- 10 层到 6 层的映射关系固定，不允许人工临时改归属
- 主页面只展示 6 层聚合视图
- 10 层明细只在开发者模式/调试信息中展示
"""

import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from infrastructure.path_resolver import get_project_root

# 加载配置
def load_config():
    config_file = Path(__file__).parent / "architecture_config.json"
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

CONFIG = load_config()

# 10层到6层的映射关系（固定，不允许修改）
LAYER_MAPPING = CONFIG["mapping_rules"]

# 6层主架构定义
MAIN_LAYERS = {layer["key"]: layer for layer in CONFIG["main_architecture"]["layers"]}

# 10层内部明细定义
INTERNAL_LAYERS = {layer["key"]: layer for layer in CONFIG["internal_detail"]["layers"]}

# 排除目录
IGNORE_DIRS = set(CONFIG["ignore_dirs"])
IGNORE_PATTERNS = CONFIG["ignore_patterns"]

def should_ignore(path: str) -> bool:
    """检查路径是否应该被忽略"""
    path_str = str(path)
    for ignore in IGNORE_DIRS:
        if ignore in path_str.split(os.sep):
            return True
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith('*'):
            if path_str.endswith(pattern[1:]):
                return True
    return False

def count_md_files(directory: Path) -> int:
    """统计 Markdown 文件数"""
    count = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
        for f in files:
            if should_ignore(os.path.join(root, f)):
                continue
            if f.endswith('.md'):
                count += 1
    return count

def count_skills(skills_dir: Path) -> dict:
    """统计技能目录（分开定义）"""
    if not skills_dir.exists():
        return {"dir_count": 0, "md_count": 0}
    
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not should_ignore(str(d))]
    
    md_count = 0
    for skill_dir in skill_dirs:
        md_count += count_md_files(skill_dir)
    
    return {
        "dir_count": len(skill_dirs),
        "md_count": md_count
    }

def scan_10_layers(workspace: Path) -> dict:
    """扫描10层内部明细"""
    raw_counts = {}
    
    for layer_key in INTERNAL_LAYERS.keys():
        layer_path = workspace / layer_key
        if layer_path.exists():
            raw_counts[layer_key] = count_md_files(layer_path)
        else:
            raw_counts[layer_key] = 0
    
    return raw_counts

def aggregate_to_6_layers(raw_counts: dict, skills: dict) -> dict:
    """将10层聚合为6层主架构"""
    aggregated = {key: 0 for key in MAIN_LAYERS.keys()}
    
    for layer_key, count in raw_counts.items():
        if layer_key in LAYER_MAPPING:
            # 映射到对应的6层
            target = LAYER_MAPPING[layer_key]
            aggregated[target] += count
        elif layer_key in aggregated:
            # 直接属于6层
            aggregated[layer_key] += count
    
    # 技能层单独统计（属于执行层，但不混入MD计数）
    aggregated["skills_dir_count"] = skills["dir_count"]
    aggregated["skills_md_count"] = skills["md_count"]
    
    return aggregated

def generate_inventory(workspace: Path) -> dict:
    """生成完整库存"""
    # 扫描10层
    raw_counts_10 = scan_10_layers(workspace)
    
    # 统计技能
    skills_dir = workspace / "skills"
    skills = count_skills(skills_dir)
    
    # 聚合为6层
    aggregated_counts_6 = aggregate_to_6_layers(raw_counts_10, skills)
    
    # 根目录文件（不混入主架构）
    root_md = len([f for f in workspace.glob("*.md") if not should_ignore(str(f))])
    
    inventory = {
        "scan_time": datetime.now().isoformat(),
        "workspace": str(workspace),
        "config_version": CONFIG["version"],
        
        # 6层主架构（前台展示）
        "main_architecture": {
            "title": "主架构（6层聚合视图）",
            "layers": {}
        },
        
        # 10层内部明细（开发者模式）
        "internal_detail": {
            "title": "统计明细（10层运行视图）",
            "layers": raw_counts_10
        },
        
        # 技能统计（分开定义）
        "skills": skills,
        
        # 根目录（不混入主架构）
        "root_files": {
            "md_count": root_md,
            "note": "根目录散落报告文件不混入主架构层统计"
        },
        
        # 排除规则
        "ignore_rules": {
            "dirs": list(IGNORE_DIRS),
            "patterns": IGNORE_PATTERNS
        }
    }
    
    # 构建6层数据
    for layer_key, layer_info in MAIN_LAYERS.items():
        inventory["main_architecture"]["layers"][layer_key] = {
            "name": layer_info["name"],
            "description": layer_info["description"],
            "md_count": aggregated_counts_6.get(layer_key, 0),
            "aggregates": layer_info["aggregates"]
        }
    
    # 添加技能统计到执行层
    inventory["main_architecture"]["layers"]["execution"]["skills_dir_count"] = skills["dir_count"]
    inventory["main_architecture"]["layers"]["execution"]["skills_md_count"] = skills["md_count"]
    
    return inventory

def render_main_display(inventory: dict) -> str:
    """渲染6层主架构展示页"""
    scan_time = inventory["scan_time"]
    layers = inventory["main_architecture"]["layers"]
    skills = inventory["skills"]
    
    md = f"""# 鸽子王智能助手 - 主架构（6层聚合视图）

> **最近扫描时间**: {scan_time}
> **统计口径**: Markdown 文档数（排除 backup/repo/site-packages/reports/scripts）
> **架构版本**: 6层主架构（10层明细见开发者模式）

## 📊 主架构概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        鸽子王智能助手 V32.0                                   │
│                          主架构（6层聚合视图）                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         核心层 (Core) - {layers['core']['md_count']} 文件                           │   │
│  │         系统骨架与身份定义                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         智能层 (Intelligence) - {layers['intelligence']['md_count']} 文件           │   │
│  │         记忆、检索、推理、知识（含 memory）                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         执行层 (Execution) - {layers['execution']['md_count']} 文件                 │   │
│  │         工作流、编排、自动化（含 skills: {skills['dir_count']}技能/{skills['md_count']}文档）│   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         控制层 (Control) - {layers['control']['md_count']} 文件                     │   │
│  │         安全、合规、审计、可靠性（含 resilience）                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         进化层 (Evolution Lab) - {layers['evolution_lab']['md_count']} 文件         │   │
│  │         优化、升级、学习、实验                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         平台层 (Platform) - {layers['platform']['md_count']} 文件                   │   │
│  │         API、SDK、市场、业务生态（含 business）                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📈 6层主架构统计

| 层级 | MD文件数 | 说明 | 包含子域 |
|------|----------|------|----------|
| 核心层 | {layers['core']['md_count']} | 系统骨架与身份定义 | core |
| 智能层 | {layers['intelligence']['md_count']} | 记忆、检索、推理、知识 | intelligence + memory |
| 执行层 | {layers['execution']['md_count']} | 工作流、编排、自动化 | execution + skills |
| 控制层 | {layers['control']['md_count']} | 安全、合规、审计、可靠性 | control + resilience |
| 进化层 | {layers['evolution_lab']['md_count']} | 优化、升级、学习、实验 | evolution_lab |
| 平台层 | {layers['platform']['md_count']} | API、SDK、市场、业务生态 | platform + business |
| **总计** | **{sum(l['md_count'] for l in layers.values())}** | - | - |

## 🔧 技能统计（执行层子项）

| 指标 | 数值 |
|------|------|
| 技能目录数 | {skills['dir_count']} |
| 技能文档数 | {skills['md_count']} |

## 📦 版本信息

- **版本**: 32.0.0
- **作者**: 鸽子王
- **ClawHub**: xiaoyi-claw-omega-final
- **技能ID**: k977z2jr14tqanspkysfkk1bhh84hvqw
- **更新时间**: {scan_time}

---

## 📋 统计明细（10层运行视图）

<details>
<summary>点击展开 10 层内部明细（开发者模式）</summary>

| 内部层级 | MD文件数 | 归属主层 |
|----------|----------|----------|
"""
    
    # 添加10层明细
    internal = inventory["internal_detail"]["layers"]
    for layer_key, count in internal.items():
        main_layer = LAYER_MAPPING.get(layer_key, layer_key)
        md += f"| {layer_key}/ | {count} | {main_layer} |\n"
    
    md += f"""
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
    
    print("=== 生成架构展示（6层主架构 + 10层明细）===")
    print(f"工作目录: {workspace}")
    print(f"配置版本: {CONFIG['version']}")
    print()
    
    # 生成库存
    print("1. 扫描目录...")
    inventory = generate_inventory(workspace)
    
    # 保存 JSON
    json_file = reports_dir / "architecture_inventory.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    print(f"   库存文件: {json_file}")
    
    # 渲染主架构展示页
    print("2. 渲染主架构展示页...")
    md_content = render_main_display(inventory)
    md_file = workspace / "architecture_display_live.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"   展示文件: {md_file}")
    
    # 输出统计
    print()
    print("=== 6层主架构统计 ===")
    for layer_key, layer_data in inventory["main_architecture"]["layers"].items():
        print(f"  {layer_data['name']}: {layer_data['md_count']} 文件")
    
    print()
    print("=== 技能统计 ===")
    print(f"  技能目录数: {inventory['skills']['dir_count']}")
    print(f"  技能文档数: {inventory['skills']['md_count']}")
    
    print()
    print("=== 10层内部明细 ===")
    for layer_key, count in inventory["internal_detail"]["layers"].items():
        main = LAYER_MAPPING.get(layer_key, layer_key)
        print(f"  {layer_key}: {count} → {main}")

if __name__ == "__main__":
    main()
