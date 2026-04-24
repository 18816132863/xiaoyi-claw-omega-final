"""创建闹钟能力"""

from typing import Optional, Dict, Any, List
import uuid


def create_alarm(
    time: str,
    label: Optional[str] = None,
    repeat: Optional[List[str]] = None,
    enabled: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    创建闹钟
    
    Args:
        time: 闹钟时间（HH:MM 格式）
        label: 闹钟标签
        repeat: 重复日期（["mon", "tue", "wed", "thu", "fri", "sat", "sun"]）
        enabled: 是否启用
        dry_run: 是否预演模式
        
    Returns:
        创建结果
    """
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "create_alarm",
            "time": time,
            "label": label,
            "message": f"预演模式：将创建 {time} 的闹钟"
        }
    
    alarm_id = f"alarm_{uuid.uuid4().hex[:16]}"
    
    # TODO: 调用小艺闹钟创建接口
    return {
        "success": True,
        "alarm_id": alarm_id,
        "time": time,
        "label": label,
        "repeat": repeat or [],
        "enabled": enabled,
        "message": f"闹钟已创建: {time}"
    }


def run(**kwargs):
    """能力入口"""
    return create_alarm(**kwargs)
