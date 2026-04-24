#!/usr/bin/env python
"""
导出每日平台调用报告
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
    export_failed_report,
    export_timeout_report,
    export_uncertain_report,
)


def get_daily_stats(date: datetime = None) -> dict:
    """
    获取每日统计
    
    Args:
        date: 日期，默认今天
    
    Returns:
        dict: 统计数据
    """
    if date is None:
        date = datetime.now()
    
    # 获取所有记录
    all_records = export_recent(10000)
    
    # 过滤当天记录
    date_str = date.strftime("%Y-%m-%d")
    daily_records = [
        r for r in all_records
        if r.get("created_at", "").startswith(date_str)
    ]
    
    # 统计
    total = len(daily_records)
    completed = sum(1 for r in daily_records if r.get("normalized_status") == "completed")
    failed = sum(1 for r in daily_records if r.get("normalized_status") == "failed")
    timeout = sum(1 for r in daily_records if r.get("normalized_status") == "timeout")
    uncertain = sum(1 for r in daily_records if r.get("result_uncertain"))
    confirmed = sum(1 for r in daily_records if r.get("confirmed_status"))
    
    # 按能力统计
    by_capability = {}
    for r in daily_records:
        cap = r.get("capability", "unknown")
        if cap not in by_capability:
            by_capability[cap] = {"total": 0, "completed": 0, "failed": 0, "timeout": 0}
        by_capability[cap]["total"] += 1
        status = r.get("normalized_status")
        if status in by_capability[cap]:
            by_capability[cap][status] += 1
    
    # 按 error_code 统计
    by_error_code = {}
    for r in daily_records:
        ec = r.get("error_code")
        if ec:
            by_error_code[ec] = by_error_code.get(ec, 0) + 1
    
    # 获取 NOTIFICATION 授权状态
    notification_auth_status = "unknown"
    try:
        from scripts.check_notification_auth import check_notification_auth
        auth_result = check_notification_auth()
        notification_auth_status = auth_result["status"]
    except:
        pass
    
    return {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "total_invocations": total,
        "completed_count": completed,
        "failed_count": failed,
        "timeout_count": timeout,
        "uncertain_count": uncertain,
        "confirmed_count": confirmed,
        "failed_rate": (failed / total * 100) if total > 0 else 0,
        "timeout_rate": (timeout / total * 100) if total > 0 else 0,
        "confirmation_rate": (confirmed / uncertain * 100) if uncertain > 0 else 100,
        "notification_auth_status": notification_auth_status,
        "by_capability": by_capability,
        "by_error_code": by_error_code,
    }


def format_report(stats: dict) -> str:
    """格式化报告"""
    lines = [
        "=" * 60,
        f"每日平台调用报告 - {stats['date']}",
        "=" * 60,
        f"生成时间: {stats['generated_at']}",
        "",
        "📊 总体统计",
        "-" * 40,
        f"总调用数: {stats['total_invocations']}",
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
        "🔐 NOTIFICATION 授权状态",
        "-" * 40,
        f"状态: {stats.get('notification_auth_status', 'unknown')}",
        "",
        "📋 按能力统计",
        "-" * 40,
    ]
    
    for cap, data in stats["by_capability"].items():
        lines.append(f"  {cap}:")
        lines.append(f"    总数: {data['total']}")
        lines.append(f"    成功: {data['completed']}")
        lines.append(f"    失败: {data['failed']}")
        lines.append(f"    超时: {data['timeout']}")
    
    # Error Code Breakdown
    if stats.get("by_error_code"):
        lines.append("")
        lines.append("📋 Error Code 分布 (Top 10)")
        lines.append("-" * 40)
        sorted_errors = sorted(stats["by_error_code"].items(), key=lambda x: x[1], reverse=True)[:10]
        for ec, cnt in sorted_errors:
            lines.append(f"  {ec}: {cnt}")
    
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
        writer.writerow(["日期", stats["date"]])
        writer.writerow(["总调用数", stats["total_invocations"]])
        writer.writerow(["成功数", stats["completed_count"]])
        writer.writerow(["失败数", stats["failed_count"]])
        writer.writerow(["超时数", stats["timeout_count"]])
        writer.writerow(["Uncertain 数", stats["uncertain_count"]])
        writer.writerow(["已确认数", stats["confirmed_count"]])
        writer.writerow(["失败率", f"{stats['failed_rate']:.2f}%"])
        writer.writerow(["超时率", f"{stats['timeout_rate']:.2f}%"])
        writer.writerow(["确认率", f"{stats['confirmation_rate']:.2f}%"])
        
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
    parser = argparse.ArgumentParser(description="导出每日平台调用报告")
    parser.add_argument("--date", help="日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--format", choices=["text", "json", "csv"], default="text", help="输出格式")
    parser.add_argument("--output", help="输出文件路径")
    
    args = parser.parse_args()
    
    # 解析日期
    if args.date:
        date = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        date = None
    
    # 获取统计
    stats = get_daily_stats(date)
    
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
            # 输出到 stdout
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["指标", "值"])
            writer.writerow(["日期", stats["date"]])
            writer.writerow(["总调用数", stats["total_invocations"]])
            writer.writerow(["失败率", f"{stats['failed_rate']:.2f}%"])
            writer.writerow(["超时率", f"{stats['timeout_rate']:.2f}%"])
            print(output.getvalue())
    else:
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(format_report(stats))
            print(f"✅ 报告已导出: {args.output}")
        else:
            print(format_report(stats))


if __name__ == "__main__":
    main()
