#!/usr/bin/env python3
"""
Export Connected Runtime Audit - 导出连接运行时审计记录

用法：
  python scripts/export_connected_runtime_audit.py --last 20
  python scripts/export_connected_runtime_audit.py --all
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_audit_records(audit_path: str) -> List[Dict[str, Any]]:
    """加载审计记录"""
    records = []
    
    if not os.path.exists(audit_path):
        return records
    
    with open(audit_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError:
                    continue
    
    return records


def filter_by_last(records: List[Dict[str, Any]], last_n: int) -> List[Dict[str, Any]]:
    """获取最近 N 条记录"""
    return records[-last_n:] if last_n > 0 else records


def generate_audit_report(records: List[Dict[str, Any]]) -> str:
    """生成审计报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("CONNECTED RUNTIME AUDIT REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    # 统计
    lines.append("[Statistics]")
    lines.append(f"  total_records: {len(records)}")
    
    if records:
        # 按事件类型分组
        event_types = {}
        for record in records:
            event_type = record.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        lines.append("  event_types:")
        for event_type, count in event_types.items():
            lines.append(f"    - {event_type}: {count}")
    
    lines.append("")
    
    # 审计记录
    lines.append("[Audit Records]")
    for record in records:
        timestamp = record.get("timestamp", "unknown")
        event_type = record.get("event_type", "unknown")
        audit_id = record.get("audit_id", "unknown")
        
        lines.append(f"  [{timestamp}] {event_type} ({audit_id})")
        
        # 显示关键字段
        if "failure_type" in record:
            lines.append(f"    failure_type: {record['failure_type']}")
        if "recovery_result" in record:
            lines.append(f"    recovery_result: {record['recovery_result']}")
        if "human_action_required" in record:
            lines.append(f"    human_action_required: {record['human_action_required']}")
        if "duration_ms" in record:
            lines.append(f"    duration_ms: {record['duration_ms']:.1f}")
    
    lines.append("")
    
    return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Export connected runtime audit records")
    parser.add_argument("--last", type=int, default=20, help="Last N records to export")
    parser.add_argument("--all", action="store_true", help="Export all records")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    # 审计文件路径
    audit_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "route_audit.jsonl"
    )
    
    # 加载记录
    records = load_audit_records(audit_path)
    
    # 过滤
    if not args.all:
        records = filter_by_last(records, args.last)
    
    # 输出
    if args.json:
        print(json.dumps(records, indent=2, ensure_ascii=False))
    else:
        print(generate_audit_report(records))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
