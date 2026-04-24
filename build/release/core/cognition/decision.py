#!/usr/bin/env python3
"""
决策系统 - V1.0.0

提供多准则决策和决策支持能力。
"""

from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import math


class DecisionCriteria(Enum):
    """决策准则"""
    MAXIMIZE = "maximize"  # 最大化
    MINIMIZE = "minimize"  # 最小化
    SATISFICE = "satisfice"  # 满意即可


@dataclass
class Option:
    """决策选项"""
    id: str
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class Criterion:
    """决策准则"""
    name: str
    weight: float
    criteria_type: DecisionCriteria
    threshold: Optional[float] = None  # 满意阈值


@dataclass
class DecisionResult:
    """决策结果"""
    selected: Option
    all_options: List[Option]
    scores: Dict[str, float]
    reasoning: List[str]
    confidence: float


class DecisionMaker:
    """决策器"""
    
    def __init__(self):
        self.decision_history: List[DecisionResult] = []
    
    def decide(self,
               options: List[Option],
               criteria: List[Criterion],
               method: str = "weighted_sum") -> DecisionResult:
        """
        执行决策
        
        Args:
            options: 可选方案
            criteria: 决策准则
            method: 决策方法 (weighted_sum, ahp, topsis)
        
        Returns:
            决策结果
        """
        if method == "weighted_sum":
            return self._weighted_sum_decision(options, criteria)
        elif method == "ahp":
            return self._ahp_decision(options, criteria)
        elif method == "topsis":
            return self._topsis_decision(options, criteria)
        else:
            raise ValueError(f"未知的决策方法: {method}")
    
    def _weighted_sum_decision(self, 
                                options: List[Option], 
                                criteria: List[Criterion]) -> DecisionResult:
        """加权求和决策"""
        reasoning = []
        reasoning.append(f"使用加权求和法，共 {len(options)} 个选项，{len(criteria)} 个准则")
        
        # 计算每个选项的加权得分
        for option in options:
            total_score = 0
            for criterion in criteria:
                attr_value = option.attributes.get(criterion.name, 0)
                
                # 根据准则类型调整得分
                if criterion.criteria_type == DecisionCriteria.MAXIMIZE:
                    score = attr_value
                elif criterion.criteria_type == DecisionCriteria.MINIMIZE:
                    score = -attr_value if attr_value > 0 else 0
                else:  # SATISFICE
                    if criterion.threshold and attr_value >= criterion.threshold:
                        score = 1
                    else:
                        score = 0
                
                weighted_score = score * criterion.weight
                total_score += weighted_score
                option.scores[criterion.name] = weighted_score
            
            option.scores["total"] = total_score
            reasoning.append(f"  {option.name}: 总分 {total_score:.2f}")
        
        # 选择最高分
        best = max(options, key=lambda o: o.scores["total"])
        reasoning.append(f"选择: {best.name}")
        
        result = DecisionResult(
            selected=best,
            all_options=options,
            scores={o.name: o.scores["total"] for o in options},
            reasoning=reasoning,
            confidence=best.scores["total"] / sum(c.weight for c in criteria) if criteria else 0
        )
        
        self.decision_history.append(result)
        return result
    
    def _ahp_decision(self, 
                      options: List[Option], 
                      criteria: List[Criterion]) -> DecisionResult:
        """层次分析法决策"""
        reasoning = []
        reasoning.append("使用层次分析法 (AHP)")
        
        # 构建判断矩阵
        n = len(criteria)
        judgment_matrix = [[1.0] * n for _ in range(n)]
        
        # 简化：使用权重比作为判断值
        for i in range(n):
            for j in range(n):
                if i != j:
                    judgment_matrix[i][j] = criteria[i].weight / criteria[j].weight
        
        # 计算特征向量（简化）
        weights = [c.weight for c in criteria]
        weight_sum = sum(weights)
        normalized_weights = [w / weight_sum for w in weights]
        
        reasoning.append(f"准则权重: {[f'{c.name}:{w:.2f}' for c, w in zip(criteria, normalized_weights)]}")
        
        # 计算选项得分
        for option in options:
            score = sum(
                option.attributes.get(c.name, 0) * w
                for c, w in zip(criteria, normalized_weights)
            )
            option.scores["ahp"] = score
            reasoning.append(f"  {option.name}: {score:.2f}")
        
        best = max(options, key=lambda o: o.scores["ahp"])
        reasoning.append(f"选择: {best.name}")
        
        return DecisionResult(
            selected=best,
            all_options=options,
            scores={o.name: o.scores["ahp"] for o in options},
            reasoning=reasoning,
            confidence=0.8
        )
    
    def _topsis_decision(self,
                         options: List[Option],
                         criteria: List[Criterion]) -> DecisionResult:
        """TOPSIS 决策法"""
        reasoning = []
        reasoning.append("使用 TOPSIS 法")
        
        # 构建决策矩阵
        n_options = len(options)
        n_criteria = len(criteria)
        
        matrix = [[0.0] * n_criteria for _ in range(n_options)]
        for i, option in enumerate(options):
            for j, criterion in enumerate(criteria):
                matrix[i][j] = option.attributes.get(criterion.name, 0)
        
        # 标准化
        for j in range(n_criteria):
            col_sum = sum(matrix[i][j] ** 2 for i in range(n_options))
            sqrt_sum = math.sqrt(col_sum) if col_sum > 0 else 1
            for i in range(n_options):
                matrix[i][j] = matrix[i][j] / sqrt_sum
        
        # 加权
        weights = [c.weight for c in criteria]
        for j in range(n_criteria):
            for i in range(n_options):
                matrix[i][j] *= weights[j]
        
        # 理想解和负理想解
        ideal = []
        negative_ideal = []
        for j, criterion in enumerate(criteria):
            col = [matrix[i][j] for i in range(n_options)]
            if criterion.criteria_type == DecisionCriteria.MAXIMIZE:
                ideal.append(max(col))
                negative_ideal.append(min(col))
            else:
                ideal.append(min(col))
                negative_ideal.append(max(col))
        
        # 计算距离
        for i, option in enumerate(options):
            d_ideal = math.sqrt(sum((matrix[i][j] - ideal[j]) ** 2 for j in range(n_criteria)))
            d_negative = math.sqrt(sum((matrix[i][j] - negative_ideal[j]) ** 2 for j in range(n_criteria)))
            
            # 相对贴近度
            closeness = d_negative / (d_ideal + d_negative) if (d_ideal + d_negative) > 0 else 0
            option.scores["topsis"] = closeness
            reasoning.append(f"  {option.name}: 贴近度 {closeness:.3f}")
        
        best = max(options, key=lambda o: o.scores["topsis"])
        reasoning.append(f"选择: {best.name}")
        
        return DecisionResult(
            selected=best,
            all_options=options,
            scores={o.name: o.scores["topsis"] for o in options},
            reasoning=reasoning,
            confidence=best.scores["topsis"]
        )
    
    def multi_stage_decision(self,
                             stages: List[Dict],
                             options: List[Option]) -> DecisionResult:
        """多阶段决策"""
        reasoning = []
        current_options = options
        
        for i, stage in enumerate(stages):
            reasoning.append(f"阶段 {i+1}: {stage.get('name', '未命名')}")
            criteria = [Criterion(**c) for c in stage.get("criteria", [])]
            result = self.decide(current_options, criteria, stage.get("method", "weighted_sum"))
            reasoning.extend(result.reasoning)
            
            # 过滤选项
            threshold = stage.get("threshold", 0)
            current_options = [o for o in current_options if o.scores.get("total", 0) >= threshold]
            
            if not current_options:
                reasoning.append("警告: 所有选项被过滤")
                break
        
        if current_options:
            best = max(current_options, key=lambda o: o.scores.get("total", 0))
        else:
            best = options[0]  # 回退到第一个选项
        
        return DecisionResult(
            selected=best,
            all_options=options,
            scores={o.name: o.scores.get("total", 0) for o in options},
            reasoning=reasoning,
            confidence=0.7
        )


# 全局决策器
_decision_maker: Optional[DecisionMaker] = None


def get_decision_maker() -> DecisionMaker:
    """获取全局决策器"""
    global _decision_maker
    if _decision_maker is None:
        _decision_maker = DecisionMaker()
    return _decision_maker
