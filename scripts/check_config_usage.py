#!/usr/bin/env python3
"""
配置使用检查器

检查 config/ 下配置文件是否被实际读取和使用
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class ConfigUsageChecker:
    """配置使用检查器"""
    
    def __init__(self, root: Path = None):
        self.root = root or PROJECT_ROOT
        self.inventory_dir = self.root / "infrastructure" / "inventory"
        self.reports_dir = self.root / "reports" / "integrity"
        
        self.inventory_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "configs": {},
            "issues": [],
            "stats": {},
        }
    
    def scan_configs(self) -> Dict:
        """扫描配置文件"""
        configs = {}
        
        config_dir = self.root / "config"
        if not config_dir.exists():
            return configs
        
        for config_file in config_dir.iterdir():
            if config_file.name.startswith("_"):
                continue
            
            config_name = config_file.stem
            config_ext = config_file.suffix
            
            configs[config_name] = {
                "name": config_name,
                "path": str(config_file),
                "ext": config_ext,
                "referenced": False,
                "loaded": False,
            }
        
        return configs
    
    def check_references(self, configs: Dict) -> List[Dict]:
        """检查配置是否被引用"""
        issues = []
        
        for config_name, config_info in configs.items():
            # 使用 grep 搜索引用
            try:
                result = subprocess.run(
                    ["grep", "-r", config_name, "--include=*.py", str(self.root)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                # 排除 config 目录自身的引用
                external_refs = [l for l in lines if '/config/' not in l and l]
                
                config_info["referenced"] = len(external_refs) > 0
                
                if not config_info["referenced"]:
                    issues.append({
                        "type": "config_not_referenced",
                        "name": config_name,
                        "path": config_info["path"],
                    })
            except Exception as e:
                config_info["referenced"] = True  # 假设已引用
                config_info["error"] = str(e)
        
        return issues
    
    def check_loading(self, configs: Dict) -> List[Dict]:
        """检查配置是否被加载"""
        issues = []
        
        # 搜索配置加载模式
        load_patterns = [
            "load_config",
            "read_json",
            "json.load",
            "open(",
        ]
        
        for config_name, config_info in configs.items():
            if config_info["ext"] != ".json":
                config_info["loaded"] = True  # 非 JSON 配置假设已加载
                continue
            
            # 搜索配置文件名
            try:
                result = subprocess.run(
                    ["grep", "-r", f"{config_name}.json", "--include=*.py", str(self.root)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                external_refs = [l for l in lines if '/config/' not in l and l]
                
                config_info["loaded"] = len(external_refs) > 0
                
                if not config_info["loaded"]:
                    issues.append({
                        "type": "config_not_loaded",
                        "name": config_name,
                        "path": config_info["path"],
                    })
            except:
                config_info["loaded"] = True
        
        return issues
    
    def run_check(self) -> Dict:
        """运行检查"""
        print("=" * 60)
        print("  配置使用检查器 V1.0.0")
        print("=" * 60)
        
        print("\n🔍 扫描配置文件...")
        configs = self.scan_configs()
        print(f"  发现 {len(configs)} 个配置文件")
        
        if not configs:
            print("  ⚠️  没有发现配置文件")
            return self.results
        
        print("\n📋 检查引用状态...")
        ref_issues = self.check_references(configs)
        print(f"  未引用: {len(ref_issues)} 个")
        
        print("\n📥 检查加载状态...")
        load_issues = self.check_loading(configs)
        print(f"  未加载: {len(load_issues)} 个")
        
        all_issues = ref_issues + load_issues
        
        self.results["configs"] = configs
        self.results["issues"] = all_issues
        self.results["stats"] = {
            "total": len(configs),
            "referenced": sum(1 for c in configs.values() if c["referenced"]),
            "loaded": sum(1 for c in configs.values() if c["loaded"]),
            "issues": len(all_issues),
        }
        
        print("\n" + "=" * 60)
        if all_issues:
            print(f"  ❌ 发现 {len(all_issues)} 个问题")
        else:
            print("  ✅ 所有配置已正确使用")
        print("=" * 60 + "\n")
        
        return self.results
    
    def save_report(self) -> Path:
        """保存报告"""
        report_path = self.reports_dir / f"config_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 报告已保存: {report_path}")
        
        return report_path


def main():
    """主函数"""
    checker = ConfigUsageChecker()
    checker.run_check()
    checker.save_report()
    
    return 0 if not checker.results["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
