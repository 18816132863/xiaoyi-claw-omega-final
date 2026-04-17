#!/usr/bin/env python3
"""
Weekly Growth Review - 每周成长复盘 V1.0.0

职责：
1. 汇总过去 7 天的执行情况
2. 分析任务成功率
3. 给出下周建议

使用方式：
- python scripts/run_weekly_growth_review.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class WeeklyGrowthReview:
    """每周成长复盘"""
    
    def __init__(self, root: Path):
        self.root = root
        self.live_loop_dir = root / "reports" / "live_loop"
        self.live_tasks_dir = root / "reports" / "live_tasks"
    
    def load_json(self, path: Path, default: Any = None) -> Any:
        """加载 JSON 文件"""
        if path.exists():
            try:
                return json.loads(path.read_text(encoding='utf-8'))
            except Exception:
                pass
        return default if default is not None else {}
    
    def save_json(self, path: Path, data: Any):
        """保存 JSON 文件"""
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def get_week_range(self) -> tuple[str, str]:
        """获取本周日期范围"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # 周一
        week_end = week_start + timedelta(days=6)  # 周日
        return str(week_start), str(week_end)
    
    def run(self) -> Dict:
        """运行每周复盘"""
        print("=" * 60)
        print("  Weekly Growth Review - 每周成长复盘 V1.0.0")
        print("=" * 60)
        print()
        
        week_start, week_end = self.get_week_range()
        print(f"📅 本周: {week_start} ~ {week_end}")
        print()
        
        # 1. 读取 top10 任务
        top10_tasks = self.load_json(self.live_tasks_dir / "top10_real_tasks.json", [])
        priority_order = self.load_json(self.live_tasks_dir / "task_priority_order.json", {})
        
        # 2. 读取本周复盘（模拟数据，实际应读取过去 7 天的 daily_review）
        # 这里用当前 daily_review 作为示例
        daily_review = self.load_json(self.live_loop_dir / "daily_review.json")
        daily_plan = self.load_json(self.live_loop_dir / "daily_plan.json")
        
        # 3. 统计任务执行情况
        task_stats = {}
        for task in top10_tasks:
            task_id = task.get("task_id")
            task_stats[task_id] = {
                "task_name": task.get("task_name"),
                "frequency": task.get("frequency"),
                "risk_level": task.get("risk_level"),
                "executed_count": 0,
                "success_count": 0,
                "failure_count": 0
            }
        
        # 模拟统计（实际应从 daily_review 历史记录统计）
        if daily_plan.get("primary_task"):
            primary_id = daily_plan["primary_task"].get("task_id")
            if primary_id in task_stats:
                task_stats[primary_id]["executed_count"] = 1
                if daily_review.get("completed"):
                    task_stats[primary_id]["success_count"] = 1
                else:
                    task_stats[primary_id]["failure_count"] = 1
        
        # 4. 分析结果
        most_frequent = sorted(
            task_stats.items(),
            key=lambda x: x[1]["executed_count"],
            reverse=True
        )[:3]
        
        highest_success = sorted(
            [(k, v) for k, v in task_stats.items() if v["executed_count"] > 0],
            key=lambda x: x[1]["success_count"] / max(x[1]["executed_count"], 1),
            reverse=True
        )[:3]
        
        most_failed = sorted(
            [(k, v) for k, v in task_stats.items() if v["failure_count"] > 0],
            key=lambda x: x[1]["failure_count"],
            reverse=True
        )[:3]
        
        # 5. 生成周报
        weekly_review = {
            "week_start": week_start,
            "week_end": week_end,
            "most_frequent_tasks": [
                {"task_id": k, "task_name": v["task_name"], "count": v["executed_count"]}
                for k, v in most_frequent if v["executed_count"] > 0
            ],
            "highest_success_tasks": [
                {"task_id": k, "task_name": v["task_name"], "rate": v["success_count"] / max(v["executed_count"], 1)}
                for k, v in highest_success
            ],
            "most_failed_tasks": [
                {"task_id": k, "task_name": v["task_name"], "count": v["failure_count"]}
                for k, v in most_failed
            ],
            "workflows_to_optimize": [],
            "skills_to_upgrade": [],
            "skills_to_downgrade": [],
            "next_week_priorities": []
        }
        
        # 6. 生成下周建议
        connect_now_tasks = [
            item for item in priority_order.get("priority_order", [])
            if item.get("stage") == "connect_now"
        ]
        
        weekly_review["next_week_priorities"] = [
            {
                "task_id": item.get("task_id"),
                "priority": item.get("priority"),
                "why": item.get("why_now", "")
            }
            for item in connect_now_tasks[:3]
        ]
        
        self.save_json(self.live_loop_dir / "weekly_review.json", weekly_review)
        
        # 7. 输出周报
        print("=" * 60)
        print("  本周总结")
        print("=" * 60)
        print()
        
        print("📊 任务执行统计:")
        print(f"   总任务数: {len(top10_tasks)}")
        print(f"   本周执行: {sum(v['executed_count'] for v in task_stats.values())} 次")
        print()
        
        if weekly_review["most_frequent_tasks"]:
            print("📈 最常执行任务:")
            for task in weekly_review["most_frequent_tasks"]:
                print(f"   - {task['task_name']}: {task['count']} 次")
            print()
        
        if weekly_review["highest_success_tasks"]:
            print("✅ 成功率最高任务:")
            for task in weekly_review["highest_success_tasks"]:
                print(f"   - {task['task_name']}: {task['rate']*100:.0f}%")
            print()
        
        if weekly_review["most_failed_tasks"]:
            print("❌ 失败最多任务:")
            for task in weekly_review["most_failed_tasks"]:
                print(f"   - {task['task_name']}: {task['count']} 次")
            print()
        
        print("=" * 60)
        print("  下周建议")
        print("=" * 60)
        print()
        
        if weekly_review["next_week_priorities"]:
            print("🎯 优先接入任务:")
            for i, task in enumerate(weekly_review["next_week_priorities"], 1):
                print(f"   {i}. {task['task_id']} (优先级 {task['priority']})")
                print(f"      原因: {task['why']}")
            print()
        
        print("📝 周报已保存到 reports/live_loop/weekly_review.json")
        print()
        
        # 输出下周开始命令
        print("=" * 60)
        print("  下周开始")
        print("=" * 60)
        print()
        print("  周一早上:")
        print("    make daily-growth-personal")
        print("    make daily-growth-enterprise")
        print()
        
        return weekly_review


def main():
    root = get_project_root()
    review = WeeklyGrowthReview(root)
    result = review.run()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
