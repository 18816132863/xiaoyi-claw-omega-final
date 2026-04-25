"""
Route Selector

Planner 使用 route_registry 选择 route
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class RouteSelection:
    """Route 选择结果"""
    selected_route_id: str
    candidate_routes: List[str]
    selection_reason: str
    risk_level: str
    policy: str
    requires_confirmation: bool
    fallback_routes: List[str]
    confidence: float
    
    def to_dict(self) -> dict:
        return asdict(self)


class RouteSelector:
    """Route 选择器"""
    
    def __init__(self, registry_path: str = "infrastructure/route_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
        self.intent_index = self._build_intent_index()
    
    def _load_registry(self) -> dict:
        if self.registry_path.exists():
            return json.loads(self.registry_path.read_text())
        return {"routes": {}}
    
    def _build_intent_index(self) -> Dict[str, List[str]]:
        """构建意图索引"""
        index = {}
        for route_id, route in self.registry.get("routes", {}).items():
            intents = route.get("user_intents", [])
            for intent in intents:
                intent_lower = intent.lower()
                if intent_lower not in index:
                    index[intent_lower] = []
                index[intent_lower].append(route_id)
        return index
    
    def _match_intent(self, goal: str) -> List[str]:
        """匹配意图"""
        goal_lower = goal.lower()
        candidates = []
        
        # 精确匹配
        if goal_lower in self.intent_index:
            candidates.extend(self.intent_index[goal_lower])
        
        # 模糊匹配
        for intent, routes in self.intent_index.items():
            if intent in goal_lower or goal_lower in intent:
                for r in routes:
                    if r not in candidates:
                        candidates.append(r)
        
        return candidates
    
    def _calculate_priority(self, route_id: str, route: dict) -> float:
        """计算优先级分数"""
        score = 0.0
        
        # 状态优先级
        status = route.get("status", "generated")
        status_scores = {"active": 100, "verified": 80, "generated": 50, "failed": 0, "deprecated": -100}
        score += status_scores.get(status, 0)
        
        # 风险等级优先级 (低风险优先)
        risk = route.get("risk_level", "L3")
        risk_scores = {"L0": 40, "L1": 30, "L2": 20, "L3": 10, "L4": 5, "BLOCKED": -50}
        score += risk_scores.get(risk, 0)
        
        # 激活次数
        activation = route.get("activation", {})
        score += min(activation.get("activation_count", 0) * 5, 20)
        
        return score
    
    def select_route(self, goal: str, context: dict = None) -> Optional[RouteSelection]:
        """选择 route"""
        context = context or {}
        
        # 匹配候选 routes
        candidates = self._match_intent(goal)
        
        if not candidates:
            return None
        
        # 计算优先级并排序
        scored_candidates = []
        for route_id in candidates:
            route = self.registry["routes"].get(route_id, {})
            score = self._calculate_priority(route_id, route)
            scored_candidates.append((route_id, score, route))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 选择最佳 route
        selected_id, selected_score, selected_route = scored_candidates[0]
        
        # 构建选择结果
        return RouteSelection(
            selected_route_id=selected_id,
            candidate_routes=[c[0] for c in scored_candidates[:5]],
            selection_reason=f"Best match for '{goal}' with score {selected_score:.1f}",
            risk_level=selected_route.get("risk_level", "L3"),
            policy=selected_route.get("policy", "confirm_once"),
            requires_confirmation=selected_route.get("requires_confirmation", True),
            fallback_routes=selected_route.get("fallback_routes", []),
            confidence=min(selected_score / 100.0, 1.0)
        )
    
    def get_route(self, route_id: str) -> Optional[dict]:
        """获取 route 详情"""
        return self.registry["routes"].get(route_id)
    
    def get_routes_by_capability(self, capability: str) -> List[str]:
        """按能力查找 routes"""
        return [
            rid for rid, r in self.registry["routes"].items()
            if r.get("capability") == capability
        ]
    
    def get_routes_by_risk(self, risk_level: str) -> List[str]:
        """按风险等级查找 routes"""
        return [
            rid for rid, r in self.registry["routes"].items()
            if r.get("risk_level") == risk_level
        ]


def get_route_selector(registry_path: str = None) -> RouteSelector:
    """获取 Route 选择器实例"""
    if registry_path:
        return RouteSelector(registry_path)
    return RouteSelector()
