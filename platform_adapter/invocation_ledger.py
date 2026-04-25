"""
平台调用审计台账
记录所有平台调用的详细信息
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent / "data" / "tasks.db"


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_table():
    """初始化表"""
    # 先确保数据库目录存在
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 读取迁移 SQL
    migration_path = Path(__file__).parent.parent / "infrastructure" / "storage" / "migrations" / "002_platform_invocations.sql"
    
    conn = get_connection()
    
    if migration_path.exists():
        with open(migration_path, "r") as f:
            sql = f.read()
        conn.executescript(sql)
    else:
        # 如果迁移文件不存在，直接创建表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS platform_invocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                task_run_id TEXT,
                task_step_id TEXT,
                capability TEXT NOT NULL,
                platform_op TEXT NOT NULL,
                idempotency_key TEXT UNIQUE,
                side_effecting INTEGER DEFAULT 0,
                request_json TEXT,
                raw_result_json TEXT,
                normalized_status TEXT NOT NULL,
                error_code TEXT,
                user_message TEXT,
                result_uncertain INTEGER DEFAULT 0,
                fallback_used INTEGER DEFAULT 0,
                elapsed_ms INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
    
    conn.commit()
    conn.close()


def record_invocation(
    capability: str,
    platform_op: str,
    normalized_status: str,
    *,
    task_id: Optional[str] = None,
    task_run_id: Optional[str] = None,
    task_step_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
    side_effecting: bool = False,
    request_json: Optional[dict] = None,
    raw_result_json: Optional[dict] = None,
    error_code: Optional[str] = None,
    user_message: Optional[str] = None,
    result_uncertain: bool = False,
    fallback_used: bool = False,
    elapsed_ms: int = 0,
) -> int:
    """
    记录平台调用
    
    Returns:
        int: 记录 ID
    """
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO platform_invocations (
            task_id, task_run_id, task_step_id,
            capability, platform_op, idempotency_key,
            side_effecting, request_json, raw_result_json,
            normalized_status, error_code, user_message,
            result_uncertain, fallback_used, elapsed_ms,
            created_at, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_id, task_run_id, task_step_id,
        capability, platform_op, idempotency_key,
        1 if side_effecting else 0,
        json.dumps(request_json, ensure_ascii=False) if request_json else None,
        json.dumps(raw_result_json, ensure_ascii=False) if raw_result_json else None,
        normalized_status, error_code, user_message,
        1 if result_uncertain else 0,
        1 if fallback_used else 0,
        elapsed_ms,
        now, now if normalized_status in ("completed", "failed") else None,
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def query_invocations(
    capability: Optional[str] = None,
    normalized_status: Optional[str] = None,
    limit: int = 100,
) -> list[dict]:
    """
    查询调用记录
    
    Returns:
        list[dict]: 记录列表
    """
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM platform_invocations WHERE 1=1"
    params = []
    
    if capability:
        sql += " AND capability = ?"
        params.append(capability)
    
    if normalized_status:
        sql += " AND normalized_status = ?"
        params.append(normalized_status)
    
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_invocation_by_id(record_id: int) -> Optional[dict]:
    """根据 ID 获取记录"""
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM platform_invocations WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def get_invocation_by_idempotency_key(key: str) -> Optional[dict]:
    """根据幂等键获取记录"""
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM platform_invocations WHERE idempotency_key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def query_by_task_id(task_id: str, limit: int = 100) -> list[dict]:
    """按 task_id 查询"""
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM platform_invocations WHERE task_id = ? ORDER BY created_at DESC LIMIT ?",
        (task_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def query_by_capability(capability: str, limit: int = 100) -> list[dict]:
    """按 capability 查询"""
    return query_invocations(capability=capability, limit=limit)


def query_by_status(normalized_status: str, limit: int = 100) -> list[dict]:
    """按 normalized_status 查询"""
    return query_invocations(normalized_status=normalized_status, limit=limit)


def export_recent(n: int = 100) -> list[dict]:
    """导出最近 N 条记录"""
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM platform_invocations ORDER BY created_at DESC LIMIT ?",
        (n,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def export_failed_report(limit: int = 100) -> list[dict]:
    """导出 failed 专项报告"""
    return query_by_status("failed", limit)


def export_timeout_report(limit: int = 100) -> list[dict]:
    """导出 timeout 专项报告"""
    return query_by_status("timeout", limit)


def export_uncertain_report(limit: int = 100) -> list[dict]:
    """导出 result_uncertain 专项报告"""
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM platform_invocations WHERE result_uncertain = 1 ORDER BY created_at DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def confirm_invocation(
    record_id: int,
    confirmed_status: str,
    confirm_note: Optional[str] = None,
) -> bool:
    """
    人工确认调用结果
    
    Args:
        record_id: 记录 ID
        confirmed_status: 确认后的状态 (confirmed_success / confirmed_failed / confirmed_duplicate)
        confirm_note: 确认备注
    
    Returns:
        bool: 是否成功
    """
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        UPDATE platform_invocations 
        SET confirmed_status = ?,
            confirm_note = ?,
            confirmed_at = ?
        WHERE id = ?
    """, (confirmed_status, confirm_note, now, record_id))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected > 0


def get_statistics() -> dict:
    """获取统计信息"""
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 总数
    cursor.execute("SELECT COUNT(*) FROM platform_invocations")
    total = cursor.fetchone()[0]
    
    # 按状态统计
    cursor.execute("""
        SELECT normalized_status, COUNT(*) as cnt 
        FROM platform_invocations 
        GROUP BY normalized_status
    """)
    by_status = {row[0]: row[1] for row in cursor.fetchall()}
    
    # uncertain 数量
    cursor.execute("SELECT COUNT(*) FROM platform_invocations WHERE result_uncertain = 1")
    uncertain_count = cursor.fetchone()[0]
    
    # 已确认数量
    cursor.execute("SELECT COUNT(*) FROM platform_invocations WHERE confirmed_status IS NOT NULL")
    confirmed_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total": total,
        "by_status": by_status,
        "uncertain_count": uncertain_count,
        "confirmed_count": confirmed_count,
    }


def cleanup_old_records(
    days_to_keep: int = 30,
    keep_failed: bool = True,
    keep_uncertain: bool = True,
) -> int:
    """
    清理旧记录
    
    Args:
        days_to_keep: 保留天数
        keep_failed: 是否保留 failed 记录
        keep_uncertain: 是否保留 uncertain 记录
    
    Returns:
        int: 删除的记录数
    """
    init_table()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 构建删除条件
    # 使用 datetime 比较
    if days_to_keep <= 0:
        # 清理所有符合条件的记录
        sql = "DELETE FROM platform_invocations WHERE 1=1"
        params = []
    else:
        sql = "DELETE FROM platform_invocations WHERE created_at < datetime('now', ?)"
        params = [f"-{days_to_keep} days"]
    
    if keep_failed:
        sql += " AND normalized_status != 'failed'"
    
    if keep_uncertain:
        sql += " AND result_uncertain = 0"
    
    cursor.execute(sql, params)
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted
