#!/usr/bin/env python3
"""
组件分级治理模块 V1.0.0

功能：
- 定义组件层级（L1-L6）
- 定义组件类型（core/engine/module/skill/tool/config/doc）
- 定义组件权限和职责
- 定义组件间调用关系
- 自动检测和修正组件位置

层级定义：
- L1 Core: 核心认知、身份、规则（不可修改）
- L2 Memory: 记忆上下文、知识库
- L3 Orchestration: 任务编排、工作流
- L4 Execution: 能力执行、技能网关
- L5 Governance: 稳定治理、安全审计
- L6 Infrastructure: 基础设施、工具链
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


class ComponentClassifier:
    """组件分级治理器"""
    
    # 层级定义
    LAYERS = {
        "L1": {
            "name": "Core",
            "description": "核心认知、身份、规则",
            "mutable": False,
            "allowed_types": ["core", "identity", "rule"],
            "directories": ["core/"],
            "priority": 1
        },
        "L2": {
            "name": "Memory",
            "description": "记忆上下文、知识库",
            "mutable": True,
            "allowed_types": ["memory", "knowledge", "embedding"],
            "directories": ["memory/", "memory_context/"],
            "priority": 2
        },
        "L3": {
            "name": "Orchestration",
            "description": "任务编排、工作流",
            "mutable": True,
            "allowed_types": ["orchestration", "workflow", "router"],
            "directories": ["orchestration/"],
            "priority": 3
        },
        "L4": {
            "name": "Execution",
            "description": "能力执行、技能网关",
            "mutable": True,
            "allowed_types": ["execution", "skill", "gateway", "module"],
            "directories": ["execution/", "skills/"],
            "priority": 4
        },
        "L5": {
            "name": "Governance",
            "description": "稳定治理、安全审计",
            "mutable": True,
            "allowed_types": ["governance", "audit", "security", "policy"],
            "directories": ["governance/"],
            "priority": 5
        },
        "L6": {
            "name": "Infrastructure",
            "description": "基础设施、工具链",
            "mutable": True,
            "allowed_types": ["infrastructure", "tool", "config", "script"],
            "directories": ["infrastructure/", "scripts/"],
            "priority": 6
        }
    }
    
    # 组件类型定义
    TYPES = {
        "core": {
            "name": "核心文件",
            "description": "架构、规则、身份等核心定义",
            "required_layer": "L1",
            "can_call": ["L2", "L3", "L4", "L5", "L6"],
            "can_be_called_by": [],
            "examples": ["ARCHITECTURE.md", "RULE_REGISTRY.json", "SOUL.md"]
        },
        "engine": {
            "name": "引擎",
            "description": "核心引擎，如融合引擎、规则引擎",
            "required_layer": "L1",
            "can_call": ["L2", "L3", "L4", "L5", "L6"],
            "can_be_called_by": ["L3", "L4", "L5", "L6"],
            "examples": ["fusion_index.json", "run_rule_engine.py"]
        },
        "module": {
            "name": "模块",
            "description": "功能模块，如例外管理器、依赖管理器",
            "required_layer": "L6",
            "can_call": ["L4", "L5", "L6"],
            "can_be_called_by": ["L3", "L4", "L5", "L6"],
            "examples": ["exception_manager.py", "dependency_manager.py"]
        },
        "skill": {
            "name": "技能",
            "description": "技能包，如 llm-memory-integration",
            "required_layer": "L4",
            "can_call": ["L4", "L5", "L6"],
            "can_be_called_by": ["L3", "L4"],
            "examples": ["llm-memory-integration", "find-skills"]
        },
        "tool": {
            "name": "工具",
            "description": "辅助工具脚本",
            "required_layer": "L6",
            "can_call": ["L4", "L5", "L6"],
            "can_be_called_by": ["L3", "L4", "L5", "L6"],
            "examples": ["full_backup.py", "unified_inspector.py"]
        },
        "config": {
            "name": "配置",
            "description": "配置文件",
            "required_layer": "L6",
            "can_call": [],
            "can_be_called_by": ["L1", "L2", "L3", "L4", "L5", "L6"],
            "examples": ["unified.json", "dependency_manifest.json"]
        },
        "registry": {
            "name": "注册表",
            "description": "索引、注册表",
            "required_layer": "L6",
            "can_call": [],
            "can_be_called_by": ["L1", "L2", "L3", "L4", "L5", "L6"],
            "examples": ["skill_registry.json", "fusion_index.json"]
        },
        "doc": {
            "name": "文档",
            "description": "说明文档",
            "required_layer": "L6",
            "can_call": [],
            "can_be_called_by": ["L1", "L2", "L3", "L4", "L5", "L6"],
            "examples": ["ARCHITECTURE.md", "PERMANENT_KEEPER_MODULE.md"]
        },
        "report": {
            "name": "报告",
            "description": "运行报告",
            "required_layer": "L6",
            "can_call": [],
            "can_be_called_by": ["L3", "L4", "L5", "L6"],
            "examples": ["rule_engine_report.json", "delete_log.json"]
        }
    }
    
    # 已注册组件
    REGISTERED_COMPONENTS = {
        # L1 Core
        "ARCHITECTURE.md": {"layer": "L1", "type": "core", "name": "架构文档"},
        "RULE_REGISTRY.json": {"layer": "L1", "type": "core", "name": "规则注册表"},
        "RULE_EXCEPTIONS.json": {"layer": "L1", "type": "core", "name": "例外注册表"},
        "SOUL.md": {"layer": "L1", "type": "core", "name": "身份定义"},
        "USER.md": {"layer": "L1", "type": "core", "name": "用户信息"},
        "IDENTITY.md": {"layer": "L1", "type": "core", "name": "身份标识"},
        "AGENTS.md": {"layer": "L1", "type": "core", "name": "工作空间规则"},
        "TOOLS.md": {"layer": "L1", "type": "core", "name": "工具规则"},
        "MEMORY.md": {"layer": "L1", "type": "core", "name": "长期记忆"},
        
        # L6 Infrastructure - 引擎
        "fusion_index.json": {"layer": "L6", "type": "engine", "name": "融合引擎"},
        "unified.json": {"layer": "L6", "type": "config", "name": "统一配置"},
        "run_rule_engine.py": {"layer": "L6", "type": "engine", "name": "规则引擎"},
        "unified_inspector.py": {"layer": "L6", "type": "tool", "name": "统一巡检器"},
        
        # L6 Infrastructure - 模块
        "exception_manager.py": {"layer": "L6", "type": "module", "name": "例外管理器"},
        "dependency_manager.py": {"layer": "L6", "type": "module", "name": "依赖管理器"},
        "delete_manager.py": {"layer": "L6", "type": "module", "name": "删除管理器"},
        "permanent_keeper.py": {"layer": "L6", "type": "module", "name": "永久守护模块"},
        "full_backup.py": {"layer": "L6", "type": "tool", "name": "备份工具"},
        
        # L6 Infrastructure - 注册表
        "skill_registry.json": {"layer": "L6", "type": "registry", "name": "技能注册表"},
        "dependency_manifest.json": {"layer": "L6", "type": "config", "name": "依赖清单"},
        "permanent_keepers.json": {"layer": "L6", "type": "config", "name": "守护配置"},
        
        # L4 Execution - 技能
        "llm-memory-integration": {"layer": "L4", "type": "skill", "name": "LLM记忆集成"},
        "find-skills": {"layer": "L4", "type": "skill", "name": "技能发现"},
        
        # L5 Governance
        "check_skill_security.py": {"layer": "L5", "type": "governance", "name": "技能安全检查"},
        "check_change_impact.py": {"layer": "L5", "type": "governance", "name": "变更影响检查"},
    }
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.config_file = self.root / "config/component_classification.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {
            "layers": self.LAYERS,
            "types": self.TYPES,
            "components": self.REGISTERED_COMPONENTS,
            "version": "1.0.0"
        }
    
    def _save_config(self, config: Dict):
        """保存配置"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def init_config(self) -> Dict:
        """初始化配置"""
        config = self._load_config()
        self._save_config(config)
        return {"status": "success", "message": "组件分级配置已初始化"}
    
    def classify_component(self, name: str, suggested_type: str = None) -> Dict:
        """
        分类组件
        
        Args:
            name: 组件名称
            suggested_type: 建议类型（如用户认为是 skill）
        
        Returns:
            分类结果，包含正确的层级和类型
        """
        config = self._load_config()
        components = config.get("components", {})
        
        # 已注册组件
        if name in components:
            return {
                "status": "registered",
                "name": name,
                "layer": components[name]["layer"],
                "type": components[name]["type"],
                "official_name": components[name]["name"]
            }
        
        # 根据名称推断
        inferred = self._infer_from_name(name)
        
        # 如果用户建议了类型，检查是否正确
        if suggested_type:
            correct_type = self._validate_type(name, suggested_type, inferred)
            if correct_type != suggested_type:
                return {
                    "status": "corrected",
                    "name": name,
                    "suggested_type": suggested_type,
                    "correct_type": correct_type,
                    "layer": self.TYPES[correct_type]["required_layer"],
                    "reason": self._get_correction_reason(name, suggested_type, correct_type)
                }
        
        return {
            "status": "inferred",
            "name": name,
            "layer": inferred["layer"],
            "type": inferred["type"],
            "confidence": inferred["confidence"]
        }
    
    def _infer_from_name(self, name: str) -> Dict:
        """从名称推断类型"""
        name_lower = name.lower()
        
        # 核心文件
        core_patterns = ["architecture", "rule", "soul", "user", "identity", "agents", "tools", "memory.md"]
        for pattern in core_patterns:
            if pattern in name_lower:
                return {"type": "core", "layer": "L1", "confidence": "high"}
        
        # 引擎
        engine_patterns = ["engine", "fusion", "router"]
        for pattern in engine_patterns:
            if pattern in name_lower:
                return {"type": "engine", "layer": "L6", "confidence": "high"}
        
        # 模块
        module_patterns = ["manager", "handler", "processor", "keeper"]
        for pattern in module_patterns:
            if pattern in name_lower:
                return {"type": "module", "layer": "L6", "confidence": "high"}
        
        # 技能
        if "skill" in name_lower or name.startswith("skills/"):
            return {"type": "skill", "layer": "L4", "confidence": "high"}
        
        # 配置
        config_patterns = ["config", "manifest", "settings"]
        for pattern in config_patterns:
            if pattern in name_lower:
                return {"type": "config", "layer": "L6", "confidence": "medium"}
        
        # 注册表
        registry_patterns = ["registry", "index", "catalog"]
        for pattern in registry_patterns:
            if pattern in name_lower:
                return {"type": "registry", "layer": "L6", "confidence": "medium"}
        
        # 报告
        report_patterns = ["report", "log", "status", "history"]
        for pattern in report_patterns:
            if pattern in name_lower:
                return {"type": "report", "layer": "L6", "confidence": "medium"}
        
        # 文档
        if name.endswith(".md"):
            return {"type": "doc", "layer": "L6", "confidence": "medium"}
        
        # 默认
        return {"type": "tool", "layer": "L6", "confidence": "low"}
    
    def _validate_type(self, name: str, suggested: str, inferred: Dict) -> str:
        """验证类型是否正确"""
        # 核心文件不能是技能
        if inferred["type"] == "core" and suggested == "skill":
            return "core"
        
        # 引擎不能是技能
        if inferred["type"] == "engine" and suggested == "skill":
            return "engine"
        
        # 模块不能是技能（除非确实是技能）
        if inferred["type"] == "module" and suggested == "skill":
            # 检查是否在 skills 目录
            if not name.startswith("skills/"):
                return "module"
        
        return suggested
    
    def _get_correction_reason(self, name: str, suggested: str, correct: str) -> str:
        """获取修正原因"""
        reasons = {
            ("skill", "core"): "核心文件属于 L1 层级，不能作为技能",
            ("skill", "engine"): "引擎属于核心基础设施，不能作为技能",
            ("skill", "module"): "模块属于 L6 基础设施层，不在 skills 目录下",
        }
        return reasons.get((suggested, correct), f"类型 {suggested} 不适合此组件，应为 {correct}")
    
    def register_component(self, name: str, layer: str, comp_type: str,
                          official_name: str, description: str = "") -> Dict:
        """注册组件"""
        config = self._load_config()
        
        if name in config.get("components", {}):
            return {"status": "error", "message": f"组件已注册: {name}"}
        
        config["components"][name] = {
            "layer": layer,
            "type": comp_type,
            "name": official_name,
            "description": description,
            "registered_at": datetime.now().isoformat()
        }
        
        self._save_config(config)
        
        return {
            "status": "success",
            "name": name,
            "layer": layer,
            "type": comp_type,
            "message": f"已注册组件: {official_name}"
        }
    
    def get_layer_info(self, layer: str) -> Dict:
        """获取层级信息"""
        if layer not in self.LAYERS:
            return {"status": "error", "message": f"层级不存在: {layer}"}
        
        info = self.LAYERS[layer]
        config = self._load_config()
        components = config.get("components", {})
        
        # 获取该层级的组件
        layer_components = [
            {"name": n, **c}
            for n, c in components.items()
            if c.get("layer") == layer
        ]
        
        return {
            "layer": layer,
            "name": info["name"],
            "description": info["description"],
            "mutable": info["mutable"],
            "allowed_types": info["allowed_types"],
            "directories": info["directories"],
            "components": layer_components
        }
    
    def get_type_info(self, comp_type: str) -> Dict:
        """获取类型信息"""
        if comp_type not in self.TYPES:
            return {"status": "error", "message": f"类型不存在: {comp_type}"}
        
        info = self.TYPES[comp_type]
        config = self._load_config()
        components = config.get("components", {})
        
        # 获取该类型的组件
        type_components = [
            {"name": n, **c}
            for n, c in components.items()
            if c.get("type") == comp_type
        ]
        
        return {
            "type": comp_type,
            "name": info["name"],
            "description": info["description"],
            "required_layer": info["required_layer"],
            "can_call": info["can_call"],
            "can_be_called_by": info["can_be_called_by"],
            "components": type_components
        }
    
    def check_call_permission(self, caller: str, callee: str) -> Dict:
        """检查调用权限"""
        config = self._load_config()
        components = config.get("components", {})
        
        if caller not in components:
            return {"status": "error", "message": f"调用者未注册: {caller}"}
        
        if callee not in components:
            return {"status": "error", "message": f"被调用者未注册: {callee}"}
        
        caller_info = components[caller]
        callee_info = components[callee]
        
        caller_type = caller_info["type"]
        callee_layer = callee_info["layer"]
        
        type_info = self.TYPES.get(caller_type, {})
        can_call = type_info.get("can_call", [])
        
        allowed = callee_layer in can_call
        
        return {
            "caller": caller,
            "callee": callee,
            "caller_layer": caller_info["layer"],
            "caller_type": caller_type,
            "callee_layer": callee_layer,
            "allowed": allowed,
            "reason": f"{caller_info['layer']} {'可以' if allowed else '不可以'}调用 {callee_layer}"
        }
    
    def list_all(self) -> Dict:
        """列出所有组件"""
        config = self._load_config()
        components = config.get("components", {})
        
        by_layer = {}
        for layer in self.LAYERS:
            by_layer[layer] = []
        
        for name, info in components.items():
            layer = info.get("layer", "L6")
            by_layer[layer].append({
                "name": name,
                "type": info["type"],
                "official_name": info["name"]
            })
        
        return {
            "total": len(components),
            "by_layer": by_layer
        }
    
    def suggest_location(self, name: str, comp_type: str) -> Dict:
        """建议组件位置"""
        if comp_type not in self.TYPES:
            return {"status": "error", "message": f"类型不存在: {comp_type}"}
        
        type_info = self.TYPES[comp_type]
        layer = type_info["required_layer"]
        layer_info = self.LAYERS[layer]
        
        # 根据类型建议目录
        location_map = {
            "core": "core/",
            "engine": "infrastructure/",
            "module": "scripts/",
            "skill": "skills/",
            "tool": "scripts/",
            "config": "config/",
            "registry": "infrastructure/inventory/",
            "doc": "docs/",
            "report": "reports/ops/"
        }
        
        suggested_dir = location_map.get(comp_type, "scripts/")
        
        return {
            "name": name,
            "type": comp_type,
            "layer": layer,
            "layer_name": layer_info["name"],
            "suggested_directory": suggested_dir,
            "reason": f"{comp_type} 类型组件应放在 {suggested_dir}"
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="组件分级治理模块 V1.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # init
    subparsers.add_parser("init", help="初始化配置")
    
    # classify
    classify_parser = subparsers.add_parser("classify", help="分类组件")
    classify_parser.add_argument("--name", required=True, help="组件名称")
    classify_parser.add_argument("--type", help="建议类型")
    
    # register
    register_parser = subparsers.add_parser("register", help="注册组件")
    register_parser.add_argument("--name", required=True, help="组件名称")
    register_parser.add_argument("--layer", required=True, help="层级")
    register_parser.add_argument("--type", required=True, help="类型")
    register_parser.add_argument("--official-name", required=True, help="正式名称")
    register_parser.add_argument("--description", default="", help="描述")
    
    # layer
    layer_parser = subparsers.add_parser("layer", help="查看层级信息")
    layer_parser.add_argument("--id", required=True, help="层级ID")
    
    # type
    type_parser = subparsers.add_parser("type", help="查看类型信息")
    type_parser.add_argument("--id", required=True, help="类型ID")
    
    # check-call
    check_parser = subparsers.add_parser("check-call", help="检查调用权限")
    check_parser.add_argument("--caller", required=True, help="调用者")
    check_parser.add_argument("--callee", required=True, help="被调用者")
    
    # list
    subparsers.add_parser("list", help="列出所有组件")
    
    # suggest
    suggest_parser = subparsers.add_parser("suggest", help="建议位置")
    suggest_parser.add_argument("--name", required=True, help="组件名称")
    suggest_parser.add_argument("--type", required=True, help="类型")
    
    args = parser.parse_args()
    
    classifier = ComponentClassifier()
    
    if args.command == "init":
        result = classifier.init_config()
    elif args.command == "classify":
        result = classifier.classify_component(args.name, args.type)
    elif args.command == "register":
        result = classifier.register_component(
            args.name, args.layer, args.type, args.official_name, args.description
        )
    elif args.command == "layer":
        result = classifier.get_layer_info(args.id)
    elif args.command == "type":
        result = classifier.get_type_info(args.id)
    elif args.command == "check-call":
        result = classifier.check_call_permission(args.caller, args.callee)
    elif args.command == "list":
        result = classifier.list_all()
    elif args.command == "suggest":
        result = classifier.suggest_location(args.name, args.type)
    else:
        parser.print_help()
        return
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
