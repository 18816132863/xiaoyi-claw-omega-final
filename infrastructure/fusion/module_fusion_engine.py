#!/usr/bin/env python3
"""
模块融合引擎 V1.0.0

自动处理新增模块的融合、层级分配、依赖检测
与 skill_fusion_engine.py 协同工作，统一管理架构融合
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ModuleFusionEngine:
    """模块融合引擎"""
    
    # 架构层级映射
    LAYER_MAP = {
        "core": "L1",
        "memory_context": "L2",
        "orchestration": "L3",
        "execution": "L4",
        "governance": "L5",
        "infrastructure": "L6",
    }
    
    # 层级名称
    LAYER_NAMES = {
        "L1": "Core",
        "L2": "Memory Context",
        "L3": "Orchestration",
        "L4": "Execution",
        "L5": "Governance",
        "L6": "Infrastructure",
    }
    
    # 模块类型到层级的映射
    MODULE_TYPE_LAYER_MAP = {
        "bus": "L4",
        "executor": "L4",
        "agent": "L4",
        "adapter": "L4",
        "governor": "L5",
        "verifier": "L5",
        "auditor": "L5",
        "registry": "L6",
        "scanner": "L6",
        "planner": "L3",
        "parser": "L3",
        "decomposer": "L3",
        "memory": "L2",
        "store": "L2",
        "loop": "L4",
        "optimizer": "L4",
    }
    
    def __init__(self, root: Optional[Path] = None):
        self.root = root or PROJECT_ROOT
        self.inventory_dir = self.root / "infrastructure" / "inventory"
        self.registry_path = self.inventory_dir / "module_registry.json"
        self.fusion_log_path = self.inventory_dir / "module_fusion_log.json"
        
        self.registry = self._load_registry()
        self.fusion_log = self._load_fusion_log()
    
    def _load_registry(self) -> Dict:
        """加载模块注册表"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "1.0.0", "modules": {}, "stats": {}}
    
    def _save_registry(self):
        """保存模块注册表"""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
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
    
    def _log_fusion(self, action: str, module_name: str, details: Dict):
        """记录融合日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "module": module_name,
            "details": details,
        }
        self.fusion_log["logs"].append(log_entry)
        self._save_fusion_log()
    
    def _determine_layer(self, module_info: Dict) -> Tuple[str, str]:
        """
        确定模块所属架构层级
        
        Returns:
            (层级代码, 层级名称)
        """
        name = module_info.get("name", "").lower()
        description = module_info.get("description", "").lower()
        path = module_info.get("path", "")
        
        # 从路径推断层级
        for path_key, layer in self.LAYER_MAP.items():
            if path_key in path:
                return layer, self.LAYER_NAMES[layer]
        
        # 从名称推断层级
        for keyword, layer in self.MODULE_TYPE_LAYER_MAP.items():
            if keyword in name:
                return layer, self.LAYER_NAMES[layer]
        
        # 从描述推断层级
        for keyword, layer in self.MODULE_TYPE_LAYER_MAP.items():
            if keyword in description:
                return layer, self.LAYER_NAMES[layer]
        
        # 默认 L4 执行层
        return "L4", "Execution"
    
    def _check_dependencies(self, module_info: Dict) -> Dict:
        """
        检查模块依赖
        
        Returns:
            依赖检查结果
        """
        result = {
            "valid": True,
            "missing": [],
            "warnings": [],
        }
        
        dependencies = module_info.get("dependencies", [])
        
        for dep in dependencies:
            if dep not in self.registry.get("modules", {}):
                result["missing"].append(dep)
                result["valid"] = False
        
        return result
    
    def _detect_circular_dependencies(self, module_name: str, dependencies: List[str]) -> bool:
        """检测循环依赖"""
        visited = set()
        
        def visit(name: str) -> bool:
            if name in visited:
                return True
            if name not in self.registry.get("modules", {}):
                return False
            
            visited.add(name)
            deps = self.registry["modules"][name].get("dependencies", [])
            for dep in deps:
                if visit(dep):
                    return True
            visited.remove(name)
            return False
        
        for dep in dependencies:
            if visit(dep):
                return True
        
        return False
    
    def fuse_module(self, module_info: Dict, strategy: str = "auto") -> Dict:
        """
        融合新增模块
        
        流程:
        1. 确定层级
        2. 检查依赖
        3. 检测循环依赖
        4. 注册到模块注册表
        
        Args:
            module_info: 模块信息
            strategy: 融合策略 (auto/register/update)
        
        Returns:
            融合结果
        """
        name = module_info.get("name", "")
        
        if not name:
            return {"success": False, "error": "模块名称不能为空"}
        
        # 确定层级
        layer, layer_name = self._determine_layer(module_info)
        
        # 检查依赖
        dep_check = self._check_dependencies(module_info)
        
        # 检测循环依赖
        has_circular = self._detect_circular_dependencies(name, module_info.get("dependencies", []))
        
        # 构建模块记录
        module_record = {
            "name": module_info.get("display_name", name),
            "layer": layer,
            "layer_name": layer_name,
            "description": module_info.get("description", ""),
            "path": module_info.get("path", f"{name}/"),
            "entry_points": module_info.get("entry_points", []),
            "dependencies": module_info.get("dependencies", []),
            "status": "active",
            "created_at": module_info.get("created_at", datetime.now().strftime("%Y-%m-%d")),
            "fused_at": datetime.now().strftime("%Y-%m-%d"),
        }
        
        # 注册
        if "modules" not in self.registry:
            self.registry["modules"] = {}
        
        self.registry["modules"][name] = module_record
        
        # 更新统计
        self._update_stats()
        
        # 保存
        self._save_registry()
        
        # 记录日志
        result = {
            "success": True,
            "name": name,
            "layer": layer,
            "layer_name": layer_name,
            "dependencies_valid": dep_check["valid"],
            "missing_dependencies": dep_check["missing"],
            "has_circular_dependency": has_circular,
            "warnings": dep_check["warnings"],
        }
        
        if has_circular:
            result["warnings"].append("检测到循环依赖")
        
        self._log_fusion("fuse_module", name, result)
        
        return result
    
    def _update_stats(self):
        """更新统计信息"""
        modules = self.registry.get("modules", {})
        
        by_layer = {}
        by_status = {}
        
        for module in modules.values():
            layer = module.get("layer", "L4")
            status = module.get("status", "active")
            
            by_layer[layer] = by_layer.get(layer, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
        
        self.registry["stats"] = {
            "total": len(modules),
            "by_layer": by_layer,
            "by_status": by_status,
        }
    
    def scan_and_fuse_new_modules(self) -> Dict:
        """
        扫描并融合新模块
        
        检查项目根目录下的所有模块目录，自动融合未注册的模块
        """
        # 已知的模块目录（排除标准目录）
        standard_dirs = {
            "core", "memory_context", "orchestration", "execution", 
            "governance", "infrastructure", "skills", "tests", 
            "scripts", "docs", "config", "data", "reports",
            "capabilities", "diagnostics", "storage", "platform_adapter",
            "memory", "repo", "build", "dist", "node_modules",
        }
        
        # 扫描根目录
        new_modules = []
        
        for item in self.root.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith(".") or item.name.startswith("_"):
                continue
            if item.name in standard_dirs:
                continue
            
            # 检查是否有 __init__.py
            init_file = item / "__init__.py"
            if not init_file.exists():
                continue
            
            # 检查是否已注册
            if item.name in self.registry.get("modules", {}):
                continue
            
            # 发现新模块
            new_modules.append(item.name)
        
        # 融合新模块
        results = []
        for module_name in new_modules:
            module_path = self.root / module_name
            
            # 收集入口点
            entry_points = []
            for py_file in module_path.glob("*.py"):
                if not py_file.name.startswith("_") or py_file.name == "__init__.py":
                    entry_points.append(py_file.name)
            
            module_info = {
                "name": module_name,
                "path": f"{module_name}/",
                "entry_points": entry_points[:5],  # 最多5个入口点
                "description": f"Auto-detected module: {module_name}",
            }
            
            result = self.fuse_module(module_info)
            results.append(result)
        
        return {
            "scanned": len(new_modules),
            "fused": sum(1 for r in results if r.get("success")),
            "results": results,
        }
    
    def get_module(self, name: str) -> Optional[Dict]:
        """获取模块信息"""
        return self.registry.get("modules", {}).get(name)
    
    def list_modules(self, layer: Optional[str] = None) -> List[Dict]:
        """列出模块"""
        modules = list(self.registry.get("modules", {}).values())
        
        if layer:
            modules = [m for m in modules if m.get("layer") == layer]
        
        return modules
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.registry.get("stats", {})
    
    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "version": self.registry.get("version", "1.0.0"),
            "total_modules": len(self.registry.get("modules", {})),
            "fusion_logs": len(self.fusion_log.get("logs", [])),
            "stats": self.get_stats(),
        }


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="模块融合引擎")
    parser.add_argument("command", choices=["scan", "status", "list", "fuse"])
    parser.add_argument("--name", help="模块名称")
    parser.add_argument("--layer", help="按层级过滤")
    
    args = parser.parse_args()
    
    engine = ModuleFusionEngine()
    
    if args.command == "scan":
        result = engine.scan_and_fuse_new_modules()
        print(f"扫描完成: 发现 {result['scanned']} 个新模块, 融合 {result['fused']} 个")
        for r in result["results"]:
            status = "✅" if r.get("success") else "❌"
            print(f"  {status} {r.get('name')}: layer={r.get('layer')}")
    
    elif args.command == "status":
        status = engine.get_status()
        print(f"模块融合引擎状态:")
        print(f"  版本: {status['version']}")
        print(f"  总模块数: {status['total_modules']}")
        print(f"  融合日志: {status['fusion_logs']} 条")
        print(f"  按层级: {status['stats'].get('by_layer', {})}")
    
    elif args.command == "list":
        modules = engine.list_modules(layer=args.layer)
        print(f"模块列表 ({len(modules)} 个):")
        for m in modules:
            print(f"  {m['name']}: {m['layer']} - {m.get('description', '')[:50]}")
    
    elif args.command == "fuse":
        if not args.name:
            print("错误: 请指定 --name")
            return
        
        result = engine.fuse_module({"name": args.name})
        status = "✅" if result.get("success") else "❌"
        print(f"{status} 融合 {args.name}: {result}")


if __name__ == "__main__":
    main()
