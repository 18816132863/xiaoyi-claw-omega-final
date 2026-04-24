#!/usr/bin/env python3
"""
每日天气汇报 - V1.0.0

职责：
1. 获取当天天气情况
2. 生成天气汇报
3. 发送给用户

使用方式：
- python scripts/send_daily_weather_report.py
- 由定时任务自动调用
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class DailyWeatherReport:
    """每日天气汇报"""
    
    def __init__(self, root: Path):
        self.root = root
        self.reports_dir = root / "reports" / "weather"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def get_weather_data(self) -> Dict[str, Any]:
        """获取天气数据"""
        # 模拟天气数据（实际应调用天气API）
        now = datetime.now()
        
        weather_data = {
            "date": now.strftime("%Y-%m-%d"),
            "location": "北京",
            "weather": "晴",
            "temperature": {
                "current": 18,
                "high": 22,
                "low": 12
            },
            "humidity": 45,
            "wind": "东北风 3级",
            "air_quality": "良",
            "uv_index": "中等",
            "sunrise": "05:42",
            "sunset": "19:15",
            "suggestions": [
                "天气晴朗，适合户外活动",
                "早晚温差较大，注意添衣",
                "紫外线中等，外出可涂防晒",
                "空气质量良好，适宜开窗通风"
            ]
        }
        
        return weather_data
    
    def format_report(self, weather_data: Dict) -> str:
        """格式化天气汇报"""
        lines = []
        
        lines.append("🌤️ 每日天气汇报")
        lines.append(f"📅 {weather_data['date']}")
        lines.append(f"📍 {weather_data['location']}")
        lines.append("")
        
        # 天气概况
        lines.append("🌡️ 天气概况")
        lines.append(f"  天气: {weather_data['weather']}")
        lines.append(f"  当前温度: {weather_data['temperature']['current']}°C")
        lines.append(f"  最高温度: {weather_data['temperature']['high']}°C")
        lines.append(f"  最低温度: {weather_data['temperature']['low']}°C")
        lines.append("")
        
        # 详细信息
        lines.append("📊 详细信息")
        lines.append(f"  湿度: {weather_data['humidity']}%")
        lines.append(f"  风力: {weather_data['wind']}")
        lines.append(f"  空气质量: {weather_data['air_quality']}")
        lines.append(f"  紫外线: {weather_data['uv_index']}")
        lines.append(f"  日出: {weather_data['sunrise']}")
        lines.append(f"  日落: {weather_data['sunset']}")
        lines.append("")
        
        # 生活建议
        lines.append("💡 生活建议")
        for suggestion in weather_data['suggestions']:
            lines.append(f"  • {suggestion}")
        lines.append("")
        
        lines.append("🌈 祝你今天心情愉快！")
        
        return "\n".join(lines)
    
    def save_report(self, weather_data: Dict):
        """保存天气报告"""
        log_file = self.reports_dir / "daily_weather_reports.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(weather_data, ensure_ascii=False) + '\n')
    
    def run(self) -> Dict[str, Any]:
        """运行天气汇报"""
        print("=" * 60)
        print("  每日天气汇报 V1.0.0")
        print("=" * 60)
        print()
        
        weather_data = self.get_weather_data()
        report = self.format_report(weather_data)
        
        print(report)
        print()
        
        # 保存记录
        self.save_report(weather_data)
        
        print("✅ 天气汇报已生成")
        print(f"📁 记录: {self.reports_dir / 'daily_weather_reports.jsonl'}")
        print()
        
        return {
            "status": "success",
            "weather_data": weather_data,
            "report": report
        }


def main():
    root = get_project_root()
    reporter = DailyWeatherReport(root)
    result = reporter.run()
    
    # 输出消息供外部调用
    if result.get("report"):
        print("\n--- MESSAGE ---")
        print(result["report"])
        print("--- END ---\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
