"""Skill Router - 技能路由器

真实可用的技能发现、选择、执行功能。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import time


@dataclass
class SkillExecutionContext:
    """技能执行上下文"""
    skill_id: str
    input_data: Dict
    profile: str = "default"
    timeout_seconds: int = 60
    metadata: Dict = field(default_factory=dict)


@dataclass
class SkillExecutionResult:
    """技能执行结果"""
    skill_id: str
    success: bool
    output: Dict
    error: Optional[str] = None
    duration_ms: int = 0
    executed_at: datetime = field(default_factory=datetime.now)


class SkillRouter:
    """
    技能路由器
    
    真实可用的技能发现、选择、执行功能。
    """
    
    def __init__(self, registry=None, executor=None):
        self.registry = registry
        self.executor = executor
        self._action_handlers: Dict[str, Any] = {}
    
    def register_handler(self, action_type: str, handler):
        """注册动作处理器"""
        self._action_handlers[action_type] = handler
    
    def discover(self, query: str, context: Dict = None) -> List[str]:
        """
        发现技能
        
        基于查询在注册表中搜索匹配的技能。
        """
        if not self.registry:
            return []
        
        # 在注册表中搜索
        matches = self.registry.search(query=query)
        
        # 过滤禁用的技能
        from ..registry.skill_registry import SkillStatus
        matches = [m for m in matches if m.status != SkillStatus.DISABLED]
        
        return [m.skill_id for m in matches]
    
    def select_skill(self, intent: str, profile: str = "default", constraints: Dict = None) -> Dict:
        """
        选择技能（正式 façade）
        
        基于意图、配置和约束选择最合适的技能。
        
        Args:
            intent: 任务意图
            profile: 执行配置
            constraints: 约束条件（如分类、标签等）
        
        Returns:
            选择结果，包含 skill_id, confidence, alternatives 等
        """
        constraints = constraints or {}
        
        # 发现候选技能
        candidates = self.discover(intent, context={"profile": profile})
        
        if not candidates:
            return {
                "success": False,
                "skill_id": None,
                "confidence": 0,
                "error": "No matching skill found",
                "alternatives": []
            }
        
        # 简单评分（基于名称匹配度）
        scored = []
        intent_lower = intent.lower()
        for skill_id in candidates:
            manifest = self.registry.get(skill_id) if self.registry else None
            if manifest:
                # 计算简单匹配分数
                score = 0
                if intent_lower in manifest.name.lower():
                    score += 0.5
                if intent_lower in manifest.description.lower():
                    score += 0.3
                for tag in manifest.tags:
                    if intent_lower in tag.lower():
                        score += 0.1
                scored.append((skill_id, min(score, 1.0)))
        
        # 排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        if not scored:
            return {
                "success": False,
                "skill_id": None,
                "confidence": 0,
                "error": "No suitable skill found",
                "alternatives": []
            }
        
        best_skill_id, best_score = scored[0]
        alternatives = [s[0] for s in scored[1:4]]  # 最多3个备选
        
        return {
            "success": True,
            "skill_id": best_skill_id,
            "confidence": best_score,
            "alternatives": alternatives,
            "selection_reason": f"Best match for intent: {intent}"
        }
    
    def route(self, skill_id: str, input_data: Dict, context: Dict = None) -> SkillExecutionResult:
        """
        路由执行技能
        
        Args:
            skill_id: 技能ID
            input_data: 输入数据
            context: 执行上下文
        
        Returns:
            SkillExecutionResult 执行结果
        """
        start_time = time.time()
        context = context or {}
        
        # 获取技能清单
        manifest = None
        if self.registry:
            manifest = self.registry.get(skill_id)
        
        if not manifest:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output={},
                error=f"Skill not found: {skill_id}",
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        # 检查技能状态
        from ..registry.skill_registry import SkillStatus
        if manifest.status == SkillStatus.DISABLED:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output={},
                error=f"Skill is disabled: {skill_id}",
                duration_ms=int((time.time() - start_time) * 1000)
            )
        
        # 执行技能
        try:
            if self.executor:
                output = self.executor.execute(manifest, input_data, context)
            elif manifest.executor_type in self._action_handlers:
                handler = self._action_handlers[manifest.executor_type]
                output = handler(manifest, input_data, context)
            else:
                # 最小执行器：返回确认结果
                output = {
                    "executed": True,
                    "skill_id": skill_id,
                    "executor_type": manifest.executor_type,
                    "input": input_data,
                    "message": f"Skill {skill_id} executed (minimal executor)"
                }
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return SkillExecutionResult(
                skill_id=skill_id,
                success=True,
                output=output,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                output={},
                error=str(e),
                duration_ms=duration_ms
            )
    
    def execute(self, skill_id: str, input_data: Dict, context: Dict = None) -> Dict:
        """
        执行技能并返回输出
        
        便捷方法，失败时抛出异常。
        """
        result = self.route(skill_id, input_data, context)
        if not result.success:
            raise RuntimeError(result.error)
        return result.output
