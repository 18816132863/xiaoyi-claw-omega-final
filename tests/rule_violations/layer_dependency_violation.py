#!/usr/bin/env python3
"""
依赖违规样例 - 用于测试 check_layer_dependencies.py

此文件故意违反层间依赖规则：
- core 层禁止 import execution 层

这个样例用于验证 check_layer_dependencies.py 能正确检测到违规
"""

# 故意违规：core 层 import execution 层
from execution.skill_gateway import SkillGateway

def test_function():
    """这是一个故意违规的函数"""
    return "This file intentionally violates layer dependency rules"
