#!/usr/bin/env python3
"""
自动注册脚本

扫描 scripts/ 目录，将所有脚本注册到 script_registry.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def categorize_script(script_name: str) -> str:
    """分类脚本"""
    # Demo 脚本
    if script_name.startswith("demo_"):
        return "demo"
    
    # 检查脚本
    if script_name.startswith("check_"):
        return "check"
    
    # 自动化脚本
    if script_name.startswith("auto_"):
        return "automation"
    
    # 维护脚本
    maintenance_keywords = ["cleanup", "backup", "restore", "migrate", "seed", "reset"]
    if any(kw in script_name for kw in maintenance_keywords):
        return "maintenance"
    
    # 工具脚本
    utility_keywords = ["export", "import", "convert", "generate", "run", "start", "stop"]
    if any(kw in script_name for kw in utility_keywords):
        return "utility"
    
    return "other"


def scan_scripts():
    """扫描所有脚本"""
    scripts = {}
    
    scripts_dir = PROJECT_ROOT / "scripts"
    if not scripts_dir.exists():
        return scripts
    
    for script_file in scripts_dir.glob("*.py"):
        if script_file.name.startswith("_"):
            continue
        
        script_name = script_file.stem
        content = script_file.read_text(encoding='utf-8')
        
        # 提取描述
        description = ""
        for line in content.split('\n')[:20]:
            if line.startswith('"""') or line.startswith("'''"):
                description = line.strip('"\' ')
                break
        
        # 分类
        category = categorize_script(script_name)
        
        scripts[script_name] = {
            "name": script_name,
            "path": f"scripts/{script_file.name}",
            "description": description or f"Script: {script_name}",
            "category": category,
            "status": "registered",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "registered_at": datetime.now().strftime("%Y-%m-%d"),
            "tested": False,
        }
    
    return scripts


def register_scripts():
    """注册所有脚本"""
    print("=" * 60)
    print("  自动注册脚本")
    print("=" * 60)
    
    # 扫描脚本
    scripts = scan_scripts()
    print(f"\n发现 {len(scripts)} 个脚本")
    
    # 加载现有注册表
    inventory_dir = PROJECT_ROOT / "infrastructure" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    
    registry_path = inventory_dir / "script_registry.json"
    
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    else:
        registry = {
            "version": "1.0.0",
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "items": {},
            "stats": {},
        }
    
    # 合并脚本
    existing = registry.get("items", {})
    new_count = 0
    
    for script_name, script_info in scripts.items():
        if script_name not in existing:
            existing[script_name] = script_info
            new_count += 1
            print(f"  ✅ 注册: {script_name} ({script_info['category']})")
        else:
            print(f"  ⏭️  已存在: {script_name}")
    
    # 更新注册表
    registry["items"] = existing
    registry["updated"] = datetime.now().strftime("%Y-%m-%d")
    
    # 统计
    by_category = {}
    by_status = {"created": 0, "registered": 0, "tested": 0, "active": 0}
    
    for script in existing.values():
        cat = script.get("category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1
        
        status = script.get("status", "registered")
        by_status[status] = by_status.get(status, 0) + 1
        if script.get("tested"):
            by_status["tested"] += 1
    
    registry["stats"] = {
        "total": len(existing),
        "by_status": by_status,
        "by_category": by_category,
    }
    
    # 保存
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"\n注册完成: 新增 {new_count} 个，总计 {len(existing)} 个")
    print(f"📄 注册表: {registry_path}")
    
    return new_count


if __name__ == "__main__":
    register_scripts()
