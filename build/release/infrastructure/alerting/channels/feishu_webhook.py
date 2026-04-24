#!/usr/bin/env python3
"""
飞书 Webhook 通知通道 - V1.0.0

支持通过飞书机器人发送告警通知
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Optional, List
from datetime import datetime

def get_feishu_webhook_url() -> Optional[str]:
    """获取飞书 Webhook URL"""
    return os.environ.get("FEISHU_WEBHOOK_URL")

def build_feishu_message(alerts_report: Dict, incident_info: Optional[Dict] = None) -> Dict:
    """构建飞书消息卡片"""
    has_blocking = alerts_report.get("has_blocking_alerts", False)
    
    # 标题
    if has_blocking:
        title = "🚨 OpenClaw 阻塞告警"
        color = "red"
    else:
        title = "✅ OpenClaw 告警恢复"
        color = "green"
    
    # 内容
    content_lines = []
    
    # 告警统计
    content_lines.append(f"**总告警数**: {alerts_report.get('total_alerts', 0)}")
    content_lines.append(f"**阻塞级**: {alerts_report.get('blocking_count', 0)}")
    content_lines.append(f"**警告级**: {alerts_report.get('warning_count', 0)}")
    content_lines.append(f"**来源**: {alerts_report.get('source_workflow', 'unknown')}")
    content_lines.append(f"**Profile**: {alerts_report.get('profile', 'unknown')}")
    content_lines.append("")
    
    # 告警详情
    alerts = alerts_report.get("alerts", [])
    if alerts:
        content_lines.append("**告警详情:**")
        for alert in alerts[:5]:
            icon = "🚨" if alert.get("severity") == "blocking" else "⚠️"
            content_lines.append(f"- {icon} {alert.get('alert_type')}: {alert.get('message')}")
        content_lines.append("")
    
    # 阻塞原因
    blocked_reasons = alerts_report.get("blocked_reasons", [])
    if blocked_reasons:
        content_lines.append("**阻塞原因:**")
        for reason in blocked_reasons[:3]:
            content_lines.append(f"- {reason}")
        content_lines.append("")
    
    # Incident 信息
    if incident_info:
        content_lines.append("**Incident:**")
        content_lines.append(f"- ID: {incident_info.get('incident_id', 'N/A')}")
        content_lines.append(f"- 状态: {incident_info.get('status', 'unknown')}")
        if incident_info.get('incident_created'):
            content_lines.append("- ✅ 已创建新 Incident")
        if incident_info.get('incident_resolved'):
            content_lines.append("- ✅ 已自动关闭 Incident")
        content_lines.append("")
    
    # 建议操作
    recommended = alerts_report.get("recommended_actions", [])
    if recommended:
        content_lines.append("**建议操作:**")
        for action in recommended[:3]:
            content_lines.append(f"- {action}")
    
    # 构建飞书卡片
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": color
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "\n".join(content_lines)
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"时间: {alerts_report.get('generated_at', datetime.now().isoformat())}"
                        }
                    ]
                }
            ]
        }
    }
    
    return card

def send_feishu(alerts_report: Dict, incident_info: Optional[Dict] = None) -> Dict:
    """发送飞书通知"""
    url = get_feishu_webhook_url()
    
    result = {
        "channel": "feishu",
        "sent": False,
        "error": None,
        "timestamp": datetime.now().isoformat()
    }
    
    if not url:
        result["error"] = "FEISHU_WEBHOOK_URL 未配置"
        return result
    
    try:
        message = build_feishu_message(alerts_report, incident_info)
        data = json.dumps(message).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            if response_data.get("code") == 0 or response_data.get("StatusCode") == 0:
                result["sent"] = True
            else:
                result["error"] = response_data
        
    except Exception as e:
        result["error"] = str(e)
    
    return result

# 兼容旧接口
def send_webhook(alerts_report: Dict) -> bool:
    """发送 webhook 通知（兼容接口）"""
    result = send_feishu(alerts_report)
    return result["sent"]
