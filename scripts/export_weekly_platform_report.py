#!/usr/bin/env python
"""
导出每周平台调用报告
输出总调用数、失败率、超时率、uncertain 数、已确认率
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
import argparse

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.invocation_ledger import (
    get_statistics,
    export_recent,
)


def get_weekly_stats(week_start: datetime = None) -> dict:
    """
    获取每周统计
    
    Args:
        week_start: 周起始日期，默认本周一
    
    Returns:
        dict: 统计数据
    """
    if week_start is None:
        # 获取本周一
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
    
    week_end = week_start + timedelta(days=7)
    
    # 获取所有记录
    all_records = export_recent(10000)
    
    # 过滤本周记录
    week_start_str = week_start.strftime("%Y-%m-%d")
    week_end_str = week_end.strftime("%Y-%m-%d")
    
    weekly_records = [
        r for r in all_records
        if week_start_str <= r.get("created_at", "")[:10] < week_end_str
    ]
    
    # 统计
    total = len(weekly_records)
    completed = sum(1 for r in weekly_records if r.get("normalized_status") == "completed")
    failed = sum(1 for r in weekly_records if r.get("normalized_status") == "failed")
    timeout = sum(1 for r in weekly_records if r.get("normalized_status") == "timeout")
    uncertain = sum(1 for r in weekly_records if r.get("result_uncertain"))
    confirmed = sum(1 for r in weekly_records if r.get("confirmed_status"))
    
    # 按天统计
    by_day = {}
    for r in weekly_records:
        day = r.get("created_at", "")[:10]
        if day not in by_day:
            by_day[day] = {"total": 0, "completed": 0, "failed": 0, "timeout": 0}
        by_day[day]["total"] += 1
        status = r.get("normalized_status")
        if status in by_day[day]:
            by_day[day][status] += 1
    
    # 按能力统计
    by_capability = {}
    for r in weekly_records:
        cap = r.get("capability", "unknown")
        if cap not in by_capability:
            by_capability[cap] = {"total": 0, "completed": 0, "failed": 0, "timeout": 0}
        by_capability[cap]["total"] += 1
        status = r.get("normalized_status")
        if status in by_capability[cap]:
            by_capability[cap][status] += 1
    
    # 计算日均
    days_with_data = len(by_day)
    daily_avg = total / days_with_data if days_with_data > 0 else 0
    
    return {
        "week_start": week_start_str,
        "week_end": week_end_str,
        "generated_at": datetime.now().isoformat(),
        "total_invocations": total,
        "daily_average": round(daily_avg, 1),
        "completed_count": completed,
        "failed_count": failed,
        "timeout_count": timeout,
        "uncertain_count": uncertain,
        "confirmed_count": confirmed,
        "failed_rate": (failed / total * 100) if total > 0 else 0,
        "timeout_rate": (timeout / total * 100) if total > 0 else 0,
        "confirmation_rate": (confirmed / uncertain * 100) if uncertain > 0 else 100,
        "by_day": by_day,
        "by_capability": by_capability,
    }


def format_report(stats: dict) -> str:
    """格式化报告"""
    lines = [
        "=" * 60,
        f"每周平台调用报告",
        f"{stats['week_start']} ~ {stats['week_end']}",
        "=" * 60,
        f"生成时间: {stats['generated_at']}",
        "",
        "📊 总体统计",
        "-" * 40,
        f"总调用数: {stats['total_invocations']}",
        f"日均调用: {stats['daily_average']}",
        f"成功数: {stats['completed_count']}",
        f"失败数: {stats['failed_count']}",
        f"超时数: {stats['timeout_count']}",
        f"Uncertain 数: {stats['uncertain_count']}",
        f"已确认数: {stats['confirmed_count']}",
        "",
        "📈 比率统计",
        "-" * 40,
        f"失败率: {stats['failed_rate']:.2f}%",
        f"超时率: {stats['timeout_rate']:.2f}%",
        f"确认率: {stats['confirmation_rate']:.2f}%",
        "",
        "📅 按天统计",
        "-" * 40,
    ]
    
    for day in sorted(stats["by_day"].keys()):
        data = stats["by_day"][day]
        lines.append(f"  {day}: 总数={data['total']}, 成功={data['completed']}, 失败={data['failed']}, 超时={data['timeout']}")
    
    lines.append("")
    lines.append("📋 按能力统计")
    lines.append("-" * 40)
    
    for cap, data in stats["by_capability"].items():
        lines.append(f"  {cap}:")
        lines.append(f"    总数: {data['total']}")
        lines.append(f"    成功: {data['completed']}")
        lines.append(f"    失败: {data['failed']}")
        lines.append(f"    超时: {data['timeout']}")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def export_json(stats: dict, output_path: str):
    """导出 JSON"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 报告已导出: {output_path}")


def export_csv(stats: dict, output_path: str):
    """导出 CSV"""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # 写入总体统计
        writer.writerow(["指标", "值"])
        writer.writerow(["周起始", stats["week_start"]])
        writer.writerow(["周结束", stats["week_end"]])
        writer.writerow(["总调用数", stats["total_invocations"]])
        writer.writerow(["日均调用", stats["daily_average"]])
        writer.writerow(["成功数", stats["completed_count"]])
        writer.writerow(["失败数", stats["failed_count"]])
        writer.writerow(["超时数", stats["timeout_count"]])
        writer.writerow(["Uncertain 数", stats["uncertain_count"]])
        writer.writerow(["已确认数", stats["confirmed_count"]])
        writer.writerow(["失败率", f"{stats['failed_rate']:.2f}%"])
        writer.writerow(["超时率", f"{stats['timeout_rate']:.2f}%"])
        writer.writerow(["确认率", f"{stats['confirmation_rate']:.2f}%"])
        
        writer.writerow([])
        writer.writerow(["日期", "总数", "成功", "失败", "超时"])
        for day in sorted(stats["by_day"].keys()):
            data = stats["by_day"][day]
            writer.writerow([day, data["total"], data["completed"], data["failed"], data["timeout"]])
        
        writer.writerow([])
        writer.writerow(["能力", "总数", "成功", "失败", "超时"])
        for cap, data in stats["by_capability"].items():
            writer.writerow([
                cap,
                data["total"],
                data["completed"],
                data["failed"],
                data["timeout"],
            ])
    
    print(f"✅ CSV 报告已导出: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="导出每周平台调用报告")
    parser.add_argument("--week-start", help="周起始日期 (YYYY-MM-DD)，默认本周一")
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text", help="输出格式")
    parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 解析日期
    if args.week_start:
        week_start = datetime.strptime(args.week_start, "%Y-%m-%d")
    else:
        week_start = None
    
    # 获取统计
    stats = get_weekly_stats(week_start)
    
    # 输出
    if args.format == "json":
        if args.output:
            export_json(stats, args.output)
        else:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        if args.output:
            export_csv(stats, args.output)
        else:
            print("请指定 --output 参数导出 CSV")
    else:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(format_report(stats))
            print(f"✅ 报告已导出: {args.output}")
        else:
            print(format_report(stats))


if __name__ == "__main__":
    main()
