"""副作用预览能力"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def preview_side_effect(
    capability: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """
    预览副作用操作的效果
    
    Args:
        capability: 能力名称
        params: 参数
        
    Returns:
        预览结果
    """
    # 定义副作用能力
    side_effect_capabilities = [
        "send_message",
        "schedule_task",
        "create_note",
        "send_notification",
        "delete_calendar_event",
        "delete_note",
        "cancel_notification",
        "update_calendar_event",
        "update_note"
    ]
    
    if capability not in side_effect_capabilities:
        return {
            "success": True,
            "is_side_effect": False,
            "message": f"{capability} 不是副作用操作"
        }
    
    # 生成预览
    preview = _generate_preview(capability, params)
    
    return {
        "success": True,
        "is_side_effect": True,
        "capability": capability,
        "preview": preview,
        "warnings": preview.get("warnings", []),
        "estimated_effects": preview.get("effects", []),
        "generated_at": datetime.now().isoformat()
    }


def _generate_preview(capability: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """生成预览"""
    previews = {
        "send_message": {
            "effects": [
                f"将发送短信到: {params.get('to', '未知')}",
                f"消息内容: {params.get('message', '')[:100]}...",
                "此操作会产生通信费用"
            ],
            "warnings": ["短信发送不可撤销"],
            "reversible": False
        },
        "schedule_task": {
            "effects": [
                f"将创建日程: {params.get('title', '无标题')}",
                f"开始时间: {params.get('start_time', '未知')}",
                f"结束时间: {params.get('end_time', '未知')}",
                f"地点: {params.get('location', '无')}"
            ],
            "warnings": [],
            "reversible": True,
            "reverse_action": "delete_calendar_event"
        },
        "create_note": {
            "effects": [
                f"将创建备忘录: {params.get('title', '无标题')}",
                f"内容长度: {len(params.get('content', ''))} 字符"
            ],
            "warnings": [],
            "reversible": True,
            "reverse_action": "delete_note"
        },
        "send_notification": {
            "effects": [
                f"将推送通知: {params.get('title', '无标题')}",
                f"内容: {params.get('content', '')[:100]}..."
            ],
            "warnings": [],
            "reversible": False
        },
        "delete_calendar_event": {
            "effects": [
                f"将删除日程: {params.get('event_id', '未知')}",
                "此操作不可撤销"
            ],
            "warnings": ["删除操作不可撤销"],
            "reversible": False
        },
        "delete_note": {
            "effects": [
                f"将删除备忘录: {params.get('note_id', '未知')}",
                "此操作不可撤销"
            ],
            "warnings": ["删除操作不可撤销"],
            "reversible": False
        },
        "cancel_notification": {
            "effects": [
                f"将取消通知: {params.get('notification_id', '未知')}"
            ],
            "warnings": ["取消后需要重新发送"],
            "reversible": False
        },
        "update_calendar_event": {
            "effects": [
                f"将更新日程: {params.get('event_id', '未知')}",
                f"更新内容: {params.get('updates', {})}"
            ],
            "warnings": [],
            "reversible": True,
            "reverse_action": "restore_previous_state"
        },
        "update_note": {
            "effects": [
                f"将更新备忘录: {params.get('note_id', '未知')}",
                f"更新内容: {params.get('updates', {})}"
            ],
            "warnings": [],
            "reversible": True,
            "reverse_action": "restore_previous_state"
        }
    }
    
    return previews.get(capability, {
        "effects": [f"将执行 {capability}"],
        "warnings": [],
        "reversible": False
    })


def batch_preview(
    actions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    批量预览副作用操作
    
    Args:
        actions: 操作列表 [{"capability": "...", "params": {...}}, ...]
        
    Returns:
        批量预览结果
    """
    previews = []
    all_effects = []
    all_warnings = []
    
    for action in actions:
        preview = preview_side_effect(
            capability=action.get("capability"),
            params=action.get("params", {})
        )
        previews.append(preview)
        
        if preview.get("is_side_effect"):
            all_effects.extend(preview.get("estimated_effects", []))
            all_warnings.extend(preview.get("warnings", []))
    
    return {
        "success": True,
        "total_actions": len(actions),
        "side_effect_count": len([p for p in previews if p.get("is_side_effect")]),
        "previews": previews,
        "all_effects": all_effects,
        "all_warnings": all_warnings,
        "has_warnings": len(all_warnings) > 0
    }


def run(**kwargs):
    """能力入口"""
    return preview_side_effect(**kwargs)
