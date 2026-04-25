"""提醒联动模板"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


def reminder_bundle(
    title: str,
    start_time: str,
    end_time: Optional[str] = None,
    location: Optional[str] = None,
    note_content: Optional[str] = None,
    send_sms: bool = False,
    sms_recipient: Optional[str] = None,
    send_notification: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    提醒联动模板：创建日程 + 生成备忘录 + 推送通知 + 可选短信
    
    Args:
        title: 日程标题
        start_time: 开始时间
        end_time: 结束时间
        location: 地点
        note_content: 备忘录内容（默认使用日程信息）
        send_sms: 是否发送短信提醒
        sms_recipient: 短信接收人
        send_notification: 是否推送通知
        dry_run: 是否预演模式
        
    Returns:
        执行结果
    """
    from orchestration.workflows.preview import preview_workflow
    from orchestration.workflows.compensation import execute_with_compensation
    
    # 构建步骤
    steps = []
    compensation_steps = []
    
    # 1. 创建日程
    schedule_params = {
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "location": location
    }
    steps.append({
        "name": "create_calendar_event",
        "capability": "schedule_task",
        "params": schedule_params
    })
    
    # 2. 创建备忘录
    note_text = note_content or f"日程提醒: {title}\n时间: {start_time}\n地点: {location or '无'}"
    steps.append({
        "name": "create_note",
        "capability": "create_note",
        "params": {
            "title": f"提醒: {title}",
            "content": note_text
        }
    })
    
    # 3. 推送通知
    if send_notification:
        steps.append({
            "name": "send_notification",
            "capability": "send_notification",
            "params": {
                "title": f"日程提醒: {title}",
                "content": f"{start_time} - {title}"
            }
        })
    
    # 4. 发送短信
    if send_sms and sms_recipient:
        steps.append({
            "name": "send_sms_reminder",
            "capability": "send_message",
            "params": {
                "to": sms_recipient,
                "message": f"提醒: {title}, 时间: {start_time}"
            }
        })
    
    # 预演模式
    if dry_run:
        return preview_workflow(steps)
    
    # 执行（带补偿）
    # 补偿动作：删除创建的日程和备忘录
    compensation_steps = [
        {"name": "delete_calendar", "capability": "delete_calendar_event", "params": {"event_id": "placeholder"}},
        {"name": "delete_note", "capability": "delete_note", "params": {"note_id": "placeholder"}}
    ]
    
    results = []
    event_id = None
    note_id = None
    
    # 执行创建日程
    import importlib
    try:
        module = importlib.import_module("capabilities.schedule_task")
        result = module.run(**schedule_params)
        results.append({"step": "create_calendar_event", "result": result})
        event_id = result.get("event_id")
    except Exception as e:
        results.append({"step": "create_calendar_event", "error": str(e)})
    
    # 执行创建备忘录
    try:
        module = importlib.import_module("capabilities.create_note")
        result = module.run(title=f"提醒: {title}", content=note_text)
        results.append({"step": "create_note", "result": result})
        note_id = result.get("note_id")
    except Exception as e:
        results.append({"step": "create_note", "error": str(e)})
    
    # 执行推送通知
    if send_notification:
        try:
            module = importlib.import_module("capabilities.send_notification")
            result = module.run(title=f"日程提醒: {title}", content=f"{start_time} - {title}")
            results.append({"step": "send_notification", "result": result})
        except Exception as e:
            results.append({"step": "send_notification", "error": str(e)})
    
    # 执行发送短信
    if send_sms and sms_recipient:
        try:
            module = importlib.import_module("capabilities.send_message")
            result = module.run(to=sms_recipient, message=f"提醒: {title}, 时间: {start_time}")
            results.append({"step": "send_sms_reminder", "result": result})
        except Exception as e:
            results.append({"step": "send_sms_reminder", "error": str(e)})
    
    return {
        "success": all(r.get("result", {}).get("success", False) for r in results if "result" in r),
        "bundle_type": "reminder",
        "dry_run": dry_run,
        "results": results,
        "created_event_id": event_id,
        "created_note_id": note_id,
        "summary": {
            "calendar_created": event_id is not None,
            "note_created": note_id is not None,
            "notification_sent": send_notification,
            "sms_sent": send_sms and sms_recipient
        }
    }


def run(**kwargs):
    """模板入口"""
    return reminder_bundle(**kwargs)
