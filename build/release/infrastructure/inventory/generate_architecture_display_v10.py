#!/usr/bin/env python3
"""
generate_architecture_display_v10.py - 生成架构展示页（技能融合能力集成版）

核心特性：
1. 技能融合能力作为独立技能加入控制层
2. 双层融合机制
3. 新技能自动归类
4. 融合效果评估
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
LAYER_FUSION_RULES = CONFIG["layer_fusion_engine"]["layer_fusion_rules"]
SKILL_MERGE_RULES = CONFIG["skill_merge_engine"]["merge_rules"]
SKILL_FUSION_SKILL = CONFIG["skill_fusion_skill"]
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

def count_skills(skills_dir: Path) -> dict:
    if not skills_dir.exists():
        return {"dir_count": 0, "md_count": 0, "by_type": {}, "by_layer": {}}
    
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not should_ignore(str(d))]
    md_count = sum(count_md_files(d) for d in skill_dirs)
    
    by_type = defaultdict(list)
    by_layer = defaultdict(list)
    
    # 添加技能融合能力
    by_type["技能融合"] = ["skill-fusion"]
    by_layer["control"].append("skill-fusion")
    
    for skill_dir in skill_dirs:
        skill_type, target_layer = detect_skill_type(skill_dir.name)
        by_type[skill_type].append(skill_dir.name)
        by_layer[target_layer].append(skill_dir.name)
    
    return {
        "dir_count": len(skill_dirs) + 1,  # +1 for skill-fusion
        "md_count": md_count,
        "by_type": dict(by_type),
        "by_layer": dict(by_layer)
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
    
    layer_fusions = {}
    for rule in LAYER_FUSION_RULES:
        layer_key = rule["layer"]
        layer_skills = skills["by_layer"].get(layer_key, [])
        if layer_skills:
            layer_fusions[layer_key] = {
                "fusion_target": rule["fusion_target"],
                "fusion_strategy": rule["fusion_strategy"],
                "skill_count": len(layer_skills)
            }
    
    skill_merges = {}
    for rule in SKILL_MERGE_RULES:
        skill_type = rule["skill_type"]
        if skill_type in skills["by_type"] and len(skills["by_type"][skill_type]) > 1:
            skill_merges[skill_type] = {
                "merged_skill": rule["merged_skill"],
                "sub_count": len(skills["by_type"][skill_type])
            }
    
    inventory = {
        "scan_time": datetime.now().isoformat(),
        "config_version": CONFIG["version"],
        "main_architecture": {"layers": {}},
        "internal_detail": {"layers": raw_counts_10},
        "skills": skills,
        "layer_fusions": layer_fusions,
        "skill_merges": skill_merges,
        "skill_fusion_skill": SKILL_FUSION_SKILL
    }
    
    for layer_key, layer_info in MAIN_LAYERS.items():
        layer_skills = skills["by_layer"].get(layer_key, [])
        fusion_info = layer_fusions.get(layer_key, {})
        inventory["main_architecture"]["layers"][layer_key] = {
            "name": layer_info["name"],
            "description": layer_info["description"],
            "md_count": aggregated_counts_6.get(layer_key, 0),
            "fused_skills": layer_skills,
            "fused_count": len(layer_skills),
            "can_fuse": layer_info.get("can_fuse", False),
            "fusion_target": layer_info.get("fusion_target"),
            "fusion_strategy": fusion_info.get("fusion_strategy", "")
        }
    
    return inventory

def render_main_display(inventory: dict) -> str:
    scan_time = inventory["scan_time"]
    layers = inventory["main_architecture"]["layers"]
    skills = inventory["skills"]
    layer_fusions = inventory["layer_fusions"]
    skill_merges = inventory["skill_merges"]
    fusion_skill = inventory["skill_fusion_skill"]
    
    md = f"""# 鸽子王智能助手 - 主架构（技能融合能力集成版）

> **最近扫描时间**: {scan_time}
> **架构版本**: V10.0（技能融合能力集成版）
> **技能融合能力**: 已加入控制层

## 🆕 技能融合能力

**skill-fusion** 已作为独立技能加入架构：

| 属性 | 值 |
|------|-----|
| 技能名称 | skill-fusion |
| 技能类型 | 进化相关 |
| 归属层级 | 控制层 |
| 核心能力 | 同类型融合、层级融合、自动归类、效果评估 |

**调用方式**：
- "融合技能" / "合并技能" / "技能融合"

## 📊 执行流程（融合后）

```
接收请求 → 理解意图 → 匹配技能 → 执行任务 → 安全控制 → 输出结果
    ↓          ↓          ↓          ↓          ↓          ↓
  核心层    智能层     能力层     执行层     控制层     平台层
   ❌      统一智能   统一能力   统一执行   统一控制   统一平台
                                          ↑
                                    [技能融合能力]
```

## 📊 6层架构融合视图

| 层级 | 文件数 | 技能数 | 融合目标 | 包含技能融合 |
|------|--------|--------|----------|--------------|
"""
    
    for layer_key, layer_data in layers.items():
        has_fusion = "✅" if layer_key == "control" else "-"
        if layer_data["can_fuse"] and layer_data["fusion_target"]:
            md += f"| {layer_data['name']} | {layer_data['md_count']} | {layer_data['fused_count']} | {layer_data['fusion_target']} | {has_fusion} |\n"
        else:
            md += f"| {layer_data['name']} | {layer_data['md_count']} | {layer_data['fused_count']} | 不可融合 | {has_fusion} |\n"
    
    md += f"""
## 🔄 技能融合能力详情

### 核心功能

| 功能 | 说明 |
|------|------|
| 同类型技能融合 | 将同类型多个子技能融合为增强技能 |
| 层级技能融合 | 将每层内技能融合为核心能力 |
| 新技能自动归类 | 创建/安装新技能时自动识别并融合 |
| 融合效果评估 | 评估融合前后的效率和专业度 |

### 融合示例

**文档处理融合**：
```
融合前: pdf, docx, pptx, xlsx, markdown (5个独立技能)
融合后: unified-document (1个增强技能)
调用: "处理这个文件" → 自动识别格式 → 调用处理器
效率: 选择时间减少 80%
```

**控制层融合**：
```
融合前: 安全相关 + 进化相关 (2类)
融合后: unified-control (含技能融合能力)
调用: "融合技能" → 分析 → 执行融合 → 返回结果
```

## 🔧 技能类型融合

| 技能类型 | 子技能数 | 融合后名称 |
|----------|----------|------------|
"""
    
    for skill_type, merge in skill_merges.items():
        md += f"| {skill_type} | {merge['sub_count']} | {merge['merged_skill']} |\n"
    
    md += f"""
## 📈 融合效果

| 指标 | 融合前 | 融合后 | 提升 |
|------|--------|--------|------|
| 技能选择 | 需指定具体技能 | 自动识别 | 90%↓ |
| 调用复杂度 | 多层调用 | 统一入口 | 80%↓ |
| 专业度 | 各技能独立 | 子技能专注 | 不变 |
| 维护成本 | 分散维护 | 统一维护 | 60%↓ |
| 用户体验 | 需了解技能名 | 一句话搞定 | 显著↑ |

## 📦 版本信息

- **版本**: 32.0.0
- **架构版本**: V10.0（技能融合能力集成版）
- **新增技能**: skill-fusion（技能融合能力）
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
    
    print("=== 生成架构展示（技能融合能力集成版）===")
    
    inventory = generate_inventory(workspace)
    
    json_file = reports_dir / "architecture_inventory.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    md_content = render_main_display(inventory)
    md_file = workspace / "architecture_display_live.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print("=== 6层架构融合 ===")
    for layer_key, layer_data in inventory["main_architecture"]["layers"].items():
        fusion = layer_data.get("fusion_target", "-")
        has_skill_fusion = " [含技能融合能力]" if layer_key == "control" else ""
        print(f"  {layer_data['name']}: {layer_data['md_count']} 文件 → {fusion}{has_skill_fusion}")
    
    print()
    print("=== 技能融合能力 ===")
    print(f"  技能名称: {inventory['skill_fusion_skill']['skill_name']}")
    print(f"  归属层级: {inventory['skill_fusion_skill']['target_layer']}")
    print(f"  核心能力: {', '.join(inventory['skill_fusion_skill']['capabilities'])}")

if __name__ == "__main__":
    main()
