"""
重试任务能力 - 真实实现
接入 TaskManager 任务内核
"""

from typing import Dict, Any
from datetime import datetime
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.task_manager import get_task_manager


class RetryTaskCapability:
    """重试任务能力"""
    
    name = "retry_task"
    description = "重试失败的任务"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务重试
        
        Args:
            params: {
                "task_id": 任务ID
            }
        
        Returns:
            {
                "success": bool,
                "task_id": str,
                "status": str,
                "delivery_status": str,
                "retry_at": str
            }
        """
        task_id = params.get("task_id")
        
        if not task_id:
            return {
                "success": False,
                "error": "缺少 task_id",
                "error_code": "MISSING_TASK_ID"
            }
        
        try:
            tm = get_task_manager()
            result = await tm.retry_task(task_id)
            
            return {
                "success": result.get("success", False),
                "task_id": task_id,
                "status": result.get("status", "unknown"),
                "delivery_status": result.get("delivery_status", "unknown"),
                "retry_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "RETRY_FAILED",
                "task_id": task_id
            }
