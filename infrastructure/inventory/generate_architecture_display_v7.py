#!/usr/bin/env python3
"""
generate_architecture_display_v7.py - 生成架构展示页（技能自动融合增强版）

核心特性：
1. 新技能自动识别类型并融合到对应层级
2. 未识别类型的技能归入能力层（默认能力库）
3. 支持技能跨层融合
4. 架构自动扩展，无需手动配置
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
DETECTION_RULES = CONFIG["skill_fusion_engine"]["detection_rules"]
DEFAULT_LAYER = CONFIG["skill_fusion_engine"]["default_layer"]
DEFAULT_TYPE = CONFIG["skill_fusion_engine"]["default_type"]
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

def detect_skill_type(skill_name: str) -> tuple:
    """检测技能类型和归属层级"""
    skill_name_lower = skill_name.lower()
    
    for rule in DETECTION_RULES:
        for keyword in rule["keywords"]:
            if keyword in skill_name_lower:
                return rule["skill_type"], rule["target_layer"]
    
    return DEFAULT_TYPE, DEFAULT_LAYER

def count_skills(skills_dir: Path) -> dict:
    """统计技能并自动分类"""
    if not skills_dir.exists():
        return {"dir_count": 0, "md_count": 0, "by_type": {}, "by_layer": {}}
    
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not should_ignore(str(d))]
    md_count = sum(count_md_files(d) for d in skill_dirs)
    
    # 按类型分类
    by_type = {}
    # 按层级分类
    by_layer = {layer: [] for layer in MAIN_LAYERS.keys()}
    
    for skill_dir in skill_dirs:
        skill_type, target_layer = detect_skill_type(skill_dir.name)
        
        # 按类型统计
        if skill_type not in by_type:
            by_type[skill_type] = []
        by_type[skill_type].append(skill_dir.name)
        
        # 按层级统计
        if target_layer in by_layer:
            by_layer[target_layer].append(skill_dir.name)
    
    return {
        "dir_count": len(skill_dirs),
        "md_count": md_count,
        "by_type": by_type,
        "by_layer": by_layer
    }

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
    
    inventory = {
        "scan_time": datetime.now().isoformat(),
        "workspace": str(workspace),
        "config_version": CONFIG["version"],
        "main_architecture": {"title": "主架构（6层动态融合视图）", "layers": {}},
        "internal_detail": {"title": "统计明细（10层运行视图）", "layers": raw_counts_10},
        "skills": skills,
        "fusion_engine": {
            "total_rules": len(DETECTION_RULES),
            "default_layer": DEFAULT_LAYER,
            "default_type": DEFAULT_TYPE
        }
    }
    
    for layer_key, layer_info in MAIN_LAYERS.items():
        layer_skills = skills["by_layer"].get(layer_key, [])
        inventory["main_architecture"]["layers"][layer_key] = {
            "name": layer_info["name"],
            "description": layer_info["description"],
            "md_count": aggregated_counts_6.get(layer_key, 0),
            "aggregates": layer_info["aggregates"],
            "execution_role": layer_info["execution_role"],
            "skill_types": layer_info["skill_types"],
            "fused_skills": layer_skills,
            "fused_count": len(layer_skills),
            "can_fuse": layer_info.get("can_fuse", False)
        }
    
    return inventory

def render_main_display(inventory: dict) -> str:
    scan_time = inventory["scan_time"]
    layers = inventory["main_architecture"]["layers"]
    skills = inventory["skills"]
    
    md = f"""# 鸽子王智能助手 - 主架构（技能自动融合版）

> **最近扫描时间**: {scan_time}
> **架构版本**: 6层主架构 V7.0（技能自动融合版）
> **特性**: 新技能自动识别类型并融合到对应层级

## 📊 执行流程

```
接收请求 → 理解意图 → 匹配技能 → 执行任务 → 安全控制 → 输出结果
    ↓          ↓          ↓          ↓          ↓          ↓
  核心层     智能层     能力层     执行层     控制层     平台层
```

## 📊 主架构概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        鸽子王智能助手 V32.0                                   │
│                    主架构（6层 - 技能自动融合版）                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         核心层 (Core) - {layers['core']['md_count']} 文件                           │   │
│  │         系统骨架、身份定义、基础配置 [不可融合]                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         智能层 (Intelligence) - {layers['intelligence']['md_count']} 文件           │   │
│  │         记忆、理解、推理、知识 + {layers['intelligence']['fused_count']}个融合技能              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         能力层 (Capabilities) - {skills['md_count']}文档 + {layers['capabilities']['fused_count']}个技能       │   │
│  │         文档/数据/开发/网络/图像/音视频/创作/通用 [默认融合层]        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         执行层 (Execution) - {layers['execution']['md_count']} 文件                 │   │
│  │         工作流、编排、自动化 + {layers['execution']['fused_count']}个融合技能                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         控制层 (Control) - {layers['control']['md_count']} 文件                     │   │
│  │         安全、合规、可靠性、进化 + {layers['control']['fused_count']}个融合技能                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         平台层 (Platform) - {layers['platform']['md_count']} 文件                   │   │
│  │         API、SDK、市场、业务 + {layers['platform']['fused_count']}个融合技能                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📈 6层主架构统计

| 层级 | MD文件数 | 融合技能数 | 可融合 | 技能类型 |
|------|----------|------------|--------|----------|
"""
    
    for layer_key, layer_data in layers.items():
        can_fuse = "✅" if layer_data["can_fuse"] else "❌"
        skill_types = ", ".join(layer_data["skill_types"]) if layer_data["skill_types"] else "-"
        md += f"| {layer_data['name']} | {layer_data['md_count']} | {layer_data['fused_count']} | {can_fuse} | {skill_types} |\n"
    
    total_md = sum(l['md_count'] for l in layers.values())
    total_skills = sum(l['fused_count'] for l in layers.values())
    md += f"| **总计** | **{total_md}** | **{total_skills}** | - | - |\n"
    
    md += f"""
## 🔧 技能分类统计（自动识别）

| 技能类型 | 数量 | 归属层级 | 技能列表 |
|----------|------|----------|----------|
"""
    
    for skill_type, skill_list in sorted(skills["by_type"].items()):
        if skill_list:
            # 找到归属层级
            target_layer = DEFAULT_LAYER
            for rule in DETECTION_RULES:
                if rule["skill_type"] == skill_type:
                    target_layer = rule["target_layer"]
                    break
            
            layer_names = {"core": "核心层", "intelligence": "智能层", "capabilities": "能力层",
                          "execution": "执行层", "control": "控制层", "platform": "平台层"}
            layer_name = layer_names.get(target_layer, "能力层")
            
            skills_str = ", ".join(skill_list[:3])
            if len(skill_list) > 3:
                skills_str += f" 等{len(skill_list)}个"
            
            md += f"| {skill_type} | {len(skill_list)} | {layer_name} | {skills_str} |\n"
    
    md += f"""
## 📐 技能自动融合规则

| 技能类型 | 归属层级 | 识别关键词 |
|----------|----------|------------|
| 文档处理 | 能力层 | pdf, docx, pptx, xlsx, markdown, document |
| 数据分析 | 能力层 | data, excel, sql, mongo, elastic, analysis |
| 开发工具 | 能力层 | git, docker, ansible, terraform, javascript |
| 网络服务 | 能力层 | web, scrap, search, api, http, fetch |
| 图像处理 | 能力层 | image, chart, screenshot, photo, visual |
| 音频视频 | 能力层 | audio, video, whisper, subtitle, speech |
| 内容创作 | 能力层 | article, copy, novel, poetry, writer |
| 通讯集成 | 平台层 | email, imsg, linkedin, message, chat |
| 效率工具 | 执行层 | obsidian, cron, productivity, task, automation |
| 市场研究 | 智能层 | market, crypto, stock, news, research |
| AI能力 | 智能层 | ai, llm, gpt, claude, model, neural |
| 手机操控 | 执行层 | phone, mobile, android, ios, app, gui |
| 安全相关 | 控制层 | security, guardian, validator, protect |
| 进化相关 | 控制层 | evolution, upgrade, optimize, improve |
| 通用能力 | 能力层 | 未匹配的其他技能（默认） |

## 🆕 新技能融合说明

当创建或安装新技能时，系统会：

1. **自动识别类型** - 根据技能名称中的关键词识别类型
2. **自动融合层级** - 将技能融合到对应的架构层级
3. **默认归入能力层** - 未识别类型的技能自动归入能力层
4. **支持跨层融合** - 一个技能可同时属于多个层级

## 📦 版本信息

- **版本**: 32.0.0
- **架构版本**: V7.0（技能自动融合版）
- **作者**: 鸽子王
- **更新时间**: {scan_time}

---

## 📋 统计明细（10层运行视图）

<details>
<summary>点击展开 10 层内部明细</summary>

| 内部层级 | MD文件数 | 归属主层 |
|----------|----------|----------|
"""
    
    internal = inventory["internal_detail"]["layers"]
    for layer_key, count in internal.items():
        main_layer = LAYER_MAPPING.get(layer_key, layer_key)
        md += f"| {layer_key}/ | {count} | {main_layer} |\n"
    
    md += """
</details>
"""
    
    return md

def main():
    workspace = Path(str(get_project_root()))
    reports_dir = workspace / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    print("=== 生成架构展示（技能自动融合版）===")
    print(f"配置版本: {CONFIG['version']}")
    print()
    
    inventory = generate_inventory(workspace)
    
    json_file = reports_dir / "architecture_inventory.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    md_content = render_main_display(inventory)
    md_file = workspace / "architecture_display_live.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("=== 6层主架构统计 ===")
    for layer_key, layer_data in inventory["main_architecture"]["layers"].items():
        fused = layer_data['fused_count']
        can_fuse = "可融合" if layer_data["can_fuse"] else "不可融合"
        print(f"  {layer_data['name']}: {layer_data['md_count']} 文件 + {fused} 技能 [{can_fuse}]")
    
    print()
    print("=== 技能分类统计 ===")
    for skill_type, skill_list in sorted(inventory["skills"]["by_type"].items()):
        if skill_list:
            print(f"  {skill_type}: {len(skill_list)} 个")

if __name__ == "__main__":
    main()
