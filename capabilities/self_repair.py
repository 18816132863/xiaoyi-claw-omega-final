"""
自修复能力 - 真实实现
检查并修复系统问题
"""

from typing import Dict, Any, List
from datetime import datetime
import sqlite3
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SelfRepairCapability:
    """自修复能力"""
    
    name = "self_repair"
    description = "自动检测并修复系统问题"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行自检和修复
        
        Args:
            params: {
                "auto_fix": bool (是否自动修复，默认False)
            }
        
        Returns:
            {
                "success": bool,
                "repairs": list,
                "fixed_count": int,
                "issues_found": int,
                "timestamp": str
            }
        """
        auto_fix = params.get("auto_fix", False)
        repairs: List[Dict[str, Any]] = []
        issues_found = 0
        fixed_count = 0
        
        db_path = project_root / "data" / "tasks.db"
        
        # 检查1: 数据库完整性
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # 检查表是否存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['tasks', 'task_runs', 'task_steps', 'task_events']
                missing_tables = [t for t in required_tables if t not in tables]
                
                if missing_tables:
                    issues_found += 1
                    repairs.append({
                        "check": "database_tables",
                        "status": "issue",
                        "message": f"缺少表: {missing_tables}",
                        "action": "none" if not auto_fix else "create_tables"
                    })
                else:
                    repairs.append({
                        "check": "database_tables",
                        "status": "ok",
                        "message": "所有必需表存在",
                        "action": "none"
                    })
                
                # 检查孤立记录
                cursor.execute("""
                    SELECT COUNT(*) FROM task_runs 
                    WHERE task_id NOT IN (SELECT id FROM tasks)
                """)
                orphan_runs = cursor.fetchone()[0]
                
                if orphan_runs > 0:
                    issues_found += 1
                    repairs.append({
                        "check": "orphaned_runs",
                        "status": "issue",
                        "message": f"发现 {orphan_runs} 条孤立运行记录",
                        "action": "none" if not auto_fix else "deleted",
                        "count": orphan_runs
                    })
                    if auto_fix:
                        cursor.execute("""
                            DELETE FROM task_runs 
                            WHERE task_id NOT IN (SELECT id FROM tasks)
                        """)
                        conn.commit()
                        fixed_count += 1
                else:
                    repairs.append({
                        "check": "orphaned_runs",
                        "status": "ok",
                        "message": "无孤立运行记录",
                        "action": "none"
                    })
                
                # 检查孤立步骤
                cursor.execute("""
                    SELECT COUNT(*) FROM task_steps 
                    WHERE task_run_id NOT IN (SELECT id FROM task_runs)
                """)
                orphan_steps = cursor.fetchone()[0]
                
                if orphan_steps > 0:
                    issues_found += 1
                    repairs.append({
                        "check": "orphaned_steps",
                        "status": "issue",
                        "message": f"发现 {orphan_steps} 条孤立步骤记录",
                        "action": "none" if not auto_fix else "deleted",
                        "count": orphan_steps
                    })
                    if auto_fix:
                        cursor.execute("""
                            DELETE FROM task_steps 
                            WHERE task_run_id NOT IN (SELECT id FROM task_runs)
                        """)
                        conn.commit()
                        fixed_count += 1
                else:
                    repairs.append({
                        "check": "orphaned_steps",
                        "status": "ok",
                        "message": "无孤立步骤记录",
                        "action": "none"
                    })
                
                conn.close()
                
            except Exception as e:
                issues_found += 1
                repairs.append({
                    "check": "database_integrity",
                    "status": "error",
                    "message": str(e),
                    "action": "none"
                })
        else:
            issues_found += 1
            repairs.append({
                "check": "database_exists",
                "status": "issue",
                "message": "数据库文件不存在",
                "action": "none"
            })
        
        # 检查2: pending_sends 文件
        pending_sends_path = project_root / "reports" / "ops" / "pending_sends.jsonl"
        if pending_sends_path.exists():
            repairs.append({
                "check": "pending_sends",
                "status": "ok",
                "message": "pending_sends 文件存在",
                "action": "none"
            })
        else:
            # 创建目录和文件
            pending_sends_path.parent.mkdir(parents=True, exist_ok=True)
            pending_sends_path.touch()
            repairs.append({
                "check": "pending_sends",
                "status": "fixed",
                "message": "已创建 pending_sends 文件",
                "action": "created"
            })
            fixed_count += 1
        
        return {
            "success": True,
            "repairs": repairs,
            "fixed_count": fixed_count,
            "issues_found": issues_found,
            "timestamp": datetime.now().isoformat()
        }
