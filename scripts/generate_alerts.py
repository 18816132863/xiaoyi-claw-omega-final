#!/usr/bin/env python3
"""
告警生成脚本 - V3.0.0

统一入口：生成告警 + 管理 incidents + 发送通知（通过 NotificationManager）
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.alerting.alert_manager import (
    generate_alerts, 
    manage_incidents, 
    print_alert_summary
)
from infrastructure.alerting.notification_manager import NotificationManager

def main():
    import argparse
    parser = argparse.ArgumentParser(description="告警生成 V3.0")
    parser.add_argument("--workflow", default="manual", help="来源 workflow")
    parser.add_argument("--profile", default="unknown", help="门禁 profile")
    parser.add_argument("--skip-notification", action="store_true", help="跳过通知发送")
    args = parser.parse_args()
    
    print("╔══════════════════════════════════════════════════╗")
    print("║              告警生成 V3.0                      ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 1. 生成告警
    print("【1】生成告警...")
    report = generate_alerts(args.workflow, args.profile)
    
    # 2. 管理 incidents
    print("【2】管理 incidents...")
    incidents = manage_incidents(report)
    
    # 3. 发送通知（通过 NotificationManager）
    if not args.skip_notification:
        print("【3】发送通知...")
        root = Path(__file__).parent.parent
        notification_manager = NotificationManager(root)
        
        # 判断是 OPEN 还是 RESOLVED
        if report.get("incident_created"):
            # 找到刚创建的 incident
            incident = None
            for inc in incidents.get("incidents", []):
                if inc.get("status") == "open":
                    incident = inc
                    break
            
            if incident:
                print("  发送 OPEN 通知...")
                notif_result = notification_manager.send_open_notification(report, incident)
            else:
                notif_result = notification_manager.send_notifications(report)
        elif report.get("incident_resolved"):
            # 找到刚关闭的 incident
            incident = None
            for inc in incidents.get("incidents", []):
                if inc.get("status") == "resolved":
                    incident = inc
                    break
            
            if incident:
                print("  发送 RESOLVED 通知...")
                notif_result = notification_manager.send_resolved_notification(report, incident)
            else:
                notif_result = notification_manager.send_notifications(report)
        else:
            notif_result = notification_manager.send_notifications(report)
        
        print(f"  发送成功: {notif_result.get('total_sent', 0)}")
        print(f"  发送失败: {notif_result.get('total_failed', 0)}")
        print(f"  冷却跳过: {notif_result.get('skipped_cooldown', False)}")
        
        for ch in notif_result.get("channels", []):
            status = "✅" if ch.get("sent") else "❌"
            error = ch.get("error", "")
            print(f"    {status} {ch.get('channel')}: {error or 'OK'}")
    else:
        print("【3】跳过通知发送")
    
    # 4. 打印摘要
    print()
    print_alert_summary(report)
    
    return 1 if report["has_blocking_alerts"] else 0

if __name__ == "__main__":
    sys.exit(main())
