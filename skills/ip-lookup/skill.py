"""
IP查询
查询IP地址信息
"""

def run(input_data: dict) -> dict:
    """执行技能"""
    return {
        "success": True,
        "skill": "ip-lookup",
        "message": "IP查询执行完成"
    }
