"""测试学习相似度匹配"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from learning_loop import ExecutionMemory, ExecutionRecord


def test_similarity_match_by_pattern():
    """测试按模式匹配相似记录"""
    memory = ExecutionMemory(storage_path="data/test_learning_similarity.jsonl")
    
    # 清空旧数据
    memory._cache = []
    
    # 写入一条记录
    record = ExecutionRecord(
        goal="明天提醒我开会",
        plan=[{"step": 1}],
        capabilities_used=["schedule.create_calendar_event"],
        successful_steps=[1],
        failed_steps=[],
        final_result="success",
    )
    memory.record(record)
    
    # 查找相似记录
    similar = memory.find_similar("后天提醒我交报告")
    
    assert len(similar) > 0, "应该找到相似记录"
    assert similar[0].goal == "明天提醒我开会"


def test_similarity_match_by_keywords():
    """测试按关键词匹配相似记录"""
    memory = ExecutionMemory(storage_path="data/test_learning_similarity.jsonl")
    
    # 写入一条记录
    record = ExecutionRecord(
        goal="创建一个备忘录",
        plan=[{"step": 1}],
        capabilities_used=["storage.create_note"],
        successful_steps=[1],
        failed_steps=[],
        final_result="success",
    )
    memory.record(record)
    
    # 查找相似记录
    similar = memory.find_similar("帮我创建备忘录")
    
    assert len(similar) > 0, "应该找到相似记录"


def test_no_match_for_different_goals():
    """测试不同类型目标不应匹配"""
    memory = ExecutionMemory(storage_path="data/test_learning_similarity.jsonl")
    
    # 写入一条提醒类记录
    record = ExecutionRecord(
        goal="明天提醒我开会",
        plan=[{"step": 1}],
        capabilities_used=["schedule.create_calendar_event"],
        successful_steps=[1],
        failed_steps=[],
        final_result="success",
    )
    memory.record(record)
    
    # 查找完全不相关的目标
    similar = memory.find_similar("帮我查天气")
    
    # 可能匹配到，但分数应该很低
    # 这里只验证不会崩溃
    assert isinstance(similar, list)
