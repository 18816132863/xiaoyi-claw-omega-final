"""
SQLite 任务仓储实现 V1.0.0

职责：
- 使用 SQLite 实现任务持久化
- 支持任务 CRUD
- 支持查询和过滤
- 支持分布式锁（基于文件锁）
"""

import sqlite3
import json
import uuid
import fcntl
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from domain.tasks import TaskSpec, TaskStatus, ScheduleType, EventType
from .interfaces import TaskRepository, TaskRunRepository, TaskEventRepository, CheckpointRepository


class SQLiteTaskRunRepository(TaskRunRepository):
    """SQLite 任务运行仓储"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            root = get_project_root()
            db_path = str(root / "data" / "tasks.db")
        
        self.db_path = db_path
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    async def create_run(self, task_id: str, run_no: int) -> str:
        """创建运行记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            run_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO task_runs (id, task_id, run_no, status, started_at, created_at)
                VALUES (?, ?, ?, 'running', ?, ?)
            """, (
                run_id,
                task_id,
                run_no,
                serialize_datetime(datetime.now()),
                serialize_datetime(datetime.now())
            ))
            
            conn.commit()
            
            return run_id
    
    async def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """获取运行记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM task_runs WHERE id = ?", (run_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
    
    async def update_run(self, run_id: str, updates: Dict[str, Any]) -> bool:
        """更新运行记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 序列化时间字段
            for field in ["started_at", "ended_at", "retry_after"]:
                if field in updates and updates[field] is not None:
                    updates[field] = serialize_datetime(updates[field])
            
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [run_id]
            
            cursor.execute(f"UPDATE task_runs SET {set_clause} WHERE id = ?", values)
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    async def list_runs(self, task_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """列出任务的运行记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM task_runs
                WHERE task_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (task_id, limit))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]


class SQLiteTaskStepRepository:
    """SQLite 任务步骤仓储"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            root = get_project_root()
            db_path = str(root / "data" / "tasks.db")
        
        self.db_path = db_path
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    async def create_step(
        self,
        task_run_id: str,
        step_index: int,
        step_name: str,
        tool_name: Optional[str] = None,
        input_json: Optional[Dict[str, Any]] = None
    ) -> str:
        """创建步骤记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            step_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO task_steps (
                    id, task_run_id, step_index, step_name, tool_name,
                    input_json, output_json, status, started_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, '{}', 'running', ?, ?)
            """, (
                step_id,
                task_run_id,
                step_index,
                step_name,
                tool_name,
                json.dumps(input_json or {}, ensure_ascii=False),
                serialize_datetime(datetime.now()),
                serialize_datetime(datetime.now())
            ))
            
            conn.commit()
            
            return step_id
    
    async def update_step(self, step_id: str, updates: Dict[str, Any]) -> bool:
        """更新步骤记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 序列化时间字段
            for field in ["started_at", "ended_at"]:
                if field in updates and updates[field] is not None:
                    updates[field] = serialize_datetime(updates[field])
            
            # 序列化 JSON 字段
            for field in ["input_json", "output_json"]:
                if field in updates and isinstance(updates[field], dict):
                    updates[field] = json.dumps(updates[field], ensure_ascii=False)
            
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [step_id]
            
            cursor.execute(f"UPDATE task_steps SET {set_clause} WHERE id = ?", values)
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    async def list_steps(self, task_run_id: str) -> List[Dict[str, Any]]:
        """列出运行的所有步骤"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM task_steps
                WHERE task_run_id = ?
                ORDER BY step_index ASC
            """, (task_run_id,))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
from ..sqlite_utils import serialize_datetime, deserialize_datetime


# 统一时间字段集合 - 所有 SQLite 时间字段必须经过 serialize_datetime()
TIME_FIELDS = {
    "run_at",
    "next_run_at",
    "last_run_at",
    "created_at",
    "updated_at",
    "delivered_at",
}


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent.parent


class SQLiteTaskRepository(TaskRepository):
    """SQLite 任务仓储"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            root = get_project_root()
            db_path = str(root / "data" / "tasks.db")
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """初始化数据库"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 任务表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    
                    trigger_mode TEXT NOT NULL DEFAULT 'immediate',
                    status TEXT NOT NULL DEFAULT 'draft',
                    
                    schedule_type TEXT,
                    run_at TEXT,
                    cron_expr TEXT,
                    timezone TEXT DEFAULT 'Asia/Shanghai',
                    next_run_at TEXT,
                    last_run_at TEXT,
                    
                    attempt_count INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    retry_backoff_seconds INTEGER DEFAULT 60,
                    
                    timeout_seconds INTEGER DEFAULT 600,
                    
                    idempotency_key TEXT UNIQUE,
                    
                    last_error TEXT,
                    
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 任务运行表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_runs (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    run_no INTEGER NOT NULL DEFAULT 1,
                    
                    workflow_thread_id TEXT,
                    checkpoint_id TEXT,
                    
                    current_step INTEGER DEFAULT 0,
                    total_steps INTEGER DEFAULT 0,
                    
                    status TEXT NOT NULL DEFAULT 'pending',
                    
                    started_at TEXT,
                    ended_at TEXT,
                    
                    error_text TEXT,
                    retry_after TEXT,
                    
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            
            # 任务步骤表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_steps (
                    id TEXT PRIMARY KEY,
                    task_run_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    step_name TEXT NOT NULL,
                    
                    tool_name TEXT,
                    input_json TEXT DEFAULT '{}',
                    output_json TEXT DEFAULT '{}',
                    
                    status TEXT NOT NULL DEFAULT 'pending',
                    
                    started_at TEXT,
                    ended_at TEXT,
                    
                    error_text TEXT,
                    
                    idempotency_key TEXT UNIQUE,
                    
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (task_run_id) REFERENCES task_runs(id) ON DELETE CASCADE
                )
            """)
            
            # 任务事件表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_events (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    task_run_id TEXT,
                    
                    event_type TEXT NOT NULL,
                    event_payload TEXT DEFAULT '{}',
                    
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            
            # 检查点表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    task_run_id TEXT NOT NULL,
                    
                    thread_id TEXT NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    checkpoint_ns TEXT DEFAULT '',
                    
                    snapshot_json TEXT NOT NULL DEFAULT '{}',
                    metadata_json TEXT DEFAULT '{}',
                    
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (task_run_id) REFERENCES task_runs(id) ON DELETE CASCADE,
                    UNIQUE (thread_id, checkpoint_id, checkpoint_ns)
                )
            """)
            
            # 索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_next_run_at ON tasks(next_run_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_idempotency_key ON tasks(idempotency_key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_runs_task_id ON task_runs(task_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_events_task_id ON task_events(task_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_thread_id ON workflow_checkpoints(thread_id)")
            
            conn.commit()
    
    async def create(self, task: TaskSpec) -> str:
        """创建任务"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            schedule_dict = task.schedule.model_dump() if task.schedule else {}
            
            # 确保 datetime 字段为字符串（使用统一序列化方法）
            schedule_dict["run_at"] = serialize_datetime(schedule_dict.get("run_at"))
            schedule_dict["next_run_at"] = serialize_datetime(schedule_dict.get("next_run_at"))
            
            # 序列化 steps
            steps_json = json.dumps(
                [s.model_dump() for s in task.steps],
                ensure_ascii=False,
                default=str
            )
            
            cursor.execute("""
                INSERT INTO tasks (
                    id, user_id, task_type, goal, payload_json,
                    trigger_mode, status, schedule_type, run_at, cron_expr,
                    timezone, next_run_at, max_attempts, retry_backoff_seconds,
                    timeout_seconds, idempotency_key, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.user_id or "default",
                task.task_type,
                task.goal,
                json.dumps({"inputs": task.inputs, "steps": steps_json}, ensure_ascii=False),
                task.trigger_mode.value,
                task.status.value,
                schedule_dict.get("mode"),
                schedule_dict.get("run_at"),
                schedule_dict.get("cron_expr"),
                schedule_dict.get("timezone", "Asia/Shanghai"),
                schedule_dict.get("next_run_at"),
                task.retry_policy.max_attempts,
                task.retry_policy.backoff_seconds,
                task.timeout_policy.task_timeout_seconds,
                task.idempotency_key,
                serialize_datetime(datetime.now()),
                serialize_datetime(datetime.now())
            ))
            
            conn.commit()
            
            return task.task_id
    
    async def get(self, task_id: str) -> Optional[TaskSpec]:
        """获取任务"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return self._row_to_task(row)
    
    async def update(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新任务"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            
            for key, value in updates.items():
                if key in ("payload_json", "inputs"):
                    set_clauses.append(f"{key} = ?")
                    values.append(json.dumps(value, ensure_ascii=False))
                elif key in TIME_FIELDS:
                    # 所有时间字段统一强制序列化
                    set_clauses.append(f"{key} = ?")
                    values.append(serialize_datetime(value))
                else:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            set_clauses.append("updated_at = ?")
            values.append(serialize_datetime(datetime.now()))
            values.append(task_id)
            
            sql = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(sql, values)
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    async def delete(self, task_id: str) -> bool:
        """删除任务"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    async def list_by_user(
        self,
        user_id: str,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TaskSpec]:
        """列出用户的任务"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute("""
                    SELECT * FROM tasks
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (user_id, status.value, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM tasks
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (user_id, limit, offset))
            
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]
    
    async def list_pending_scheduled(
        self,
        before: datetime,
        limit: int = 100
    ) -> List[TaskSpec]:
        """列出待执行的定时任务"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tasks
                WHERE status IN ('persisted', 'waiting_retry')
                  AND trigger_mode = 'scheduled'
                  AND next_run_at IS NOT NULL
                  AND next_run_at <= ?
                ORDER BY next_run_at ASC
                LIMIT ?
            """, (serialize_datetime(before), limit))
            
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]
    
    async def acquire_lock(self, task_id: str, lock_ttl: int = 60) -> bool:
        """获取任务锁"""
        # SQLite 使用文件锁，这里简化实现
        lock_file = f"/tmp/task_lock_{task_id}.lock"
        try:
            fd = os.open(lock_file, os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            return False
    
    async def release_lock(self, task_id: str) -> bool:
        """释放任务锁"""
        lock_file = f"/tmp/task_lock_{task_id}.lock"
        try:
            os.remove(lock_file)
            return True
        except:
            return False
    
    def _row_to_task(self, row: sqlite3.Row) -> TaskSpec:
        """将数据库行转换为 TaskSpec"""
        from domain.tasks import ScheduleSpec, RetryPolicy, TimeoutPolicy, StepSpec
        
        schedule = None
        if row["schedule_type"]:
            schedule = ScheduleSpec(
                mode=ScheduleType(row["schedule_type"]),
                run_at=deserialize_datetime(row["run_at"]),
                cron_expr=row["cron_expr"],
                timezone=row["timezone"] or "Asia/Shanghai"
            )
        
        # 解析 payload_json
        payload = json.loads(row["payload_json"])
        
        # 兼容旧格式和新格式
        if isinstance(payload, dict):
            inputs = payload.get("inputs", payload)
            steps_json = payload.get("steps", "[]")
            
            # 解析 steps
            if isinstance(steps_json, str):
                steps_data = json.loads(steps_json)
            else:
                steps_data = steps_json
            
            steps = [StepSpec(**s) for s in steps_data] if steps_data else []
        else:
            inputs = payload
            steps = []
        
        return TaskSpec(
            task_id=row["id"],
            user_id=row["user_id"],
            task_type=row["task_type"],
            goal=row["goal"],
            inputs=inputs,
            steps=steps,
            trigger_mode=row["trigger_mode"],
            status=TaskStatus(row["status"]),
            schedule=schedule,
            retry_policy=RetryPolicy(
                max_attempts=row["max_attempts"],
                backoff_seconds=row["retry_backoff_seconds"]
            ),
            timeout_policy=TimeoutPolicy(
                task_timeout_seconds=row["timeout_seconds"]
            ),
            idempotency_key=row["idempotency_key"],
            created_at=deserialize_datetime(row["created_at"])
        )


class SQLiteTaskEventRepository(TaskEventRepository):
    """SQLite 任务事件仓储"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            root = get_project_root()
            db_path = str(root / "data" / "tasks.db")
        
        self.db_path = db_path
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    async def record_event(
        self,
        task_id: str,
        event_type: str,
        event_payload: Dict[str, Any],
        run_id: Optional[str] = None
    ) -> str:
        """记录事件"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            event_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO task_events (id, task_id, task_run_id, event_type, event_payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                task_id,
                run_id,
                event_type,
                json.dumps(event_payload, ensure_ascii=False),
                serialize_datetime(datetime.now())
            ))
            
            conn.commit()
            
            return event_id
    
    async def list_events(
        self,
        task_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """列出任务事件"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM task_events
                WHERE task_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (task_id, limit))
            
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "task_id": row["task_id"],
                    "task_run_id": row["task_run_id"],
                    "event_type": row["event_type"],
                    "event_payload": json.loads(row["event_payload"]),
                    "created_at": row["created_at"]
                }
                for row in rows
            ]


class SQLiteCheckpointRepository(CheckpointRepository):
    """SQLite 检查点仓储"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            root = get_project_root()
            db_path = str(root / "data" / "tasks.db")
        
        self.db_path = db_path
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    async def save_checkpoint(
        self,
        task_id: str,
        run_id: str,
        thread_id: str,
        checkpoint_id: str,
        snapshot: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """保存检查点"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cp_id = str(uuid.uuid4())
            
            # 使用 INSERT OR REPLACE 处理唯一约束
            cursor.execute("""
                INSERT OR REPLACE INTO workflow_checkpoints (
                    id, task_id, task_run_id, thread_id, checkpoint_id,
                    checkpoint_ns, snapshot_json, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cp_id,
                task_id,
                run_id,
                thread_id,
                checkpoint_id,
                "",
                json.dumps(snapshot, ensure_ascii=False),
                json.dumps(metadata or {}, ensure_ascii=False),
                serialize_datetime(datetime.now())
            ))
            
            conn.commit()
            
            return True
    
    async def get_latest_checkpoint(
        self,
        thread_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取最新检查点"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM workflow_checkpoints
                WHERE thread_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (thread_id,))
            
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "id": row["id"],
                "task_id": row["task_id"],
                "task_run_id": row["task_run_id"],
                "thread_id": row["thread_id"],
                "checkpoint_id": row["checkpoint_id"],
                "snapshot": json.loads(row["snapshot_json"]),
                "metadata": json.loads(row["metadata_json"]),
                "created_at": row["created_at"]
            }
    
    async def list_checkpoints(
        self,
        task_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """列出检查点"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM workflow_checkpoints
                WHERE task_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (task_id, limit))
            
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "thread_id": row["thread_id"],
                    "checkpoint_id": row["checkpoint_id"],
                    "snapshot": json.loads(row["snapshot_json"]),
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
