#!/usr/bin/env python3
"""
每日健康提醒 - V1.1.0

职责：
1. 每天早上9点发送健康提醒
2. 包含睡眠、运动、饮水、作息建议
3. 根据用户历史数据个性化提醒
4. V1.1.0: 集成消息发送功能

使用方式：
- python scripts/send_daily_health_reminder.py
- 由定时任务自动调用
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any, Optional

# 添加消息发送能力
sys.path.insert(0, str(Path(__file__).resolve().parent))
from send_message_helper import send_message


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class DailyHealthReminder:
    """每日健康提醒"""
    
    def __init__(self, root: Path):
        self.root = root
        self.reports_dir = root / "reports" / "health"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 健康提醒配置
        self.reminders = {
            "sleep": {
                "title": "😴 睡眠提醒",
                "tips": [
                    "昨晚睡得好吗？建议保持7-8小时睡眠",
                    "睡前1小时放下手机，让大脑放松",
                    "保持规律的作息时间，周末也不要熬夜哦",
                    "如果睡眠质量不好，可以试试睡前冥想"
                ]
            },
            "exercise": {
                "title": "🏃 运动提醒",
                "tips": [
                    "今天记得运动30分钟",
                    "久坐记得起来活动一下",
                    "可以选择散步、跑步、瑜伽等运动",
                    "运动后记得拉伸，避免肌肉酸痛"
                ]
            },
            "water": {
                "title": "💧 饮水提醒",
                "tips": [
                    "记得喝水，每天8杯水",
                    "早起一杯温水，唤醒身体",
                    "不要等口渴了再喝水",
                    "少喝含糖饮料，多喝白开水"
                ]
            },
            "schedule": {
                "title": "⏰ 作息提醒",
                "tips": [
                    "保持规律作息，早睡早起",
                    "中午可以小憩20分钟",
                    "晚上11点前入睡最佳",
                    "避免熬夜，保护肝脏"
                ]
            }
        }
    
    def get_random_tip(self, category: str) -> str:
        """获取随机提示"""
        import random
        tips = self.reminders.get(category, {}).get("tips", [])
        return random.choice(tips) if tips else ""
    
    def generate_reminder(self) -> Dict[str, Any]:
        """生成健康提醒"""
        now = datetime.now()
        today = str(date.today())
        
        reminder = {
            "date": today,
            "time": now.strftime("%H:%M"),
            "reminders": []
        }
        
        # 根据时间选择提醒内容
        hour = now.hour
        
        # 早上：睡眠 + 作息
        if 6 <= hour < 12:
            reminder["reminders"].append({
                "category": "sleep",
                "title": self.reminders["sleep"]["title"],
                "tip": self.get_random_tip("sleep"),
                "priority": "high"
            })
            reminder["reminders"].append({
                "category": "schedule",
                "title": self.reminders["schedule"]["title"],
                "tip": self.get_random_tip("schedule"),
                "priority": "medium"
            })
        
        # 中午：饮水 + 运动
        elif 12 <= hour < 14:
            reminder["reminders"].append({
                "category": "water",
                "title": self.reminders["water"]["title"],
                "tip": self.get_random_tip("water"),
                "priority": "high"
            })
            reminder["reminders"].append({
                "category": "exercise",
                "title": self.reminders["exercise"]["title"],
                "tip": self.get_random_tip("exercise"),
                "priority": "medium"
            })
        
        # 下午：运动 + 饮水
        elif 14 <= hour < 18:
            reminder["reminders"].append({
                "category": "exercise",
                "title": self.reminders["exercise"]["title"],
                "tip": self.get_random_tip("exercise"),
                "priority": "high"
            })
            reminder["reminders"].append({
                "category": "water",
                "title": self.reminders["water"]["title"],
                "tip": self.get_random_tip("water"),
                "priority": "medium"
            })
        
        # 晚上：作息 + 睡眠
        else:
            reminder["reminders"].append({
                "category": "schedule",
                "title": self.reminders["schedule"]["title"],
                "tip": self.get_random_tip("schedule"),
                "priority": "high"
            })
            reminder["reminders"].append({
                "category": "sleep",
                "title": self.reminders["sleep"]["title"],
                "tip": self.get_random_tip("sleep"),
                "priority": "medium"
            })
        
        return reminder
    
    def format_message(self, reminder: Dict) -> str:
        """格式化消息"""
        lines = []
        lines.append("🌅 每日健康提醒")
        lines.append(f"📅 {reminder['date']} {reminder['time']}")
        lines.append("")
        
        for r in reminder["reminders"]:
            lines.append(f"{r['title']}")
            lines.append(f"  {r['tip']}")
            lines.append("")
        
        lines.append("💪 保持健康，从每一天开始！")
        
        return "\n".join(lines)
    
    def save_reminder(self, reminder: Dict):
        """保存提醒记录"""
        log_file = self.reports_dir / "daily_reminders.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(reminder, ensure_ascii=False) + '\n')
    
    def run(self) -> Dict:
        """运行健康提醒"""
        print("=" * 60)
        print("  每日健康提醒 V1.1.0")
        print("=" * 60)
        print()
        
        reminder = self.generate_reminder()
        message = self.format_message(reminder)
        
        print(message)
        print()
        
        # 保存记录
        self.save_reminder(reminder)
        
        # V1.1.0: 发送消息给用户
        send_result = send_message(
            title="🌅 每日健康提醒",
            content=message
        )
        
        print("✅ 健康提醒已生成")
        print(f"📁 记录: {self.reports_dir / 'daily_reminders.jsonl'}")
        print(f"📤 消息: {send_result.get('status')}")
        print()
        
        return {
            "status": "success",
            "reminder": reminder,
            "message": message,
            "send_result": send_result
        }


def main():
    root = get_project_root()
    reminder = DailyHealthReminder(root)
    result = reminder.run()
    
    # V1.1.0: 消息已在 run() 中发送
    # 这里只需返回状态
    
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
