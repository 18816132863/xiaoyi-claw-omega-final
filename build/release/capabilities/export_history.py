"""
导出历史能力 - 真实实现
读取 tasks / task_runs / task_steps / task_events
"""

from typing import Dict, Any
from datetime import datetime
import sqlite3
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ExportHistoryCapability:
    """导出历史能力"""
    
    name = "export_history"
    description = "导出任务历史记录"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        导出任务历史
        
        Args:
            params: {
                "task_id": 任务ID,
                "format": "json" | "dict"
            }
        
        Returns:
            {
                "success": bool,
                "task_id": str,
                "task": dict,
                "runs": list,
                "steps": list,
                "events": list,
                "record_count": int,
                "exported_at": str
            }
        """
        task_id = params.get("task_id")
        format_type = params.get("format", "json")
        
        if not task_id:
            return {
                "success": False,
                "error": "缺少 task_id",
                "error_code": "MISSING_TASK_ID"
            }
        
        db_path = project_root / "data" / "tasks.db"
        
        if not db_path.exists():
            return {
                "success": False,
                "error": "数据库不存在",
                "error_code": "DATABASE_NOT_FOUND",
                "task_id": task_id
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询任务
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            task_row = cursor.fetchone()
            task = dict(task_row) if task_row else None
            
            if not task:
                conn.close()
                return {
                    "success": False,
                    "error": "任务不存在",
                    "error_code": "TASK_NOT_FOUND",
                    "task_id": task_id
                }
            
            # 查询运行记录
            cursor.execute("SELECT * FROM task_runs WHERE task_id = ? ORDER BY created_at DESC", (task_id,))
            runs = [dict(row) for row in cursor.fetchall()]
            
            # 查询步骤记录
            steps = []
            for run in runs:
                cursor.execute("SELECT * FROM task_steps WHERE task_run_id = ? ORDER BY step_no", (run["id"],))
                steps.extend([dict(row) for row in cursor.fetchall()])
            
            # 查询事件记录
            cursor.execute("SELECT * FROM task_events WHERE task_id = ? ORDER BY created_at DESC", (task_id,))
            events = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            record_count = 1 + len(runs) + len(steps) + len(events)
            
            return {
                "success": True,
                "task_id": task_id,
                "task": task,
                "runs": runs,
                "steps": steps,
                "events": events,
                "record_count": record_count,
                "exported_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "EXPORT_FAILED",
                "task_id": task_id
            }
