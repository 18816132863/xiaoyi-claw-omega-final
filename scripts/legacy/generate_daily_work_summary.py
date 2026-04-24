#!/usr/bin/env python3
"""
每日工作总结 - V1.0.0

职责：
1. 每天下午6点生成工作总结
2. 汇总今日完成情况
3. 生成明日计划
4. 记录问题与建议

使用方式：
- python scripts/generate_daily_work_summary.py
- 由定时任务自动调用
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class DailyWorkSummary:
    """每日工作总结"""
    
    def __init__(self, root: Path):
        self.root = root
        self.reports_dir = root / "reports" / "work"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 工作记录
        self.work_log = self.reports_dir / "work_log.jsonl"
    
    def load_today_work(self) -> List[Dict]:
        """加载今日工作记录"""
        today = str(date.today())
        records = []
        
        if self.work_log.exists():
            with open(self.work_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        if record.get("date") == today:
                            records.append(record)
                    except Exception:
                        pass
        
        return records
    
    def analyze_work(self, records: List[Dict]) -> Dict:
        """分析工作情况"""
        analysis = {
            "total_tasks": len(records),
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "categories": {},
            "highlights": [],
            "issues": []
        }
        
        for record in records:
            status = record.get("status", "pending")
            if status == "completed":
                analysis["completed"] += 1
            elif status == "in_progress":
                analysis["in_progress"] += 1
            else:
                analysis["pending"] += 1
            
            # 分类统计
            category = record.get("category", "other")
            analysis["categories"][category] = analysis["categories"].get(category, 0) + 1
            
            # 亮点
            if record.get("highlight"):
                analysis["highlights"].append(record.get("task"))
            
            # 问题
            if record.get("issue"):
                analysis["issues"].append(record.get("issue"))
        
        return analysis
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成工作总结"""
        now = datetime.now()
        today = str(date.today())
        tomorrow = str(date.today() + timedelta(days=1))
        
        # 加载今日工作
        records = self.load_today_work()
        analysis = self.analyze_work(records)
        
        summary = {
            "date": today,
            "time": now.strftime("%H:%M"),
            "analysis": analysis,
            "today_summary": {
                "completed": analysis["completed"],
                "in_progress": analysis["in_progress"],
                "pending": analysis["pending"],
                "highlights": analysis["highlights"][:3],
                "issues": analysis["issues"][:3]
            },
            "tomorrow_plan": self.generate_tomorrow_plan(analysis),
            "suggestions": self.generate_suggestions(analysis)
        }
        
        return summary
    
    def generate_tomorrow_plan(self, analysis: Dict) -> List[str]:
        """生成明日计划"""
        plans = []
        
        # 未完成的任务
        if analysis["pending"] > 0:
            plans.append(f"完成 {analysis['pending']} 个待办任务")
        
        # 进行中的任务
        if analysis["in_progress"] > 0:
            plans.append(f"推进 {analysis['in_progress']} 个进行中任务")
        
        # 问题处理
        if analysis["issues"]:
            plans.append("处理今日遗留问题")
        
        # 默认计划
        if not plans:
            plans = [
                "继续推进当前工作",
                "关注用户反馈",
                "优化产品体验"
            ]
        
        return plans
    
    def generate_suggestions(self, analysis: Dict) -> List[str]:
        """生成建议"""
        suggestions = []
        
        # 完成率建议
        total = analysis["total_tasks"]
        if total > 0:
            completion_rate = analysis["completed"] / total
            if completion_rate < 0.5:
                suggestions.append("今日完成率较低，建议优先处理重要任务")
            elif completion_rate > 0.8:
                suggestions.append("今日完成率很高，继续保持！")
        
        # 问题建议
        if analysis["issues"]:
            suggestions.append("有遗留问题需要处理，建议优先解决")
        
        # 默认建议
        if not suggestions:
            suggestions = [
                "保持良好的工作节奏",
                "注意劳逸结合",
                "及时记录工作进展"
            ]
        
        return suggestions
    
    def format_message(self, summary: Dict) -> str:
        """格式化消息"""
        lines = []
        lines.append("📊 每日工作总结")
        lines.append(f"📅 {summary['date']} {summary['time']}")
        lines.append("")
        
        # 今日完成情况
        lines.append("✅ 今日完成情况")
        today = summary["today_summary"]
        lines.append(f"  已完成: {today['completed']} 项")
        lines.append(f"  进行中: {today['in_progress']} 项")
        lines.append(f"  待办: {today['pending']} 项")
        lines.append("")
        
        # 亮点
        if today["highlights"]:
            lines.append("🌟 今日亮点")
            for h in today["highlights"]:
                lines.append(f"  • {h}")
            lines.append("")
        
        # 问题
        if today["issues"]:
            lines.append("⚠️ 遗留问题")
            for i in today["issues"]:
                lines.append(f"  • {i}")
            lines.append("")
        
        # 明日计划
        lines.append("📋 明日计划")
        for p in summary["tomorrow_plan"]:
            lines.append(f"  • {p}")
        lines.append("")
        
        # 建议
        lines.append("💡 建议")
        for s in summary["suggestions"]:
            lines.append(f"  • {s}")
        lines.append("")
        
        lines.append("💪 辛苦了，明天继续加油！")
        
        return "\n".join(lines)
    
    def save_summary(self, summary: Dict):
        """保存总结记录"""
        log_file = self.reports_dir / "daily_summaries.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(summary, ensure_ascii=False) + '\n')
    
    def run(self) -> Dict:
        """运行工作总结"""
        print("=" * 60)
        print("  每日工作总结")
        print("=" * 60)
        print()
        
        summary = self.generate_summary()
        message = self.format_message(summary)
        
        print(message)
        print()
        
        # 保存记录
        self.save_summary(summary)
        
        print("✅ 工作总结已生成")
        print(f"📁 记录: {self.reports_dir / 'daily_summaries.jsonl'}")
        print()
        
        return {
            "status": "success",
            "summary": summary,
            "message": message
        }


def main():
    root = get_project_root()
    summary = DailyWorkSummary(root)
    result = summary.run()
    
    # 发送消息给用户
    if result.get("message"):
        # 导入消息发送器
        sys.path.insert(0, str(root))
        from scripts.message_sender import MessageSender
        
        # 发送消息
        MessageSender.send(result["message"], "每日工作总结")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
