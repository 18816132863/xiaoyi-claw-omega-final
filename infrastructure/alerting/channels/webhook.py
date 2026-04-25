#!/usr/bin/env python3
"""
Webhook 通知通道 - V1.0.0

支持通过 webhook 发送告警通知
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Optional

def get_webhook_url() -> Optional[str]:
    """获取 webhook URL"""
    return os.environ.get("ALERT_WEBHOOK_URL")

def send_webhook(alerts_report: Dict) -> bool:
    """发送 webhook 通知"""
    url = get_webhook_url()
    if not url:
        return False
    
    # 构建消息
    message = {
        "text": "🚨 OpenClaw 告警通知" if alerts_report.get("has_blocking_alerts") else "📋 OpenClaw 告警摘要",
        "alerts": alerts_report.get("alerts", []),
        "blocking_count": alerts_report.get("blocking_count", 0),
        "warning_count": alerts_report.get("warning_count", 0),
        "recommended_actions": alerts_report.get("recommended_actions", [])
    }
    
    try:
        data = json.dumps(message).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        print(f"Webhook 发送失败: {e}")
        return False
