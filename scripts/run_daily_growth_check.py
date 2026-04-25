#!/usr/bin/env python3
"""
每日引导检查 - 心跳任务 V1.0.0

职责：
1. 检查今天是否已启动日引导
2. 检查当前时间阶段，提醒用户执行对应操作
3. 自动触发必要的引导流程

使用方式：
- python scripts/run_daily_growth_check.py
- 由心跳执行器自动调用
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date, time
from typing import Dict, Any, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class DailyGrowthCheck:
    """每日引导检查"""
    
    def __init__(self, root: Path):
        self.root = root
        self.live_loop_dir = root / "reports" / "live_loop"
    
    def load_json(self, path: Path, default: Any = None) -> Any:
        """加载 JSON 文件"""
        if path.exists():
            try:
                return json.loads(path.read_text(encoding='utf-8'))
            except Exception:
                pass
        return default if default is not None else {}
    
    def get_current_phase(self) -> str:
        """根据当前时间判断阶段"""
        now = datetime.now().time()
        
        # 早上 6:00 - 12:00
        if time(6, 0) <= now < time(12, 0):
            return "morning"
        # 中午 12:00 - 14:00
        elif time(12, 0) <= now < time(14, 0):
            return "midday"
        # 下午 14:00 - 18:00
        elif time(14, 0) <= now < time(18, 0):
            return "afternoon"
        # 晚上 18:00 - 23:00
        elif time(18, 0) <= now < time(23, 0):
            return "evening"
        # 深夜 23:00 - 6:00
        else:
            return "night"
    
    def run(self) -> Dict:
        """运行每日引导检查"""
        print("=" * 60)
        print("  每日引导检查")
        print("=" * 60)
        print()
        
        today = str(date.today())
        current_phase = self.get_current_phase()
        current_time = datetime.now().strftime("%H:%M")
        
        print(f"📅 日期: {today}")
        print(f"⏰ 时间: {current_time}")
        print(f"📍 阶段: {current_phase}")
        print()
        
        # 读取今天状态
        daily_state = self.load_json(self.live_loop_dir / "daily_state.json")
        
        # 检查今天是否已启动
        if daily_state.get("date") != today:
            print("🔔 今天还没有启动日引导")
            print()
            
            if current_phase in ["morning", "afternoon"]:
                print("💡 建议执行:")
                print("   make daily-growth-personal")
                print("   python scripts/run_daily_growth_loop.py --mode personal")
                print()
                return {
                    "status": "not_started",
                    "action": "start_daily_growth",
                    "commands": ["make daily-growth-personal"]
                }
            else:
                print("💡 当前时间较晚，建议明天早上启动")
                return {
                    "status": "not_started",
                    "action": "wait_tomorrow"
                }
        
        # 今天已启动，检查阶段
        started_phase = daily_state.get("current_phase")
        completed = daily_state.get("completed", False)
        midday_checked = daily_state.get("midday_checked", False)
        
        print(f"✅ 今天已启动日引导")
        print(f"   模式: {daily_state.get('mode')}")
        print(f"   主任务: {daily_state.get('primary_task', {}).get('task_name')}")
        print()
        
        # 检查是否已完成
        if completed:
            print("✅ 今天已完成晚间复盘")
            print()
            return {
                "status": "completed",
                "action": "none"
            }
        
        # 根据当前时间和阶段给出建议
        if current_phase == "midday" and not midday_checked:
            print("🔔 当前是中午，建议执行中午检查")
            print()
            print("💡 建议执行:")
            print("   make midday-check")
            print("   python scripts/run_midday_check.py")
            print()
            return {
                "status": "need_midday_check",
                "action": "run_midday_check",
                "commands": ["make midday-check"]
            }
        
        elif current_phase == "evening" and not completed:
            print("🔔 当前是晚上，建议执行晚间复盘")
            print()
            print("💡 建议执行:")
            print("   make daily-review")
            print("   python scripts/run_end_of_day_review.py")
            print()
            return {
                "status": "need_daily_review",
                "action": "run_daily_review",
                "commands": ["make daily-review"]
            }
        
        elif current_phase == "night":
            print("🌙 当前是深夜，建议休息")
            print("   明天早上运行: make daily-growth-personal")
            print()
            return {
                "status": "night",
                "action": "rest"
            }
        
        else:
            print(f"📍 当前阶段: {current_phase}")
            print(f"   已完成中午检查: {'是' if midday_checked else '否'}")
            print(f"   已完成晚间复盘: {'是' if completed else '否'}")
            print()
            return {
                "status": "in_progress",
                "action": "continue"
            }


def main():
    root = get_project_root()
    check = DailyGrowthCheck(root)
    result = check.run()
    
    # 返回码：0=正常，1=需要操作
    return 0 if result.get("action") in ["none", "rest", "continue"] else 0


if __name__ == "__main__":
    sys.exit(main())
