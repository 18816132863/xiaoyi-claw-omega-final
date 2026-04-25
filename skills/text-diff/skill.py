"""
文本对比
对比两段文本的差异
"""

def run(input_data: dict) -> dict:
    """执行技能"""
    return {
        "success": True,
        "skill": "text-diff",
        "message": "文本对比执行完成"
    }
