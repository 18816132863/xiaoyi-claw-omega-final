#!/usr/bin/env python3
"""
技能融合引擎 V1.0.0

自动处理新增技能的融合、优先级分配、架构层级映射
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent

class SkillFusionEngine:
    """技能融合引擎"""
    
    # 层级映射
    LAYER_MAP = {
        "xiaoyi-": "L4",
        "web-": "L4",
        "search": "L2",
        "memory": "L2",
        "analysis": "L2",
        "data-": "L2",
        "git": "L6",
        "docker": "L6",
        "mysql": "L6",
        "mongodb": "L6",
        "cron": "L3",
        "orchestrat": "L3",
        "governance": "L5",
        "security": "L5",
        "audit": "L5",
        "ecommerce": "L4",
        "shop": "L4",
        "marketing": "L4",
        "image": "L4",
        "video": "L4",
        "audio": "L4",
        "doc": "L4",
        "pdf": "L4",
        "ppt": "L4",
        "email": "L5",
        "discord": "L5",
        "slack": "L5",
        "telegram": "L5",
    }
    
    # 优先级映射
    PRIORITY_MAP = {
        "xiaoyi-": "P0",
        "web-search": "P0",
        "gui-agent": "P0",
        "image-understanding": "P0",
        "doc-convert": "P0",
        "find-skills": "P0",
        "git": "P0",
        "cron": "P0",
        "ecommerce": "P1",
        "shop": "P1",
        "marketing": "P1",
        "stock": "P1",
        "crypto": "P1",
        "weather": "P1",
        "news": "P1",
        "analysis": "P2",
        "research": "P2",
        "writer": "P2",
        "architect": "P2",
        "scientist": "P2",
        "security": "P2",
        "playwright": "P3",
        "scraper": "P3",
        "screenshot": "P3",
        "video": "P3",
        "audio": "P3",
        "ppt": "P3",
        "docker": "P4",
        "mysql": "P4",
        "mongodb": "P4",
        "api-gateway": "P4",
        "email": "P5",
        "discord": "P5",
        "slack": "P5",
        "obsidian": "P5",
    }
    
    def __init__(self, root: Path):
        self.root = root
        self.registry_path = self.root / "infrastructure" / "inventory" / "skill_registry.json"
        self.skills_dir = self.root / "skills"
        self.registry = self._load_registry()
        self.fusion_results = []
    
    def _load_registry(self) -> Dict:
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0.0", "skills": {}, "total_skills": 0}
    
    def _save_registry(self):
        self.registry["total_skills"] = len(self.registry.get("skills", {}))
        self.registry["updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
    def _determine_layer(self, skill_name: str) -> str:
        name_lower = skill_name.lower()
        for pattern, layer in self.LAYER_MAP.items():
            if pattern in name_lower:
                return layer
        return "L4"
    
    def _determine_priority(self, skill_name: str) -> str:
        name_lower = skill_name.lower()
        for pattern, priority in self.PRIORITY_MAP.items():
            if pattern in name_lower:
                return priority
        return "P6"
    
    def _parse_skill_md(self, skill_path: Path) -> Optional[Dict]:
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return None
        
        try:
            content = skill_md.read_text(encoding='utf-8')
            lines = content.split('\n')
            description = ""
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    description = line
                    break
            
            return {
                "name": skill_path.name,
                "description": description[:200] if description else "",
                "path": f"skills/{skill_path.name}",
            }
        except Exception:
            return None
    
    def scan_skills(self) -> List[Dict]:
        skills = []
        if not self.skills_dir.exists():
            return skills
        
        for skill_path in self.skills_dir.iterdir():
            if not skill_path.is_dir():
                continue
            
            skill_info = self._parse_skill_md(skill_path)
            if skill_info:
                skills.append(skill_info)
        
        return skills
    
    def fuse_all(self) -> Dict:
        skills = self.scan_skills()
        results = {
            "total": len(skills),
            "fused": 0,
            "skipped": 0,
            "details": []
        }
        
        for skill_info in skills:
            name = skill_info["name"]
            layer = self._determine_layer(name)
            priority = self._determine_priority(name)
            
            skill_info["layer"] = layer
            skill_info["priority"] = priority
            skill_info["status"] = "active"
            skill_info["registered"] = True
            skill_info["routable"] = True
            skill_info["callable"] = False
            skill_info["fused_at"] = datetime.now().isoformat()
            
            if name in self.registry.get("skills", {}):
                results["skipped"] += 1
                continue
            
            if "skills" not in self.registry:
                self.registry["skills"] = {}
            
            self.registry["skills"][name] = skill_info
            results["fused"] += 1
            results["details"].append({
                "name": name,
                "layer": layer,
                "priority": priority
            })
        
        self._save_registry()
        return results

def main():
    root = get_project_root()
    engine = SkillFusionEngine(root)
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          技能融合引擎 V1.0.0                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    print("【扫描技能目录】")
    skills = engine.scan_skills()
    print(f"  发现 {len(skills)} 个技能")
    print()
    
    print("【执行融合】")
    results = engine.fuse_all()
    print(f"  总计: {results['total']}")
    print(f"  已融合: {results['fused']}")
    print(f"  已跳过: {results['skipped']}")
    print()
    
    if results['details']:
        print("【融合详情（前20个）】")
        for detail in results['details'][:20]:
            print(f"  {detail['name']}: {detail['layer']} / {detail['priority']}")
        if len(results['details']) > 20:
            print(f"  ... 还有 {len(results['details']) - 20} 个")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
