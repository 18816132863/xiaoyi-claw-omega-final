"""
Response Formatter - 响应格式化器
提供统一的响应格式化功能
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class ResponseFormatter:
    """响应格式化器"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        格式化成功响应
        
        Args:
            data: 响应数据
            message: 成功消息
            metadata: 元数据
            
        Returns:
            格式化的响应字典
        """
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    @staticmethod
    def error(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        格式化错误响应
        
        Args:
            error_code: 错误码
            message: 错误消息
            details: 错误详情
            suggestions: 建议列表
            
        Returns:
            格式化的错误响应字典
        """
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if details:
            response["error"]["details"] = details
        
        if suggestions:
            response["error"]["suggestions"] = suggestions
        
        return response
    
    @staticmethod
    def partial_success(
        succeeded: List[Dict[str, Any]],
        failed: List[Dict[str, Any]],
        summary: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        格式化部分成功响应（批量操作）
        
        Args:
            succeeded: 成功的项目列表
            failed: 失败的项目列表
            summary: 摘要信息
            
        Returns:
            格式化的部分成功响应
        """
        total = len(succeeded) + len(failed)
        
        response = {
            "success": len(failed) == 0,
            "partial": len(failed) > 0 and len(succeeded) > 0,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "succeeded": len(succeeded),
                "failed": len(failed),
                "success_rate": len(succeeded) / total if total > 0 else 0
            },
            "results": {
                "succeeded": succeeded,
                "failed": failed
            }
        }
        
        if summary:
            response["summary"].update(summary)
        
        return response
    
    @staticmethod
    def paginated(
        items: List[Any],
        page: int,
        page_size: int,
        total: int,
        has_more: bool
    ) -> Dict[str, Any]:
        """
        格式化分页响应
        
        Args:
            items: 当前页数据
            page: 当前页码
            page_size: 每页大小
            total: 总数量
            has_more: 是否有更多
            
        Returns:
            格式化的分页响应
        """
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "data": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
                "has_more": has_more
            }
        }
    
    @staticmethod
    def task_created(
        task_id: str,
        task_type: str,
        status: str = "pending",
        estimated_completion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        格式化任务创建响应
        
        Args:
            task_id: 任务ID
            task_type: 任务类型
            status: 任务状态
            estimated_completion: 预计完成时间
            
        Returns:
            格式化的任务创建响应
        """
        response = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "task": {
                "id": task_id,
                "type": task_type,
                "status": status
            }
        }
        
        if estimated_completion:
            response["task"]["estimated_completion"] = estimated_completion
        
        return response
    
    @staticmethod
    def diagnostic(
        status: str,
        checks: List[Dict[str, Any]],
        recommendations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        格式化诊断响应
        
        Args:
            status: 整体状态
            checks: 检查项列表
            recommendations: 建议列表
            
        Returns:
            格式化的诊断响应
        """
        passed = sum(1 for c in checks if c.get("status") == "pass")
        failed = sum(1 for c in checks if c.get("status") == "fail")
        warning = sum(1 for c in checks if c.get("status") == "warning")
        
        response = {
            "success": failed == 0,
            "timestamp": datetime.now().isoformat(),
            "diagnostic": {
                "overall_status": status,
                "summary": {
                    "total_checks": len(checks),
                    "passed": passed,
                    "failed": failed,
                    "warnings": warning
                },
                "checks": checks
            }
        }
        
        if recommendations:
            response["diagnostic"]["recommendations"] = recommendations
        
        return response


def format_response(
    success: bool,
    data: Any = None,
    error: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    通用响应格式化函数
    
    Args:
        success: 是否成功
        data: 响应数据
        error: 错误信息
        **kwargs: 其他字段
        
    Returns:
        格式化的响应字典
    """
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        response["data"] = data
    else:
        response["error"] = error or {"message": "Unknown error"}
    
    response.update(kwargs)
    
    return response
