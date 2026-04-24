#!/usr/bin/env python3
"""
Midday Check - 中午检查纠偏 V1.0.0

职责：
1. 检查主任务推进进度
2. 询问是否卡住
3. 决定是否切换任务或进入安全模式

使用方式：
- python scripts/run_midday_check.py
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


class MiddayCheck:
    """中午检查纠偏"""
    
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
    
    def save_json(self, path: Path, data: Any):
        """保存 JSON 文件"""
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def append_jsonl(self, path: Path, data: Dict):
        """追加 JSONL 记录"""
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def run(self) -> Dict:
        """运行中午检查"""
        print("=" * 60)
        print("  Midday Check - 中午检查纠偏 V1.0.0")
        print("=" * 60)
        print()
        
        # 1. 读取今天计划和状态
        daily_plan = self.load_json(self.live_loop_dir / "daily_plan.json")
        daily_state = self.load_json(self.live_loop_dir / "daily_state.json")
        
        if not daily_plan.get("date"):
            print("⚠️  今天还没有启动日引导")
            print("   请先运行: python scripts/run_daily_growth_loop.py")
            return {"error": "not_started"}
        
        if daily_state.get("midday_checked"):
            print("📅 今天已经做过中午检查")
            return daily_state
        
        # 2. 显示当前任务
        primary_task = daily_plan.get("primary_task", {})
        print(f"📋 当前主任务: {primary_task.get('task_name')}")
        print(f"   Workflow: {primary_task.get('workflow_id')}")
        print()
        
        # 3. 中午 4 个问题
        print("☀️ 中午检查 - 请回答以下问题：")
        print()
        
        answers = {
            "progress": "进行中",  # 默认值
            "blocked": False,
            "switch_task": False,
            "safe_mode": daily_state.get("safe_mode", False)
        }
        
        print(f"  1. 主任务进度: {answers['progress']}")
        print(f"  2. 是否卡住: {'是' if answers['blocked'] else '否'}")
        print(f"  3. 是否切换任务: {'是' if answers['switch_task'] else '否'}")
        print(f"  4. 是否进入安全模式: {'是' if answers['safe_mode'] else '否'}")
        print()
        
        # 4. 记录检查
        self.append_jsonl(
            self.live_loop_dir / "daily_checkin_log.jsonl",
            {
                "timestamp": datetime.now().isoformat(),
                "event": "midday_check",
                "answers": answers
            }
        )
        
        # 5. 生成建议
        print("=" * 60)
        print("  中午检查结果")
        print("=" * 60)
        print()
        
        if answers["blocked"]:
            print("⚠️  检测到任务卡住")
            print("   建议: 检查 workflow 执行日志，或切换到次任务")
            print()
        
        if answers["switch_task"]:
            secondary_tasks = daily_plan.get("secondary_tasks", [])
            if secondary_tasks:
                print(f"🔄 建议切换到次任务: {secondary_tasks[0].get('task_name')}")
                print()
        
        if answers["safe_mode"]:
            print("🛡️  安全模式已启用")
            print("   建议: 降低风险操作，增加人工确认")
            print()
        
        if not answers["blocked"] and not answers["switch_task"]:
            print("✅ 继续按原计划推进")
            print()
        
        # 输出后续命令
        print("=" * 60)
        print("  后续步骤")
        print("=" * 60)
        print()
        print("  晚间复盘:")
        print("    make daily-review")
        print("    python scripts/run_end_of_day_review.py")
        print()
        
        # 6. 更新状态
        daily_state["midday_checked"] = True
        daily_state["current_phase"] = "midday"
        daily_state["safe_mode"] = answers["safe_mode"]
        self.save_json(self.live_loop_dir / "daily_state.json", daily_state)
        
        return daily_state


def main():
    root = get_project_root()
    check = MiddayCheck(root)
    result = check.run()
    
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
