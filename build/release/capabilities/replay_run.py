"""
回放运行能力 - 真实实现
读取 task_runs / task_steps
"""

from typing import Dict, Any
from datetime import datetime
import sqlite3
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ReplayRunCapability:
    """回放运行能力"""
    
    name = "replay_run"
    description = "回放任务运行过程"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        回放任务运行
        
        Args:
            params: {
                "run_id": 运行ID
            }
        
        Returns:
            {
                "success": bool,
                "run_id": str,
                "run": dict,
                "steps": list,
                "timeline": list,
                "replayed_at": str
            }
        """
        run_id = params.get("run_id")
        
        if not run_id:
            return {
                "success": False,
                "error": "缺少 run_id",
                "error_code": "MISSING_RUN_ID"
            }
        
        db_path = project_root / "data" / "tasks.db"
        
        if not db_path.exists():
            return {
                "success": False,
                "error": "数据库不存在",
                "error_code": "DATABASE_NOT_FOUND",
                "run_id": run_id
            }
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询运行记录
            cursor.execute("SELECT * FROM task_runs WHERE id = ?", (run_id,))
            run_row = cursor.fetchone()
            run = dict(run_row) if run_row else None
            
            if not run:
                conn.close()
                return {
                    "success": False,
                    "error": "运行记录不存在",
                    "error_code": "RUN_NOT_FOUND",
                    "run_id": run_id
                }
            
            # 查询步骤记录
            cursor.execute("SELECT * FROM task_steps WHERE task_run_id = ? ORDER BY step_index", (run_id,))
            steps = [dict(row) for row in cursor.fetchall()]
            
            # 构建时间线
            timeline = []
            
            # 添加运行开始
            timeline.append({
                "type": "run_start",
                "timestamp": run.get("started_at"),
                "status": run.get("status")
            })
            
            # 添加步骤
            for step in steps:
                timeline.append({
                    "type": "step",
                    "step_name": step.get("step_name"),
                    "tool_name": step.get("tool_name"),
                    "timestamp": step.get("started_at"),
                    "status": step.get("status"),
                    "duration_ms": step.get("duration_ms")
                })
            
            # 添加运行结束
            timeline.append({
                "type": "run_end",
                "timestamp": run.get("ended_at"),
                "status": run.get("status")
            })
            
            conn.close()
            
            return {
                "success": True,
                "run_id": run_id,
                "run": run,
                "steps": steps,
                "timeline": timeline,
                "replayed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "REPLAY_FAILED",
                "run_id": run_id
            }
