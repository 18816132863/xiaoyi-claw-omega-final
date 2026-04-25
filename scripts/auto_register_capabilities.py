#!/usr/bin/env python3
"""
自动注册能力

扫描 capabilities/ 目录，将所有能力注册到 capability_registry.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def scan_capabilities():
    """扫描所有能力"""
    capabilities = {}
    
    cap_dir = PROJECT_ROOT / "capabilities"
    if not cap_dir.exists():
        return capabilities
    
    for cap_file in cap_dir.glob("*.py"):
        if cap_file.name.startswith("_"):
            continue
        
        cap_name = cap_file.stem
        content = cap_file.read_text(encoding='utf-8')
        
        # 提取描述
        description = ""
        for line in content.split('\n')[:20]:
            if line.startswith('"""') or line.startswith("'''"):
                description = line.strip('"\' ')
                break
        
        capabilities[cap_name] = {
            "name": cap_name,
            "path": f"capabilities/{cap_file.name}",
            "description": description or f"Capability: {cap_name}",
            "status": "registered",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "registered_at": datetime.now().strftime("%Y-%m-%d"),
            "wired": False,
            "tested": False,
            "documented": False,
        }
    
    return capabilities


def register_capabilities():
    """注册所有能力"""
    print("=" * 60)
    print("  自动注册能力")
    print("=" * 60)
    
    # 扫描能力
    capabilities = scan_capabilities()
    print(f"\n发现 {len(capabilities)} 个能力")
    
    # 加载现有注册表
    inventory_dir = PROJECT_ROOT / "infrastructure" / "inventory"
    inventory_dir.mkdir(parents=True, exist_ok=True)
    
    registry_path = inventory_dir / "capability_registry.json"
    
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
    
    # 合并能力
    existing = registry.get("items", {})
    new_count = 0
    
    for cap_name, cap_info in capabilities.items():
        if cap_name not in existing:
            existing[cap_name] = cap_info
            new_count += 1
            print(f"  ✅ 注册: {cap_name}")
        else:
            print(f"  ⏭️  已存在: {cap_name}")
    
    # 更新注册表
    registry["items"] = existing
    registry["updated"] = datetime.now().strftime("%Y-%m-%d")
    registry["stats"] = {
        "total": len(existing),
        "by_status": {
            "created": 0,
            "registered": len(existing),
            "wired": sum(1 for c in existing.values() if c.get("wired")),
            "tested": sum(1 for c in existing.values() if c.get("tested")),
            "documented": sum(1 for c in existing.values() if c.get("documented")),
            "active": sum(1 for c in existing.values() if c.get("status") == "active"),
        }
    }
    
    # 保存
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"\n注册完成: 新增 {new_count} 个，总计 {len(existing)} 个")
    print(f"📄 注册表: {registry_path}")
    
    return new_count


if __name__ == "__main__":
    register_capabilities()
