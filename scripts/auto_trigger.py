#!/usr/bin/env python3
"""
自动触发器 - V1.0.0

职责：
1. 监听文件变更，自动触发对应任务
2. 支持多种触发场景
3. 与现有系统无缝集成

触发场景：
- 新增 .py 文件 → 技能安全检查
- 修改 core/ 文件 → 架构巡检
- 修改 governance/ 文件 → 规则检查
- 每日首次启动 → 日引导
- 每周首次启动 → 周复盘

使用方式：
- python scripts/auto_trigger.py
- 由心跳执行器自动调用
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class AutoTrigger:
    """自动触发器"""
    
    def __init__(self, root: Path):
        self.root = root
        self.reports_dir = root / "reports" / "ops"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 触发记录
        self.trigger_log = self.reports_dir / "auto_trigger_log.jsonl"
        
        # 触发规则
        self.trigger_rules = [
            {
                "id": "new_python_file",
                "name": "新增 Python 文件",
                "pattern": "*.py",
                "action": "skill_security_check",
                "command": [sys.executable, str(root / "scripts/check_skill_security.py"), "--scan-new"],
                "enabled": True
            },
            {
                "id": "core_file_change",
                "name": "Core 文件变更",
                "pattern": "core/**/*",
                "action": "architecture_inspection",
                "command": [sys.executable, str(root / "scripts/unified_inspector_v7.py"), "--quick"],
                "enabled": True
            },
            {
                "id": "governance_file_change",
                "name": "Governance 文件变更",
                "pattern": "governance/**/*",
                "action": "rule_check",
                "command": [sys.executable, str(root / "scripts/run_rule_engine.py"), "--profile", "premerge"],
                "enabled": True
            },
            {
                "id": "daily_first_start",
                "name": "每日首次启动",
                "pattern": "time:daily",
                "action": "daily_growth",
                "command": [sys.executable, str(root / "scripts/run_daily_growth_check.py")],
                "enabled": True
            },
            {
                "id": "weekly_first_start",
                "name": "每周首次启动",
                "pattern": "time:weekly",
                "action": "weekly_review",
                "command": [sys.executable, str(root / "scripts/run_weekly_growth_review.py")],
                "enabled": True
            }
        ]
    
    def log_trigger(self, trigger_id: str, action: str, result: str):
        """记录触发日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "trigger_id": trigger_id,
            "action": action,
            "result": result
        }
        with open(self.trigger_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_today_triggers(self) -> List[str]:
        """获取今天已触发的任务"""
        triggered = []
        if self.trigger_log.exists():
            today = str(date.today())
            with open(self.trigger_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("timestamp", "").startswith(today):
                            triggered.append(entry.get("trigger_id"))
                    except Exception:
                        pass
        return triggered
    
    def get_week_triggers(self) -> List[str]:
        """获取本周已触发的任务"""
        triggered = []
        if self.trigger_log.exists():
            week_start = str(date.today() - timedelta(days=date.today().weekday()))
            with open(self.trigger_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("timestamp", "") >= week_start:
                            triggered.append(entry.get("trigger_id"))
                    except Exception:
                        pass
        return triggered
    
    def get_git_changed_files(self) -> List[str]:
        """获取 Git 变更文件"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1'],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except Exception:
            pass
        return []
    
    def match_pattern(self, filepath: str, pattern: str) -> bool:
        """匹配文件模式"""
        if pattern.startswith("time:"):
            return False  # 时间模式单独处理
        
        # 简单的 glob 匹配
        import fnmatch
        return fnmatch.fnmatch(filepath, pattern) or fnmatch.fnmatch(Path(filepath).name, pattern)
    
    def run_command(self, command: List[str], timeout: int = 60) -> tuple[bool, str]:
        """运行命令"""
        try:
            result = subprocess.run(
                command,
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout[-500:] if result.stdout else ""
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
    
    def check_time_triggers(self) -> List[Dict]:
        """检查时间触发"""
        triggers = []
        today_triggered = self.get_today_triggers()
        week_triggered = self.get_week_triggers()
        
        # 每日首次启动
        if "daily_first_start" not in today_triggered:
            triggers.append({
                "id": "daily_first_start",
                "name": "每日首次启动",
                "action": "daily_growth",
                "command": [sys.executable, str(self.root / "scripts/run_daily_growth_check.py")],
                "reason": "今天首次运行"
            })
        
        # 每周首次启动 (周一)
        if date.today().weekday() == 0 and "weekly_first_start" not in week_triggered:
            triggers.append({
                "id": "weekly_first_start",
                "name": "每周首次启动",
                "action": "weekly_review",
                "command": [sys.executable, str(self.root / "scripts/run_weekly_growth_review.py")],
                "reason": "本周首次运行"
            })
        
        return triggers
    
    def check_file_triggers(self) -> List[Dict]:
        """检查文件变更触发"""
        triggers = []
        changed_files = self.get_git_changed_files()
        
        if not changed_files:
            return triggers
        
        for rule in self.trigger_rules:
            if rule["id"].startswith("time:"):
                continue
            
            # 检查是否有匹配的文件
            matched_files = [f for f in changed_files if self.match_pattern(f, rule["pattern"])]
            
            if matched_files:
                triggers.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "action": rule["action"],
                    "command": rule["command"],
                    "reason": f"文件变更: {matched_files[:3]}{'...' if len(matched_files) > 3 else ''}"
                })
        
        return triggers
    
    def run(self) -> Dict:
        """运行自动触发器"""
        print("=" * 60)
        print("  自动触发器 V1.0.0")
        print("=" * 60)
        print()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "time_triggers": [],
            "file_triggers": [],
            "executed": [],
            "skipped": []
        }
        
        # 1. 检查时间触发
        print("⏰ 检查时间触发...")
        time_triggers = self.check_time_triggers()
        results["time_triggers"] = time_triggers
        
        if time_triggers:
            for t in time_triggers:
                print(f"   - {t['name']}: {t['reason']}")
        else:
            print("   无时间触发")
        print()
        
        # 2. 检查文件触发
        print("📁 检查文件触发...")
        file_triggers = self.check_file_triggers()
        results["file_triggers"] = file_triggers
        
        if file_triggers:
            for t in file_triggers:
                print(f"   - {t['name']}: {t['reason']}")
        else:
            print("   无文件触发")
        print()
        
        # 3. 执行触发
        all_triggers = time_triggers + file_triggers
        
        if not all_triggers:
            print("✅ 无需触发任何任务")
            return results
        
        print("=" * 60)
        print("  执行触发任务")
        print("=" * 60)
        print()
        
        for trigger in all_triggers:
            print(f"🔧 [{trigger['id']}] {trigger['name']}...")
            
            success, output = self.run_command(trigger["command"])
            
            if success:
                print(f"   ✅ 成功")
                self.log_trigger(trigger["id"], trigger["action"], "success")
                results["executed"].append(trigger["id"])
            else:
                print(f"   ❌ 失败: {output[:100]}")
                self.log_trigger(trigger["id"], trigger["action"], f"failed: {output[:100]}")
                results["skipped"].append(trigger["id"])
            
            print()
        
        return results


def main():
    root = get_project_root()
    trigger = AutoTrigger(root)
    result = trigger.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
