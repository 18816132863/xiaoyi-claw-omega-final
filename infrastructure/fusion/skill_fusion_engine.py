#!/usr/bin/env python3
"""
技能融合引擎 V3.0.0

按照小艺Claw Beta 设计规范实现：
1. 架构融合检查清单（所有新增内容）
2. 技能融合策略（A/B/C/D）
3. 静默融合规则（不通知用户）
4. 优先级排序输出
5. 内容类型识别（技能/模块/文件/目录）
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

class ContentFusionEngine:
    """内容融合引擎 V3.0.0 - 支持所有新增内容类型"""
    
    # 内容类型
    CONTENT_TYPES = ["skill", "module", "file", "directory"]
    
    # 架构层级映射
    LAYER_MAP = {
        "L1": {"name": "Core", "directory": "core/", "description": "核心认知、身份、规则、标准"},
        "L2": {"name": "Memory Context", "directory": "memory_context/", "description": "记忆上下文、知识库"},
        "L3": {"name": "Orchestration", "directory": "orchestration/", "description": "任务编排、工作流"},
        "L4": {"name": "Execution", "directory": "execution/", "description": "能力执行、技能网关"},
        "L5": {"name": "Governance", "directory": "governance/", "description": "稳定治理、安全审计"},
        "L6": {"name": "Infrastructure", "directory": "infrastructure/", "description": "基础设施、工具链"},
    }
    
    # 内容类型到层级的映射
    CONTENT_TYPE_LAYER = {
        # 技能类型
        "核心认知": "L1",
        "身份": "L1",
        "规则": "L1",
        "标准": "L1",
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
        # 文件类型
        "schema": "L1",
        "contract": "L1",
        "validator": "L5",
        "script": "L6",
        "config": "L6",
    }
    
    # 优先级映射
    PRIORITY_MAP = {
        # P0 - 核心必需
        "xiaoyi-": "P0",
        "web-search": "P0",
        "gui-agent": "P0",
        "image-understanding": "P0",
        "doc-convert": "P0",
        "find-skills": "P0",
        "git": "P0",
        "cron": "P0",
        # P1 - 高频使用
        "ecommerce": "P1",
        "shop": "P1",
        "marketing": "P1",
        "stock": "P1",
        "crypto": "P1",
        "weather": "P1",
        "news": "P1",
        "xiaohongshu": "P1",
        "bilibili": "P1",
        "douyin": "P1",
        # P2 - 专业领域
        "analysis": "P2",
        "research": "P2",
        "writer": "P2",
        "architect": "P2",
        "scientist": "P2",
        "security": "P2",
        "data-": "P2",
        # P3 - 工具类
        "playwright": "P3",
        "scraper": "P3",
        "screenshot": "P3",
        "video": "P3",
        "audio": "P3",
        "ppt": "P3",
        "image": "P3",
        "doc": "P3",
        "pdf": "P3",
        # P4 - 基础设施
        "docker": "P4",
        "mysql": "P4",
        "mongodb": "P4",
        "api-gateway": "P4",
        "ansible": "P4",
        "terraform": "P4",
        # P5 - 通信集成
        "email": "P5",
        "discord": "P5",
        "slack": "P5",
        "telegram": "P5",
        "obsidian": "P5",
        "feishu": "P5",
        "weixin": "P5",
        # P6 - 辅助实验
        "beginner": "P6",
        "persona": "P6",
        "experiment": "P6",
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
        return {"version": "3.0.0", "skills": {}, "total_skills": 0}
    
    def _save_registry(self):
        self.registry["total_skills"] = len(self.registry.get("skills", {}))
        self.registry["updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
    def _determine_content_type(self, content_info: Dict) -> str:
        """确定内容类型"""
        path = content_info.get("path", "")
        name = content_info.get("name", "")
        
        # 检查是否是技能
        if "skills/" in path or path.startswith("skills/"):
            return "skill"
        
        # 检查是否是模块（有子目录）
        if content_info.get("is_module", False):
            return "module"
        
        # 检查是否是目录
        if content_info.get("is_directory", False):
            return "directory"
        
        # 默认是文件
        return "file"
    
    def _determine_layer(self, content_name: str, description: str = "", content_type: str = "skill") -> str:
        """确定内容所属层级"""
        name_lower = content_name.lower()
        desc_lower = description.lower()
        
        # xiaoyi-* 前缀归入 L4
        if name_lower.startswith("xiaoyi-"):
            return "L4"
        
        # 按内容类型映射
        for content_type_key, layer in self.CONTENT_TYPE_LAYER.items():
            if content_type_key in name_lower or content_type_key in desc_lower:
                return layer
        
        # 根据目录路径判断
        if "core/" in name_lower or "core/" in desc_lower:
            return "L1"
        if "memory_context/" in name_lower or "memory/" in name_lower:
            return "L2"
        if "orchestration/" in name_lower:
            return "L3"
        if "execution/" in name_lower or "skills/" in name_lower:
            return "L4"
        if "governance/" in name_lower:
            return "L5"
        if "infrastructure/" in name_lower:
            return "L6"
        
        return "L4"  # 默认执行层
    
    def _determine_priority(self, content_name: str) -> str:
        """确定内容优先级"""
        name_lower = content_name.lower()
        for pattern, priority in self.PRIORITY_MAP.items():
            if pattern in name_lower:
                return priority
        return "P6"
    
    def _determine_target_directory(self, content_name: str, layer: str, content_type: str) -> str:
        """确定目标目录"""
        layer_info = self.LAYER_MAP.get(layer, self.LAYER_MAP["L4"])
        base_dir = layer_info["directory"]
        
        if content_type == "skill":
            return f"skills/{content_name}"
        elif content_type == "module":
            return f"{base_dir}{content_name}/"
        elif content_type == "directory":
            return f"{base_dir}{content_name}/"
        else:  # file
            return base_dir
    
    def _check_conflicts(self, content_name: str) -> Tuple[bool, List[str]]:
        """检查是否与现有内容冲突"""
        conflicts = []
        existing_skills = self.registry.get("skills", {})
        
        for existing_name, existing_info in existing_skills.items():
            if existing_info.get("status") in ["deprecated", "merged"]:
                continue
            
            # 名称相似度检测
            if content_name in existing_name or existing_name in content_name:
                if content_name != existing_name:
                    conflicts.append(existing_name)
        
        return len(conflicts) > 0, conflicts
    
    def _determine_strategy(self, content_name: str, has_conflicts: bool, has_dependencies: bool = False) -> str:
        """确定融合策略"""
        # 策略 B: 替换（版本升级）
        if "-v2" in content_name or "-next" in content_name or "-pro" in content_name:
            return "B"
        
        # 策略 C: 合并（功能重叠）
        if has_conflicts:
            return "C"
        
        # 策略 D: 依赖（有依赖）
        if has_dependencies:
            return "D"
        
        # 策略 A: 阶梯化（默认）
        return "A"
    
    def _is_silent(self, strategy: str, content_type: str) -> bool:
        """判断是否静默（不通知用户）"""
        # 策略 A 和 D 静默
        if strategy in ["A", "D"]:
            return True
        # 新增文件/目录静默
        if content_type in ["file", "directory"]:
            return True
        return False
    
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
    
    def fuse_content(self, content_info: Dict) -> Dict:
        """
        融合新增内容（技能/模块/文件/目录）
        
        流程:
        1. 架构融合 - 确定层级、目标目录、检查边界
        2. 技能融合 - 确定策略、优先级、注册（仅技能）
        """
        name = content_info.get("name", "")
        description = content_info.get("description", "")
        
        if not name:
            return {"status": "error", "reason": "name_required"}
        
        # 确定内容类型
        content_type = self._determine_content_type(content_info)
        content_info["content_type"] = content_type
        
        # ========== 第一步：架构融合 ==========
        layer = self._determine_layer(name, description, content_type)
        target_dir = self._determine_target_directory(name, layer, content_type)
        
        # 架构融合检查清单
        architecture_checklist = {
            "determine_layer": True,
            "determine_target_directory": True,
            "check_conflicts": None,
            "determine_dependencies": None,
            "determine_dependents": None,
            "update_architecture_doc": False,
            "verify_layer_rules": True,
        }
        
        # ========== 第二步：技能融合（仅技能类型）==========
        if content_type == "skill":
            has_conflicts, conflicts = self._check_conflicts(name)
            architecture_checklist["check_conflicts"] = has_conflicts
            
            strategy = self._determine_strategy(name, has_conflicts)
            priority = self._determine_priority(name)
        else:
            strategy = "A"
            priority = self._determine_priority(name)
            conflicts = []
        
        is_silent = self._is_silent(strategy, content_type)
        
        # 构建内容信息
        content_info["layer"] = layer
        content_info["layer_name"] = self.LAYER_MAP[layer]["name"]
        content_info["target_directory"] = target_dir
        content_info["priority"] = priority
        content_info["strategy"] = strategy
        content_info["silent"] = is_silent
        content_info["status"] = "active"
        content_info["registered"] = True
        content_info["fused_at"] = datetime.now().isoformat()
        
        # 检查是否已注册（仅技能）
        if content_type == "skill" and name in self.registry.get("skills", {}):
            return {
                "name": name,
                "status": "skipped",
                "reason": "already_registered"
            }
        
        # 注册（仅技能）
        if content_type == "skill":
            if "skills" not in self.registry:
                self.registry["skills"] = {}
            self.registry["skills"][name] = content_info
        
        return {
            "name": name,
            "content_type": content_type,
            "layer": layer,
            "layer_name": self.LAYER_MAP[layer]["name"],
            "target_directory": target_dir,
            "priority": priority,
            "strategy": strategy,
            "silent": is_silent,
            "conflicts": conflicts if content_type == "skill" and conflicts else None,
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
            result = self.fuse_content(skill_info)
            
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
    
    def get_priority_sorted_skills(self) -> List[Dict]:
        """按优先级排序输出所有技能"""
        skills = self.registry.get("skills", {})
        sorted_skills = sorted(
            skills.items(),
            key=lambda x: (x[1].get("priority", "P6"), x[0])
        )
        return [{"name": k, **v} for k, v in sorted_skills]
    
    def print_priority_report(self):
        """打印优先级报告"""
        sorted_skills = self.get_priority_sorted_skills()
        
        print("\n【优先级排序报告】")
        print()
        
        current_priority = None
        count = 0
        
        for skill in sorted_skills:
            priority = skill.get("priority", "P6")
            
            if priority != current_priority:
                if current_priority is not None:
                    print(f"  小计: {count} 个")
                    print()
                current_priority = priority
                count = 0
                print(f"【{priority}】")
            
            count += 1
            layer = skill.get("layer", "L4")
            silent = "✅" if skill.get("silent") else "❌"
            print(f"  {skill['name']}: {layer} {silent}")
        
        if count > 0:
            print(f"  小计: {count} 个")

def main():
    root = get_project_root()
    engine = ContentFusionEngine(root)
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          内容融合引擎 V3.0.0                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    print("【核心原则】")
    print("  所有新增内容（技能/模块/文件/目录）必须先融合到六层架构中")
    print("  禁止在架构外新增任何内容")
    print()
    
    print("【内容类型】")
    print("  - 技能: skills/ 目录下")
    print("  - 模块: 有子目录的功能模块")
    print("  - 文件: 单个文件")
    print("  - 目录: 任意子目录")
    print()
    
    print("【融合策略】")
    print("  A: 阶梯化 - 新增独立技能，无冲突 ✅静默")
    print("  B: 替换 - 功能重叠，版本升级 ❌通知")
    print("  C: 合并 - 多技能功能重叠 ❌通知")
    print("  D: 依赖 - 新技能有依赖 ✅静默")
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
    
    # 打印优先级报告
    engine.print_priority_report()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
