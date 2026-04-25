"""层间依赖违规样例 - 用于测试守卫"""

# 这是故意违规的样例，用于测试层间依赖检查器
# execution 层不应该直接 import core 层

from core.some_module import something  # 违规：跨层依赖

def bad_function():
    pass
