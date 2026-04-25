#!/usr/bin/env python3
"""
技能版本检查脚本
检查已安装技能的版本状态
"""

import json
from pathlib import Path
from datetime import datetime

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILLS_DIR = WORKSPACE / "skills"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

class SkillVersionChecker:
    """技能版本检查器"""
    
    def __init__(self):
        self.skills = []
    
    def scan_skills(self):
        """扫描所有技能"""
        if not SKILLS_DIR.exists():
            return []
        
        skills = []
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                skill_info = self._get_skill_info(skill_dir)
                skills.append(skill_info)
        
        return skills
    
    def _get_skill_info(self, skill_dir):
        """获取技能信息"""
        info = {
            "name": skill_dir.name,
            "path": str(skill_dir),
            "has_skill_md": (skill_dir / "SKILL.md").exists(),
            "has_config": False,
            "version": "unknown",
            "last_modified": None
        }
        
        # 检查配置文件
        config_files = list(skill_dir.glob("*.json"))
        if config_files:
            info["has_config"] = True
            for cf in config_files:
                try:
                    config = json.loads(cf.read_text())
                    if "version" in config:
                        info["version"] = config["version"]
                        break
                except Exception as e:
                    pass
            logger.error(f"操作失败: {e}")
        
        # 获取最后修改时间
        try:
            stat = skill_dir.stat()
            info["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        except Exception as e:
            logger.error(f"操作失败: {e}")
        
        return info
    
    def check_versions(self):
        """检查版本状态"""
        self.skills = self.scan_skills()
        return self.skills
    
    def print_report(self):
        """打印版本报告"""
        print("=" * 60)
        print("   技能版本报告")
        print("=" * 60)
        print(f"检查时间: {datetime.now().isoformat()}")
        print()
        
        if not self.skills:
            print("未找到技能")
            return
        
        print(f"技能总数: {len(self.skills)}")
        print()
        
        # 按状态分类
        complete = [s for s in self.skills if s["has_skill_md"] and s["has_config"]]
        incomplete = [s for s in self.skills if not (s["has_skill_md"] and s["has_config"])]
        
        if complete:
            print(f"✅ 完整技能 ({len(complete)}):")
            for s in complete[:10]:
                print(f"   - {s['name']} (v{s['version']})")
            if len(complete) > 10:
                print(f"   ... 还有 {len(complete) - 10} 个")
        
        if incomplete:
            print()
            print(f"⚠️ 不完整技能 ({len(incomplete)}):")
            for s in incomplete[:5]:
                missing = []
                if not s["has_skill_md"]:
                    missing.append("SKILL.md")
                if not s["has_config"]:
                    missing.append("config")
                print(f"   - {s['name']} (缺少: {', '.join(missing)})")

def main():
    checker = SkillVersionChecker()
    checker.check_versions()
    checker.print_report()

if __name__ == "__main__":
    main()
