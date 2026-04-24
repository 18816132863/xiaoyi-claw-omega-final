"""
暂停任务能力 - 真实实现
接入 TaskManager 任务内核
"""

from typing import Dict, Any
from datetime import datetime
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.task_manager import get_task_manager


class PauseTaskCapability:
    """暂停任务能力"""
    
    name = "pause_task"
    description = "暂停正在运行的任务"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务暂停
        
        Args:
            params: {
                "task_id": 任务ID
            }
        
        Returns:
            {
                "success": bool,
                "task_id": str,
                "status": str,
                "paused_at": str
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
            result = await tm.pause_task(task_id)
            
            return {
                "success": result.get("success", False),
                "task_id": task_id,
                "status": result.get("status", "paused"),
                "paused_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "PAUSE_FAILED",
                "task_id": task_id
            }
