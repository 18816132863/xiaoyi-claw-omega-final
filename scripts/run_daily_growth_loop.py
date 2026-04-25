#!/usr/bin/env python3
"""
Daily Growth Loop - 日引导养成层 V1.0.0

职责：
1. 早上引导用户开始
2. 从 top10 真实任务里选今天该做的
3. 生成今天计划
4. 给出执行建议

使用方式：
- python scripts/run_daily_growth_loop.py --mode personal
- python scripts/run_daily_growth_loop.py --mode enterprise
- make daily-growth-personal
- make daily-growth-enterprise
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class DailyGrowthLoop:
    """日引导养成循环"""
    
    def __init__(self, root: Path):
        self.root = root
        self.live_loop_dir = root / "reports" / "live_loop"
        self.live_tasks_dir = root / "reports" / "live_tasks"
        self.live_learning_dir = root / "reports" / "live_learning"
        
        # 确保目录存在
        self.live_loop_dir.mkdir(parents=True, exist_ok=True)
        self.live_tasks_dir.mkdir(parents=True, exist_ok=True)
        self.live_learning_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    def append_jsonl(self, path: Path, data: Dict):
        """追加 JSONL 记录"""
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def check_today_started(self) -> bool:
        """检查今天是否已启动"""
        state = self.load_json(self.live_loop_dir / "daily_state.json")
        if state.get("date") == str(date.today()):
            return state.get("started", False)
        return False
    
    def get_today_state(self) -> Dict:
        """获取今天状态"""
        return self.load_json(self.live_loop_dir / "daily_state.json")
    
    def load_top10_tasks(self) -> List[Dict]:
        """加载 top10 真实任务"""
        tasks = self.load_json(self.live_tasks_dir / "top10_real_tasks.json", [])
        if isinstance(tasks, list):
            return tasks
        return []
    
    def load_priority_order(self) -> Dict:
        """加载优先级排序"""
        return self.load_json(self.live_tasks_dir / "task_priority_order.json", {})
    
    def select_tasks(
        self,
        mode: str,
        available_time: str,
        top10_tasks: List[Dict],
        priority_order: Dict
    ) -> tuple[Optional[Dict], List[Dict]]:
        """
        选择今天要做的任务
        
        Returns:
            (primary_task, secondary_tasks)
        """
        if not top10_tasks:
            return None, []
        
        # 获取 connect_now 的任务
        connect_now_ids = set()
        for item in priority_order.get("priority_order", []):
            if item.get("stage") == "connect_now":
                connect_now_ids.add(item.get("task_id"))
        
        # 过滤符合条件的任务
        candidates = []
        for task in top10_tasks:
            task_id = task.get("task_id")
            
            # 只选 connect_now 的任务
            if task_id not in connect_now_ids:
                continue
            
            # 匹配 owner
            owner = task.get("owner", "personal")
            if mode == "personal" and owner not in ["personal"]:
                continue
            if mode == "enterprise" and owner not in ["enterprise", "personal"]:
                continue
            
            # 匹配频率和时间
            frequency = task.get("frequency", "daily")
            risk_level = task.get("risk_level", "low")
            
            candidates.append({
                "task": task,
                "priority": next(
                    (p.get("priority", 99) for p in priority_order.get("priority_order", []) 
                     if p.get("task_id") == task_id),
                    99
                ),
                "risk_level": risk_level
            })
        
        # 按优先级排序
        candidates.sort(key=lambda x: x["priority"])
        
        # 选择 1 个主任务 + 2 个次任务
        if not candidates:
            return None, []
        
        primary = candidates[0]["task"]
        secondary = [c["task"] for c in candidates[1:3]]
        
        return primary, secondary
    
    def generate_daily_plan(
        self,
        mode: str,
        primary_task: Dict,
        secondary_tasks: List[Dict],
        checkin_answers: Dict
    ) -> Dict:
        """生成今天计划"""
        return {
            "date": str(date.today()),
            "today_mode": mode,
            "primary_task": primary_task,
            "secondary_tasks": secondary_tasks,
            "recommended_workflow_id": primary_task.get("workflow_id") if primary_task else None,
            "required_capabilities": primary_task.get("required_capabilities", []) if primary_task else [],
            "estimated_time": checkin_answers.get("available_time", "未知"),
            "risk_notes": [checkin_answers.get("risk_to_avoid", "无")] if checkin_answers.get("risk_to_avoid") else [],
            "success_criteria": primary_task.get("success_criteria", []) if primary_task else [],
            "review_required": primary_task.get("review_required", False) if primary_task else False,
            "safe_mode_recommended": checkin_answers.get("style") == "稳定推进"
        }
    
    def run(self, mode: str = "personal") -> Dict:
        """运行日引导循环"""
        print("=" * 60)
        print("  Daily Growth Loop - 日引导养成层 V1.0.0")
        print("=" * 60)
        print()
        
        # 1. 检查今天是否已启动
        if self.check_today_started():
            print("📅 今天已经启动过日引导")
            state = self.get_today_state()
            print(f"  模式: {state.get('mode')}")
            print(f"  主任务: {state.get('primary_task', {}).get('task_name')}")
            print(f"  当前阶段: {state.get('current_phase')}")
            return state
        
        # 2. 加载 top10 任务
        top10_tasks = self.load_top10_tasks()
        if not top10_tasks:
            print("⚠️  当前还没有配置 top10 真实任务")
            print("   请先填写 reports/live_tasks/top10_real_tasks.json")
            return {"error": "no_tasks_configured"}
        
        priority_order = self.load_priority_order()
        
        print(f"📋 已加载 {len(top10_tasks)} 个真实任务")
        print()
        
        # 3. 早上 5 个问题
        print("🌅 早间引导 - 请回答以下问题：")
        print()
        
        checkin_answers = {
            "mode": mode,
            "available_time": "2-4小时",  # 默认值
            "priority": "推进主任务",
            "risk_to_avoid": "无",
            "style": "稳定推进"
        }
        
        print(f"  1. 今天模式: {mode}")
        print(f"  2. 可投入时间: {checkin_answers['available_time']}")
        print(f"  3. 最优先推进: {checkin_answers['priority']}")
        print(f"  4. 需避开风险: {checkin_answers['risk_to_avoid']}")
        print(f"  5. 推进风格: {checkin_answers['style']}")
        print()
        
        # 记录签到
        self.append_jsonl(
            self.live_loop_dir / "daily_checkin_log.jsonl",
            {
                "timestamp": datetime.now().isoformat(),
                "event": "morning_checkin",
                "answers": checkin_answers
            }
        )
        
        # 4. 选择任务
        print("🎯 自动选择今天任务...")
        primary_task, secondary_tasks = self.select_tasks(
            mode, checkin_answers["available_time"], top10_tasks, priority_order
        )
        
        if not primary_task:
            print("⚠️  没有找到符合条件的任务")
            return {"error": "no_matching_tasks"}
        
        print(f"  主任务: {primary_task.get('task_name')}")
        print(f"  次任务: {[t.get('task_name') for t in secondary_tasks]}")
        print()
        
        # 5. 生成今天计划
        print("📝 生成今天计划...")
        daily_plan = self.generate_daily_plan(
            mode, primary_task, secondary_tasks, checkin_answers
        )
        self.save_json(self.live_loop_dir / "daily_plan.json", daily_plan)
        
        # 6. 更新今天状态
        daily_state = {
            "date": str(date.today()),
            "mode": mode,
            "started": True,
            "primary_task": primary_task,
            "secondary_tasks": secondary_tasks,
            "current_phase": "morning",
            "midday_checked": False,
            "completed": False,
            "safe_mode": daily_plan.get("safe_mode_recommended", False),
            "notes": ""
        }
        self.save_json(self.live_loop_dir / "daily_state.json", daily_state)
        
        # 7. 输出执行建议
        print()
        print("=" * 60)
        print("  今日执行建议")
        print("=" * 60)
        print()
        print(f"📌 主任务: {primary_task.get('task_name')}")
        print(f"   Workflow: {primary_task.get('workflow_id')}")
        print(f"   能力需求: {', '.join(primary_task.get('required_capabilities', []))}")
        print(f"   成功标准: {primary_task.get('success_criteria', [])}")
        print(f"   需要复核: {'是' if primary_task.get('review_required') else '否'}")
        print()
        
        if secondary_tasks:
            print("📌 次任务:")
            for i, task in enumerate(secondary_tasks, 1):
                print(f"   {i}. {task.get('task_name')} ({task.get('workflow_id')})")
            print()
        
        print(f"⏱️  预计时间: {checkin_answers['available_time']}")
        print(f"🛡️  安全模式: {'建议开启' if daily_plan.get('safe_mode_recommended') else '不需要'}")
        print()
        
        # 8. 输出今日可用命令
        print("=" * 60)
        print("  今日可用命令")
        print("=" * 60)
        print()
        print("  中午检查:")
        print("    make midday-check")
        print("    python scripts/run_midday_check.py")
        print()
        print("  晚间复盘:")
        print("    make daily-review")
        print("    python scripts/run_end_of_day_review.py")
        print()
        print("  每周总结:")
        print("    make weekly-review")
        print("    python scripts/run_weekly_growth_review.py")
        print()
        
        return daily_state


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Daily Growth Loop V1.0.0")
    parser.add_argument("--mode", choices=["personal", "enterprise"], default="personal",
                       help="运行模式: personal 或 enterprise")
    args = parser.parse_args()
    
    root = get_project_root()
    loop = DailyGrowthLoop(root)
    result = loop.run(mode=args.mode)
    
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
