"""
调度任务能力 - 真实实现
接入 TaskManager 任务内核
"""

from typing import Dict, Any
from datetime import datetime
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.task_manager import get_task_manager


class ScheduleTaskCapability:
    """调度任务能力"""
    
    name = "schedule_task"
    description = "创建定时任务"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务调度
        
        Args:
            params: {
                "task_type": "once" | "recurring",
                "run_at": ISO时间字符串（once任务）,
                "cron_expr": cron表达式（recurring任务）,
                "message": 任务内容,
                "user_id": 用户ID
            }
        
        Returns:
            {
                "success": bool,
                "task_id": str,
                "task_type": str,
                "status": str,
                "created_at": str,
                "idempotent": bool
            }
        """
        task_type = params.get("task_type", "once")
        run_at = params.get("run_at")
        cron_expr = params.get("cron_expr")
        message = params.get("message", "")
        user_id = params.get("user_id", "default")
        
        if not message:
            return {
                "success": False,
                "error": "任务内容不能为空",
                "error_code": "EMPTY_MESSAGE"
            }
        
        try:
            tm = get_task_manager()
            
            if task_type == "recurring" or cron_expr:
                # 循环任务
                result = await tm.create_recurring_message(
                    user_id=user_id,
                    message=message,
                    cron_expr=cron_expr or "* * * * *"
                )
            else:
                # 一次性任务
                result = await tm.create_scheduled_message(
                    user_id=user_id,
                    message=message,
                    run_at=run_at or datetime.now().isoformat()
                )
            
            return {
                "success": result.get("success", False),
                "task_id": result.get("task_id"),
                "task_type": task_type,
                "status": result.get("status", "unknown"),
                "created_at": datetime.now().isoformat(),
                "idempotent": result.get("idempotent", False)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SCHEDULE_FAILED"
            }
