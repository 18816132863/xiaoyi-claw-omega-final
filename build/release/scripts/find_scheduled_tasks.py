#!/usr/bin/env python3
"""
定时任务发现器 - V1.0.0

自动发现架构中所有需要定时执行的任务
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class ScheduledTaskFinder:
    """定时任务发现器"""
    
    def __init__(self, root: Path):
        self.root = root
        self.findings = defaultdict(list)
    
    def find_scripts_with_keywords(self) -> Dict[str, List[str]]:
        """查找包含定时关键词的脚本"""
        keywords = [
            'schedule', 'cron', 'timer', 'periodic',
            'daily', 'weekly', 'monthly', 'hourly',
            '定时', '定期', '自动', '监控', '巡检',
            'cleanup', 'backup', 'audit', 'check',
            'monitor', 'refresh', 'sync', 'update'
        ]
        
        results = defaultdict(list)
        scripts_dir = self.root / "scripts"
        
        if not scripts_dir.exists():
            return results
        
        for script in scripts_dir.glob("*.py"):
            try:
                content = script.read_text(encoding='utf-8', errors='ignore')
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        results[keyword].append(str(script.name))
                        break
            except Exception:
                pass
        
        return results
    
    def find_skills_with_scheduled_tasks(self) -> Dict[str, List[str]]:
        """查找包含定时任务的技能"""
        keywords = [
            'daily', 'weekly', 'schedule', 'cron',
            '定时', '定期', '自动', '监控'
        ]
        
        results = defaultdict(list)
        skills_dir = self.root / "skills"
        
        if not skills_dir.exists():
            return results
        
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            # 检查 SKILL.md
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                try:
                    content = skill_md.read_text(encoding='utf-8', errors='ignore')
                    for keyword in keywords:
                        if keyword.lower() in content.lower():
                            results[skill_dir.name].append(f"SKILL.md contains '{keyword}'")
                            break
                except Exception:
                    pass
            
            # 检查 skill.py
            skill_py = skill_dir / "skill.py"
            if skill_py.exists():
                try:
                    content = skill_py.read_text(encoding='utf-8', errors='ignore')
                    for keyword in keywords:
                        if keyword.lower() in content.lower():
                            results[skill_dir.name].append(f"skill.py contains '{keyword}'")
                            break
                except Exception:
                    pass
        
        return results
    
    def find_docs_with_scheduled_tasks(self) -> Dict[str, List[str]]:
        """查找文档中提到的定时任务"""
        keywords = [
            '定时', '定期', '自动', '监控', '巡检',
            'schedule', 'cron', 'timer', 'periodic',
            'daily', 'weekly', 'monthly'
        ]
        
        results = defaultdict(list)
        docs_dir = self.root / "docs"
        
        if not docs_dir.exists():
            return results
        
        for doc in docs_dir.glob("**/*.md"):
            try:
                content = doc.read_text(encoding='utf-8', errors='ignore')
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        results[str(doc.relative_to(self.root))] = f"contains '{keyword}'"
                        break
            except Exception:
                pass
        
        return results
    
    def analyze_existing_scheduled_tasks(self) -> Dict[str, Any]:
        """分析现有的定时任务"""
        # 读取 auto_trigger.py
        auto_trigger = self.root / "scripts" / "auto_trigger.py"
        existing_tasks = []
        
        if auto_trigger.exists():
            try:
                content = auto_trigger.read_text(encoding='utf-8', errors='ignore')
                # 提取 trigger_rules 中的任务
                pattern = r'"id":\s*"([^"]+)"'
                matches = re.findall(pattern, content)
                existing_tasks = list(set(matches))
            except Exception:
                pass
        
        # 读取 HEARTBEAT.md
        heartbeat = self.root / "HEARTBEAT.md"
        heartbeat_tasks = []
        
        if heartbeat.exists():
            try:
                content = heartbeat.read_text(encoding='utf-8', errors='ignore')
                # 提取任务列表
                lines = content.split('\n')
                for line in lines:
                    if '|' in line and ('自动' in line or 'auto' in line.lower()):
                        heartbeat_tasks.append(line.strip())
            except Exception:
                pass
        
        return {
            "auto_trigger_tasks": existing_tasks,
            "heartbeat_tasks": heartbeat_tasks
        }
    
    def suggest_new_tasks(self) -> List[Dict[str, str]]:
        """建议新的定时任务"""
        suggestions = []
        
        # 基于脚本分析
        scripts_with_keywords = self.find_scripts_with_keywords()
        
        for keyword, scripts in scripts_with_keywords.items():
            for script in scripts:
                # 检查是否已在 auto_trigger 中
                existing = self.analyze_existing_scheduled_tasks()
                if script.replace('.py', '') not in existing.get("auto_trigger_tasks", []):
                    suggestions.append({
                        "script": script,
                        "keyword": keyword,
                        "reason": f"脚本包含关键词 '{keyword}'，可能需要定时执行"
                    })
        
        return suggestions
    
    def run(self) -> Dict[str, Any]:
        """运行发现器"""
        print("=" * 60)
        print("  定时任务发现器 V1.0.0")
        print("=" * 60)
        print()
        
        # 1. 分析现有任务
        print("📋 分析现有定时任务...")
        existing = self.analyze_existing_scheduled_tasks()
        print(f"   auto_trigger.py: {len(existing['auto_trigger_tasks'])} 个任务")
        print(f"   HEARTBEAT.md: {len(existing['heartbeat_tasks'])} 个任务")
        print()
        
        # 2. 查找脚本
        print("🔍 查找包含定时关键词的脚本...")
        scripts = self.find_scripts_with_keywords()
        total_scripts = sum(len(v) for v in scripts.values())
        print(f"   找到 {total_scripts} 个相关脚本")
        for keyword, script_list in scripts.items():
            if script_list:
                print(f"   - {keyword}: {len(script_list)} 个")
        print()
        
        # 3. 查找技能
        print("🎯 查找包含定时任务的技能...")
        skills = self.find_skills_with_scheduled_tasks()
        print(f"   找到 {len(skills)} 个相关技能")
        for skill, reasons in list(skills.items())[:5]:
            print(f"   - {skill}")
        if len(skills) > 5:
            print(f"   ... 还有 {len(skills) - 5} 个")
        print()
        
        # 4. 查找文档
        print("📄 查找文档中提到的定时任务...")
        docs = self.find_docs_with_scheduled_tasks()
        print(f"   找到 {len(docs)} 个相关文档")
        for doc in list(docs.keys())[:5]:
            print(f"   - {doc}")
        if len(docs) > 5:
            print(f"   ... 还有 {len(docs) - 5} 个")
        print()
        
        # 5. 建议新任务
        print("💡 建议新的定时任务...")
        suggestions = self.suggest_new_tasks()
        print(f"   找到 {len(suggestions)} 个建议")
        for s in suggestions[:10]:
            print(f"   - {s['script']} ({s['keyword']})")
        if len(suggestions) > 10:
            print(f"   ... 还有 {len(suggestions) - 10} 个建议")
        print()
        
        return {
            "existing_tasks": existing,
            "scripts_with_keywords": scripts,
            "skills_with_scheduled_tasks": skills,
            "docs_with_scheduled_tasks": docs,
            "suggestions": suggestions
        }


def main():
    root = get_project_root()
    finder = ScheduledTaskFinder(root)
    result = finder.run()
    
    # 保存结果
    import json
    output = root / "reports" / "ops" / "scheduled_tasks_discovery.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"📁 结果已保存: {output}")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
