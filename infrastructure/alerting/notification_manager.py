#!/usr/bin/env python3
"""
通知管理器 - V1.0.0

职责：
1. 路由告警到正确渠道
2. 去重和冷却机制
3. 记录通知历史
4. 发送 OPEN/RESOLVED 通知
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent

def load_json(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return None

def save_json(path: Path, data: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class NotificationManager:
    """通知管理器"""
    
    def __init__(self, root: Path):
        self.root = root
        self.routing_config = load_json(root / "infrastructure/alerting/alert_routing.json")
        self.history_path = root / "reports/alerts/notification_history.json"
        self.result_path = root / "reports/alerts/notification_result.json"
        
        # 加载历史
        self.history = load_json(self.history_path) or {"notifications": []}
    
    def is_in_cooldown(self, alert_type: str, blocked_reasons: List[str]) -> bool:
        """检查是否在冷却期"""
        if not self.routing_config:
            return False
        
        cooldown_minutes = self.routing_config.get("cooldown_policy", {}).get("window_minutes", 30)
        cooldown_delta = timedelta(minutes=cooldown_minutes)
        
        # 查找最近相同告警
        for notif in reversed(self.history.get("notifications", [])):
            if notif.get("alert_type") != alert_type:
                continue
            
            # 检查时间
            notif_time = datetime.fromisoformat(notif.get("timestamp", "2000-01-01"))
            if datetime.now() - notif_time > cooldown_delta:
                continue
            
            # 检查 blocked_reasons 是否相同
            prev_reasons = set(notif.get("blocked_reasons", []))
            curr_reasons = set(blocked_reasons)
            if prev_reasons == curr_reasons:
                return True
        
        return False
    
    def get_channels_for_alert(self, alert_type: str) -> List[str]:
        """获取告警应发送的渠道"""
        if not self.routing_config:
            return ["github_summary"]
        
        rules = self.routing_config.get("routing_rules", {})
        rule = rules.get(alert_type, {})
        return rule.get("channels", ["github_summary"])
    
    def send_to_channel(self, channel: str, alerts_report: Dict, incident_info: Optional[Dict] = None) -> Dict:
        """发送到指定渠道"""
        result = {
            "channel": channel,
            "sent": False,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        if channel == "github_summary":
            # GitHub Summary 总是成功（由 workflow 处理）
            result["sent"] = True
            result["note"] = "GitHub Summary 由 workflow 生成"
        
        elif channel == "feishu":
            try:
                from infrastructure.alerting.channels.feishu_webhook import send_feishu
                feishu_result = send_feishu(alerts_report, incident_info)
                result["sent"] = feishu_result.get("sent", False)
                result["error"] = feishu_result.get("error")
            except Exception as e:
                result["error"] = str(e)
        
        elif channel == "webhook":
            try:
                from infrastructure.alerting.channels.webhook import send_webhook
                result["sent"] = send_webhook(alerts_report)
            except Exception as e:
                result["error"] = str(e)
        
        return result
    
    def send_notifications(self, alerts_report: Dict, incident_info: Optional[Dict] = None) -> Dict:
        """发送通知"""
        results = {
            "sent_at": datetime.now().isoformat(),
            "channels": [],
            "total_sent": 0,
            "total_failed": 0,
            "skipped_cooldown": False
        }
        
        alerts = alerts_report.get("alerts", [])
        
        if not alerts:
            # 无告警，发送恢复通知
            if alerts_report.get("incident_resolved"):
                # 发送 RESOLVED 通知
                for channel in ["github_summary", "feishu"]:
                    result = self.send_to_channel(channel, alerts_report, incident_info)
                    results["channels"].append(result)
                    if result["sent"]:
                        results["total_sent"] += 1
                    else:
                        results["total_failed"] += 1
        else:
            # 有告警，检查冷却
            for alert in alerts:
                alert_type = alert.get("alert_type")
                blocked_reasons = alerts_report.get("blocked_reasons", [])
                
                # 检查冷却
                if self.is_in_cooldown(alert_type, blocked_reasons):
                    results["skipped_cooldown"] = True
                    continue
                
                # 获取渠道
                channels = self.get_channels_for_alert(alert_type)
                
                for channel in channels:
                    result = self.send_to_channel(channel, alerts_report, incident_info)
                    results["channels"].append(result)
                    if result["sent"]:
                        results["total_sent"] += 1
                    else:
                        results["total_failed"] += 1
                
                # 记录历史
                self.history["notifications"].append({
                    "timestamp": datetime.now().isoformat(),
                    "alert_type": alert_type,
                    "severity": alert.get("severity"),
                    "blocked_reasons": blocked_reasons,
                    "channels": channels,
                    "incident_id": incident_info.get("incident_id") if incident_info else None
                })
        
        # 保存历史
        # 只保留最近 100 条
        self.history["notifications"] = self.history["notifications"][-100:]
        save_json(self.history_path, self.history)
        
        # 保存结果
        save_json(self.result_path, results)
        
        return results
    
    def send_open_notification(self, alerts_report: Dict, incident: Dict) -> Dict:
        """发送 OPEN 通知"""
        incident_info = {
            "incident_id": incident.get("incident_id"),
            "status": "open",
            "incident_created": True
        }
        
        # OPEN 通知正常走冷却逻辑
        return self.send_notifications(alerts_report, incident_info)
    
    def send_resolved_notification(self, alerts_report: Dict, incident: Dict) -> Dict:
        """发送 RESOLVED 通知（不受冷却限制）"""
        # 清除该 incident 的冷却记录
        incident_id = incident.get("incident_id")
        self.history["notifications"] = [
            n for n in self.history.get("notifications", [])
            if n.get("incident_id") != incident_id
        ]
        
        incident_info = {
            "incident_id": incident_id,
            "status": "resolved",
            "incident_resolved": True
        }
        
        # 强制发送，跳过冷却检查
        results = {
            "sent_at": datetime.now().isoformat(),
            "channels": [],
            "total_sent": 0,
            "total_failed": 0,
            "skipped_cooldown": False
        }
        
        for channel in ["github_summary", "feishu"]:
            result = self.send_to_channel(channel, alerts_report, incident_info)
            results["channels"].append(result)
            if result["sent"]:
                results["total_sent"] += 1
            else:
                results["total_failed"] += 1
        
        # 保存结果
        save_json(self.result_path, results)
        
        return results

def main():
    """测试通知"""
    root = get_project_root()
    
    # 加载最新告警
    alerts = load_json(root / "reports/alerts/latest_alerts.json")
    if not alerts:
        print("无告警报告")
        return 0
    
    manager = NotificationManager(root)
    results = manager.send_notifications(alerts)
    
    print("通知发送结果:")
    print(f"  发送成功: {results['total_sent']}")
    print(f"  发送失败: {results['total_failed']}")
    print(f"  冷却跳过: {results['skipped_cooldown']}")
    
    for ch in results["channels"]:
        status = "✅" if ch["sent"] else "❌"
        print(f"  {status} {ch['channel']}: {ch.get('error', 'OK')}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
