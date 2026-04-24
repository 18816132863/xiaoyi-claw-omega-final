"""
Error Explainer - 错误解释器
"""

from typing import Dict, Any, Optional, List
from skill_entry.error_codes import ErrorCodes, ErrorCode, ErrorCategory


class ErrorExplainer:
    """错误解释器"""
    
    ERROR_EXPLANATIONS = {
        "E1001": {
            "title": "输入参数无效",
            "explanation": "提供的参数不符合预期格式或类型",
            "common_causes": [
                "参数类型错误（如期望字符串但提供了数字）",
                "缺少必要参数",
                "参数格式不正确"
            ],
            "solutions": [
                "检查参数类型是否正确",
                "确保所有必填参数都已提供",
                "参考API文档确认参数格式"
            ]
        },
        "E2001": {
            "title": "任务未找到",
            "explanation": "指定的任务ID不存在于系统中",
            "common_causes": [
                "任务ID拼写错误",
                "任务已被删除",
                "使用了错误的数据库"
            ],
            "solutions": [
                "确认任务ID是否正确",
                "检查任务是否已被删除",
                "确认当前使用的数据库"
            ]
        },
        "E2004": {
            "title": "任务状态无效",
            "explanation": "当前任务状态不允许执行此操作",
            "common_causes": [
                "尝试恢复未暂停的任务",
                "尝试取消已完成的任务",
                "尝试重试未失败的任务"
            ],
            "solutions": [
                "先查询任务当前状态",
                "确认操作与状态兼容",
                "参考状态机定义"
            ]
        },
        "E4001": {
            "title": "平台服务不可用",
            "explanation": "依赖的平台服务暂时不可用",
            "common_causes": [
                "平台服务维护中",
                "网络连接问题",
                "平台API变更"
            ],
            "solutions": [
                "稍后重试",
                "检查平台状态",
                "使用降级模式"
            ]
        }
    }
    
    @classmethod
    def explain(cls, error_code: str) -> Dict[str, Any]:
        """解释错误"""
        explanation = cls.ERROR_EXPLANATIONS.get(error_code, {
            "title": "未知错误",
            "explanation": f"错误码 {error_code} 没有详细解释",
            "common_causes": ["未知原因"],
            "solutions": ["联系技术支持"]
        })
        
        # 获取错误码定义
        error_def = ErrorCodes.get(error_code)
        
        result = {
            "error_code": error_code,
            **explanation
        }
        
        if error_def:
            result["category"] = error_def.category.value
            result["retryable"] = error_def.retryable
            result["http_status"] = error_def.http_status
        
        return result
    
    @classmethod
    def suggest_solution(cls, error_code: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """建议解决方案"""
        explanation = cls.explain(error_code)
        solutions = explanation.get("solutions", [])
        
        # 根据上下文调整建议
        if context:
            if context.get("retry_count", 0) > 3:
                solutions.append("已多次重试失败，建议检查根本原因")
        
        return solutions
