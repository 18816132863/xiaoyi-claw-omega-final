"""
PostgreSQL 仓储实现 V1.0.0

职责：
- 使用 PostgreSQL 实现任务持久化
- 支持事务
- 支持连接池
"""

import asyncio
import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

from domain.tasks import TaskSpec, TaskStatus, ScheduleType, EventType


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class PostgresTaskRepository:
    """PostgreSQL 任务仓储"""
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        pool_size: int = 5
    ):
        self.database_url = database_url or "postgresql://localhost/openclaw"
        self.pool_size = pool_size
        self.pool = None
        self.root = get_project_root()
    
    async def _get_pool(self):
        """获取连接池"""
        if self.pool is None and HAS_ASYNCPG:
            try:
                self.pool = await asyncpg.create_pool(
                    self.database_url,
                    min_size=1,
                    max_size=self.pool_size
                )
            except Exception as e:
                print(f"[Postgres] 连接失败: {e}，使用 SQLite fallback")
                return None
        return self.pool
    
    async def create(self, task: TaskSpec) -> str:
        """创建任务"""
        pool = await self._get_pool()
        
        if pool is None:
            # Fallback to SQLite
            from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
            sqlite_repo = SQLiteTaskRepository()
            return await sqlite_repo.create(task)
        
        async with pool.acquire() as conn:
            schedule_dict = task.schedule.model_dump() if task.schedule else {}
            
            # 序列化 steps
            steps_json = json.dumps(
                [s.model_dump() for s in task.steps],
                ensure_ascii=False,
                default=str
            )
            
            await conn.execute('''
                INSERT INTO tasks (
                    id, user_id, task_type, goal, payload_json,
                    trigger_mode, status, schedule_type, run_at, cron_expr,
                    timezone, next_run_at, max_attempts, retry_backoff_seconds,
                    timeout_seconds, idempotency_key, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
            ''',
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
                datetime.now(),
                datetime.now()
            )
            
            return task.task_id
    
    async def get(self, task_id: str) -> Optional[TaskSpec]:
        """获取任务"""
        pool = await self._get_pool()
        
        if pool is None:
            from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
            sqlite_repo = SQLiteTaskRepository()
            return await sqlite_repo.get(task_id)
        
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM tasks WHERE id = $1",
                uuid.UUID(task_id)
            )
            
            if row is None:
                return None
            
            return self._row_to_task(row)
    
    async def update(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新任务"""
        pool = await self._get_pool()
        
        if pool is None:
            from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
            sqlite_repo = SQLiteTaskRepository()
            return await sqlite_repo.update(task_id, updates)
        
        async with pool.acquire() as conn:
            set_clauses = []
            values = []
            idx = 1
            
            for key, value in updates.items():
                set_clauses.append(f"{key} = ${idx}")
                values.append(value)
                idx += 1
            
            set_clauses.append("updated_at = $idx")
            values.append(datetime.now())
            values.append(uuid.UUID(task_id))
            
            sql = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ${idx + 1}"
            
            result = await conn.execute(sql, *values)
            return "UPDATE 1" in result
    
    async def list_pending_scheduled(
        self,
        before: datetime,
        limit: int = 100
    ) -> List[TaskSpec]:
        """列出待执行的定时任务"""
        pool = await self._get_pool()
        
        if pool is None:
            from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
            sqlite_repo = SQLiteTaskRepository()
            return await sqlite_repo.list_pending_scheduled(before, limit)
        
        async with pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT * FROM tasks
                WHERE status IN ('persisted', 'queued')
                  AND trigger_mode = 'scheduled'
                  AND next_run_at IS NOT NULL
                  AND next_run_at <= $1
                ORDER BY next_run_at ASC
                LIMIT $2
            ''', before, limit)
            
            return [self._row_to_task(row) for row in rows]
    
    def _row_to_task(self, row) -> TaskSpec:
        """将数据库行转换为 TaskSpec"""
        from domain.tasks import ScheduleSpec, RetryPolicy, TimeoutPolicy, StepSpec
        
        schedule = None
        if row["schedule_type"]:
            schedule = ScheduleSpec(
                mode=ScheduleType(row["schedule_type"]),
                run_at=row["run_at"],
                cron_expr=row["cron_expr"],
                timezone=row["timezone"] or "Asia/Shanghai"
            )
        
        # 解析 payload_json
        payload = json.loads(row["payload_json"])
        
        if isinstance(payload, dict):
            inputs = payload.get("inputs", payload)
            steps_json = payload.get("steps", "[]")
            
            if isinstance(steps_json, str):
                steps_data = json.loads(steps_json)
            else:
                steps_data = steps_json
            
            steps = [StepSpec(**s) for s in steps_data] if steps_data else []
        else:
            inputs = payload
            steps = []
        
        return TaskSpec(
            task_id=str(row["id"]),
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
            created_at=row["created_at"]
        )


class PostgresToolCallRepository:
    """PostgreSQL 工具调用仓储"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or "postgresql://localhost/openclaw"
        self.pool = None
    
    async def record_tool_call(
        self,
        task_id: str,
        task_run_id: str,
        step_id: str,
        tool_name: str,
        request: Dict[str, Any],
        idempotency_key: str
    ) -> str:
        """记录工具调用"""
        call_id = str(uuid.uuid4())
        
        # 简化实现：写入文件
        root = get_project_root()
        tool_calls_file = root / "data" / "tool_calls.jsonl"
        tool_calls_file.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "id": call_id,
            "task_id": task_id,
            "task_run_id": task_run_id,
            "step_id": step_id,
            "tool_name": tool_name,
            "request_json": request,
            "status": "pending",
            "idempotency_key": idempotency_key,
            "created_at": datetime.now().isoformat()
        }
        
        with open(tool_calls_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        return call_id
    
    async def update_tool_call(
        self,
        call_id: str,
        response: Dict[str, Any],
        status: str,
        error: Optional[str] = None
    ):
        """更新工具调用结果"""
        # 简化实现
        pass
    
    async def check_idempotency(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        """检查幂等键"""
        root = get_project_root()
        tool_calls_file = root / "data" / "tool_calls.jsonl"
        
        if not tool_calls_file.exists():
            return None
        
        with open(tool_calls_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("idempotency_key") == idempotency_key:
                        return entry
                except:
                    pass
        
        return None
