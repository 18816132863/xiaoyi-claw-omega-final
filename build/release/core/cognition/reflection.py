#!/usr/bin/env python3
"""
反思系统 - V1.0.0

提供自我评估、错误分析和改进建议能力。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ReflectionType(Enum):
    """反思类型"""
    ACTION = "action"          # 行动反思
    OUTCOME = "outcome"        # 结果反思
    PROCESS = "process"        # 过程反思
    STRATEGY = "strategy"      # 策略反思
    LEARNING = "learning"      # 学习反思


class FeedbackType(Enum):
    """反馈类型"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CONSTRUCTIVE = "constructive"


@dataclass
class Reflection:
    """反思记录"""
    id: str
    type: ReflectionType
    context: str
    observation: str
    analysis: str
    insights: List[str]
    improvements: List[str]
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Feedback:
    """反馈"""
    type: FeedbackType
    content: str
    source: str
    relevance: float


class ReflectionSystem:
    """反思系统"""
    
    def __init__(self):
        self.reflections: List[Reflection] = []
        self.feedback_history: List[Feedback] = []
        self.reflection_counter = 0
    
    def reflect(self,
                context: str,
                action: str,
                outcome: str,
                reflection_type: ReflectionType = ReflectionType.OUTCOME) -> Reflection:
        """
        执行反思
        
        Args:
            context: 上下文
            action: 执行的动作
            outcome: 结果
            reflection_type: 反思类型
        
        Returns:
            反思记录
        """
        # 观察分析
        observation = self._observe(context, action, outcome)
        
        # 分析原因
        analysis = self._analyze(context, action, outcome, observation)
        
        # 提取洞察
        insights = self._extract_insights(context, action, outcome, analysis)
        
        # 生成改进建议
        improvements = self._generate_improvements(insights)
        
        # 计算置信度
        confidence = self._calculate_confidence(observation, analysis)
        
        reflection = Reflection(
            id=f"reflection_{self.reflection_counter}",
            type=reflection_type,
            context=context,
            observation=observation,
            analysis=analysis,
            insights=insights,
            improvements=improvements,
            confidence=confidence
        )
        
        self.reflections.append(reflection)
        self.reflection_counter += 1
        
        return reflection
    
    def _observe(self, context: str, action: str, outcome: str) -> str:
        """观察并描述情况"""
        observations = []
        
        # 检查结果是否符合预期
        if "成功" in outcome or "完成" in outcome:
            observations.append("结果: 成功")
        elif "失败" in outcome or "错误" in outcome:
            observations.append("结果: 失败")
        else:
            observations.append("结果: 部分成功")
        
        # 检查动作执行情况
        if action:
            observations.append(f"执行动作: {action[:100]}")
        
        # 检查上下文因素
        if context:
            observations.append(f"上下文: {context[:100]}")
        
        return "; ".join(observations)
    
    def _analyze(self, context: str, action: str, outcome: str, observation: str) -> str:
        """分析原因"""
        analyses = []
        
        # 成功因素分析
        if "成功" in outcome:
            analyses.append("成功因素:")
            if action:
                analyses.append(f"  - 动作执行正确: {action[:50]}")
            if context:
                analyses.append(f"  - 上下文有利: {context[:50]}")
        
        # 失败因素分析
        elif "失败" in outcome:
            analyses.append("失败原因:")
            analyses.append("  - 可能原因: 执行过程中的问题")
            analyses.append("  - 可能原因: 上下文不匹配")
            analyses.append("  - 可能原因: 资源不足")
        
        # 部分成功分析
        else:
            analyses.append("部分成功分析:")
            analyses.append("  - 成功部分: 基本目标达成")
            analyses.append("  - 待改进: 效率或质量可提升")
        
        return "\n".join(analyses)
    
    def _extract_insights(self, context: str, action: str, outcome: str, analysis: str) -> List[str]:
        """提取洞察"""
        insights = []
        
        # 从分析中提取关键洞察
        if "成功" in outcome:
            insights.append("成功模式可复制")
            insights.append("当前策略有效")
        elif "失败" in outcome:
            insights.append("需要调整策略")
            insights.append("检查前置条件")
            insights.append("考虑备选方案")
        else:
            insights.append("优化空间存在")
            insights.append("细节可改进")
        
        # 基于历史反思提取模式
        if len(self.reflections) > 0:
            recent = self.reflections[-5:]
            success_rate = sum(1 for r in recent if "成功" in r.observation) / len(recent)
            if success_rate > 0.7:
                insights.append("近期表现良好，保持当前策略")
            elif success_rate < 0.3:
                insights.append("近期表现不佳，需要根本性调整")
        
        return insights
    
    def _generate_improvements(self, insights: List[str]) -> List[str]:
        """生成改进建议"""
        improvements = []
        
        for insight in insights:
            if "调整策略" in insight:
                improvements.append("建议: 重新评估当前方法")
                improvements.append("建议: 寻求替代方案")
            elif "检查前置" in insight:
                improvements.append("建议: 增加预检查步骤")
                improvements.append("建议: 验证输入条件")
            elif "备选方案" in insight:
                improvements.append("建议: 准备 Plan B")
                improvements.append("建议: 增加容错机制")
            elif "优化空间" in insight:
                improvements.append("建议: 分析瓶颈环节")
                improvements.append("建议: 优化关键路径")
            elif "细节可改进" in insight:
                improvements.append("建议: 关注细节质量")
                improvements.append("建议: 增加验证步骤")
        
        return improvements[:5]  # 限制建议数量
    
    def _calculate_confidence(self, observation: str, analysis: str) -> float:
        """计算置信度"""
        # 基于分析深度计算置信度
        base_confidence = 0.5
        
        # 根据观察质量调整
        if len(observation) > 50:
            base_confidence += 0.1
        
        # 根据分析深度调整
        if len(analysis) > 100:
            base_confidence += 0.1
        
        # 根据历史反思数量调整
        if len(self.reflections) > 10:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def add_feedback(self, feedback: Feedback):
        """添加外部反馈"""
        self.feedback_history.append(feedback)
    
    def get_patterns(self) -> Dict[str, Any]:
        """识别反思模式"""
        if not self.reflections:
            return {}
        
        # 统计成功/失败比例
        success_count = sum(1 for r in self.reflections if "成功" in r.observation)
        failure_count = sum(1 for r in self.reflections if "失败" in r.observation)
        
        # 常见洞察
        all_insights = []
        for r in self.reflections:
            all_insights.extend(r.insights)
        
        insight_counts = {}
        for insight in all_insights:
            insight_counts[insight] = insight_counts.get(insight, 0) + 1
        
        # 常见改进建议
        all_improvements = []
        for r in self.reflections:
            all_improvements.extend(r.improvements)
        
        improvement_counts = {}
        for imp in all_improvements:
            improvement_counts[imp] = improvement_counts.get(imp, 0) + 1
        
        return {
            "total_reflections": len(self.reflections),
            "success_rate": success_count / len(self.reflections),
            "failure_rate": failure_count / len(self.reflections),
            "common_insights": sorted(insight_counts.items(), key=lambda x: -x[1])[:5],
            "common_improvements": sorted(improvement_counts.items(), key=lambda x: -x[1])[:5]
        }
    
    def learn_from_reflections(self) -> List[str]:
        """从反思中学习"""
        patterns = self.get_patterns()
        learnings = []
        
        if patterns.get("success_rate", 0) > 0.7:
            learnings.append("学习: 当前策略整体有效，继续优化")
        elif patterns.get("failure_rate", 0) > 0.5:
            learnings.append("学习: 需要系统性改进策略")
        
        # 从常见洞察中学习
        for insight, count in patterns.get("common_insights", []):
            if count > 2:
                learnings.append(f"学习: {insight} (出现 {count} 次)")
        
        return learnings


# 全局反思系统
_reflection_system: Optional[ReflectionSystem] = None


def get_reflection_system() -> ReflectionSystem:
    """获取全局反思系统"""
    global _reflection_system
    if _reflection_system is None:
        _reflection_system = ReflectionSystem()
    return _reflection_system
