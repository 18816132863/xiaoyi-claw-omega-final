#!/usr/bin/env python3
"""
自动路由注册器
从 capability_registry.json 自动生成 route_registry.json
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


# 用户意图到能力的映射
INTENT_MAPPING = {
    # 消息相关
    "发送消息": ["send_message"],
    "发消息": ["send_message"],
    "给某人发消息": ["send_message"],
    "重发消息": ["resend_message"],
    "查看消息状态": ["query_message_status"],
    "列出最近消息": ["list_recent_messages"],
    "解释消息结果": ["explain_message_result"],
    
    # 备忘录相关
    "查询备忘录": ["query_note"],
    "搜索备忘录": ["search_notes"],
    "列出备忘录": ["list_recent_notes"],
    "更新备忘录": ["update_note"],
    "删除备忘录": ["delete_note"],
    
    # 日程相关
    "查询日程": ["query_calendar_event"],
    "列出日程": ["list_calendar_events"],
    "更新日程": ["update_calendar_event"],
    "删除日程": ["delete_calendar_event"],
    "检查日程冲突": ["check_calendar_conflicts"],
    
    # 闹钟相关
    "创建闹钟": ["create_alarm"],
    "设置闹钟": ["create_alarm"],
    "查询闹钟": ["query_alarm"],
    "更新闹钟": ["update_alarm"],
    "删除闹钟": ["delete_alarm"],
    
    # 联系人相关
    "创建联系人": ["create_contact"],
    "添加联系人": ["create_contact"],
    "查询联系人": ["query_contact"],
    "更新联系人": ["update_contact"],
    "删除联系人": ["delete_contact"],
    
    # 图库相关
    "查询照片": ["query_photo"],
    "创建相册": ["create_album"],
    "删除照片": ["delete_photo"],
    
    # 文件相关
    "查询文件": ["query_file"],
    "管理文件": ["manage_file"],
    "删除文件": ["delete_file"],
    
    # 通知相关
    "查询通知状态": ["query_notification_status"],
    "取消通知": ["cancel_notification"],
    "刷新通知授权": ["refresh_notification_auth"],
    "解释通知授权状态": ["explain_notification_auth_state"],
    
    # 位置相关
    "获取位置": ["get_location"],
    "定位": ["get_location"],
    
    # 电话相关
    "拨打电话": ["make_call"],
    "打电话": ["make_call"],
    
    # 任务相关
    "调度任务": ["schedule_task"],
    "暂停任务": ["pause_task"],
    "恢复任务": ["resume_task"],
    "取消任务": ["cancel_task"],
    "重试任务": ["retry_task"],
    
    # 小艺帮记相关
    "查询小艺帮记": ["query_xiaoyi_note"],
    "删除小艺帮记": ["delete_xiaoyi_note"],
    
    # 审批相关
    "审批动作": ["approve_action"],
    "预览副作用": ["preview_side_effect"],
    
    # 系统相关
    "诊断": ["diagnostics"],
    "自修复": ["self_repair"],
    "引导": ["bootstrap"],
    "注册表": ["registry"],
    "导出历史": ["export_history"],
    "重放运行": ["replay_run"],
    "审计查询": ["audit_queries"],
    "解释调用状态": ["explain_invocation_status"],
    "确认调用": ["confirm_invocation"],
}

# 能力风险等级
RISK_LEVELS = {
    # 高风险 - 不可逆操作
    "delete_note": "HIGH",
    "delete_contact": "HIGH",
    "delete_photo": "HIGH",
    "delete_file": "HIGH",
    "delete_calendar_event": "HIGH",
    "delete_alarm": "HIGH",
    "delete_xiaoyi_note": "HIGH",
    "make_call": "HIGH",
    "send_message": "HIGH",
    "resend_message": "HIGH",
    
    # 中风险 - 可逆但有影响
    "update_note": "MEDIUM",
    "update_contact": "MEDIUM",
    "update_calendar_event": "MEDIUM",
    "update_alarm": "MEDIUM",
    "create_contact": "MEDIUM",
    "create_alarm": "MEDIUM",
    "create_album": "MEDIUM",
    "manage_file": "MEDIUM",
    "schedule_task": "MEDIUM",
    "cancel_task": "MEDIUM",
    "approve_action": "MEDIUM",
    "cancel_notification": "MEDIUM",
    
    # 低风险 - 只读或无副作用
    "query_note": "LOW",
    "query_contact": "LOW",
    "query_photo": "LOW",
    "query_file": "LOW",
    "query_calendar_event": "LOW",
    "query_alarm": "LOW",
    "query_message_status": "LOW",
    "query_notification_status": "LOW",
    "query_xiaoyi_note": "LOW",
    "list_recent_notes": "LOW",
    "list_recent_messages": "LOW",
    "list_calendar_events": "LOW",
    "search_notes": "LOW",
    "check_calendar_conflicts": "LOW",
    "get_location": "LOW",
    "diagnostics": "LOW",
    "explain_message_result": "LOW",
    "explain_notification_auth_state": "LOW",
    "explain_invocation_status": "LOW",
    "export_history": "LOW",
    "audit_queries": "LOW",
    
    # 系统级 - 需特殊处理
    "self_repair": "SYSTEM",
    "bootstrap": "SYSTEM",
    "registry": "SYSTEM",
    "replay_run": "SYSTEM",
    "confirm_invocation": "SYSTEM",
    "preview_side_effect": "SYSTEM",
    "refresh_notification_auth": "SYSTEM",
    "pause_task": "LOW",
    "resume_task": "LOW",
    "retry_task": "LOW",
}

# Fallback 路由
FALLBACK_ROUTES = {
    "send_message": ["list_recent_messages", "query_message_status"],
    "make_call": ["query_contact"],
    "create_alarm": ["query_alarm"],
    "create_calendar_event": ["query_calendar_event", "check_calendar_conflicts"],
    "delete_note": ["query_note"],
    "delete_contact": ["query_contact"],
    "delete_photo": ["query_photo"],
    "delete_file": ["query_file"],
    "delete_calendar_event": ["query_calendar_event"],
    "delete_alarm": ["query_alarm"],
    "schedule_task": ["query_note"],  # 失败时记录到备忘录
}

# Handler 映射
HANDLER_MAPPING = {
    "send_message": "device_capability_bus.capabilities.message.send_message",
    "resend_message": "device_capability_bus.capabilities.message.resend_message",
    "query_message_status": "device_capability_bus.capabilities.message.query_status",
    "list_recent_messages": "device_capability_bus.capabilities.message.list_recent",
    "explain_message_result": "device_capability_bus.capabilities.message.explain_result",
    
    "create_note": "device_capability_bus.capabilities.note.create_note",
    "query_note": "device_capability_bus.capabilities.note.query_note",
    "search_notes": "device_capability_bus.capabilities.note.search_notes",
    "list_recent_notes": "device_capability_bus.capabilities.note.list_recent",
    "update_note": "device_capability_bus.capabilities.note.update_note",
    "delete_note": "device_capability_bus.capabilities.note.delete_note",
    
    "create_calendar_event": "device_capability_bus.capabilities.calendar.create_event",
    "query_calendar_event": "device_capability_bus.capabilities.calendar.query_event",
    "list_calendar_events": "device_capability_bus.capabilities.calendar.list_events",
    "update_calendar_event": "device_capability_bus.capabilities.calendar.update_event",
    "delete_calendar_event": "device_capability_bus.capabilities.calendar.delete_event",
    "check_calendar_conflicts": "device_capability_bus.capabilities.calendar.check_conflicts",
    
    "create_alarm": "device_capability_bus.capabilities.alarm.create_alarm",
    "query_alarm": "device_capability_bus.capabilities.alarm.query_alarm",
    "update_alarm": "device_capability_bus.capabilities.alarm.update_alarm",
    "delete_alarm": "device_capability_bus.capabilities.alarm.delete_alarm",
    
    "create_contact": "device_capability_bus.capabilities.contact.create_contact",
    "query_contact": "device_capability_bus.capabilities.contact.query_contact",
    "update_contact": "device_capability_bus.capabilities.contact.update_contact",
    "delete_contact": "device_capability_bus.capabilities.contact.delete_contact",
    
    "query_photo": "device_capability_bus.capabilities.photo.query_photo",
    "create_album": "device_capability_bus.capabilities.photo.create_album",
    "delete_photo": "device_capability_bus.capabilities.photo.delete_photo",
    
    "query_file": "device_capability_bus.capabilities.file.query_file",
    "manage_file": "device_capability_bus.capabilities.file.manage_file",
    "delete_file": "device_capability_bus.capabilities.file.delete_file",
    
    "get_location": "device_capability_bus.capabilities.location.get_location",
    "make_call": "device_capability_bus.capabilities.call.make_call",
    
    "query_notification_status": "device_capability_bus.capabilities.notification.query_status",
    "cancel_notification": "device_capability_bus.capabilities.notification.cancel_notification",
    "refresh_notification_auth": "device_capability_bus.capabilities.notification.refresh_auth",
    "explain_notification_auth_state": "device_capability_bus.capabilities.notification.explain_auth_state",
    
    "query_xiaoyi_note": "device_capability_bus.capabilities.xiaoyi_note.query_note",
    "delete_xiaoyi_note": "device_capability_bus.capabilities.xiaoyi_note.delete_note",
    
    "schedule_task": "autonomous_planner.task_decomposer.schedule_task",
    "pause_task": "autonomous_planner.task_decomposer.pause_task",
    "resume_task": "autonomous_planner.task_decomposer.resume_task",
    "cancel_task": "autonomous_planner.task_decomposer.cancel_task",
    "retry_task": "autonomous_planner.task_decomposer.retry_task",
    
    "approve_action": "governance.review.change_review.approve_action",
    "preview_side_effect": "governance.review.change_review.preview_side_effect",
    
    "diagnostics": "core.diagnostics.run_diagnostics",
    "self_repair": "core.recovery.self_repair",
    "bootstrap": "core.bootstrap.run_bootstrap",
    "registry": "core.registry.manage_registry",
    "export_history": "core.history.export_history",
    "replay_run": "core.replay.replay_run",
    "audit_queries": "core.audit.audit_queries",
    "explain_invocation_status": "core.invocation.explain_status",
    "confirm_invocation": "core.invocation.confirm_invocation",
}

# Input Schema 模板
INPUT_SCHEMAS = {
    "send_message": {
        "type": "object",
        "properties": {
            "recipient": {"type": "string", "description": "接收者"},
            "message": {"type": "string", "description": "消息内容"},
            "channel": {"type": "string", "description": "发送渠道"}
        },
        "required": ["recipient", "message"]
    },
    "create_note": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "标题"},
            "content": {"type": "string", "description": "内容"}
        },
        "required": ["title", "content"]
    },
    "create_alarm": {
        "type": "object",
        "properties": {
            "time": {"type": "string", "description": "闹钟时间"},
            "label": {"type": "string", "description": "标签"},
            "repeat": {"type": "boolean", "description": "是否重复"}
        },
        "required": ["time"]
    },
    "create_calendar_event": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "事件标题"},
            "start_time": {"type": "string", "description": "开始时间"},
            "end_time": {"type": "string", "description": "结束时间"},
            "location": {"type": "string", "description": "地点"}
        },
        "required": ["title", "start_time"]
    },
    "make_call": {
        "type": "object",
        "properties": {
            "contact": {"type": "string", "description": "联系人姓名或号码"}
        },
        "required": ["contact"]
    },
    "query_note": {
        "type": "object",
        "properties": {
            "keyword": {"type": "string", "description": "搜索关键词"},
            "limit": {"type": "integer", "description": "返回数量限制"}
        }
    },
    "delete_note": {
        "type": "object",
        "properties": {
            "note_id": {"type": "string", "description": "备忘录ID"}
        },
        "required": ["note_id"]
    },
}

# Output Schema 模板
OUTPUT_SCHEMAS = {
    "send_message": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "message_id": {"type": "string"},
            "error": {"type": "string"}
        }
    },
    "create_note": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "note_id": {"type": "string"},
            "error": {"type": "string"}
        }
    },
    "query_note": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "notes": {"type": "array"},
            "error": {"type": "string"}
        }
    },
}


def load_capability_registry() -> Dict[str, Any]:
    """加载能力注册表"""
    registry_path = Path(__file__).parent.parent / "infrastructure" / "inventory" / "capability_registry.json"
    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_route_id(capability_name: str) -> str:
    """生成路由ID"""
    return f"route.{capability_name}"


def generate_route(capability_name: str, capability_info: Dict) -> Dict:
    """为单个能力生成路由"""
    route_id = generate_route_id(capability_name)
    
    # 查找对应的用户意图
    user_intents = []
    for intent, caps in INTENT_MAPPING.items():
        if capability_name in caps:
            user_intents.append(intent)
    
    # 获取风险等级
    risk_level = RISK_LEVELS.get(capability_name, "LOW")
    
    # 是否需要确认
    requires_confirmation = risk_level in ["HIGH", "SYSTEM"]
    
    # 获取 handler
    handler = HANDLER_MAPPING.get(capability_name, f"capabilities.{capability_name}.execute")
    
    # 获取 fallback
    fallback_routes = FALLBACK_ROUTES.get(capability_name, [])
    
    # 获取 input/output schema
    input_schema = INPUT_SCHEMAS.get(capability_name, {
        "type": "object",
        "properties": {},
        "required": []
    })
    output_schema = OUTPUT_SCHEMAS.get(capability_name, {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "error": {"type": "string"}
        }
    })
    
    return {
        "route_id": route_id,
        "capability": capability_name,
        "user_intents": user_intents,
        "handler": handler,
        "input_schema": input_schema,
        "output_schema": output_schema,
        "risk_level": risk_level,
        "requires_confirmation": requires_confirmation,
        "fallback_routes": fallback_routes,
        "tested_by": f"tests.test_route_{capability_name}",
        "documented_in": f"docs/routes/{capability_name}.md",
        "status": "generated",
        "created_at": datetime.now().isoformat(),
        "metadata": {
            "description": capability_info.get("description", ""),
            "original_path": capability_info.get("path", "")
        }
    }


def auto_register_routes() -> Dict[str, Any]:
    """自动注册所有路由"""
    capability_registry = load_capability_registry()
    items = capability_registry.get("items", {})
    
    routes = {}
    stats = {
        "total": 0,
        "by_risk_level": {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "SYSTEM": 0
        },
        "by_status": {
            "generated": 0,
            "verified": 0,
            "active": 0
        },
        "with_fallback": 0,
        "requires_confirmation": 0
    }
    
    for cap_name, cap_info in items.items():
        route = generate_route(cap_name, cap_info)
        routes[route["route_id"]] = route
        
        # 更新统计
        stats["total"] += 1
        stats["by_risk_level"][route["risk_level"]] += 1
        stats["by_status"][route["status"]] += 1
        if route["fallback_routes"]:
            stats["with_fallback"] += 1
        if route["requires_confirmation"]:
            stats["requires_confirmation"] += 1
    
    route_registry = {
        "version": "1.0.0",
        "updated": datetime.now().isoformat(),
        "routes": routes,
        "intent_index": build_intent_index(routes),
        "stats": stats,
        "description": "路由注册表 - 用户意图到能力的映射"
    }
    
    return route_registry


def build_intent_index(routes: Dict) -> Dict[str, List[str]]:
    """构建意图索引"""
    intent_index = {}
    for route_id, route in routes.items():
        for intent in route.get("user_intents", []):
            if intent not in intent_index:
                intent_index[intent] = []
            intent_index[intent].append(route_id)
    return intent_index


def save_route_registry(registry: Dict) -> str:
    """保存路由注册表"""
    output_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    return str(output_path)


def main():
    """主函数"""
    print("=" * 60)
    print("自动路由注册器")
    print("=" * 60)
    
    # 生成路由注册表
    registry = auto_register_routes()
    
    # 保存
    output_path = save_route_registry(registry)
    
    # 打印统计
    stats = registry["stats"]
    print(f"\n✅ 路由注册表已生成")
    print(f"   文件: {output_path}")
    print(f"\n📊 统计:")
    print(f"   总路由数: {stats['total']}")
    print(f"   按风险等级:")
    print(f"     - LOW: {stats['by_risk_level']['LOW']}")
    print(f"     - MEDIUM: {stats['by_risk_level']['MEDIUM']}")
    print(f"     - HIGH: {stats['by_risk_level']['HIGH']}")
    print(f"     - SYSTEM: {stats['by_risk_level']['SYSTEM']}")
    print(f"   带 fallback: {stats['with_fallback']}")
    print(f"   需确认: {stats['requires_confirmation']}")
    print(f"   意图索引: {len(registry['intent_index'])} 条")
    
    return 0


if __name__ == "__main__":
    exit(main())
