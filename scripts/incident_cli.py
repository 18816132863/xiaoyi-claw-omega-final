#!/usr/bin/env python3
"""
Incident CLI - V1.0.0

运维值守工具，支持：
- list: 列出 incidents
- acknowledge: 确认 incident
- resolve: 关闭 incident
- annotate: 添加备注
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

def load_incidents(root: Path) -> List[dict]:
    """加载 incidents"""
    path = root / "governance/ops/incident_tracker.json"
    if not path.exists():
        return []
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return []

def save_incidents(root: Path, incidents: List[dict]):
    """保存 incidents"""
    path = root / "governance/ops/incident_tracker.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(incidents, f, ensure_ascii=False, indent=2)

def cmd_list(root: Path, args: List[str]):
    """列出 incidents"""
    incidents = load_incidents(root)
    
    # 过滤
    status_filter = None
    for arg in args:
        if arg in ["open", "resolved"]:
            status_filter = arg
    
    if status_filter:
        incidents = [i for i in incidents if i.get("status") == status_filter]
    
    if not incidents:
        print("无 incident")
        return
    
    print(f"共 {len(incidents)} 个 incident:")
    print()
    
    for inc in incidents:
        status_icon = "🔴" if inc.get("status") == "open" else "🟢"
        print(f"{status_icon} {inc.get('incident_id', '?')}")
        print(f"   类型: {inc.get('alert_type', '?')}")
        print(f"   状态: {inc.get('status', '?')}")
        print(f"   打开: {inc.get('opened_at', '?')}")
        if inc.get("resolved_at"):
            print(f"   关闭: {inc.get('resolved_at')}")
        if inc.get("owner"):
            print(f"   负责人: {inc.get('owner')}")
        if inc.get("resolution_note"):
            print(f"   备注: {inc.get('resolution_note')}")
        print()

def cmd_acknowledge(root: Path, args: List[str]):
    """确认 incident"""
    if not args:
        print("用法: incident_cli.py acknowledge <incident_id> [owner]")
        return
    
    incident_id = args[0]
    owner = args[1] if len(args) > 1 else None
    
    incidents = load_incidents(root)
    
    for inc in incidents:
        if inc.get("incident_id") == incident_id:
            inc["status"] = "acknowledged"
            if owner:
                inc["owner"] = owner
            inc["acknowledged_at"] = datetime.now().isoformat()
            save_incidents(root, incidents)
            print(f"✅ 已确认 {incident_id}")
            return
    
    print(f"❌ 未找到 {incident_id}")

def cmd_resolve(root: Path, args: List[str]):
    """关闭 incident"""
    if not args:
        print("用法: incident_cli.py resolve <incident_id> [note]")
        return
    
    incident_id = args[0]
    note = " ".join(args[1:]) if len(args) > 1 else "手动关闭"
    
    incidents = load_incidents(root)
    
    for inc in incidents:
        if inc.get("incident_id") == incident_id:
            inc["status"] = "resolved"
            inc["resolved_at"] = datetime.now().isoformat()
            inc["resolution_note"] = note
            save_incidents(root, incidents)
            print(f"✅ 已关闭 {incident_id}")
            return
    
    print(f"❌ 未找到 {incident_id}")

def cmd_annotate(root: Path, args: List[str]):
    """添加备注"""
    if len(args) < 2:
        print("用法: incident_cli.py annotate <incident_id> <note>")
        return
    
    incident_id = args[0]
    note = " ".join(args[1:])
    
    incidents = load_incidents(root)
    
    for inc in incidents:
        if inc.get("incident_id") == incident_id:
            if "annotations" not in inc:
                inc["annotations"] = []
            inc["annotations"].append({
                "timestamp": datetime.now().isoformat(),
                "note": note
            })
            save_incidents(root, incidents)
            print(f"✅ 已添加备注到 {incident_id}")
            return
    
    print(f"❌ 未找到 {incident_id}")

def cmd_stats(root: Path, args: List[str]):
    """统计"""
    incidents = load_incidents(root)
    
    total = len(incidents)
    open_count = sum(1 for i in incidents if i.get("status") in ["open", "acknowledged"])
    resolved = sum(1 for i in incidents if i.get("status") == "resolved")
    
    print("Incident 统计:")
    print(f"  总数: {total}")
    print(f"  打开: {open_count}")
    print(f"  已关闭: {resolved}")

def main():
    if len(sys.argv) < 2:
        print("用法: incident_cli.py <command> [args]")
        print()
        print("命令:")
        print("  list [open|resolved]  - 列出 incidents")
        print("  acknowledge <id> [owner] - 确认 incident")
        print("  resolve <id> [note]   - 关闭 incident")
        print("  annotate <id> <note>  - 添加备注")
        print("  stats                 - 统计")
        return 0
    
    root = get_project_root()
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "list":
        cmd_list(root, args)
    elif command == "acknowledge" or command == "ack":
        cmd_acknowledge(root, args)
    elif command == "resolve":
        cmd_resolve(root, args)
    elif command == "annotate":
        cmd_annotate(root, args)
    elif command == "stats":
        cmd_stats(root, args)
    else:
        print(f"未知命令: {command}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
