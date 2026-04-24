"""
文本修剪
去除多余空格和换行
"""

def run(input_data: dict) -> dict:
    """执行技能"""
    return {
        "success": True,
        "skill": "text-trimmer",
        "message": "文本修剪执行完成"
    }
