#!/usr/bin/env python3
"""
推理引擎 - V1.0.0

提供多种推理模式，增强思考能力。
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class ReasoningType(Enum):
    """推理类型"""
    DEDUCTIVE = "deductive"      # 演绎推理
    INDUCTIVE = "inductive"      # 归纳推理
    ABDUCTIVE = "abductive"      # 溯因推理
    ANALOGICAL = "analogical"    # 类比推理
    CAUSAL = "causal"            # 因果推理
    COUNTERFACTUAL = "counterfactual"  # 反事实推理


@dataclass
class Premise:
    """前提"""
    content: str
    confidence: float = 1.0
    source: str = "unknown"


@dataclass
class Conclusion:
    """结论"""
    content: str
    confidence: float
    reasoning_type: ReasoningType
    premises: List[Premise]
    steps: List[str]


class ReasoningEngine:
    """推理引擎"""
    
    def __init__(self):
        self.reasoning_strategies = {
            ReasoningType.DEDUCTIVE: self._deductive_reasoning,
            ReasoningType.INDUCTIVE: self._inductive_reasoning,
            ReasoningType.ABDUCTIVE: self._abductive_reasoning,
            ReasoningType.ANALOGICAL: self._analogical_reasoning,
            ReasoningType.CAUSAL: self._causal_reasoning,
            ReasoningType.COUNTERFACTUAL: self._counterfactual_reasoning,
        }
    
    def reason(self, 
               premises: List[Premise],
               question: str,
               reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE) -> Conclusion:
        """执行推理"""
        strategy = self.reasoning_strategies.get(reasoning_type)
        if not strategy:
            raise ValueError(f"未知的推理类型: {reasoning_type}")
        
        return strategy(premises, question)
    
    def _deductive_reasoning(self, premises: List[Premise], question: str) -> Conclusion:
        """
        演绎推理：从一般到特殊
        
        形式：如果 P 则 Q，P 为真，因此 Q 为真
        """
        steps = []
        confidence = 1.0
        
        # 提取规则和事实
        rules = []
        facts = []
        
        for p in premises:
            if "如果" in p.content or "若" in p.content or "when" in p.content.lower():
                rules.append(p)
            else:
                facts.append(p)
        
        steps.append(f"识别到 {len(rules)} 条规则和 {len(facts)} 个事实")
        
        # 应用规则
        conclusions = []
        for rule in rules:
            for fact in facts:
                if self._rule_applies(rule.content, fact.content):
                    conclusion = self._apply_rule(rule.content, fact.content)
                    if conclusion:
                        conclusions.append(conclusion)
                        steps.append(f"应用规则: {rule.content} -> {conclusion}")
                        confidence = min(confidence, rule.confidence * fact.confidence)
        
        final_conclusion = conclusions[-1] if conclusions else "无法得出结论"
        
        return Conclusion(
            content=final_conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.DEDUCTIVE,
            premises=premises,
            steps=steps
        )
    
    def _inductive_reasoning(self, premises: List[Premise], question: str) -> Conclusion:
        """
        归纳推理：从特殊到一般
        
        形式：观察到多个实例，推断出一般规律
        """
        steps = []
        
        # 收集观察
        observations = [p.content for p in premises]
        steps.append(f"收集到 {len(observations)} 个观察")
        
        # 寻找模式
        patterns = self._find_patterns(observations)
        steps.append(f"识别到 {len(patterns)} 个模式")
        
        # 归纳规律
        if patterns:
            general_rule = self._generalize_pattern(patterns)
            confidence = len(observations) / (len(observations) + 1)  # 简单置信度
            steps.append(f"归纳出规律: {general_rule}")
        else:
            general_rule = "未发现明显规律"
            confidence = 0.0
        
        return Conclusion(
            content=general_rule,
            confidence=confidence,
            reasoning_type=ReasoningType.INDUCTIVE,
            premises=premises,
            steps=steps
        )
    
    def _abductive_reasoning(self, premises: List[Premise], question: str) -> Conclusion:
        """
        溯因推理：从结果推断原因
        
        形式：观察到现象 B，寻找最佳解释 A
        """
        steps = []
        
        # 识别现象
        phenomenon = question
        steps.append(f"观察到的现象: {phenomenon}")
        
        # 生成可能原因
        possible_causes = self._generate_hypotheses(phenomenon, premises)
        steps.append(f"生成 {len(possible_causes)} 个可能原因")
        
        # 评估最佳解释
        best_cause = None
        best_score = 0
        
        for cause, score in possible_causes:
            steps.append(f"  - {cause} (得分: {score:.2f})")
            if score > best_score:
                best_score = score
                best_cause = cause
        
        steps.append(f"最佳解释: {best_cause}")
        
        return Conclusion(
            content=best_cause or "无法确定原因",
            confidence=best_score,
            reasoning_type=ReasoningType.ABDUCTIVE,
            premises=premises,
            steps=steps
        )
    
    def _analogical_reasoning(self, premises: List[Premise], question: str) -> Conclusion:
        """
        类比推理：基于相似性推断
        
        形式：A 和 B 相似，A 有属性 X，因此 B 也可能有属性 X
        """
        steps = []
        
        # 找到源域和目标域
        source = None
        target = question
        
        for p in premises:
            if "类似于" in p.content or "像" in p.content or "similar to" in p.content.lower():
                parts = re.split(r'类似于|像|similar to', p.content)
                if len(parts) >= 2:
                    source = parts[0].strip()
                    target = parts[1].strip()
                    steps.append(f"识别类比: {source} -> {target}")
                    break
        
        if not source:
            # 尝试从前提中找相似性
            similarities = self._find_similarities([p.content for p in premises])
            if similarities:
                source, target = similarities[0]
                steps.append(f"发现相似性: {source} 和 {target}")
        
        # 迁移属性
        if source:
            source_props = self._extract_properties(source, premises)
            transferred = self._transfer_properties(source_props, target)
            steps.append(f"迁移属性: {transferred}")
            
            conclusion = f"基于与 {source} 的相似性，{target} 可能具有: {', '.join(transferred)}"
            confidence = 0.7  # 类比推理的置信度通常较低
        else:
            conclusion = "无法建立类比关系"
            confidence = 0.0
        
        return Conclusion(
            content=conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.ANALOGICAL,
            premises=premises,
            steps=steps
        )
    
    def _causal_reasoning(self, premises: List[Premise], question: str) -> Conclusion:
        """
        因果推理：分析因果关系
        
        形式：A 导致 B，因此 A 是 B 的原因
        """
        steps = []
        
        # 识别因果链
        causal_chains = self._build_causal_chains(premises)
        steps.append(f"构建了 {len(causal_chains)} 条因果链")
        
        # 分析问题中的因果关系
        cause_effect = self._analyze_causality(question, causal_chains)
        steps.append(f"分析结果: {cause_effect}")
        
        return Conclusion(
            content=cause_effect,
            confidence=0.8,
            reasoning_type=ReasoningType.CAUSAL,
            premises=premises,
            steps=steps
        )
    
    def _counterfactual_reasoning(self, premises: List[Premise], question: str) -> Conclusion:
        """
        反事实推理：假设性思考
        
        形式：如果 A 没有发生，那么 B 会怎样？
        """
        steps = []
        
        # 识别事实和反事实假设
        actual_fact = None
        counterfactual = None
        
        for p in premises:
            if "如果" in p.content or "假如" in p.content:
                counterfactual = p.content
            else:
                actual_fact = p.content
        
        steps.append(f"实际事实: {actual_fact}")
        steps.append(f"反事实假设: {counterfactual}")
        
        # 推导反事实结果
        if counterfactual:
            result = self._simulate_counterfactual(actual_fact, counterfactual)
            steps.append(f"反事实结果: {result}")
            conclusion = f"如果 {counterfactual}，那么 {result}"
            confidence = 0.6  # 反事实推理不确定性较高
        else:
            conclusion = "无法进行反事实推理"
            confidence = 0.0
        
        return Conclusion(
            content=conclusion,
            confidence=confidence,
            reasoning_type=ReasoningType.COUNTERFACTUAL,
            premises=premises,
            steps=steps
        )
    
    # 辅助方法
    def _rule_applies(self, rule: str, fact: str) -> bool:
        """检查规则是否适用于事实"""
        # 简化实现
        return True
    
    def _apply_rule(self, rule: str, fact: str) -> Optional[str]:
        """应用规则得出结论"""
        # 提取规则的结论部分
        if "则" in rule:
            return rule.split("则")[-1].strip()
        elif "那么" in rule:
            return rule.split("那么")[-1].strip()
        return None
    
    def _find_patterns(self, observations: List[str]) -> List[str]:
        """寻找观察中的模式"""
        patterns = []
        # 简化实现：寻找共同关键词
        words = [set(obs.split()) for obs in observations]
        if words:
            common = set.intersection(*words) if len(words) > 1 else words[0]
            if common:
                patterns.append(f"共同特征: {', '.join(common)}")
        return patterns
    
    def _generalize_pattern(self, patterns: List[str]) -> str:
        """从模式归纳规律"""
        return f"归纳规律: {patterns[0]}"
    
    def _generate_hypotheses(self, phenomenon: str, premises: List[Premise]) -> List[Tuple[str, float]]:
        """生成可能的假设"""
        hypotheses = []
        for p in premises:
            score = 0.5 + 0.5 * p.confidence
            hypotheses.append((p.content, score))
        return hypotheses
    
    def _find_similarities(self, items: List[str]) -> List[Tuple[str, str]]:
        """寻找相似项"""
        similarities = []
        for i, item1 in enumerate(items):
            for item2 in items[i+1:]:
                # 简化：基于共同词判断相似
                words1 = set(item1.split())
                words2 = set(item2.split())
                if words1 & words2:
                    similarities.append((item1, item2))
        return similarities
    
    def _extract_properties(self, source: str, premises: List[Premise]) -> List[str]:
        """提取源域属性"""
        props = []
        for p in premises:
            if source in p.content:
                props.append(p.content)
        return props
    
    def _transfer_properties(self, properties: List[str], target: str) -> List[str]:
        """迁移属性到目标域"""
        return [f"{target} 的类似属性" for _ in properties]
    
    def _build_causal_chains(self, premises: List[Premise]) -> List[List[str]]:
        """构建因果链"""
        chains = []
        for p in premises:
            if "导致" in p.content or "引起" in p.content:
                parts = re.split(r'导致|引起', p.content)
                if len(parts) >= 2:
                    chains.append([parts[0].strip(), parts[1].strip()])
        return chains
    
    def _analyze_causality(self, question: str, chains: List[List[str]]) -> str:
        """分析因果关系"""
        for chain in chains:
            if any(part in question for part in chain):
                return f"因果链: {' -> '.join(chain)}"
        return "未找到直接因果关系"
    
    def _simulate_counterfactual(self, actual: str, counterfactual: str) -> str:
        """模拟反事实结果"""
        return f"结果可能不同"


# 全局推理引擎
_reasoning_engine: Optional[ReasoningEngine] = None


def get_reasoning_engine() -> ReasoningEngine:
    """获取全局推理引擎"""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine
