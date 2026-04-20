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
            },
            # 新增定时任务
            {
                "id": "daily_health_reminder",
                "name": "每日健康提醒",
                "pattern": "time:daily:09:00",
                "action": "health_reminder",
                "command": [sys.executable, str(root / "scripts/send_daily_health_reminder.py")],
                "enabled": True
            },
            {
                "id": "daily_work_summary",
                "name": "每日工作总结",
                "pattern": "time:daily:18:00",
                "action": "work_summary",
                "command": [sys.executable, str(root / "scripts/generate_daily_work_summary.py")],
                "enabled": True
            },
            {
                "id": "weekly_skill_report",
                "name": "每周技能报告",
                "pattern": "time:weekly:monday:09:00",
                "action": "skill_report",
                "command": [sys.executable, str(root / "scripts/generate_weekly_skill_report.py")],
                "enabled": True
            },
            # 高优先级任务
            {
                "id": "nightly_audit",
                "name": "夜间巡检",
                "pattern": "time:daily:02:00",
                "action": "nightly_audit",
                "command": [sys.executable, str(root / "scripts/run_nightly_audit.py")],
                "enabled": True
            },
            {
                "id": "full_backup",
                "name": "全面备份",
                "pattern": "time:weekly:sunday:03:00",
                "action": "full_backup",
                "command": [sys.executable, str(root / "scripts/full_backup.py")],
                "enabled": True
            },
            # 中优先级任务
            {
                "id": "report_cleanup",
                "name": "报告清理",
                "pattern": "time:daily:03:00",
                "action": "cleanup_reports",
                "command": [sys.executable, str(root / "scripts/cleanup_reports.py")],
                "enabled": True
            },
            {
                "id": "skill_health_check",
                "name": "技能健康检查",
                "pattern": "time:weekly:monday:10:00",
                "action": "check_skill_health",
                "command": [sys.executable, str(root / "scripts/skill_health_check.py")],
                "enabled": True
            },
            {
                "id": "dependency_check",
                "name": "依赖更新检查",
                "pattern": "time:weekly:monday:08:00",
                "action": "check_dependencies",
                "command": [sys.executable, str(root / "scripts/dependency_manager.py"), "--check"],
                "enabled": True
            },
            # 低优先级任务
            {
                "id": "ai_api_check",
                "name": "AI API 状态检查",
                "pattern": "time:daily:08:00",
                "action": "check_ai_apis",
                "command": [sys.executable, str(root / "scripts/check_ai_apis.py")],
                "enabled": True
            },
            # 第二阶段任务
            {
                "id": "midday_check",
                "name": "中午检查",
                "pattern": "time:daily:12:00",
                "action": "midday_check",
                "command": [sys.executable, str(root / "scripts/run_midday_check.py")],
                "enabled": True
            },
            {
                "id": "end_of_day_review",
                "name": "晚间复盘",
                "pattern": "time:daily:21:00",
                "action": "end_of_day_review",
                "command": [sys.executable, str(root / "scripts/run_end_of_day_review.py")],
                "enabled": True
            },
            {
                "id": "control_plane_audit",
                "name": "控制平面审计",
                "pattern": "time:daily:04:00",
                "action": "control_plane_audit",
                "command": [sys.executable, str(root / "scripts/control_plane_audit.py")],
                "enabled": True
            },
            {
                "id": "json_contract_check",
                "name": "JSON 契约检查",
                "pattern": "time:daily:05:00",
                "action": "check_json_contracts",
                "command": [sys.executable, str(root / "scripts/check_json_contracts.py")],
                "enabled": True
            },
            {
                "id": "continuous_improvement",
                "name": "持续改进",
                "pattern": "time:daily:06:00",
                "action": "continuous_improvement",
                "command": [sys.executable, str(root / "scripts/continuous_improvement.py")],
                "enabled": True
            },
            {
                "id": "exception_management",
                "name": "异常管理",
                "pattern": "time:daily:07:00",
                "action": "exception_management",
                "command": [sys.executable, str(root / "scripts/exception_manager.py")],
                "enabled": True
            },
            {
                "id": "auto_classify_skills",
                "name": "技能自动分类",
                "pattern": "time:weekly:monday:11:00",
                "action": "auto_classify_skills",
                "command": [sys.executable, str(root / "scripts/auto_classify_skills.py")],
                "enabled": True
            },
            {
                "id": "repo_integrity_check",
                "name": "仓库完整性检查",
                "pattern": "time:weekly:saturday:03:00",
                "action": "check_repo_integrity",
                "command": [sys.executable, str(root / "scripts/check_repo_integrity.py")],
                "enabled": True
            },
            {
                "id": "layer_dependency_check",
                "name": "层间依赖检查",
                "pattern": "time:weekly:saturday:04:00",
                "action": "check_layer_dependencies",
                "command": [sys.executable, str(root / "scripts/check_layer_dependencies.py")],
                "enabled": True
            },
            {
                "id": "deep_inspection",
                "name": "深度巡检",
                "pattern": "time:weekly:sunday:02:00",
                "action": "deep_inspection",
                "command": [sys.executable, str(root / "scripts/deep_inspection.py")],
                "enabled": True
            },
            # 第三阶段任务 - 新发现
            {
                "id": "backup_cleanup",
                "name": "备份清理",
                "pattern": "time:daily:01:00",
                "action": "backup_cleanup",
                "command": [sys.executable, str(root / "skills/backup-cleaner/cleaner.py")],
                "enabled": True
            },
            {
                "id": "vector_optimization",
                "name": "向量系统优化",
                "pattern": "time:weekly:sunday:04:00",
                "action": "vector_optimization",
                "command": [sys.executable, str(root / "skills/llm-memory-integration/src/scripts/vector_system_optimizer.py")],
                "enabled": True
            },
            {
                "id": "session_cleanup",
                "name": "会话清理",
                "pattern": "time:daily:00:00",
                "action": "session_cleanup",
                "command": [sys.executable, str(root / "scripts/cleanup_sessions.py")],
                "enabled": True
            },
            {
                "id": "cache_cleanup",
                "name": "缓存清理",
                "pattern": "time:daily:00:30",
                "action": "cache_cleanup",
                "command": [sys.executable, str(root / "scripts/cleanup_cache.py")],
                "enabled": True
            },
            {
                "id": "skill_usage_stats",
                "name": "技能使用统计",
                "pattern": "time:daily:23:00",
                "action": "skill_usage_stats",
                "command": [sys.executable, str(root / "scripts/generate_skill_usage_stats.py")],
                "enabled": True
            },
            {
                "id": "system_health_report",
                "name": "系统健康报告",
                "pattern": "time:daily:22:00",
                "action": "system_health_report",
                "command": [sys.executable, str(root / "scripts/generate_system_health_report.py")],
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
        now = datetime.now()
        current_time = now.time()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_weekday = date.today().weekday()  # 0=周一, 6=周日
        
        # 调试日志
        print(f"  当前时间: {current_hour:02d}:{current_minute:02d}")
        print(f"  今日已触发: {today_triggered}")
        print(f"  本周已触发: {week_triggered}")
        print()
        
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
        if current_weekday == 0 and "weekly_first_start" not in week_triggered:
            triggers.append({
                "id": "weekly_first_start",
                "name": "每周首次启动",
                "action": "weekly_review",
                "command": [sys.executable, str(self.root / "scripts/run_weekly_growth_review.py")],
                "reason": "本周首次运行"
            })
        
        # === 每日任务 ===
        
        # 夜间巡检 (02:00)
        if "nightly_audit" not in today_triggered:
            if current_hour == 2:  # 扩大到整个小时
                triggers.append({
                    "id": "nightly_audit",
                    "name": "夜间巡检",
                    "action": "nightly_audit",
                    "command": [sys.executable, str(self.root / "scripts/run_nightly_audit.py")],
                    "reason": "夜间巡检时间 (02:00)"
                })
        
        # 报告清理 (03:00)
        if "report_cleanup" not in today_triggered:
            if current_hour == 3:  # 扩大到整个小时
                triggers.append({
                    "id": "report_cleanup",
                    "name": "报告清理",
                    "action": "cleanup_reports",
                    "command": [sys.executable, str(self.root / "scripts/cleanup_reports.py")],
                    "reason": "报告清理时间 (03:00)"
                })
        
        # AI API 检查 (08:00)
        if "ai_api_check" not in today_triggered:
            if current_hour == 8:  # 扩大到整个小时
                triggers.append({
                    "id": "ai_api_check",
                    "name": "AI API 状态检查",
                    "action": "check_ai_apis",
                    "command": [sys.executable, str(self.root / "scripts/check_ai_apis.py")],
                    "reason": "AI API 检查时间 (08:00)"
                })
        
        # 每日健康提醒 (09:00)
        if "daily_health_reminder" not in today_triggered:
            if current_hour == 9:  # 扩大到整个小时
                triggers.append({
                    "id": "daily_health_reminder",
                    "name": "每日健康提醒",
                    "action": "health_reminder",
                    "command": [sys.executable, str(self.root / "scripts/send_daily_health_reminder.py")],
                    "reason": "每日健康提醒时间 (09:00)"
                })
        
        # 每日工作总结 (18:00)
        if "daily_work_summary" not in today_triggered:
            if current_hour == 18:  # 扩大到整个小时
                triggers.append({
                    "id": "daily_work_summary",
                    "name": "每日工作总结",
                    "action": "work_summary",
                    "command": [sys.executable, str(self.root / "scripts/generate_daily_work_summary.py")],
                    "reason": "每日工作总结时间 (18:00)"
                })
        
        # === 每周任务 (周一) ===
        
        if current_weekday == 0:
            # 依赖更新检查 (08:00)
            if "dependency_check" not in week_triggered:
                if current_hour == 8 and current_minute < 30:
                    triggers.append({
                        "id": "dependency_check",
                        "name": "依赖更新检查",
                        "action": "check_dependencies",
                        "command": [sys.executable, str(self.root / "scripts/dependency_manager.py"), "--check"],
                        "reason": "依赖更新检查时间 (周一 08:00)"
                    })
            
            # 每周技能报告 (09:00)
            if "weekly_skill_report" not in week_triggered:
                if current_hour == 9 and current_minute < 30:
                    triggers.append({
                        "id": "weekly_skill_report",
                        "name": "每周技能报告",
                        "action": "skill_report",
                        "command": [sys.executable, str(self.root / "scripts/generate_weekly_skill_report.py")],
                        "reason": "每周技能报告时间 (周一 09:00)"
                    })
            
            # 技能健康检查 (10:00)
            if "skill_health_check" not in week_triggered:
                if current_hour == 10 and current_minute < 30:
                    triggers.append({
                        "id": "skill_health_check",
                        "name": "技能健康检查",
                        "action": "check_skill_health",
                        "command": [sys.executable, str(self.root / "scripts/skill_health_check.py")],
                        "reason": "技能健康检查时间 (周一 10:00)"
                    })
        
        # === 每周任务 (周日) ===
        
        if current_weekday == 6:
            # 深度巡检 (02:00)
            if "deep_inspection" not in week_triggered:
                if current_hour == 2 and current_minute < 30:
                    triggers.append({
                        "id": "deep_inspection",
                        "name": "深度巡检",
                        "action": "deep_inspection",
                        "command": [sys.executable, str(self.root / "scripts/deep_inspection.py")],
                        "reason": "深度巡检时间 (周日 02:00)"
                    })
            
            # 全面备份 (03:00)
            if "full_backup" not in week_triggered:
                if current_hour == 3 and current_minute < 30:
                    triggers.append({
                        "id": "full_backup",
                        "name": "全面备份",
                        "action": "full_backup",
                        "command": [sys.executable, str(self.root / "scripts/full_backup.py")],
                        "reason": "全面备份时间 (周日 03:00)"
                    })
        
        # === 每周任务 (周六) ===
        
        if current_weekday == 5:
            # 仓库完整性检查 (03:00)
            if "repo_integrity_check" not in week_triggered:
                if current_hour == 3 and current_minute < 30:
                    triggers.append({
                        "id": "repo_integrity_check",
                        "name": "仓库完整性检查",
                        "action": "check_repo_integrity",
                        "command": [sys.executable, str(self.root / "scripts/check_repo_integrity.py")],
                        "reason": "仓库完整性检查时间 (周六 03:00)"
                    })
            
            # 层间依赖检查 (04:00)
            if "layer_dependency_check" not in week_triggered:
                if current_hour == 4 and current_minute < 30:
                    triggers.append({
                        "id": "layer_dependency_check",
                        "name": "层间依赖检查",
                        "action": "check_layer_dependencies",
                        "command": [sys.executable, str(self.root / "scripts/check_layer_dependencies.py")],
                        "reason": "层间依赖检查时间 (周六 04:00)"
                    })
        
        # === 更多每日任务 ===
        
        # 控制平面审计 (04:00)
        if "control_plane_audit" not in today_triggered:
            if current_hour == 4 and current_minute < 30:
                triggers.append({
                    "id": "control_plane_audit",
                    "name": "控制平面审计",
                    "action": "control_plane_audit",
                    "command": [sys.executable, str(self.root / "scripts/control_plane_audit.py")],
                    "reason": "控制平面审计时间 (04:00)"
                })
        
        # JSON 契约检查 (05:00)
        if "json_contract_check" not in today_triggered:
            if current_hour == 5 and current_minute < 30:
                triggers.append({
                    "id": "json_contract_check",
                    "name": "JSON 契约检查",
                    "action": "check_json_contracts",
                    "command": [sys.executable, str(self.root / "scripts/check_json_contracts.py")],
                    "reason": "JSON 契约检查时间 (05:00)"
                })
        
        # 持续改进 (06:00)
        if "continuous_improvement" not in today_triggered:
            if current_hour == 6 and current_minute < 30:
                triggers.append({
                    "id": "continuous_improvement",
                    "name": "持续改进",
                    "action": "continuous_improvement",
                    "command": [sys.executable, str(self.root / "scripts/continuous_improvement.py")],
                    "reason": "持续改进时间 (06:00)"
                })
        
        # 异常管理 (07:00)
        if "exception_management" not in today_triggered:
            if current_hour == 7 and current_minute < 30:
                triggers.append({
                    "id": "exception_management",
                    "name": "异常管理",
                    "action": "exception_management",
                    "command": [sys.executable, str(self.root / "scripts/exception_manager.py")],
                    "reason": "异常管理时间 (07:00)"
                })
        
        # 中午检查 (12:00)
        if "midday_check" not in today_triggered:
            if current_hour == 12 and current_minute < 30:
                triggers.append({
                    "id": "midday_check",
                    "name": "中午检查",
                    "action": "midday_check",
                    "command": [sys.executable, str(self.root / "scripts/run_midday_check.py")],
                    "reason": "中午检查时间 (12:00)"
                })
        
        # 晚间复盘 (21:00)
        if "end_of_day_review" not in today_triggered:
            if current_hour == 21:  # 扩大到整个小时
                triggers.append({
                    "id": "end_of_day_review",
                    "name": "晚间复盘",
                    "action": "end_of_day_review",
                    "command": [sys.executable, str(self.root / "scripts/run_end_of_day_review.py")],
                    "reason": "晚间复盘时间 (21:00)"
                })
        
        # === 第三阶段任务 ===
        
        # 会话清理 (00:00)
        if "session_cleanup" not in today_triggered:
            if current_hour == 0:  # 扩大到整个小时
                triggers.append({
                    "id": "session_cleanup",
                    "name": "会话清理",
                    "action": "session_cleanup",
                    "command": [sys.executable, str(self.root / "scripts/cleanup_sessions.py")],
                    "reason": "会话清理时间 (00:00)"
                })
        
        # 缓存清理 (00:30) - 特殊处理，保持在 00:30-00:59
        if "cache_cleanup" not in today_triggered:
            if current_hour == 0 and current_minute >= 30:
                triggers.append({
                    "id": "cache_cleanup",
                    "name": "缓存清理",
                    "action": "cache_cleanup",
                    "command": [sys.executable, str(self.root / "scripts/cleanup_cache.py")],
                    "reason": "缓存清理时间 (00:30)"
                })
        
        # 备份清理 (01:00)
        if "backup_cleanup" not in today_triggered:
            if current_hour == 1:  # 扩大到整个小时
                triggers.append({
                    "id": "backup_cleanup",
                    "name": "备份清理",
                    "action": "backup_cleanup",
                    "command": [sys.executable, str(self.root / "skills/backup-cleaner/cleaner.py")],
                    "reason": "备份清理时间 (01:00)"
                })
        
        # 系统健康报告 (22:00)
        if "system_health_report" not in today_triggered:
            if current_hour == 22:  # 扩大到整个小时
                triggers.append({
                    "id": "system_health_report",
                    "name": "系统健康报告",
                    "action": "system_health_report",
                    "command": [sys.executable, str(self.root / "scripts/generate_system_health_report.py")],
                    "reason": "系统健康报告时间 (22:00)"
                })
        
        # 技能使用统计 (23:00)
        if "skill_usage_stats" not in today_triggered:
            if current_hour == 23:  # 扩大到整个小时
                triggers.append({
                    "id": "skill_usage_stats",
                    "name": "技能使用统计",
                    "action": "skill_usage_stats",
                    "command": [sys.executable, str(self.root / "scripts/generate_skill_usage_stats.py")],
                    "reason": "技能使用统计时间 (23:00)"
                })
        
        # === 每周任务 (周日) - 向量优化 ===
        
        if current_weekday == 6:
            # 向量系统优化 (04:00)
            if "vector_optimization" not in week_triggered:
                if current_hour == 4 and current_minute < 30:
                    triggers.append({
                        "id": "vector_optimization",
                        "name": "向量系统优化",
                        "action": "vector_optimization",
                        "command": [sys.executable, str(self.root / "skills/llm-memory-integration/src/scripts/vector_system_optimizer.py")],
                        "reason": "向量系统优化时间 (周日 04:00)"
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
