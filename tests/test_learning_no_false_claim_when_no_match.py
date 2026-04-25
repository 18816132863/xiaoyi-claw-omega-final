"""测试学习不虚假声明"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from learning_loop import ExecutionMemory, PlanOptimizer


def test_no_false_claim_when_no_match():
    """测试无匹配时不虚假声明"""
    # 使用空的记忆
    memory = ExecutionMemory(storage_path="data/test_learning_no_match.jsonl")
    memory._cache = []
    
    # 查找相似记录
    similar = memory.find_similar("完全陌生的目标 xyz123")
    
    # 应该返回空列表
    assert len(similar) == 0, "无匹配时应返回空列表"


def test_explain_does_not_claim_history_when_none():
    """测试无历史时不声称基于历史"""
    memory = ExecutionMemory(storage_path="data/test_learning_no_match.jsonl")
    memory._cache = []
    
    optimizer = PlanOptimizer(memory=memory)
    explanation = optimizer.explain("完全陌生的目标")
    
    # 应该说明是首次执行
    assert "首次" in explanation or "默认" in explanation


def test_no_preferred_capabilities_when_no_history():
    """测试无历史时不返回偏好能力"""
    memory = ExecutionMemory(storage_path="data/test_learning_no_match.jsonl")
    memory._cache = []
    
    hints = memory.get_preference_hints("陌生目标")
    
    # 应该返回空或默认值
    assert hints.get("preferred_capabilities", []) == []


def test_confidence_low_when_no_history():
    """测试无历史时置信度低"""
    memory = ExecutionMemory(storage_path="data/test_learning_no_match.jsonl")
    memory._cache = []
    
    optimizer = PlanOptimizer(memory=memory)
    result = optimizer.optimize("陌生目标", [{"step": 1}])
    
    # 置信度应该是默认值
    assert result["confidence"] <= 0.6
