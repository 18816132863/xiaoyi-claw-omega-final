#!/usr/bin/env python3
"""
技能融合引擎 V2.0.0

按照小艺Claw Beta 设计规范实现：
1. 架构融合检查清单
2. 技能融合策略（A/B/C/D）
3. 静默融合规则
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
    """技能融合引擎 V2.0.0"""
    
    # 架构层级映射
    LAYER_MAP = {
        "L1": {"name": "Core", "directory": "core/", "description": "核心认知、身份、规则、标准"},
        "L2": {"name": "Memory Context", "directory": "memory_context/", "description": "记忆上下文、知识库"},
        "L3": {"name": "Orchestration", "directory": "orchestration/", "description": "任务编排、工作流"},
        "L4": {"name": "Execution", "directory": "execution/", "description": "能力执行、技能网关"},
        "L5": {"name": "Governance", "directory": "governance/", "description": "稳定治理、安全审计"},
        "L6": {"name": "Infrastructure", "directory": "infrastructure/", "description": "基础设施、工具链"},
    }
    
    # 技能类型到层级的映射
    SKILL_TYPE_LAYER = {
        "核心认知": "L1",
        "身份": "L1",
        "规则": "L1",
        "记忆": "L2",
        "搜索": "L2",
        "知识库": "L2",
        "编排": "L3",
        "工作流": "L3",
        "路由": "L3",
        "执行": "L4",
        "网关": "L4",
        "技能": "L4",
        "安全": "L5",
        "审计": "L5",
        "合规": "L5",
        "基础设施": "L6",
        "工具链": "L6",
        "注册表": "L6",
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
        self.fusion_log = []
    
    def _load_registry(self) -> Dict:
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "2.0.0", "skills": {}, "total_skills": 0}
    
    def _save_registry(self):
        self.registry["total_skills"] = len(self.registry.get("skills", {}))
        self.registry["updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
    def _determine_layer(self, skill_name: str, description: str = "") -> str:
        """确定技能所属层级"""
        name_lower = skill_name.lower()
        desc_lower = description.lower()
        
        # xiaoyi-* 前缀归入 L4
        if name_lower.startswith("xiaoyi-"):
            return "L4"
        
        # 按技能类型映射
        for skill_type, layer in self.SKILL_TYPE_LAYER.items():
            if skill_type in name_lower or skill_type in desc_lower:
                return layer
        
        return "L4"  # 默认执行层
    
    def _determine_priority(self, skill_name: str) -> str:
        """确定技能优先级"""
        name_lower = skill_name.lower()
        for pattern, priority in self.PRIORITY_MAP.items():
            if pattern in name_lower:
                return priority
        return "P6"
    
    def _determine_target_directory(self, skill_name: str, layer: str) -> str:
        """确定目标目录"""
        layer_info = self.LAYER_MAP.get(layer, self.LAYER_MAP["L4"])
        return f"skills/{skill_name}"
    
    def _check_conflicts(self, skill_name: str) -> Tuple[bool, List[str]]:
        """检查是否与现有技能冲突"""
        conflicts = []
        existing_skills = self.registry.get("skills", {})
        
        for existing_name, existing_info in existing_skills.items():
            if existing_info.get("status") in ["deprecated", "merged"]:
                continue
            
            # 名称相似度检测
            if skill_name in existing_name or existing_name in skill_name:
                if skill_name != existing_name:
                    conflicts.append(existing_name)
        
        return len(conflicts) > 0, conflicts
    
    def _determine_strategy(self, skill_name: str, has_conflicts: bool) -> str:
        """确定融合策略"""
        # 策略 B: 替换（版本升级）
        if "-v2" in skill_name or "-next" in skill_name or "-pro" in skill_name:
            return "B"
        
        # 策略 C: 合并（功能重叠）
        if has_conflicts:
            return "C"
        
        # 策略 D: 依赖（有依赖）
        # TODO: 检查依赖
        
        # 策略 A: 阶梯化（默认）
        return "A"
    
    def _is_silent(self, strategy: str) -> bool:
        """判断是否静默"""
        return strategy in ["A", "D"]
    
    def _parse_skill_md(self, skill_path: Path) -> Optional[Dict]:
        """解析 SKILL.md 文件"""
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
        """扫描所有技能"""
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
    
    def fuse_skill(self, skill_info: Dict) -> Dict:
        """
        融合单个技能
        
        流程:
        1. 架构融合 - 确定层级、目标目录、检查边界
        2. 技能融合 - 确定策略、优先级、注册
        """
        name = skill_info["name"]
        description = skill_info.get("description", "")
        
        # ========== 第一步：架构融合 ==========
        layer = self._determine_layer(name, description)
        target_dir = self._determine_target_directory(name, layer)
        
        # 架构融合检查清单
        architecture_checklist = {
            "determine_layer": True,
            "check_conflicts": None,
            "determine_dependencies": None,
            "determine_dependents": None,
            "update_architecture_doc": False,
            "verify_layer_rules": True,
        }
        
        # ========== 第二步：技能融合 ==========
        has_conflicts, conflicts = self._check_conflicts(name)
        architecture_checklist["check_conflicts"] = has_conflicts
        
        strategy = self._determine_strategy(name, has_conflicts)
        priority = self._determine_priority(name)
        is_silent = self._is_silent(strategy)
        
        # 构建技能信息
        skill_info["layer"] = layer
        skill_info["layer_name"] = self.LAYER_MAP[layer]["name"]
        skill_info["target_directory"] = target_dir
        skill_info["priority"] = priority
        skill_info["strategy"] = strategy
        skill_info["silent"] = is_silent
        skill_info["status"] = "active"
        skill_info["registered"] = True
        skill_info["routable"] = True
        skill_info["callable"] = False
        skill_info["fused_at"] = datetime.now().isoformat()
        
        # 检查是否已注册
        if name in self.registry.get("skills", {}):
            return {
                "name": name,
                "status": "skipped",
                "reason": "already_registered"
            }
        
        # 注册技能
        if "skills" not in self.registry:
            self.registry["skills"] = {}
        
        self.registry["skills"][name] = skill_info
        
        return {
            "name": name,
            "layer": layer,
            "layer_name": self.LAYER_MAP[layer]["name"],
            "priority": priority,
            "strategy": strategy,
            "silent": is_silent,
            "conflicts": conflicts if has_conflicts else None,
            "architecture_checklist": architecture_checklist,
        }
    
    def fuse_all(self) -> Dict:
        """融合所有技能"""
        skills = self.scan_skills()
        results = {
            "total": len(skills),
            "fused": 0,
            "skipped": 0,
            "silent_count": 0,
            "notify_count": 0,
            "details": []
        }
        
        for skill_info in skills:
            result = self.fuse_skill(skill_info)
            
            if result.get("status") == "skipped":
                results["skipped"] += 1
            else:
                results["fused"] += 1
                if result.get("silent"):
                    results["silent_count"] += 1
                else:
                    results["notify_count"] += 1
                results["details"].append(result)
        
        self._save_registry()
        return results

def main():
    root = get_project_root()
    engine = SkillFusionEngine(root)
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          技能融合引擎 V2.0.0                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    print("【核心原则】")
    print("  所有新增内容必须先融合到六层架构中")
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
    print(f"  静默融合: {results['silent_count']}")
    print(f"  需通知: {results['notify_count']}")
    print()
    
    if results['details']:
        print("【融合详情（前20个）】")
        for detail in results['details'][:20]:
            silent_mark = "✅" if detail.get('silent') else "❌"
            print(f"  {detail['name']}: {detail['layer']} / {detail['priority']} / 策略{detail['strategy']} {silent_mark}")
        if len(results['details']) > 20:
            print(f"  ... 还有 {len(results['details']) - 20} 个")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
