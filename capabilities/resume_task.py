"""
恢复任务能力 - 真实实现
接入 TaskManager 任务内核
"""

from typing import Dict, Any
from datetime import datetime
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.task_manager import get_task_manager


class ResumeTaskCapability:
    """恢复任务能力"""
    
    name = "resume_task"
    description = "恢复暂停的任务"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务恢复
        
        Args:
            params: {
                "task_id": 任务ID
            }
        
        Returns:
            {
                "success": bool,
                "task_id": str,
                "status": str,
                "resumed_at": str
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
            result = await tm.resume_task(task_id)
            
            return {
                "success": result.get("success", False),
                "task_id": task_id,
                "status": result.get("status", "resumed"),
                "resumed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "RESUME_FAILED",
                "task_id": task_id
            }
