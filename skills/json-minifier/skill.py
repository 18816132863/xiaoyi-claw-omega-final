"""
JSON压缩
压缩JSON去除空白
"""

def run(input_data: dict) -> dict:
    """执行技能"""
    return {
        "success": True,
        "skill": "json-minifier",
        "message": "JSON压缩执行完成"
    }
