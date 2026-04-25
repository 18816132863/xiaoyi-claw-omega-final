#!/usr/bin/env python
"""
审计操作 CLI
提供命令行接口查询和管理 platform_invocations
"""

import argparse
import json
import csv
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.invocation_ledger import (
    query_by_task_id,
    query_by_capability,
    query_by_status,
    export_recent,
    export_failed_report,
    export_timeout_report,
    export_uncertain_report,
    get_statistics,
    confirm_invocation,
    get_invocation_by_id,
    cleanup_old_records,
)


def redact_value(value: str, max_length: int = 20) -> str:
    """
    脱敏单个值
    
    Args:
        value: 原始值
        max_length: 最大显示长度
    
    Returns:
        str: 脱敏后的值
    """
    if not value or not isinstance(value, str):
        return value
    
    # 手机号脱敏
    if len(value) >= 11 and value.isdigit():
        return value[:3] + "****" + value[-4:]
    
    # 长内容截断
    if len(value) > max_length:
        return value[:max_length] + "..."
    
    return value


def redact_json_string(json_str: str, fields_to_redact: list) -> str:
    """
    脱敏 JSON 字符串中的敏感字段
    
    Args:
        json_str: JSON 字符串
        fields_to_redact: 需要脱敏的字段列表
    
    Returns:
        str: 脱敏后的 JSON 字符串
    """
    if not json_str:
        return json_str
    
    try:
        data = json.loads(json_str) if isinstance(json_str, str) else json_str
        
        if isinstance(data, dict):
            for key in fields_to_redact:
                if key in data:
                    data[key] = redact_value(str(data[key]))
            
            # 特殊处理嵌套的 request/response
            for nested_key in ["request", "response", "params", "body"]:
                if nested_key in data and isinstance(data[nested_key], dict):
                    for key in fields_to_redact:
                        if key in data[nested_key]:
                            data[nested_key][key] = redact_value(str(data[nested_key][key]))
        
        return json.dumps(data, ensure_ascii=False)
    except:
        return json_str


def redact_sensitive(data: dict) -> dict:
    """
    脱敏敏感信息
    
    脱敏规则：
    1. 手机号字段: phone_number, phoneNumber, phone - 保留前3后4
    2. 用户内容字段: content, message, title, body, text - 截断到20字
    3. request_json - 脱敏其中的敏感字段
    4. raw_result_json - 脱敏其中的敏感字段
    5. confirm_note - 截断到50字
    """
    if not data:
        return data
    
    result = data.copy()
    
    # 需要脱敏的字段列表
    phone_fields = ["phone_number", "phoneNumber", "phone", "mobile", "tel"]
    content_fields = ["content", "message", "title", "body", "text", "description", "note"]
    
    # 脱敏顶层字段
    for key in phone_fields:
        if key in result:
            val = str(result[key])
            if len(val) >= 7:
                result[key] = val[:3] + "****" + val[-4:]
    
    for key in content_fields:
        if key in result and isinstance(result[key], str) and len(result[key]) > 20:
            result[key] = result[key][:20] + "..."
    
    # 脱敏 request_json
    if "request_json" in result and result["request_json"]:
        result["request_json"] = redact_json_string(
            result["request_json"],
            phone_fields + content_fields
        )
    
    # 脱敏 raw_result_json
    if "raw_result_json" in result and result["raw_result_json"]:
        result["raw_result_json"] = redact_json_string(
            result["raw_result_json"],
            phone_fields + content_fields
        )
    
    # 脱敏 confirm_note
    if "confirm_note" in result and result["confirm_note"]:
        note = str(result["confirm_note"])
        if len(note) > 50:
            result["confirm_note"] = note[:50] + "..."
    
    return result


def cmd_query_recent(args):
    """查询最近 N 条记录"""
    records = export_recent(args.limit)
    
    if args.redact:
        records = [redact_sensitive(r) for r in records]
    
    if args.format == "json":
        print(json.dumps(records, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        print_csv(records)
    else:
        print_table(records)


def cmd_query_uncertain(args):
    """查询 uncertain 记录"""
    records = export_uncertain_report(args.limit)
    
    if args.redact:
        records = [redact_sensitive(r) for r in records]
    
    if args.format == "json":
        print(json.dumps(records, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        print_csv(records)
    else:
        print_table(records)


def cmd_query_failed(args):
    """查询 failed 记录"""
    records = export_failed_report(args.limit)
    
    if args.redact:
        records = [redact_sensitive(r) for r in records]
    
    if args.format == "json":
        print(json.dumps(records, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        print_csv(records)
    else:
        print_table(records)


def cmd_query_timeout(args):
    """查询 timeout 记录"""
    records = export_timeout_report(args.limit)
    
    if args.redact:
        records = [redact_sensitive(r) for r in records]
    
    if args.format == "json":
        print(json.dumps(records, ensure_ascii=False, indent=2))
    elif args.format == "csv":
        print_csv(records)
    else:
        print_table(records)


def cmd_confirm(args):
    """手动确认记录"""
    result = confirm_invocation(
        record_id=args.id,
        confirmed_status=args.status,
        confirm_note=args.note,
    )
    
    if result:
        print(f"✅ 记录 #{args.id} 已确认为: {args.status}")
        if args.note:
            print(f"   备注: {args.note}")
    else:
        print(f"❌ 确认失败，记录 #{args.id} 不存在")


def cmd_stats(args):
    """显示统计信息"""
    stats = get_statistics()
    
    print("=" * 50)
    print("平台调用审计统计")
    print("=" * 50)
    print(f"总调用数: {stats['total']}")
    print(f"Uncertain 记录: {stats['uncertain_count']}")
    print(f"已确认记录: {stats['confirmed_count']}")
    print()
    print("按状态分布:")
    for status, count in stats['by_status'].items():
        pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {status}: {count} ({pct:.1f}%)")


def cmd_breakdown(args):
    """按 capability / status / error_code 汇总"""
    import sqlite3
    from pathlib import Path
    
    db_path = project_root / "data" / "tasks.db"
    if not db_path.exists():
        print("数据库不存在，请先运行 seed_platform_invocations.py")
        return
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("=" * 60)
    print("平台调用 Breakdown 报告")
    print("=" * 60)
    
    # 按 capability 统计
    print("\n📊 按 Capability 统计:")
    print("-" * 40)
    cursor.execute("""
        SELECT capability, 
               COUNT(*) as total,
               SUM(CASE WHEN normalized_status = 'completed' THEN 1 ELSE 0 END) as completed,
               SUM(CASE WHEN normalized_status = 'failed' THEN 1 ELSE 0 END) as failed,
               SUM(CASE WHEN normalized_status = 'timeout' THEN 1 ELSE 0 END) as timeout,
               SUM(CASE WHEN result_uncertain = 1 THEN 1 ELSE 0 END) as uncertain
        FROM platform_invocations
        GROUP BY capability
        ORDER BY total DESC
    """)
    
    for row in cursor.fetchall():
        print(f"  {row['capability']}:")
        print(f"    总数: {row['total']}, 成功: {row['completed']}, 失败: {row['failed']}, 超时: {row['timeout']}, Uncertain: {row['uncertain']}")
    
    # 按 error_code 统计
    print("\n📋 按 Error Code 统计 (Top 10):")
    print("-" * 40)
    cursor.execute("""
        SELECT error_code, COUNT(*) as cnt
        FROM platform_invocations
        WHERE error_code IS NOT NULL
        GROUP BY error_code
        ORDER BY cnt DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"  {row['error_code']}: {row['cnt']}")
    
    # 按 capability + error_code 统计
    print("\n📋 按 Capability + Error Code 统计:")
    print("-" * 40)
    cursor.execute("""
        SELECT capability, error_code, COUNT(*) as cnt
        FROM platform_invocations
        WHERE error_code IS NOT NULL
        GROUP BY capability, error_code
        ORDER BY capability, cnt DESC
    """)
    
    current_cap = None
    for row in cursor.fetchall():
        if current_cap != row['capability']:
            current_cap = row['capability']
            print(f"  {current_cap}:")
        print(f"    {row['error_code']}: {row['cnt']}")
    
    conn.close()


def cmd_seed_demo(args):
    """预热演示数据"""
    import subprocess
    
    cmd = ["python", "scripts/seed_platform_invocations.py", "--preset", "demo_standard"]
    if args.reset:
        cmd.append("--reset-before-seed")
    
    result = subprocess.run(cmd, cwd=str(project_root))
    
    if result.returncode == 0:
        print("\n✅ 演示数据预热完成")
    else:
        print("\n❌ 演示数据预热失败")


def cmd_export(args):
    """导出报告"""
    if args.type == "failed":
        records = export_failed_report(args.limit)
    elif args.type == "timeout":
        records = export_timeout_report(args.limit)
    elif args.type == "uncertain":
        records = export_uncertain_report(args.limit)
    else:
        records = export_recent(args.limit)
    
    if args.redact:
        records = [redact_sensitive(r) for r in records]
    
    if args.format == "json":
        output = json.dumps(records, ensure_ascii=False, indent=2)
    else:
        output = records_to_csv(records)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ 已导出到: {args.output}")
    else:
        print(output)


def cmd_cleanup(args):
    """清理旧记录"""
    deleted = cleanup_old_records(
        days_to_keep=args.days,
        keep_failed=args.keep_failed,
        keep_uncertain=args.keep_uncertain,
    )
    print(f"✅ 已清理 {deleted} 条记录")


def print_table(records):
    """打印表格格式"""
    if not records:
        print("无记录")
        return
    
    # 选择关键字段
    fields = ["id", "capability", "platform_op", "normalized_status", "result_uncertain", "created_at"]
    
    # 打印表头
    header = " | ".join(fields)
    print(header)
    print("-" * len(header))
    
    # 打印记录
    for r in records:
        row = " | ".join(str(r.get(f, ""))[:20] for f in fields)
        print(row)


def print_csv(records):
    """打印 CSV 格式"""
    if not records:
        return
    
    writer = csv.writer(sys.stdout)
    writer.writerow(records[0].keys())
    for r in records:
        writer.writerow(r.values())


def records_to_csv(records):
    """转换为 CSV 字符串"""
    import io
    output = io.StringIO()
    if records:
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description="平台调用审计 CLI")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # query-recent
    p = subparsers.add_parser("query-recent", help="查询最近 N 条记录")
    p.add_argument("--limit", type=int, default=10, help="记录数量")
    p.add_argument("--format", choices=["table", "json", "csv"], default="table", help="输出格式")
    p.add_argument("--redact", action="store_true", help="脱敏敏感信息")
    p.set_defaults(func=cmd_query_recent)
    
    # query-uncertain
    p = subparsers.add_parser("query-uncertain", help="查询 uncertain 记录")
    p.add_argument("--limit", type=int, default=10, help="记录数量")
    p.add_argument("--format", choices=["table", "json", "csv"], default="table", help="输出格式")
    p.add_argument("--redact", action="store_true", help="脱敏敏感信息")
    p.set_defaults(func=cmd_query_uncertain)
    
    # query-failed
    p = subparsers.add_parser("query-failed", help="查询 failed 记录")
    p.add_argument("--limit", type=int, default=10, help="记录数量")
    p.add_argument("--format", choices=["table", "json", "csv"], default="table", help="输出格式")
    p.add_argument("--redact", action="store_true", help="脱敏敏感信息")
    p.set_defaults(func=cmd_query_failed)
    
    # query-timeout
    p = subparsers.add_parser("query-timeout", help="查询 timeout 记录")
    p.add_argument("--limit", type=int, default=10, help="记录数量")
    p.add_argument("--format", choices=["table", "json", "csv"], default="table", help="输出格式")
    p.add_argument("--redact", action="store_true", help="脱敏敏感信息")
    p.set_defaults(func=cmd_query_timeout)
    
    # confirm
    p = subparsers.add_parser("confirm", help="手动确认记录")
    p.add_argument("--id", type=int, required=True, help="记录 ID")
    p.add_argument("--status", required=True, 
                   choices=["confirmed_success", "confirmed_failed", "confirmed_duplicate"],
                   help="确认状态")
    p.add_argument("--note", help="确认备注")
    p.set_defaults(func=cmd_confirm)
    
    # stats
    p = subparsers.add_parser("stats", help="显示统计信息")
    p.set_defaults(func=cmd_stats)
    
    # breakdown
    p = subparsers.add_parser("breakdown", help="按 capability/status/error_code 汇总")
    p.set_defaults(func=cmd_breakdown)
    
    # seed-demo
    p = subparsers.add_parser("seed-demo", help="预热演示数据")
    p.add_argument("--reset", action="store_true", help="重置数据库后再预热")
    p.set_defaults(func=cmd_seed_demo)
    
    # export
    p = subparsers.add_parser("export", help="导出报告")
    p.add_argument("--type", choices=["failed", "timeout", "uncertain", "recent"], 
                   default="recent", help="报告类型")
    p.add_argument("--limit", type=int, default=100, help="记录数量")
    p.add_argument("--format", choices=["json", "csv"], default="json", help="导出格式")
    p.add_argument("--output", help="输出文件路径")
    p.add_argument("--redact", action="store_true", help="脱敏敏感信息")
    p.set_defaults(func=cmd_export)
    
    # cleanup
    p = subparsers.add_parser("cleanup", help="清理旧记录")
    p.add_argument("--days", type=int, default=30, help="保留天数")
    p.add_argument("--keep-failed", action="store_true", default=True, help="保留 failed 记录")
    p.add_argument("--keep-uncertain", action="store_true", default=True, help="保留 uncertain 记录")
    p.set_defaults(func=cmd_cleanup)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
