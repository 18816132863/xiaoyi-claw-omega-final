"""任务分解器"""

from typing import List, Dict, Any
from .goal_parser import ParsedGoal
from .plan_schema import Plan, PlanStep


class TaskDecomposer:
    """任务分解器"""
    
    # 意图到能力的映射
    INTENT_CAPABILITY_MAP = {
        "remind": ["schedule.create_calendar_event", "notification.push"],
        "schedule": ["schedule.create_calendar_event"],
        "notify": ["notification.push"],
        "query": ["storage.search_notes"],
        "create": ["storage.create_note"],
        "delete": ["storage.delete_note"],
        "update": ["storage.update_note"],
    }
    
    def decompose(self, parsed_goal: ParsedGoal) -> Plan:
        """分解任务"""
        steps = []
        
        # 根据意图选择能力
        capabilities = self.INTENT_CAPABILITY_MAP.get(parsed_goal.intent, [])
        
        # 如果没有匹配，使用通用流程
        if not capabilities:
            capabilities = ["storage.create_note"]
        
        # 创建步骤
        for i, cap in enumerate(capabilities):
            step = PlanStep(
                step_id=i + 1,
                capability=cap,
                params=self._build_params(cap, parsed_goal),
                description=f"执行 {cap}",
                risk_level=self._assess_risk(cap),
            )
            steps.append(step)
        
        return Plan(
            goal=parsed_goal.original,
            intent=parsed_goal.intent,
            steps=steps,
            estimated_time=len(steps) * 2,  # 每步估计2秒
        )
    
    def _build_params(self, capability: str, parsed_goal: ParsedGoal) -> Dict[str, Any]:
        """构建参数"""
        params = {}
        
        if "calendar" in capability:
            params = {
                "title": parsed_goal.original[:50],
                "time": parsed_goal.entities.get("time", "09:00"),
                "date": parsed_goal.entities.get("date", "tomorrow"),
            }
        elif "notification" in capability:
            params = {
                "message": parsed_goal.original,
            }
        elif "note" in capability:
            params = {
                "content": parsed_goal.original,
                "title": parsed_goal.original[:30],
            }
        
        return params
    
    def _assess_risk(self, capability: str) -> str:
        """评估风险"""
        if "delete" in capability:
            return "L3"
        elif "send" in capability or "push" in capability:
            return "L2"
        elif "create" in capability or "update" in capability:
            return "L1"
        return "L0"
