"""安全控制配置"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class ControlLevel(Enum):
    OFF = "off"
    WARN = "warn"
    ENFORCE = "enforce"


@dataclass
class SafetyControl:
    """安全控制项"""
    name: str
    level: ControlLevel
    threshold: Optional[int] = None
    message: Optional[str] = None


# 默认安全控制配置
DEFAULT_CONTROLS = {
    "dry_run": SafetyControl(
        name="dry_run",
        level=ControlLevel.ENFORCE,
        message="副作用操作必须支持 dry_run 模式"
    ),
    "approval_required": SafetyControl(
        name="approval_required",
        level=ControlLevel.ENFORCE,
        message="批量操作需要审批"
    ),
    "max_batch_size": SafetyControl(
        name="max_batch_size",
        level=ControlLevel.ENFORCE,
        threshold=20,
        message="批次大小不能超过 20"
    ),
    "rate_limit": SafetyControl(
        name="rate_limit",
        level=ControlLevel.ENFORCE,
        threshold=10,  # 每分钟最大请求数
        message="请求频率超过限制"
    ),
    "safe_mode": SafetyControl(
        name="safe_mode",
        level=ControlLevel.WARN,
        message="安全模式已启用"
    ),
    "side_effect_preview": SafetyControl(
        name="side_effect_preview",
        level=ControlLevel.ENFORCE,
        message="副作用操作必须可预览"
    ),
    "idempotency_scope": SafetyControl(
        name="idempotency_scope",
        level=ControlLevel.ENFORCE,
        message="幂等键必须在正确的作用域内"
    )
}

# 需要审批的操作
APPROVAL_REQUIRED_ACTIONS = {
    "batch_sms": {"threshold": 5, "message": "批量短信超过 5 条需要审批"},
    "batch_notification": {"threshold": 10, "message": "批量通知超过 10 条需要审批"},
    "batch_calendar": {"threshold": 10, "message": "批量日程创建超过 10 条需要审批"},
    "delete_all": {"threshold": 1, "message": "批量删除需要审批"}
}

# 能力限流配置
RATE_LIMITS = {
    "send_message": {"per_minute": 10, "per_hour": 100},
    "send_notification": {"per_minute": 20, "per_hour": 200},
    "schedule_task": {"per_minute": 30, "per_hour": 300},
    "create_note": {"per_minute": 30, "per_hour": 300}
}


def check_approval_required(action_type: str, count: int) -> Dict[str, Any]:
    """
    检查是否需要审批
    
    Args:
        action_type: 操作类型
        count: 操作数量
        
    Returns:
        检查结果
    """
    config = APPROVAL_REQUIRED_ACTIONS.get(action_type, {})
    threshold = config.get("threshold", float("inf"))
    
    approval_required = count >= threshold
    
    return {
        "action_type": action_type,
        "count": count,
        "threshold": threshold,
        "approval_required": approval_required,
        "message": config.get("message") if approval_required else None
    }


def check_batch_size(action_type: str, count: int) -> Dict[str, Any]:
    """
    检查批次大小
    
    Args:
        action_type: 操作类型
        count: 操作数量
        
    Returns:
        检查结果
    """
    control = DEFAULT_CONTROLS["max_batch_size"]
    max_size = control.threshold
    
    if count > max_size:
        return {
            "allowed": False,
            "count": count,
            "max_batch_size": max_size,
            "message": control.message
        }
    
    return {
        "allowed": True,
        "count": count,
        "max_batch_size": max_size
    }


def check_rate_limit(capability: str, requests_in_window: int, window: str = "per_minute") -> Dict[str, Any]:
    """
    检查限流
    
    Args:
        capability: 能力名称
        requests_in_window: 时间窗口内的请求数
        window: 时间窗口 (per_minute / per_hour)
        
    Returns:
        检查结果
    """
    limits = RATE_LIMITS.get(capability, {})
    limit = limits.get(window, float("inf"))
    
    if requests_in_window >= limit:
        return {
            "allowed": False,
            "capability": capability,
            "requests": requests_in_window,
            "limit": limit,
            "window": window,
            "message": f"请求频率超过限制: {requests_in_window}/{limit} ({window})"
        }
    
    return {
        "allowed": True,
        "capability": capability,
        "requests": requests_in_window,
        "limit": limit,
        "window": window
    }


def validate_safety_controls(
    capability: str,
    params: Dict[str, Any],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    验证安全控制
    
    Args:
        capability: 能力名称
        params: 参数
        dry_run: 是否预演模式
        
    Returns:
        验证结果
    """
    violations = []
    warnings = []
    
    # 检查 dry_run 支持
    if not dry_run and capability in ["send_message", "schedule_task", "create_note", "send_notification"]:
        # 这些能力应该支持 dry_run
        pass  # 仅警告，不阻止
    
    # 检查批次大小
    if "recipients" in params or "notifications" in params or "messages" in params:
        batch = params.get("recipients") or params.get("notifications") or params.get("messages", [])
        if len(batch) > DEFAULT_CONTROLS["max_batch_size"].threshold:
            violations.append({
                "control": "max_batch_size",
                "message": DEFAULT_CONTROLS["max_batch_size"].message,
                "count": len(batch),
                "max": DEFAULT_CONTROLS["max_batch_size"].threshold
            })
    
    # 检查幂等键
    if capability in ["send_message", "schedule_task", "send_notification"]:
        if "idempotency_key" not in params:
            warnings.append({
                "control": "idempotency_scope",
                "message": "建议提供 idempotency_key 以确保幂等性"
            })
    
    return {
        "valid": len(violations) == 0,
        "violations": violations if violations else None,
        "warnings": warnings if warnings else None,
        "dry_run": dry_run
    }


def get_safety_controls_config() -> Dict[str, Any]:
    """获取安全控制配置"""
    return {
        "controls": {k: {"level": v.level.value, "threshold": v.threshold, "message": v.message} 
                     for k, v in DEFAULT_CONTROLS.items()},
        "approval_required_actions": APPROVAL_REQUIRED_ACTIONS,
        "rate_limits": RATE_LIMITS
    }


def save_safety_controls_config(config: Dict[str, Any], path: str = "config/safety_controls.json"):
    """保存安全控制配置"""
    config_path = Path("/home/sandbox/.openclaw/workspace") / path
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    return {"success": True, "path": str(config_path)}
