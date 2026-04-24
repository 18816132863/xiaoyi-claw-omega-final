"""
Event Timeline - 事件时间线
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sqlite3
from pathlib import Path


class EventTimeline:
    """事件时间线"""
    
    def __init__(self, db_path: str = "data/tasks.db"):
        self.db_path = db_path
    
    def get_task_events(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务的所有事件"""
        if not Path(self.db_path).exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM task_events 
            WHERE task_id = ? 
            ORDER BY created_at ASC
        """, (task_id,))
        
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return events
    
    def get_run_events(self, run_id: str) -> List[Dict[str, Any]]:
        """获取运行的所有事件"""
        if not Path(self.db_path).exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM task_events 
            WHERE run_id = ? 
            ORDER BY created_at ASC
        """, (run_id,))
        
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return events
    
    def build_timeline(self, task_id: str) -> Dict[str, Any]:
        """构建任务时间线"""
        events = self.get_task_events(task_id)
        
        timeline = {
            "task_id": task_id,
            "events": events,
            "total_events": len(events),
            "event_types": {},
            "first_event": None,
            "last_event": None
        }
        
        if events:
            timeline["first_event"] = events[0]["created_at"]
            timeline["last_event"] = events[-1]["created_at"]
            
            for event in events:
                event_type = event.get("event_type", "unknown")
                timeline["event_types"][event_type] = timeline["event_types"].get(event_type, 0) + 1
        
        return timeline
