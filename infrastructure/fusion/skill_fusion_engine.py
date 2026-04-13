#!/usr/bin/env python3
"""
技能融合引擎 V1.0.0

自动处理新增技能的融合、优先级分配、冲突检测
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.path_resolver import get_project_root, get_infrastructure_dir


class SkillFusionEngine:
    """技能融合引擎"""
    
    # 内容类型
    CONTENT_TYPES = ["skill", "module", "file", "directory"]
    
    # 架构层级映射
    LAYER_MAP = {
        "core": "L1",
        "memory_context": "L2",
        "orchestration": "L3",
        "execution": "L4",
        "governance": "L5",
        "infrastructure": "L6",
    }
    
    # 技能类型到层级的映射
    SKILL_TYPE_LAYER_MAP = {
        "认知": "L1",
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
    
    # 类别到优先级的映射
    CATEGORY_PRIORITY_MAP = {
        "xiaoyi-*": "P0",
        "ecommerce": "P1",
        "search": "P2",
        "data": "P2",
        "image": "P3",
        "document": "P3",
        "automation": "P4",
        "system": "P4",
        "communication": "P5",
        "other": "P6",
    }
    
    # 核心技能列表（P0）
    CORE_SKILLS = [
        "xiaoyi-web-search",
        "xiaoyi-gui-agent",
        "xiaoyi-image-understanding",
        "xiaoyi-image-search",
        "xiaoyi-doc-convert",
        "find-skills",
        "git",
        "cron",
        "docx",
        "pdf",
        "file-manager",
        "huawei-drive",
    ]
    
    def __init__(self):
        self.project_root = get_project_root()
        self.registry_path = self.project_root / "infrastructure" / "inventory" / "skill_registry.json"
        self.index_path = self.project_root / "infrastructure" / "inventory" / "skill_inverted_index.json"
        self.fusion_log_path = self.project_root / "infrastructure" / "fusion" / "fusion_log.json"
        
        self.registry = self._load_registry()
        self.index = self._load_index()
        self.fusion_log = self._load_fusion_log()
    
    def _load_registry(self) -> Dict:
        """加载技能注册表"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0.0", "skills": {}, "total_skills": 0}
    
    def _save_registry(self):
        """保存技能注册表"""
        self.registry["total_skills"] = len(self.registry.get("skills", {}))
        self.registry["updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
    def _load_index(self) -> Dict:
        """加载反向索引"""
        if self.index_path.exists():
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0.0", "triggers": {}}
    
    def _save_index(self):
        """保存反向索引"""
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _load_fusion_log(self) -> Dict:
        """加载融合日志"""
        if self.fusion_log_path.exists():
            with open(self.fusion_log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0.0", "logs": []}
    
    def _save_fusion_log(self):
        """保存融合日志"""
        self.fusion_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.fusion_log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fusion_log, f, ensure_ascii=False, indent=2)
    
    def _log_fusion(self, action: str, skill_name: str, details: Dict):
        """记录融合日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "skill": skill_name,
            "details": details,
        }
        self.fusion_log["logs"].append(log_entry)
        self._save_fusion_log()
    
    def _determine_content_type(self, content_info: Dict) -> str:
        """
        确定内容类型
        
        Returns:
            skill/module/file/directory
        """
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
    
    def _determine_target_directory(self, content_info: Dict, layer: str) -> str:
        """
        确定目标目录
        
        Args:
            content_info: 内容信息
            layer: 架构层级
        
        Returns:
            目标目录路径
        """
        content_type = self._determine_content_type(content_info)
        name = content_info.get("name", "")
        
        # 层级到目录的映射
        layer_dirs = {
            "L1": "core",
            "L2": "memory_context",
            "L3": "orchestration",
            "L4": "execution",
            "L5": "governance",
            "L6": "infrastructure",
        }
        
        base_dir = layer_dirs.get(layer, "infrastructure")
        
        if content_type == "skill":
            return f"skills/{name}"
        elif content_type == "module":
            return f"{base_dir}/{name}"
        else:
            return base_dir
    
    def _determine_layer(self, skill_info: Dict) -> Tuple[str, str]:
        """
        确定技能所属架构层级
        
        Returns:
            (层级代码, 层级名称)
        """
        name = skill_info.get("name", "")
        description = skill_info.get("description", "").lower()
        category = skill_info.get("category", "other")
        path = skill_info.get("path", "")
        
        # 从路径推断层级
        for path_key, layer in self.LAYER_MAP.items():
            if path_key in path:
                return layer, self._get_layer_name(layer)
        
        # 从描述推断层级
        for keyword, layer in self.SKILL_TYPE_LAYER_MAP.items():
            if keyword in description or keyword in name:
                return layer, self._get_layer_name(layer)
        
        # 默认 L4 执行层
        return "L4", "Execution"
    
    def _get_layer_name(self, layer: str) -> str:
        """获取层级名称"""
        names = {
            "L1": "Core",
            "L2": "Memory Context",
            "L3": "Orchestration",
            "L4": "Execution",
            "L5": "Governance",
            "L6": "Infrastructure",
        }
        return names.get(layer, "Execution")
    
    def _check_layer_boundary(self, skill_info: Dict, layer: str) -> Dict:
        """
        检查层级边界
        
        Returns:
            边界检查结果
        """
        result = {
            "valid": True,
            "warnings": [],
            "errors": [],
        }
        
        dependencies = skill_info.get("dependencies", [])
        
        # L1 不能依赖其他层
        if layer == "L1" and dependencies:
            result["warnings"].append("L1 核心层不应依赖其他层级")
        
        # L6 不能被其他层依赖（除了 L5）
        if layer == "L6":
            for dep in dependencies:
                if dep not in ["L5", "L6"]:
                    result["warnings"].append(f"L6 基础设施层不应依赖 {dep}")
        
        return result
    
    def _determine_priority(self, skill_info: Dict) -> str:
        """确定技能优先级"""
        name = skill_info.get("name", "")
        category = skill_info.get("category", "other")
        
        # 核心技能直接 P0
        if name in self.CORE_SKILLS:
            return "P0"
        
        # xiaoyi-* 前缀 P0
        if name.startswith("xiaoyi-"):
            return "P0"
        
        # 按类别分配
        if category in self.CATEGORY_PRIORITY_MAP:
            return self.CATEGORY_PRIORITY_MAP[category]
        
        return "P6"
    
    def _detect_conflicts(self, skill_info: Dict) -> List[Dict]:
        """检测技能冲突"""
        conflicts = []
        name = skill_info.get("name", "")
        description = skill_info.get("description", "").lower()
        
        for existing_name, existing_info in self.registry.get("skills", {}).items():
            if existing_info.get("status") in ["deprecated", "merged"]:
                continue
            
            # 名称相似度检测
            if name in existing_name or existing_name in name:
                if name != existing_name:
                    conflicts.append({
                        "type": "name_similarity",
                        "existing": existing_name,
                        "suggestion": "replace" if "-v2" in name or "-next" in name else "merge"
                    })
            
            # 功能重叠检测（简单关键词匹配）
            existing_desc = existing_info.get("description", "").lower()
            common_keywords = self._extract_common_keywords(description, existing_desc)
            if len(common_keywords) >= 3:
                conflicts.append({
                    "type": "function_overlap",
                    "existing": existing_name,
                    "keywords": common_keywords,
                    "suggestion": "merge"
                })
        
        return conflicts
    
    def _extract_common_keywords(self, desc1: str, desc2: str) -> List[str]:
        """提取共同关键词"""
        keywords = []
        important_words = [
            "搜索", "search", "图像", "image", "视频", "video",
            "文档", "document", "电商", "ecommerce", "数据", "data",
            "分析", "analysis", "生成", "generate", "转换", "convert"
        ]
        for word in important_words:
            if word in desc1 and word in desc2:
                keywords.append(word)
        return keywords
    
    def fuse_content(self, content_info: Dict, strategy: str = "auto") -> Dict:
        """
        融合新增内容（技能/模块/文件/目录）
        
        流程:
        1. 架构融合 - 确定层级、目标目录、检查边界
        2. 技能融合 - 仅技能类型执行
        
        Args:
            content_info: 内容信息
            strategy: 融合策略 (auto/replace/merge/dependency)
        
        Returns:
            融合结果
        """
        name = content_info.get("name", "")
        if not name:
            return {"success": False, "error": "内容名称不能为空"}
        
        # 确定内容类型
        content_type = self._determine_content_type(content_info)
        content_info["content_type"] = content_type
        
        # ========== 第一步：架构融合 ==========
        layer, layer_name = self._determine_layer(content_info)
        target_dir = self._determine_target_directory(content_info, layer)
        
        content_info["layer"] = layer
        content_info["layer_name"] = layer_name
        content_info["target_directory"] = target_dir
        
        # 检查层级边界
        boundary_check = self._check_layer_boundary(content_info, layer)
        
        # 记录架构融合信息
        architecture_fusion = {
            "content_type": content_type,
            "layer": layer,
            "layer_name": layer_name,
            "target_directory": target_dir,
            "boundary_check": boundary_check,
        }
        
        result = {
            "success": True,
            "name": name,
            "architecture_fusion": architecture_fusion,
            "silent": True,
        }
        
        # ========== 第二步：技能融合（仅技能类型）==========
        if content_type == "skill":
            skill_result = self._fuse_skill_internal(content_info, strategy)
            result.update(skill_result)
        
        # 记录日志
        self._log_fusion("fuse_content", name, result)
        
        return result
    
    def _fuse_skill_internal(self, skill_info: Dict, strategy: str = "auto") -> Dict:
        """
        技能融合内部实现
        
        Args:
            skill_info: 技能信息
            strategy: 融合策略
        
        Returns:
            融合结果
        """
        name = skill_info.get("name", "")
        
        # 检测冲突
        conflicts = self._detect_conflicts(skill_info)
        
        # 确定优先级
        priority = self._determine_priority(skill_info)
        skill_info["priority"] = priority
        skill_info["last_verified"] = datetime.now().strftime("%Y-%m-%d")
        
        # 处理冲突
        if conflicts and strategy == "auto":
            # 自动选择策略
            for conflict in conflicts:
                if conflict["suggestion"] == "replace":
                    strategy = "replace"
                    break
                elif conflict["suggestion"] == "merge":
                    strategy = "merge"
        
        result = {
            "skill": name,
            "priority": priority,
            "strategy": strategy,
            "conflicts": conflicts,
        }
        
        if strategy == "replace" and conflicts:
            # 替换策略
            for conflict in conflicts:
                if conflict["type"] == "name_similarity":
                    old_name = conflict["existing"]
                    if old_name in self.registry.get("skills", {}):
                        # 标记旧技能为 deprecated
                        self.registry["skills"][old_name]["status"] = "deprecated"
                        self.registry["skills"][old_name]["replaced_by"] = name
                        skill_info["replaces"] = old_name
                        skill_info["priority"] = self.registry["skills"][old_name].get("priority", priority)
                        result["replaced"] = old_name
                        result["silent"] = False  # 替换需要通知
                        break
        
        elif strategy == "merge" and conflicts:
            # 合并策略
            merged_skills = []
            for conflict in conflicts:
                if conflict["type"] == "function_overlap":
                    old_name = conflict["existing"]
                    if old_name in self.registry.get("skills", {}):
                        self.registry["skills"][old_name]["status"] = "merged"
                        self.registry["skills"][old_name]["merged_into"] = name
                        merged_skills.append(old_name)
            
            if merged_skills:
                skill_info["merges"] = merged_skills
                result["merged"] = merged_skills
                result["silent"] = False  # 合并需要通知
        
        # 检查依赖
        dependencies = skill_info.get("dependencies", [])
        missing_deps = []
        for dep in dependencies:
            if dep not in self.registry.get("skills", {}):
                missing_deps.append(dep)
        
        if missing_deps:
            result["missing_dependencies"] = missing_deps
            result["silent"] = False  # 缺少依赖需要通知
        
        # 注册技能
        skill_info["status"] = skill_info.get("status", "active")
        skill_info["registered"] = True
        skill_info["routable"] = True
        
        if "skills" not in self.registry:
            self.registry["skills"] = {}
        
        self.registry["skills"][name] = skill_info
        
        # 更新反向索引
        self._update_index(skill_info)
        
        # 保存
        self._save_registry()
        self._save_index()
        
        return result
    
    def fuse_skill(self, skill_info: Dict, strategy: str = "auto") -> Dict:
        """
        融合新技能（兼容旧接口）
        
        Args:
            skill_info: 技能信息
            strategy: 融合策略 (auto/replace/merge/dependency)
        
        Returns:
            融合结果
        """
        return self.fuse_content(skill_info, strategy)
    
    def _update_index(self, skill_info: Dict):
        """更新反向索引"""
        name = skill_info.get("name", "")
        triggers = skill_info.get("triggers", [])
        
        # 从名称提取触发词
        name_parts = name.replace("-", " ").replace("_", " ").split()
        for part in name_parts:
            if len(part) > 2:
                triggers.append(part.lower())
        
        # 从描述提取触发词
        description = skill_info.get("description", "")
        important_words = [
            "搜索", "search", "图像", "image", "视频", "video",
            "文档", "document", "电商", "ecommerce", "数据", "data"
        ]
        for word in important_words:
            if word in description.lower():
                triggers.append(word)
        
        # 更新索引
        if "triggers" not in self.index:
            self.index["triggers"] = {}
        
        for trigger in set(triggers):
            if trigger not in self.index["triggers"]:
                self.index["triggers"][trigger] = []
            if name not in self.index["triggers"][trigger]:
                self.index["triggers"][trigger].append(name)
    
    def get_status(self) -> Dict:
        """获取融合状态"""
        skills = self.registry.get("skills", {})
        
        # 按优先级统计
        priority_stats = {}
        for priority in ["P0", "P1", "P2", "P3", "P4", "P5", "P6"]:
            priority_stats[priority] = len([
                s for s in skills.values() 
                if s.get("priority") == priority
            ])
        
        # 按状态统计
        status_stats = {}
        for status in ["active", "healthy", "deprecated", "merged"]:
            status_stats[status] = len([
                s for s in skills.values() 
                if s.get("status") == status
            ])
        
        # 按层级统计
        layer_stats = {}
        for layer in ["L1", "L2", "L3", "L4", "L5", "L6"]:
            layer_stats[layer] = len([
                s for s in skills.values() 
                if s.get("layer") == layer
            ])
        
        # 最近融合记录
        recent_logs = self.fusion_log.get("logs", [])[-10:]
        
        return {
            "total_skills": len(skills),
            "priority_distribution": priority_stats,
            "layer_distribution": layer_stats,
            "status_distribution": status_stats,
            "recent_fusions": recent_logs,
        }
    
    def scan_new_skills(self) -> List[Dict]:
        """扫描新技能目录"""
        skills_dir = self.project_root / "skills"
        new_skills = []
        
        if not skills_dir.exists():
            return new_skills
        
        for skill_path in skills_dir.iterdir():
            if not skill_path.is_dir():
                continue
            
            skill_name = skill_path.name
            if skill_name in self.registry.get("skills", {}):
                continue
            
            # 检查是否有 SKILL.md
            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                continue
            
            # 解析技能信息
            skill_info = self._parse_skill_md(skill_md, skill_name)
            if skill_info:
                new_skills.append(skill_info)
        
        return new_skills
    
    def _parse_skill_md(self, skill_md: Path, skill_name: str) -> Optional[Dict]:
        """解析 SKILL.md 文件"""
        try:
            content = skill_md.read_text(encoding='utf-8')
            
            # 提取描述（第一段非标题内容）
            lines = content.split('\n')
            description = ""
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    description = line
                    break
            
            return {
                "name": skill_name,
                "display_name": skill_name,
                "description": description[:200] if description else "",
                "category": "other",
                "risk_level": "high",
                "layer": 4,
                "path": f"skills/{skill_name}",
                "entry_point": "SKILL.md",
                "executor_type": "skill_md",
            }
        except Exception as e:
            print(f"解析 {skill_md} 失败: {e}")
            return None
    
    def auto_fuse_all(self, silent: bool = True) -> List[Dict]:
        """自动融合所有新技能"""
        new_skills = self.scan_new_skills()
        results = []
        
        for skill_info in new_skills:
            result = self.fuse_skill(skill_info, strategy="auto")
            if not silent or not result.get("silent", True):
                results.append(result)
        
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="技能融合引擎")
    parser.add_argument("--status", action="store_true", help="查看融合状态")
    parser.add_argument("--scan", action="store_true", help="扫描新技能")
    parser.add_argument("--silent", action="store_true", help="静默模式")
    parser.add_argument("--replace", nargs=2, metavar=("OLD", "NEW"), help="替换技能")
    parser.add_argument("--merge", nargs="+", metavar="SKILL", help="合并技能")
    
    args = parser.parse_args()
    
    engine = SkillFusionEngine()
    
    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return
    
    if args.scan:
        new_skills = engine.scan_new_skills()
        print(f"发现 {len(new_skills)} 个新技能:")
        for skill in new_skills:
            print(f"  - {skill['name']}: {skill['description'][:50]}...")
        return
    
    if args.replace:
        old_name, new_name = args.replace
        print(f"替换技能: {old_name} -> {new_name}")
        # 这里需要先获取新技能信息
        return
    
    if args.merge:
        print(f"合并技能: {', '.join(args.merge)}")
        return
    
    # 默认：自动融合
    results = engine.auto_fuse_all(silent=args.silent)
    if results:
        print(f"融合完成，处理了 {len(results)} 个技能:")
        for result in results:
            print(f"  - {result['skill']}: {result['strategy']} (P{result['priority']})")
    else:
        print("没有需要融合的新技能")


if __name__ == "__main__":
    main()
