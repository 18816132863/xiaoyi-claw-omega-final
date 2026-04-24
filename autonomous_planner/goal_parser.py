"""目标解析器"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ParsedGoal:
    """解析后的目标"""
    original: str
    intent: str  # remind, schedule, notify, query, automate
    entities: Dict[str, Any]
    constraints: List[str]
    priority: str  # high, medium, low


class GoalParser:
    """目标解析器"""
    
    INTENT_KEYWORDS = {
        "remind": ["提醒", "记得", "别忘了", "通知我"],
        "schedule": ["日程", "安排", "预约", "会议", "日历"],
        "notify": ["通知", "推送", "发消息", "告诉"],
        "query": ["查询", "看看", "帮我查", "搜索"],
        "automate": ["自动", "帮我", "操作", "执行"],
        "create": ["创建", "新建", "添加", "写"],
        "delete": ["删除", "移除", "取消"],
        "update": ["更新", "修改", "更改"],
    }
    
    def parse(self, goal: str) -> ParsedGoal:
        """解析目标"""
        goal_lower = goal.lower()
        
        # 确定意图
        intent = "automate"
        for i, keywords in self.INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in goal_lower:
                    intent = i
                    break
        
        # 提取实体
        entities = self._extract_entities(goal)
        
        # 提取约束
        constraints = self._extract_constraints(goal)
        
        # 确定优先级
        priority = self._determine_priority(goal)
        
        return ParsedGoal(
            original=goal,
            intent=intent,
            entities=entities,
            constraints=constraints,
            priority=priority,
        )
    
    def _extract_entities(self, goal: str) -> Dict[str, Any]:
        """提取实体"""
        import re
        entities = {}
        
        # 时间
        time_patterns = [
            (r"(\d{1,2}:\d{2})", "time"),
            (r"明天", "date"),
            (r"后天", "date"),
            (r"下周", "week"),
            (r"(\d+)月(\d+)日", "date"),
        ]
        
        for pattern, key in time_patterns:
            match = re.search(pattern, goal)
            if match:
                entities[key] = match.group(0)
        
        # 人物
        if "我" in goal:
            entities["subject"] = "user"
        
        # 地点
        location_patterns = ["去", "在", "到"]
        for lp in location_patterns:
            if lp in goal:
                idx = goal.index(lp)
                entities["location_hint"] = goal[idx:idx+10]
        
        return entities
    
    def _extract_constraints(self, goal: str) -> List[str]:
        """提取约束"""
        constraints = []
        
        constraint_keywords = {
            "必须": "required",
            "尽量": "preferred",
            "不要": "avoid",
            "避免": "avoid",
        }
        
        for kw, constraint in constraint_keywords.items():
            if kw in goal:
                constraints.append(constraint)
        
        return constraints
    
    def _determine_priority(self, goal: str) -> str:
        """确定优先级"""
        high_keywords = ["紧急", "重要", "马上", "立即", "尽快"]
        for kw in high_keywords:
            if kw in goal:
                return "high"
        
        low_keywords = ["有空", "方便", "稍后"]
        for kw in low_keywords:
            if kw in goal:
                return "low"
        
        return "medium"
