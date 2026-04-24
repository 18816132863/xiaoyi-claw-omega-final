#!/usr/bin/env python3
"""
generate_architecture_display_v6.py - 生成架构展示页（动态融合版）

核心特性：
1. 新技能按类型自动融合到对应层级
2. 技能分类与层级职责匹配
3. 架构可扩展，支持动态归类
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
SKILL_FUSION_RULES = CONFIG["skill_fusion_rules"]["rules"]
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
        return {"dir_count": 0, "md_count": 0, "by_type": {}}
    
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not should_ignore(str(d))]
    md_count = sum(count_md_files(d) for d in skill_dirs)
    
    # 按类型分类技能
    skill_types = {
        "文档处理": [], "数据分析": [], "开发工具": [], "网络服务": [],
        "图像处理": [], "音频视频": [], "内容创作": [], "通讯集成": [],
        "效率工具": [], "市场研究": [], "安全相关": [], "其他": []
    }
    
    for skill_dir in skill_dirs:
        skill_name = skill_dir.name.lower()
        categorized = False
        
        # 文档处理
        if any(k in skill_name for k in ['pdf', 'docx', 'pptx', 'xlsx', 'markdown', 'document', 'doc']):
            skill_types["文档处理"].append(skill_dir.name)
            categorized = True
        # 数据分析
        elif any(k in skill_name for k in ['data', 'excel', 'sql', 'mongo', 'elastic', 'analysis']):
            skill_types["数据分析"].append(skill_dir.name)
            categorized = True
        # 开发工具
        elif any(k in skill_name for k in ['git', 'docker', 'ansible', 'terraform', 'javascript', 'code']):
            skill_types["开发工具"].append(skill_dir.name)
            categorized = True
        # 网络服务
        elif any(k in skill_name for k in ['web', 'scrap', 'search', 'api', 'tavily']):
            skill_types["网络服务"].append(skill_dir.name)
            categorized = True
        # 图像处理
        elif any(k in skill_name for k in ['image', 'chart', 'screenshot', 'seedream']):
            skill_types["图像处理"].append(skill_dir.name)
            categorized = True
        # 音频视频
        elif any(k in skill_name for k in ['audio', 'video', 'whisper', 'subtitle']):
            skill_types["音频视频"].append(skill_dir.name)
            categorized = True
        # 内容创作
        elif any(k in skill_name for k in ['article', 'copy', 'novel', 'poetry', 'story', 'writer']):
            skill_types["内容创作"].append(skill_dir.name)
            categorized = True
        # 通讯集成
        elif any(k in skill_name for k in ['email', 'imsg', 'linkedin', 'klaviyo', 'message']):
            skill_types["通讯集成"].append(skill_dir.name)
            categorized = True
        # 效率工具
        elif any(k in skill_name for k in ['obsidian', 'cron', 'productivity', 'proactivity']):
            skill_types["效率工具"].append(skill_dir.name)
            categorized = True
        # 市场研究
        elif any(k in skill_name for k in ['market', 'crypto', 'stock', 'news']):
            skill_types["市场研究"].append(skill_dir.name)
            categorized = True
        # 安全相关
        elif any(k in skill_name for k in ['security', 'guardian', 'validator']):
            skill_types["安全相关"].append(skill_dir.name)
            categorized = True
        
        if not categorized:
            skill_types["其他"].append(skill_dir.name)
    
    return {
        "dir_count": len(skill_dirs),
        "md_count": md_count,
        "by_type": {k: v for k, v in skill_types.items() if v}
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
        "skill_fusion_rules": SKILL_FUSION_RULES
    }
    
    for layer_key, layer_info in MAIN_LAYERS.items():
        inventory["main_architecture"]["layers"][layer_key] = {
            "name": layer_info["name"],
            "description": layer_info["description"],
            "md_count": aggregated_counts_6.get(layer_key, 0),
            "aggregates": layer_info["aggregates"],
            "execution_role": layer_info["execution_role"],
            "skill_types": layer_info["skill_types"],
            "rationale": layer_info["rationale"]
        }
    
    inventory["main_architecture"]["layers"]["capabilities"]["skills_dir_count"] = skills["dir_count"]
    inventory["main_architecture"]["layers"]["capabilities"]["skills_md_count"] = skills["md_count"]
    
    return inventory

def render_main_display(inventory: dict) -> str:
    scan_time = inventory["scan_time"]
    layers = inventory["main_architecture"]["layers"]
    skills = inventory["skills"]
    
    md = f"""# 鸽子王智能助手 - 主架构（动态融合版）

> **最近扫描时间**: {scan_time}
> **架构版本**: 6层主架构 V6.0（动态融合版）
> **特性**: 新技能按类型自动融合到对应层级

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
│                      主架构（6层 - 动态融合版）                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         核心层 (Core) - {layers['core']['md_count']} 文件                           │   │
│  │         系统骨架、身份定义、基础配置                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         智能层 (Intelligence) - {layers['intelligence']['md_count']} 文件           │   │
│  │         记忆、理解、推理、知识 + 市场研究技能                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         能力层 (Capabilities) - {skills['dir_count']}技能/{skills['md_count']}文档  │   │
│  │         文档/数据/开发/网络/图像/音视频/创作技能                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         执行层 (Execution) - {layers['execution']['md_count']} 文件                 │   │
│  │         工作流、编排、自动化 + 效率工具技能                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         控制层 (Control) - {layers['control']['md_count']} 文件                     │   │
│  │         安全、合规、可靠性、进化 + 安全/进化技能                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         平台层 (Platform) - {layers['platform']['md_count']} 文件                   │   │
│  │         API、SDK、市场、业务 + 通讯集成技能                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📈 6层主架构统计

| 层级 | MD文件数 | 执行角色 | 融合技能类型 |
|------|----------|----------|--------------|
| 核心层 | {layers['core']['md_count']} | 入口定义 | 无 |
| 智能层 | {layers['intelligence']['md_count']} | 理解意图 | 市场研究 |
| 能力层 | {skills['md_count']} | 匹配技能 | 文档/数据/开发/网络/图像/音视频/创作 |
| 执行层 | {layers['execution']['md_count']} | 执行任务 | 效率工具 |
| 控制层 | {layers['control']['md_count']} | 安全控制 | 安全相关、进化相关 |
| 平台层 | {layers['platform']['md_count']} | 输出结果 | 通讯集成 |
| **总计** | **{sum(l['md_count'] for l in layers.values())}** | - | - |

## 🔧 技能分类统计

| 技能类型 | 数量 | 归属层级 |
|----------|------|----------|
"""
    
    for skill_type, skill_list in skills["by_type"].items():
        if skill_list:
            # 确定归属层级
            target_layer = "能力层"
            for rule in SKILL_FUSION_RULES:
                if rule["skill_type"] == skill_type:
                    target_layer = rule["target_layer"]
                    if target_layer == "capabilities":
                        target_layer = "能力层"
                    elif target_layer == "intelligence":
                        target_layer = "智能层"
                    elif target_layer == "execution":
                        target_layer = "执行层"
                    elif target_layer == "control":
                        target_layer = "控制层"
                    elif target_layer == "platform":
                        target_layer = "平台层"
                    break
            md += f"| {skill_type} | {len(skill_list)} | {target_layer} |\n"
    
    md += f"""
## 📐 技能融合规则

| 技能类型 | 归属层级 | 融合理由 |
|----------|----------|----------|
| 文档处理 | 能力层 | 属于可插拔能力 |
| 数据分析 | 能力层 | 属于可插拔能力 |
| 开发工具 | 能力层 | 属于可插拔能力 |
| 网络服务 | 能力层 | 属于可插拔能力 |
| 图像处理 | 能力层 | 属于可插拔能力 |
| 音频视频 | 能力层 | 属于可插拔能力 |
| 内容创作 | 能力层 | 属于可插拔能力 |
| 通讯集成 | 平台层 | 对外连接能力 |
| 效率工具 | 执行层 | 自动化执行能力 |
| 市场研究 | 智能层 | 知识获取能力 |
| 安全相关 | 控制层 | 安全保障能力 |
| 进化相关 | 控制层 | 自我改进能力 |

## 📦 版本信息

- **版本**: 32.0.0
- **架构版本**: V6.0（动态融合版）
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
    
    print("=== 生成架构展示（动态融合版）===")
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
        skill_types = layer_data.get('skill_types', [])
        types_str = f" [{', '.join(skill_types)}]" if skill_types else ""
        print(f"  {layer_data['name']}: {layer_data['md_count']} 文件{types_str}")
    
    print()
    print("=== 技能分类统计 ===")
    for skill_type, skill_list in inventory["skills"]["by_type"].items():
        if skill_list:
            print(f"  {skill_type}: {len(skill_list)} 个")

if __name__ == "__main__":
    main()
