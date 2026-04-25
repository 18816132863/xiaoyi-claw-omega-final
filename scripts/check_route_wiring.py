#!/usr/bin/env python3
"""
路由接线检查器

检查 skill_entry/input_router.py 是否能路由所有已注册能力
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class RouteWiringChecker:
    """路由接线检查器"""
    
    def __init__(self, root: Path = None):
        self.root = root or PROJECT_ROOT
        self.inventory_dir = self.root / "infrastructure" / "inventory"
        self.reports_dir = self.root / "reports" / "integrity"
        
        self.inventory_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "routes": {},
            "issues": [],
            "stats": {},
        }
    
    def scan_routes(self) -> Dict:
        """扫描路由配置"""
        routes = {}
        
        # 检查路由文件
        router_paths = [
            self.root / "skill_entry" / "input_router.py",
            self.root / "infrastructure" / "skill_router.py",
            self.root / "skills" / "runtime" / "skill_router.py",
        ]
        
        for router_path in router_paths:
            if not router_path.exists():
                continue
            
            content = router_path.read_text(encoding='utf-8')
            
            # 提取导入的能力
            imports = re.findall(r'from\s+(\S+)\s+import', content)
            imports += re.findall(r'import\s+(\S+)', content)
            
            # 提取路由映射
            route_mappings = re.findall(r'[\'"](\S+)[\'"]:\s*(\w+)', content)
            
            router_name = router_path.relative_to(self.root)
            routes[str(router_name)] = {
                "imports": imports,
                "mappings": route_mappings,
                "routed_items": set(m[0] for m in route_mappings),
            }
        
        return routes
    
    def scan_registered_capabilities(self) -> Set[str]:
        """扫描已注册的能力"""
        capabilities = set()
        
        # 从能力注册表加载
        registry_path = self.inventory_dir / "capability_registry.json"
        if registry_path.exists():
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            capabilities.update(registry.get("items", {}).keys())
        
        # 从能力目录扫描
        cap_dir = self.root / "capabilities"
        if cap_dir.exists():
            for cap_file in cap_dir.glob("*.py"):
                if not cap_file.name.startswith("_"):
                    capabilities.add(cap_file.stem)
        
        return capabilities
    
    def scan_registered_skills(self) -> Set[str]:
        """扫描已注册的技能"""
        skills = set()
        
        # 从技能注册表加载
        registry_path = self.inventory_dir / "skill_registry.json"
        if registry_path.exists():
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
            skills.update(registry.get("skills", {}).keys())
        
        # 从技能目录扫描
        skills_dir = self.root / "skills"
        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                    skills.add(skill_dir.name)
        
        return skills
    
    def check_wiring(self) -> List[Dict]:
        """检查路由接线"""
        issues = []
        
        # 扫描路由
        routes = self.scan_routes()
        
        # 扫描已注册的能力和技能
        capabilities = self.scan_registered_capabilities()
        skills = self.scan_registered_skills()
        
        # 合并所有已路由的项目
        all_routed = set()
        for router_info in routes.values():
            all_routed.update(router_info.get("routed_items", set()))
        
        # 检查能力是否已路由
        for cap in capabilities:
            if cap not in all_routed:
                # 检查是否在导入中
                imported = any(cap in r.get("imports", []) for r in routes.values())
                
                if not imported:
                    issues.append({
                        "type": "capability_not_routed",
                        "name": cap,
                        "reason": "未在路由器中配置",
                    })
        
        # 检查技能是否已路由
        for skill in skills:
            if skill not in all_routed:
                issues.append({
                    "type": "skill_not_routed",
                    "name": skill,
                    "reason": "未在路由器中配置",
                })
        
        self.results["routes"] = {k: {"imports": v["imports"], "mappings_count": len(v["mappings"])} for k, v in routes.items()}
        self.results["issues"] = issues
        self.results["stats"] = {
            "total_routes": len(routes),
            "total_capabilities": len(capabilities),
            "total_skills": len(skills),
            "routed_items": len(all_routed),
            "unrouted": len(issues),
        }
        
        return issues
    
    def run_check(self) -> Dict:
        """运行检查"""
        print("=" * 60)
        print("  路由接线检查器 V1.0.0")
        print("=" * 60)
        
        print("\n🔍 扫描路由配置...")
        issues = self.check_wiring()
        
        print(f"\n路由器: {self.results['stats']['total_routes']} 个")
        print(f"已注册能力: {self.results['stats']['total_capabilities']} 个")
        print(f"已注册技能: {self.results['stats']['total_skills']} 个")
        print(f"已路由项目: {self.results['stats']['routed_items']} 个")
        print(f"未路由: {self.results['stats']['unrouted']} 个")
        
        print("\n" + "=" * 60)
        if issues:
            print(f"  ❌ 发现 {len(issues)} 个未路由项目")
            for issue in issues[:10]:
                print(f"    - [{issue['type']}] {issue['name']}")
        else:
            print("  ✅ 所有项目已正确路由")
        print("=" * 60 + "\n")
        
        return self.results
    
    def save_report(self) -> Path:
        """保存报告"""
        report_path = self.reports_dir / f"route_wiring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 报告已保存: {report_path}")
        
        return report_path


def main():
    """主函数"""
    checker = RouteWiringChecker()
    checker.run_check()
    checker.save_report()
    
    return 0 if not checker.results["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
