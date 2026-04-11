#!/usr/bin/env python3
"""架构巡检器 - V4.3.2 最终版

功能：
1. 检查六层架构完整性
2. 检查文件保护规则
3. 检查技能注册表一致性
4. 检查配置文件完整性
5. 检查依赖关系
6. 生成巡检报告
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 六层架构定义
LAYERS = {
    "L1_Core": {
        "name": "核心层",
        "path": "core",
        "protected_files": [
            "ARCHITECTURE.md", "AGENTS.md", "SOUL.md", "USER.md", 
            "TOOLS.md", "IDENTITY.md"
        ],
        "required_dirs": ["config", "health"]
    },
    "L2_Memory": {
        "name": "记忆层",
        "path": "memory_context",
        "protected_files": ["MEMORY.md"],
        "required_dirs": ["index", "vector"]
    },
    "L3_Orchestration": {
        "name": "编排层",
        "path": "orchestration",
        "protected_files": ["router/router.py"],
        "required_dirs": ["router"]
    },
    "L4_Execution": {
        "name": "执行层",
        "path": "execution",
        "protected_files": ["skill_gateway.py"],
        "required_dirs": ["ecommerce"]
    },
    "L5_Governance": {
        "name": "治理层",
        "path": "governance",
        "protected_files": ["security.py", "audit/explainer.py", "validators/architecture_validator.py"],
        "required_dirs": ["security", "audit", "validators"]
    },
    "L6_Infrastructure": {
        "name": "基础设施层",
        "path": "infrastructure",
        "protected_files": ["token_budget.py", "path_resolver.py"],
        "required_dirs": ["loader", "cache", "inventory"]
    }
}

# 受保护文件列表
PROTECTED_FILES = {
    "AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md",
    "MEMORY.md", "HEARTBEAT.md", "core/ARCHITECTURE.md"
}

class ArchitectureInspector:
    """架构巡检器"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "layers": {},
            "protected_files": {},
            "skill_registry": {},
            "config_files": {},
            "dependencies": {},
            "issues": [],
            "warnings": [],
            "summary": {}
        }
    
    def inspect_all(self) -> Dict:
        """执行完整巡检"""
        print("=" * 60)
        print("架构巡检 - V4.3.2 最终版")
        print("=" * 60)
        
        # 1. 检查六层架构
        self._inspect_layers()
        
        # 2. 检查受保护文件
        self._inspect_protected_files()
        
        # 3. 检查技能注册表
        self._inspect_skill_registry()
        
        # 4. 检查配置文件
        self._inspect_config_files()
        
        # 5. 检查依赖关系
        self._inspect_dependencies()
        
        # 6. 生成摘要
        self._generate_summary()
        
        return self.results
    
    def _inspect_layers(self):
        """检查六层架构"""
        print("\n【1. 六层架构检查】")
        
        for layer_id, layer_info in LAYERS.items():
            layer_path = PROJECT_ROOT / layer_info["path"]
            status = {
                "exists": layer_path.exists(),
                "files": 0,
                "dirs": 0,
                "protected_ok": True,
                "required_ok": True,
                "issues": []
            }
            
            if layer_path.exists():
                # 统计文件
                status["files"] = len(list(layer_path.rglob("*.py")))
                status["dirs"] = len([d for d in layer_path.rglob("*") if d.is_dir()])
                
                # 检查受保护文件
                for pf in layer_info.get("protected_files", []):
                    pf_path = layer_path / pf
                    if not pf_path.exists():
                        status["protected_ok"] = False
                        status["issues"].append(f"缺失受保护文件: {pf}")
                
                # 检查必需目录
                for rd in layer_info.get("required_dirs", []):
                    rd_path = layer_path / rd
                    if not rd_path.exists():
                        status["required_ok"] = False
                        status["issues"].append(f"缺失必需目录: {rd}")
            
            self.results["layers"][layer_id] = status
            
            # 输出
            icon = "✅" if status["exists"] and status["protected_ok"] and status["required_ok"] else "❌"
            print(f"  {icon} {layer_info['name']}: {status['files']} 文件, {status['dirs']} 目录")
            
            for issue in status["issues"]:
                print(f"      ⚠️ {issue}")
    
    def _inspect_protected_files(self):
        """检查受保护文件"""
        print("\n【2. 受保护文件检查】")
        
        for pf in PROTECTED_FILES:
            pf_path = PROJECT_ROOT / pf
            status = {
                "exists": pf_path.exists(),
                "size": pf_path.stat().st_size if pf_path.exists() else 0,
                "modified": datetime.fromtimestamp(pf_path.stat().st_mtime).isoformat() if pf_path.exists() else None
            }
            
            self.results["protected_files"][pf] = status
            
            icon = "✅" if status["exists"] else "❌"
            print(f"  {icon} {pf}")
    
    def _inspect_skill_registry(self):
        """检查技能注册表"""
        print("\n【3. 技能注册表检查】")
        
        registry_path = PROJECT_ROOT / "infrastructure" / "inventory" / "skill_registry.json"
        
        if registry_path.exists():
            try:
                registry = json.loads(registry_path.read_text())
                skills = registry.get("skills", [])
                
                status = {
                    "exists": True,
                    "skill_count": len(skills),
                    "categories": {},
                    "issues": []
                }
                
                # 统计分类
                for skill in skills:
                    cat = skill.get("category", "unknown")
                    status["categories"][cat] = status["categories"].get(cat, 0) + 1
                
                # 检查必需字段
                required_fields = ["name", "category", "layer", "status"]
                for i, skill in enumerate(skills):
                    for field in required_fields:
                        if field not in skill:
                            status["issues"].append(f"技能 {i} 缺失字段: {field}")
                
                self.results["skill_registry"] = status
                
                print(f"  ✅ 技能总数: {status['skill_count']}")
                for cat, count in status["categories"].items():
                    print(f"      • {cat}: {count}")
                
                for issue in status["issues"][:5]:
                    print(f"      ⚠️ {issue}")
                    
            except Exception as e:
                self.results["skill_registry"] = {"exists": True, "error": str(e)}
                print(f"  ❌ 解析失败: {e}")
        else:
            self.results["skill_registry"] = {"exists": False}
            print("  ❌ 技能注册表不存在")
    
    def _inspect_config_files(self):
        """检查配置文件"""
        print("\n【4. 配置文件检查】")
        
        config_files = [
            "core/CONFIG.json",
            "infrastructure/inventory/load_config.json",
            "infrastructure/inventory/exclude_config.json",
            "skills/llm-memory-integration/config/llm_config.json",
            "skills/llm-memory-integration/config/unified_config.json"
        ]
        
        for cf in config_files:
            cf_path = PROJECT_ROOT / cf
            status = {
                "exists": cf_path.exists(),
                "valid_json": False,
                "size": 0
            }
            
            if cf_path.exists():
                status["size"] = cf_path.stat().st_size
                try:
                    json.loads(cf_path.read_text())
                    status["valid_json"] = True
                except:
                    pass
            
            self.results["config_files"][cf] = status
            
            icon = "✅" if status["exists"] and status["valid_json"] else "❌"
            print(f"  {icon} {cf}")
    
    def _inspect_dependencies(self):
        """检查依赖关系"""
        print("\n【5. 依赖关系检查】")
        
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))
        
        # 检查关键模块导入
        critical_imports = [
            ("memory_context.unified_search", "统一搜索"),
            ("infrastructure.token_budget", "Token 预算"),
            ("infrastructure.path_resolver", "路径解析"),
            ("execution.skill_gateway", "技能网关"),
        ]
        
        status = {"imports": {}}
        
        for module, name in critical_imports:
            try:
                __import__(module)
                status["imports"][module] = {"ok": True, "name": name}
                print(f"  ✅ {name} ({module})")
            except Exception as e:
                status["imports"][module] = {"ok": False, "name": name, "error": str(e)}
                print(f"  ❌ {name} ({module}): {e}")
                self.results["issues"].append(f"导入失败: {module}")
        
        self.results["dependencies"] = status
    
    def _generate_summary(self):
        """生成摘要"""
        print("\n" + "=" * 60)
        print("巡检摘要")
        print("=" * 60)
        
        # 统计
        layer_ok = sum(1 for s in self.results["layers"].values() 
                       if s["exists"] and s["protected_ok"] and s["required_ok"])
        layer_total = len(LAYERS)
        
        protected_ok = sum(1 for s in self.results["protected_files"].values() if s["exists"])
        protected_total = len(PROTECTED_FILES)
        
        config_ok = sum(1 for s in self.results["config_files"].values() 
                        if s["exists"] and s["valid_json"])
        config_total = len(self.results["config_files"])
        
        import_ok = sum(1 for s in self.results["dependencies"]["imports"].values() if s["ok"])
        import_total = len(self.results["dependencies"]["imports"])
        
        # 汇总
        self.results["summary"] = {
            "layers": f"{layer_ok}/{layer_total}",
            "protected_files": f"{protected_ok}/{protected_total}",
            "config_files": f"{config_ok}/{config_total}",
            "imports": f"{import_ok}/{import_total}",
            "issues": len(self.results["issues"]),
            "warnings": len(self.results["warnings"])
        }
        
        print(f"  六层架构: {layer_ok}/{layer_total} 通过")
        print(f"  受保护文件: {protected_ok}/{protected_total} 存在")
        print(f"  配置文件: {config_ok}/{config_total} 有效")
        print(f"  关键导入: {import_ok}/{import_total} 成功")
        print(f"  问题数: {len(self.results['issues'])}")
        print(f"  警告数: {len(self.results['warnings'])}")
        
        # 总体状态
        all_ok = (layer_ok == layer_total and 
                  protected_ok == protected_total and 
                  import_ok == import_total)
        
        print()
        if all_ok:
            print("✅ 架构巡检通过")
        else:
            print("❌ 架构巡检发现问题，请检查上述项目")
        
        # 自动 Git 提交
        print()
        print("【自动 Git 同步】")
        try:
            from infrastructure.auto_git import auto_commit_if_changed
            ok, msg = auto_commit_if_changed(f"架构巡检: {layer_ok}/{layer_total} 通过")
            print(f"  {'✅' if ok else '❌'} {msg}")
        except Exception as e:
            print(f"  ⚠️ 自动提交失败: {e}")
    
    def save_report(self, path: Path = None):
        """保存报告"""
        path = path or PROJECT_ROOT / "reports" / f"inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.results, ensure_ascii=False, indent=2))
        print(f"\n报告已保存: {path}")


def main():
    inspector = ArchitectureInspector()
    results = inspector.inspect_all()
    inspector.save_report()
    
    # 返回退出码
    issues = results["summary"]["issues"]
    return 0 if issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
