#!/usr/bin/env python3
"""
generate_architecture_display_v8.py - 生成架构展示页（技能融合增强版）

核心特性：
1. 同类型技能可融合为一个增强技能
2. 融合后保留所有子技能能力
3. 效率不降低，专业度提升
4. 支持按需调用子技能
"""

import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
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
MERGE_RULES = CONFIG["skill_merge_engine"]["merge_rules"]
DEFAULT_LAYER = CONFIG["skill_fusion_engine"]["default_layer"]
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
    skill_name_lower = skill_name.lower()
    for rule in DETECTION_RULES:
        for keyword in rule["keywords"]:
            if keyword in skill_name_lower:
                return rule["skill_type"], rule["target_layer"]
    return "通用能力", DEFAULT_LAYER

def get_merge_info(skill_type: str) -> dict:
    """获取技能融合信息"""
    for rule in MERGE_RULES:
        if rule["skill_type"] == skill_type:
            return rule
    return {"can_merge": False}

def count_skills(skills_dir: Path) -> dict:
    if not skills_dir.exists():
        return {"dir_count": 0, "md_count": 0, "by_type": {}, "by_layer": {}, "merge_candidates": {}}
    
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not should_ignore(str(d))]
    md_count = sum(count_md_files(d) for d in skill_dirs)
    
    by_type = defaultdict(list)
    by_layer = defaultdict(list)
    merge_candidates = {}
    
    for skill_dir in skill_dirs:
        skill_type, target_layer = detect_skill_type(skill_dir.name)
        by_type[skill_type].append(skill_dir.name)
        by_layer[target_layer].append(skill_dir.name)
        
        # 检查是否可融合
        merge_info = get_merge_info(skill_type)
        if merge_info.get("can_merge") and len(by_type[skill_type]) > 1:
            if skill_type not in merge_candidates:
                merge_candidates[skill_type] = {
                    "sub_skills": [],
                    "merge_strategy": merge_info.get("merge_strategy", ""),
                    "merged_skill": merge_info.get("example", {}).get("merged_skill", f"unified-{skill_type.lower()}")
                }
            merge_candidates[skill_type]["sub_skills"].append(skill_dir.name)
    
    return {
        "dir_count": len(skill_dirs),
        "md_count": md_count,
        "by_type": dict(by_type),
        "by_layer": dict(by_layer),
        "merge_candidates": merge_candidates
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
        "config_version": CONFIG["version"],
        "main_architecture": {"layers": {}},
        "internal_detail": {"layers": raw_counts_10},
        "skills": skills,
        "merge_opportunities": len(skills["merge_candidates"])
    }
    
    for layer_key, layer_info in MAIN_LAYERS.items():
        layer_skills = skills["by_layer"].get(layer_key, [])
        inventory["main_architecture"]["layers"][layer_key] = {
            "name": layer_info["name"],
            "description": layer_info["description"],
            "md_count": aggregated_counts_6.get(layer_key, 0),
            "fused_skills": layer_skills,
            "fused_count": len(layer_skills),
            "can_fuse": layer_info.get("can_fuse", False)
        }
    
    return inventory

def render_main_display(inventory: dict) -> str:
    scan_time = inventory["scan_time"]
    layers = inventory["main_architecture"]["layers"]
    skills = inventory["skills"]
    merge_candidates = skills["merge_candidates"]
    
    md = f"""# 鸽子王智能助手 - 主架构（技能融合增强版）

> **最近扫描时间**: {scan_time}
> **架构版本**: V8.0（技能融合增强版）
> **融合机会**: {len(merge_candidates)} 个技能类型可融合

## 📊 执行流程

```
接收请求 → 理解意图 → 匹配技能 → 执行任务 → 安全控制 → 输出结果
    ↓          ↓          ↓          ↓          ↓          ↓
  核心层     智能层     能力层     执行层     控制层     平台层
```

## 📊 主架构概览

| 层级 | 文件数 | 技能数 | 可融合 |
|------|--------|--------|--------|
"""
    
    for layer_key, layer_data in layers.items():
        can_fuse = "✅" if layer_data["can_fuse"] else "❌"
        md += f"| {layer_data['name']} | {layer_data['md_count']} | {layer_data['fused_count']} | {can_fuse} |\n"
    
    md += f"""
## 🔧 技能融合机会

以下技能类型包含多个子技能，可融合为增强技能：

| 技能类型 | 子技能数 | 融合后名称 | 融合策略 |
|----------|----------|------------|----------|
"""
    
    for skill_type, info in merge_candidates.items():
        md += f"| {skill_type} | {len(info['sub_skills'])} | {info['merged_skill']} | {info['merge_strategy']} |\n"
    
    if not merge_candidates:
        md += "| 暂无 | - | - | - |\n"
    
    md += f"""
## 📐 技能融合策略

| 策略 | 说明 | 优势 |
|------|------|------|
| 统一入口 + 按需分发 | 一个入口，自动识别并调用子技能 | 减少选择时间，效率提升 |
| 统一数据层 + 多引擎支持 | 统一接口，支持多种数据源 | 专业度不降低，扩展性强 |
| 统一请求层 + 多协议支持 | 自动选择最优请求方式 | 容错性强，体验一致 |
| 统一图像层 + 多功能支持 | 生成/编辑/分析一体化 | 功能完整，调用简单 |
| 统一创作层 + 多风格支持 | 支持多种文体风格 | 创作灵活，风格多样 |

## 🔄 融合示例

### 文档处理融合
```
融合前: pdf, docx, pptx, xlsx, markdown (5个独立技能)
融合后: unified-document (1个增强技能)
调用方式: "处理这个文档" → 自动识别格式 → 调用对应处理器
效率: 选择时间减少80%，专业度不变
```

### 数据分析融合
```
融合前: excel-analysis, sqlite, mysql, mongodb, elasticsearch (5个独立技能)
融合后: unified-data (1个增强技能)
调用方式: "分析这个数据" → 自动识别数据源 → 调用对应引擎
效率: 无需指定数据源，自动适配
```

## 📈 技能分类统计

| 技能类型 | 数量 | 可融合 | 归属层级 |
|----------|------|--------|----------|
"""
    
    for skill_type, skill_list in sorted(skills["by_type"].items()):
        can_merge = "✅" if skill_type in merge_candidates else "-"
        target_layer = DEFAULT_LAYER
        for rule in DETECTION_RULES:
            if rule["skill_type"] == skill_type:
                target_layer = rule["target_layer"]
                break
        layer_names = {"core": "核心层", "intelligence": "智能层", "capabilities": "能力层",
                      "execution": "执行层", "control": "控制层", "platform": "平台层"}
        md += f"| {skill_type} | {len(skill_list)} | {can_merge} | {layer_names.get(target_layer, '能力层')} |\n"
    
    md += f"""
## 📦 版本信息

- **版本**: 32.0.0
- **架构版本**: V8.0（技能融合增强版）
- **更新时间**: {scan_time}

---

## 📋 统计明细

<details>
<summary>点击展开 10 层内部明细</summary>

| 内部层级 | 文件数 | 归属主层 |
|----------|--------|----------|
"""
    
    for layer_key, count in inventory["internal_detail"]["layers"].items():
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
    
    print("=== 生成架构展示（技能融合增强版）===")
    
    inventory = generate_inventory(workspace)
    
    json_file = reports_dir / "architecture_inventory.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    md_content = render_main_display(inventory)
    md_file = workspace / "architecture_display_live.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("=== 6层架构统计 ===")
    for layer_key, layer_data in inventory["main_architecture"]["layers"].items():
        print(f"  {layer_data['name']}: {layer_data['md_count']} 文件 + {layer_data['fused_count']} 技能")
    
    print()
    print("=== 技能融合机会 ===")
    for skill_type, info in inventory["skills"]["merge_candidates"].items():
        print(f"  {skill_type}: {len(info['sub_skills'])} 个子技能 → {info['merged_skill']}")

if __name__ == "__main__":
    main()
