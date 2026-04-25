"""计划优化器 - 基于历史经验优化计划"""

from typing import Dict, Any, List, Optional
from .execution_memory import ExecutionMemory
from .success_path_store import SuccessPathStore
from .preference_profile import PreferenceProfile
from .pattern_extractor import PatternExtractor


class PlanOptimizer:
    """计划优化器"""
    
    def __init__(
        self,
        memory: Optional[ExecutionMemory] = None,
        path_store: Optional[SuccessPathStore] = None,
        preferences: Optional[PreferenceProfile] = None,
    ):
        self.memory = memory or ExecutionMemory()
        self.path_store = path_store or SuccessPathStore()
        self.preferences = preferences or PreferenceProfile.load()
    
    def optimize(self, goal: str, initial_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """优化计划"""
        goal_pattern = PatternExtractor.extract_goal_pattern(goal)
        
        # 查找成功路径
        best_path = self.path_store.find_best_path(goal_pattern)
        
        # 获取偏好提示
        pref_hints = self.memory.get_preference_hints(goal)
        
        # 获取失败步骤
        failed_steps = self.memory.get_failed_steps(goal)
        
        # 构建优化结果
        optimized_plan = initial_plan.copy()
        optimizations = []
        
        # 如果有成功路径，复用
        if best_path:
            optimizations.append({
                "type": "reuse_success_path",
                "path_id": best_path.path_id,
                "success_count": best_path.success_count,
            })
            
            # 使用成功路径的计划
            optimized_plan = best_path.plan
        
        # 应用偏好
        if pref_hints.get("preferred_capabilities"):
            optimizations.append({
                "type": "apply_preferred_capabilities",
                "capabilities": pref_hints["preferred_capabilities"],
            })
        
        # 避开失败步骤
        if failed_steps:
            optimizations.append({
                "type": "avoid_failed_steps",
                "steps": failed_steps,
            })
        
        # 减少追问（如果偏好如此）
        if self.preferences.prefer_less_questions:
            optimizations.append({
                "type": "reduce_confirmations",
                "hint": "基于历史经验，减少不必要的确认",
            })
        
        return {
            "goal": goal,
            "goal_pattern": goal_pattern,
            "initial_plan": initial_plan,
            "optimized_plan": optimized_plan,
            "optimizations": optimizations,
            "confidence": self._calculate_confidence(best_path, pref_hints),
            "warning": self._generate_warning(goal_pattern),
        }
    
    def _calculate_confidence(self, best_path, pref_hints) -> float:
        """计算置信度"""
        if not best_path and not pref_hints:
            return 0.5  # 无历史，中等置信度
        
        confidence = 0.5
        
        if best_path:
            confidence += min(0.3, best_path.success_count * 0.1)
        
        if pref_hints.get("preferred_capabilities"):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_warning(self, goal_pattern: str) -> Optional[str]:
        """生成警告"""
        # L4 操作始终需要强确认
        l4_patterns = ["payment", "account", "privacy", "financial"]
        if goal_pattern in l4_patterns:
            return "⚠️ 该操作属于高风险类别，即使有历史经验，仍需强确认"
        return None
    
    def explain(self, goal: str) -> str:
        """解释为什么这样优化"""
        goal_pattern = PatternExtractor.extract_goal_pattern(goal)
        best_path = self.path_store.find_best_path(goal_pattern)
        similar = self.memory.find_similar(goal, limit=1)
        
        # 如果有匹配的历史记录
        if similar:
            record = similar[0]
            explanation = f"基于历史记录 {record.execution_id}（{record.goal}）：\n"
            explanation += f"1. 上次使用了 {len(record.capabilities_used)} 个能力\n"
            explanation += f"2. 成功步骤: {record.successful_steps}\n"
            
            if record.final_result == "success":
                explanation += f"3. 上次执行成功，将复用相同路径\n"
            else:
                explanation += f"3. 上次执行失败，将调整策略\n"
            
            if record.optimization_hints:
                explanation += f"4. 优化建议: {record.optimization_hints}\n"
            
            warning = self._generate_warning(goal_pattern)
            if warning:
                explanation += f"\n{warning}"
            
            return explanation
        
        if best_path:
            explanation = f"基于历史经验（成功 {best_path.success_count} 次），我将：\n"
            explanation += f"1. 复用成功路径：{best_path.path_id}\n"
            explanation += f"2. 使用能力：{', '.join(best_path.capabilities)}\n"
            
            if best_path.skills:
                explanation += f"3. 使用技能：{', '.join(best_path.skills)}\n"
            
            warning = self._generate_warning(goal_pattern)
            if warning:
                explanation += f"\n{warning}"
            
            return explanation
        
        return f"这是首次执行「{goal}」类型任务，将采用默认计划。"
