#!/usr/bin/env python3
"""
技能 Manifest 生成器
从 skill_registry.json 生成运行时 manifest，作为技能元数据的单一真源
"""
import json
import os
from datetime import datetime
from pathlib import Path

MANIFEST_VERSION = "1.0.0"
REGISTRY_PATH = Path(__file__).parent.parent / "inventory" / "skill_registry.json"
MANIFEST_OUTPUT = Path(__file__).parent / "skill_manifest.json"

def generate_manifest():
    """从注册表生成 manifest"""
    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)
    
    # 只包含已激活的技能
    active_skills = {
        name: {
            "name": skill.get("name"),
            "display_name": skill.get("display_name"),
            "description": skill.get("description", "")[:200],  # 截断描述
            "category": skill.get("category"),
            "risk_level": skill.get("risk_level"),
            "priority": skill.get("priority", "P2"),
            "timeout": skill.get("timeout", 60),
            "path": skill.get("path"),
            "status": skill.get("status"),
            "entry": skill.get("entry", "SKILL.md"),
        }
        for name, skill in registry["skills"].items()
        if skill.get("registered") and skill.get("routable")
    }
    
    manifest = {
        "version": MANIFEST_VERSION,
        "generated": datetime.now().isoformat(),
        "source": "skill_registry.json",
        "total_skills": len(registry["skills"]),
        "active_skills": len(active_skills),
        "skills": active_skills,
        "categories": registry.get("categories", {}),
        "routing_rules": {
            "P0": {"max_concurrent": 3, "timeout_multiplier": 1.0},
            "P1": {"max_concurrent": 5, "timeout_multiplier": 1.5},
            "P2": {"max_concurrent": 10, "timeout_multiplier": 2.0},
        }
    }
    
    with open(MANIFEST_OUTPUT, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    return manifest

if __name__ == "__main__":
    manifest = generate_manifest()
    print(f"✅ Manifest 生成完成")
    print(f"📊 总技能: {manifest['total_skills']}, 已激活: {manifest['active_skills']}")
    print(f"📄 输出: {MANIFEST_OUTPUT}")
