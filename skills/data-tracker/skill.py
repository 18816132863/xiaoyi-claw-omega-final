#!/usr/bin/env python3
"""
Data Tracker - 数据记录与复盘系统 V1.0.0

功能：
1. 记录用户数据
2. 每日汇总
3. 生成复盘报告
4. 沉淀到长期记忆
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import re


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class DataTracker:
    """数据记录器"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.data_dir = self.root / "reports" / "live_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据文件
        self.records_file = self.data_dir / "daily_records.jsonl"
        self.summary_file = self.data_dir / "daily_summary.json"
        self.goals_file = self.data_dir / "goals.json"
        
        # 默认目标
        self.default_goals = {
            "sleep": {"target": 8, "unit": "hours"},
            "exercise": {"target": 30, "unit": "minutes"},
            "reading": {"target": 30, "unit": "pages"},
            "water": {"target": 8, "unit": "cups"},
            "steps": {"target": 10000, "unit": "steps"}
        }
        
        # 数据类型映射
        self.type_keywords = {
            "sleep": ["睡眠", "睡觉", "睡", "sleep"],
            "exercise": ["运动", "锻炼", "健身", "跑步", "exercise"],
            "reading": ["阅读", "读书", "看书", "reading"],
            "water": ["喝水", "饮水", "water"],
            "steps": ["步数", "步", "steps"],
            "weight": ["体重", "weight"],
            "mood": ["心情", "情绪", "mood"],
            "work": ["工作", "上班", "work"],
            "writing": ["写作", "写字", "writing"]
        }
    
    def load_goals(self) -> Dict:
        """加载目标"""
        if self.goals_file.exists():
            return json.loads(self.goals_file.read_text(encoding='utf-8'))
        return self.default_goals
    
    def save_goals(self, goals: Dict):
        """保存目标"""
        self.goals_file.write_text(json.dumps(goals, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def parse_data(self, text: str) -> List[Dict]:
        """解析用户输入的数据"""
        records = []
        
        # 匹配模式: "睡眠7小时", "运动30分钟", "阅读20页"
        patterns = [
            r"(睡眠|睡觉|睡)\s*(\d+\.?\d*)\s*(小时|时|h)?",
            r"(运动|锻炼|健身|跑步)\s*(\d+\.?\d*)\s*(分钟|分|min)?",
            r"(阅读|读书|看书)\s*(\d+\.?\d*)\s*(页|张)?",
            r"(喝水|饮水)\s*(\d+\.?\d*)\s*(杯|ml|毫升)?",
            r"(步数|步)\s*(\d+\.?\d*)\s*(步)?",
            r"(体重)\s*(\d+\.?\d*)\s*(kg|公斤|斤)?",
            r"(心情|情绪)\s*(\d+\.?\d*)\s*(分)?",
            r"(工作|上班)\s*(\d+\.?\d*)\s*(小时|时|h)?",
            r"(写作|写字)\s*(\d+\.?\d*)\s*(字)?",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                data_type = self._normalize_type(match[0])
                value = float(match[1])
                unit = match[2] if len(match) > 2 else self._get_default_unit(data_type)
                
                records.append({
                    "type": data_type,
                    "value": value,
                    "unit": self._normalize_unit(unit, data_type)
                })
        
        return records
    
    def _normalize_type(self, type_text: str) -> str:
        """标准化数据类型"""
        type_text = type_text.lower()
        for data_type, keywords in self.type_keywords.items():
            if any(kw in type_text for kw in keywords):
                return data_type
        return type_text
    
    def _normalize_unit(self, unit: str, data_type: str) -> str:
        """标准化单位"""
        unit_map = {
            "小时": "hours", "时": "hours", "h": "hours",
            "分钟": "minutes", "分": "minutes", "min": "minutes",
            "页": "pages", "张": "pages",
            "杯": "cups", "ml": "ml", "毫升": "ml",
            "步": "steps",
            "kg": "kg", "公斤": "kg", "斤": "jin",
            "分": "score",
            "字": "chars"
        }
        return unit_map.get(unit, unit)
    
    def _get_default_unit(self, data_type: str) -> str:
        """获取默认单位"""
        units = {
            "sleep": "hours",
            "exercise": "minutes",
            "reading": "pages",
            "water": "cups",
            "steps": "steps",
            "weight": "kg",
            "mood": "score",
            "work": "hours",
            "writing": "chars"
        }
        return units.get(data_type, "unknown")
    
    def record(self, text: str, note: str = "") -> Dict:
        """记录数据"""
        records = self.parse_data(text)
        
        if not records:
            return {"success": False, "message": "未识别到有效数据"}
        
        now = datetime.now()
        today = str(date.today())
        
        # 写入记录
        for record in records:
            entry = {
                "timestamp": now.isoformat(),
                "date": today,
                "type": record["type"],
                "value": record["value"],
                "unit": record["unit"],
                "note": note,
                "source": "user_input"
            }
            
            with open(self.records_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        # 更新今日汇总
        self._update_summary(today)
        
        return {
            "success": True,
            "records": records,
            "message": f"已记录 {len(records)} 项数据"
        }
    
    def _update_summary(self, today: str):
        """更新今日汇总"""
        summary = self._load_summary()
        
        if summary.get("date") != today:
            summary = {"date": today, "data": {}}
        
        # 重新计算今日数据
        today_records = self._get_today_records(today)
        
        for record in today_records:
            data_type = record["type"]
            if data_type not in summary["data"]:
                summary["data"][data_type] = {
                    "total": 0,
                    "count": 0,
                    "unit": record["unit"]
                }
            summary["data"][data_type]["total"] += record["value"]
            summary["data"][data_type]["count"] += 1
        
        self._save_summary(summary)
    
    def _load_summary(self) -> Dict:
        """加载今日汇总"""
        if self.summary_file.exists():
            return json.loads(self.summary_file.read_text(encoding='utf-8'))
        return {"date": None, "data": {}}
    
    def _save_summary(self, summary: Dict):
        """保存今日汇总"""
        self.summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def _get_today_records(self, today: str) -> List[Dict]:
        """获取今日记录"""
        records = []
        if self.records_file.exists():
            with open(self.records_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        if record.get("date") == today:
                            records.append(record)
                    except Exception:
                        pass
        return records
    
    def get_today_summary(self) -> Dict:
        """获取今日汇总"""
        summary = self._load_summary()
        goals = self.load_goals()
        
        today = str(date.today())
        if summary.get("date") != today:
            return {"date": today, "data": {}, "message": "今日暂无记录"}
        
        # 计算完成率
        result = {
            "date": today,
            "data": summary["data"],
            "goals": {},
            "completion_rate": 0
        }
        
        achieved = 0
        total = 0
        
        for data_type, data in summary["data"].items():
            if data_type in goals:
                target = goals[data_type]["target"]
                actual = data["total"]
                rate = min(actual / target, 1.0) if target > 0 else 0
                
                result["goals"][data_type] = {
                    "target": target,
                    "actual": actual,
                    "unit": data["unit"],
                    "achieved": actual >= target,
                    "rate": rate
                }
                
                total += 1
                if actual >= target:
                    achieved += 1
        
        result["completion_rate"] = achieved / total if total > 0 else 0
        
        return result
    
    def generate_review(self) -> str:
        """生成今日复盘"""
        summary = self.get_today_summary()
        goals = self.load_goals()
        
        lines = []
        lines.append(f"# {summary['date']} 复盘")
        lines.append("")
        lines.append("## 数据汇总")
        lines.append("")
        
        for data_type, data in summary.get("data", {}).items():
            goal_info = summary.get("goals", {}).get(data_type, {})
            target = goal_info.get("target", "?")
            actual = data.get("total", 0)
            unit = data.get("unit", "")
            achieved = goal_info.get("achieved", False)
            status = "✅" if achieved else "⚠️"
            
            lines.append(f"- {data_type}: {actual}{unit} (目标: {target}{unit}) {status}")
        
        lines.append("")
        lines.append("## 完成率")
        rate = summary.get("completion_rate", 0)
        lines.append(f"- 总体: {rate*100:.0f}%")
        
        achieved_count = sum(1 for g in summary.get("goals", {}).values() if g.get("achieved"))
        total_count = len(summary.get("goals", {}))
        lines.append(f"- 达标项: {achieved_count}/{total_count}")
        
        lines.append("")
        lines.append("## 建议")
        
        # 生成建议
        for data_type, goal_info in summary.get("goals", {}).items():
            if not goal_info.get("achieved"):
                target = goal_info.get("target", 0)
                actual = goal_info.get("actual", 0)
                gap = target - actual
                lines.append(f"- {data_type}不足{gap:.1f}，建议明天补上")
        
        lines.append("")
        lines.append("## 明天计划")
        for data_type, goal in goals.items():
            lines.append(f"- {data_type}: 目标{goal['target']}{goal['unit']}")
        
        return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Data Tracker V1.0.0")
    parser.add_argument("action", choices=["record", "summary", "review"], help="操作类型")
    parser.add_argument("--text", help="要记录的文本")
    args = parser.parse_args()
    
    root = get_project_root()
    tracker = DataTracker(root)
    
    if args.action == "record":
        if not args.text:
            print("请提供要记录的文本: --text '睡眠7小时'")
            return 1
        
        result = tracker.record(args.text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "summary":
        summary = tracker.get_today_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        
    elif args.action == "review":
        review = tracker.generate_review()
        print(review)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
