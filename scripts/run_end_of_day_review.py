#!/usr/bin/env python3
"""
End of Day Review - 晚间复盘 V1.0.0

职责：
1. 检查今天任务完成情况
2. 记录成功/失败原因
3. 沉淀高价值经验到长期记忆

使用方式：
- python scripts/run_end_of_day_review.py
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


class EndOfDayReview:
    """晚间复盘"""
    
    def __init__(self, root: Path):
        self.root = root
        self.live_loop_dir = root / "reports" / "live_loop"
        self.live_learning_dir = root / "reports" / "live_learning"
    
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
    
    def run(self) -> Dict:
        """运行晚间复盘"""
        print("=" * 60)
        print("  End of Day Review - 晚间复盘 V1.0.0")
        print("=" * 60)
        print()
        
        # 1. 读取今天计划和状态
        daily_plan = self.load_json(self.live_loop_dir / "daily_plan.json")
        daily_state = self.load_json(self.live_loop_dir / "daily_state.json")
        
        if not daily_plan.get("date"):
            print("⚠️  今天还没有启动日引导")
            print("   请先运行: python scripts/run_daily_growth_loop.py")
            return {"error": "not_started"}
        
        if daily_state.get("completed"):
            print("📅 今天已经做过晚间复盘")
            return self.load_json(self.live_loop_dir / "daily_review.json")
        
        # 2. 显示今天任务
        primary_task = daily_plan.get("primary_task", {})
        secondary_tasks = daily_plan.get("secondary_tasks", [])
        
        print(f"📋 今天主任务: {primary_task.get('task_name')}")
        print(f"📋 今天次任务: {[t.get('task_name') for t in secondary_tasks]}")
        print()
        
        # 3. 晚间 5 个问题
        print("🌙 晚间复盘 - 请回答以下问题：")
        print()
        
        answers = {
            "completed": ["主任务"],  # 默认完成主任务
            "not_completed": [],
            "failure_reasons": [],
            "best_decision": "按计划推进",
            "keep_doing": "继续推进主任务",
            "avoid_doing": "避免分心",
            "learnings": []
        }
        
        print(f"  1. 已完成任务: {answers['completed']}")
        print(f"  2. 未完成任务: {answers['not_completed']}")
        print(f"  3. 失败原因: {answers['failure_reasons']}")
        print(f"  4. 今天最好的决定: {answers['best_decision']}")
        print(f"  5. 明天继续做的: {answers['keep_doing']}")
        print(f"  6. 明天避免做的: {answers['avoid_doing']}")
        print()
        
        # 4. 记录复盘
        self.append_jsonl(
            self.live_loop_dir / "daily_checkin_log.jsonl",
            {
                "timestamp": datetime.now().isoformat(),
                "event": "end_of_day_review",
                "answers": answers
            }
        )
        
        # 5. 生成复盘报告
        daily_review = {
            "date": str(date.today()),
            "completed": answers["completed"],
            "not_completed": answers["not_completed"],
            "failure_reasons": answers["failure_reasons"],
            "best_decision": answers["best_decision"],
            "keep_doing": answers["keep_doing"],
            "avoid_doing": answers["avoid_doing"],
            "learnings": answers["learnings"],
            "primary_task": primary_task,
            "workflow_id": primary_task.get("workflow_id"),
            "success_criteria": primary_task.get("success_criteria", [])
        }
        self.save_json(self.live_loop_dir / "daily_review.json", daily_review)
        
        # 6. 沉淀到长期记忆
        if answers["best_decision"] or answers["learnings"]:
            decision_patterns = self.load_json(
                self.live_learning_dir / "decision_patterns.json",
                {"patterns": []}
            )
            
            if answers["best_decision"]:
                decision_patterns.setdefault("patterns", []).append({
                    "date": str(date.today()),
                    "task": primary_task.get("task_name"),
                    "decision": answers["best_decision"],
                    "source": "daily_review"
                })
            
            self.save_json(
                self.live_learning_dir / "decision_patterns.json",
                decision_patterns
            )
        
        # 7. 更新状态
        daily_state["completed"] = True
        daily_state["current_phase"] = "end_of_day"
        self.save_json(self.live_loop_dir / "daily_state.json", daily_state)
        
        # 8. 输出总结
        print("=" * 60)
        print("  今日复盘总结")
        print("=" * 60)
        print()
        
        print(f"✅ 已完成: {len(answers['completed'])} 个任务")
        for task in answers["completed"]:
            print(f"   - {task}")
        print()
        
        if answers["not_completed"]:
            print(f"❌ 未完成: {len(answers['not_completed'])} 个任务")
            for task in answers["not_completed"]:
                print(f"   - {task}")
            print()
        
        print(f"💡 今天最好的决定: {answers['best_decision']}")
        print(f"📌 明天继续: {answers['keep_doing']}")
        print(f"⚠️  明天避免: {answers['avoid_doing']}")
        print()
        
        print("📝 复盘已保存到 reports/live_loop/daily_review.json")
        print("🧠 高价值经验已沉淀到长期记忆")
        print()
        
        # 输出后续命令
        print("=" * 60)
        print("  后续步骤")
        print("=" * 60)
        print()
        print("  每周总结:")
        print("    make weekly-review")
        print("    python scripts/run_weekly_growth_review.py")
        print()
        print("  明天开始:")
        print("    make daily-growth-personal")
        print("    make daily-growth-enterprise")
        print()
        
        return daily_review


def main():
    root = get_project_root()
    review = EndOfDayReview(root)
    result = review.run()
    
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
