#!/usr/bin/env python3
"""
Export Route Audit Records

导出 route 审计记录
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.route_audit import get_route_audit_log


def main():
    parser = argparse.ArgumentParser(description="Export Route Audit Records")
    parser.add_argument("--last", type=int, default=20, help="Last N records")
    parser.add_argument("--route", type=str, help="Filter by route_id")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Route Audit Export")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    audit_log = get_route_audit_log()
    
    if args.stats:
        stats = audit_log.get_statistics()
        print(f"\n📊 Audit Statistics:")
        print(f"   Total records: {stats['total']}")
        print(f"\n   By Status:")
        for status, count in sorted(stats.get("by_status", {}).items()):
            print(f"      {status}: {count}")
        print(f"\n   By Risk Level:")
        for risk, count in sorted(stats.get("by_risk_level", {}).items()):
            print(f"      {risk}: {count}")
        print(f"\n   Top Routes:")
        sorted_routes = sorted(stats.get("by_route", {}).items(), key=lambda x: x[1], reverse=True)[:10]
        for route, count in sorted_routes:
            print(f"      {route}: {count}")
        return 0
    
    if args.route:
        records = audit_log.get_records_by_route(args.route, limit=args.last)
        print(f"\n📋 Records for route: {args.route}")
    else:
        records = audit_log.get_recent_records(limit=args.last)
        print(f"\n📋 Last {args.last} records:")
    
    if not records:
        print("   No records found")
        return 0
    
    for i, record in enumerate(records, 1):
        print(f"\n   [{i}] {record.get('audit_id', 'unknown')}")
        print(f"       Route: {record.get('route_id', 'unknown')}")
        print(f"       Capability: {record.get('capability', 'unknown')}")
        print(f"       Risk: {record.get('risk_level', 'unknown')}")
        print(f"       Status: {record.get('status', 'unknown')}")
        print(f"       Dry-run: {record.get('dry_run', False)}")
        print(f"       Duration: {record.get('duration_ms', 0)}ms")
        if record.get('error_code'):
            print(f"       Error: {record.get('error_code')} - {record.get('error_message', '')}")
        if record.get('fallback_used'):
            print(f"       Fallback: {record.get('fallback_used')}")
    
    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
