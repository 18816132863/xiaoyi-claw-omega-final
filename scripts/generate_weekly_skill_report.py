#!/usr/bin/env python3
"""
每周技能报告 - V1.0.0

职责：
1. 每周一早上生成技能报告
2. 统计技能使用情况
3. 展示热门技能排行
4. 提供优化建议

使用方式：
- python scripts/generate_weekly_skill_report.py
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


class WeeklySkillReport:
    """每周技能报告"""
    
    def __init__(self, root: Path):
        self.root = root
        self.reports_dir = root / "reports" / "skills"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 技能注册表
        self.skill_registry = root / "infrastructure" / "inventory" / "skill_registry.json"
        
        # 技能使用日志
        self.skill_log = self.reports_dir / "skill_usage.jsonl"
    
    def load_skill_registry(self) -> Dict:
        """加载技能注册表"""
        if self.skill_registry.exists():
            try:
                return json.loads(self.skill_registry.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {"skills": []}
    
    def load_weekly_usage(self) -> List[Dict]:
        """加载本周技能使用记录"""
        records = []
        week_start = date.today() - timedelta(days=date.today().weekday())
        
        if self.skill_log.exists():
            with open(self.skill_log, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        record_date = datetime.fromisoformat(record.get("timestamp", "")).date()
                        if record_date >= week_start:
                            records.append(record)
                    except Exception:
                        pass
        
        return records
    
    def analyze_usage(self, records: List[Dict]) -> Dict:
        """分析技能使用情况"""
        analysis = {
            "total_calls": len(records),
            "unique_skills": set(),
            "skill_calls": {},
            "category_calls": {},
            "success_rate": 0,
            "success_count": 0,
            "fail_count": 0
        }
        
        for record in records:
            skill_id = record.get("skill_id", "unknown")
            category = record.get("category", "other")
            success = record.get("success", False)
            
            analysis["unique_skills"].add(skill_id)
            analysis["skill_calls"][skill_id] = analysis["skill_calls"].get(skill_id, 0) + 1
            analysis["category_calls"][category] = analysis["category_calls"].get(category, 0) + 1
            
            if success:
                analysis["success_count"] += 1
            else:
                analysis["fail_count"] += 1
        
        analysis["unique_skills"] = len(analysis["unique_skills"])
        
        if analysis["total_calls"] > 0:
            analysis["success_rate"] = analysis["success_count"] / analysis["total_calls"]
        
        return analysis
    
    def get_top_skills(self, skill_calls: Dict, limit: int = 10) -> List[Dict]:
        """获取热门技能"""
        sorted_skills = sorted(skill_calls.items(), key=lambda x: x[1], reverse=True)
        return [{"skill_id": s[0], "calls": s[1]} for s in sorted_skills[:limit]]
    
    def generate_report(self) -> Dict[str, Any]:
        """生成技能报告"""
        now = datetime.now()
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_end = week_start + timedelta(days=6)
        
        # 加载数据
        registry = self.load_skill_registry()
        usage_records = self.load_weekly_usage()
        analysis = self.analyze_usage(usage_records)
        
        report = {
            "week": f"{week_start} ~ {week_end}",
            "generated_at": now.isoformat(),
            "total_skills": len(registry.get("skills", [])),
            "usage_analysis": {
                "total_calls": analysis["total_calls"],
                "unique_skills": analysis["unique_skills"],
                "success_rate": f"{analysis['success_rate']:.1%}",
                "success_count": analysis["success_count"],
                "fail_count": analysis["fail_count"]
            },
            "top_skills": self.get_top_skills(analysis["skill_calls"]),
            "category_distribution": analysis["category_calls"],
            "suggestions": self.generate_suggestions(analysis)
        }
        
        return report
    
    def generate_suggestions(self, analysis: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 成功率建议
        if analysis["success_rate"] < 0.9:
            suggestions.append("技能调用成功率较低，建议检查失败原因")
        elif analysis["success_rate"] > 0.95:
            suggestions.append("技能调用成功率很高，继续保持！")
        
        # 使用频率建议
        if analysis["total_calls"] < 10:
            suggestions.append("本周技能使用较少，可以尝试更多功能")
        elif analysis["total_calls"] > 100:
            suggestions.append("本周技能使用频繁，系统运行良好")
        
        # 默认建议
        if not suggestions:
            suggestions = [
                "继续探索新技能",
                "关注技能使用体验",
                "及时反馈问题"
            ]
        
        return suggestions
    
    def format_message(self, report: Dict) -> str:
        """格式化消息"""
        lines = []
        lines.append("📊 每周技能报告")
        lines.append(f"📅 {report['week']}")
        lines.append("")
        
        # 技能统计
        lines.append("📈 技能统计")
        lines.append(f"  总技能数: {report['total_skills']}")
        usage = report["usage_analysis"]
        lines.append(f"  本周调用: {usage['total_calls']} 次")
        lines.append(f"  使用技能: {usage['unique_skills']} 个")
        lines.append(f"  成功率: {usage['success_rate']}")
        lines.append("")
        
        # 热门技能
        if report["top_skills"]:
            lines.append("🔥 热门技能 TOP 10")
            for i, skill in enumerate(report["top_skills"], 1):
                lines.append(f"  {i}. {skill['skill_id']} ({skill['calls']} 次)")
            lines.append("")
        
        # 分类分布
        if report["category_distribution"]:
            lines.append("📂 分类分布")
            for category, count in sorted(report["category_distribution"].items(), key=lambda x: x[1], reverse=True)[:5]:
                lines.append(f"  • {category}: {count} 次")
            lines.append("")
        
        # 建议
        lines.append("💡 优化建议")
        for s in report["suggestions"]:
            lines.append(f"  • {s}")
        lines.append("")
        
        lines.append("🚀 新的一周，继续探索更多可能！")
        
        return "\n".join(lines)
    
    def save_report(self, report: Dict):
        """保存报告记录"""
        log_file = self.reports_dir / "weekly_reports.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(report, ensure_ascii=False) + '\n')
    
    def run(self) -> Dict:
        """运行技能报告"""
        print("=" * 60)
        print("  每周技能报告")
        print("=" * 60)
        print()
        
        report = self.generate_report()
        message = self.format_message(report)
        
        print(message)
        print()
        
        # 保存记录
        self.save_report(report)
        
        print("✅ 技能报告已生成")
        print(f"📁 记录: {self.reports_dir / 'weekly_reports.jsonl'}")
        print()
        
        return {
            "status": "success",
            "report": report,
            "message": message
        }


def main():
    root = get_project_root()
    report = WeeklySkillReport(root)
    result = report.run()
    
    # 发送消息给用户
    if result.get("message"):
        # 导入消息发送器
        sys.path.insert(0, str(root))
        from scripts.message_sender import MessageSender
        
        # 发送消息
        MessageSender.send(result["message"], "每周技能报告")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
