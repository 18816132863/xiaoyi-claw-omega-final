#!/usr/bin/env python
"""
预热平台调用审计台账 - V8.4.0 最终版
支持标准演示数据集，确保所有报告口径一致
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import argparse

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 数据库路径
DB_PATH = project_root / "data" / "tasks.db"


def reset_database():
    """重置数据库（仅 demo/test 用）"""
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("   ✓ 数据库已重置")


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_table():
    """初始化表"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_invocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT,
            capability TEXT NOT NULL,
            platform_op TEXT NOT NULL,
            idempotency_key TEXT UNIQUE,
            normalized_status TEXT NOT NULL,
            error_code TEXT,
            user_message TEXT,
            result_uncertain INTEGER DEFAULT 0,
            fallback_used INTEGER DEFAULT 0,
            elapsed_ms INTEGER,
            request_json TEXT,
            raw_result_json TEXT,
            confirmed_status TEXT,
            confirmed_at TEXT,
            confirm_note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_capability ON platform_invocations(capability)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON platform_invocations(normalized_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON platform_invocations(created_at)")
    
    conn.commit()
    conn.close()


def insert_record(
    capability: str,
    platform_op: str,
    normalized_status: str,
    error_code: str = None,
    user_message: str = None,
    result_uncertain: bool = False,
    fallback_used: bool = False,
    elapsed_ms: int = 1000,
    request_json: str = None,
    raw_result_json: str = None,
    confirmed_status: str = None,
    confirm_note: str = None,
    created_at: str = None,
) -> int:
    """插入记录"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO platform_invocations (
            capability, platform_op, normalized_status, error_code, user_message,
            result_uncertain, fallback_used, elapsed_ms, request_json, raw_result_json,
            confirmed_status, confirm_note, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        capability, platform_op, normalized_status, error_code, user_message,
        1 if result_uncertain else 0, 1 if fallback_used else 0, elapsed_ms,
        request_json, raw_result_json, confirmed_status, confirm_note, created_at
    ))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return record_id


def seed_demo_standard():
    """
    预热标准演示数据集
    确保所有报告口径一致
    
    数据分布：
    - completed: 60
    - failed: 12
    - timeout: 8
    - result_uncertain: 10
    - auth_required: 5
    - queued_for_delivery: 5
    - confirmed_success: 6
    - confirmed_failed: 2
    - confirmed_duplicate: 1
    """
    print("🌱 开始预热标准演示数据集...")
    
    # 初始化表
    init_table()
    
    now = datetime.now()
    created_at_base = now.strftime("%Y-%m-%d")
    
    record_ids = []
    
    # ========== completed: 60 条 ==========
    print("   插入 completed 记录 (60 条)...")
    
    # MESSAGE_SENDING: 25 条
    for i in range(25):
        record_id = insert_record(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
            error_code=None,
            user_message="已完成",
            result_uncertain=False,
            elapsed_ms=1000 + i * 50,
            request_json=json.dumps({
                "phone_number": f"1380013{i:04d}",
                "content": f"短信内容 {i}"
            }),
            raw_result_json=json.dumps({"code": 0, "result": {"message": "send success"}}),
            created_at=f"{created_at_base}T{10 + i % 12:02d}:{i % 60:02d}:00",
        )
        record_ids.append(record_id)
    
    # TASK_SCHEDULING: 20 条
    for i in range(20):
        record_id = insert_record(
            capability="TASK_SCHEDULING",
            platform_op="create_event",
            normalized_status="completed",
            error_code=None,
            user_message="已完成",
            result_uncertain=False,
            elapsed_ms=1500 + i * 50,
            request_json=json.dumps({
                "title": f"日程 {i}",
                "start_time": f"2026-04-{25 + i % 5:02d} 10:00:00"
            }),
            raw_result_json=json.dumps({"code": 0, "result": {"entityId": f"199{i}"}}),
            created_at=f"{created_at_base}T{10 + i % 12:02d}:{i % 60:02d}:00",
        )
        record_ids.append(record_id)
    
    # STORAGE: 10 条
    for i in range(10):
        record_id = insert_record(
            capability="STORAGE",
            platform_op="create_note",
            normalized_status="completed",
            error_code=None,
            user_message="已完成",
            result_uncertain=False,
            elapsed_ms=800 + i * 30,
            request_json=json.dumps({
                "title": f"备忘录 {i}",
                "content": f"内容 {i}"
            }),
            raw_result_json=json.dumps({"code": 0, "result": {"entityId": f"abc{i}"}}),
            created_at=f"{created_at_base}T{10 + i % 12:02d}:{i % 60:02d}:00",
        )
        record_ids.append(record_id)
    
    # NOTIFICATION: 5 条
    for i in range(5):
        record_id = insert_record(
            capability="NOTIFICATION",
            platform_op="push_notification",
            normalized_status="completed",
            error_code=None,
            user_message="已完成",
            result_uncertain=False,
            elapsed_ms=500 + i * 20,
            request_json=json.dumps({
                "title": f"通知 {i}",
                "content": f"通知内容 {i}"
            }),
            raw_result_json=json.dumps({"code": "0000000000", "desc": "OK"}),
            created_at=f"{created_at_base}T{10 + i % 12:02d}:{i % 60:02d}:00",
        )
        record_ids.append(record_id)
    
    # ========== failed: 12 条 ==========
    print("   插入 failed 记录 (12 条)...")
    
    failed_reasons = [
        ("PLATFORM_EXECUTION_FAILED", "网络错误"),
        ("PLATFORM_EXECUTION_FAILED", "服务不可用"),
        ("PLATFORM_INVALID_PARAMS", "参数错误"),
        ("PLATFORM_RATE_LIMITED", "请求过快"),
    ]
    
    for i in range(12):
        reason = failed_reasons[i % len(failed_reasons)]
        capability = ["MESSAGE_SENDING", "TASK_SCHEDULING", "STORAGE", "NOTIFICATION"][i % 4]
        
        record_id = insert_record(
            capability=capability,
            platform_op="send_message" if capability == "MESSAGE_SENDING" else "create_event",
            normalized_status="failed",
            error_code=reason[0],
            user_message="操作失败，请稍后重试",
            result_uncertain=False,
            elapsed_ms=3000 + i * 100,
            request_json=json.dumps({"phone_number": f"1390013{i:04d}"}),
            raw_result_json=json.dumps({"code": -1, "desc": reason[1]}),
            created_at=f"{created_at_base}T{11 + i % 8:02d}:{i % 60:02d}:00",
        )
        record_ids.append(record_id)
    
    # ========== timeout: 8 条 ==========
    print("   插入 timeout 记录 (8 条)...")
    
    for i in range(8):
        capability = ["MESSAGE_SENDING", "TASK_SCHEDULING", "NOTIFICATION", "STORAGE"][i % 4]
        
        record_id = insert_record(
            capability=capability,
            platform_op="send_message" if capability == "MESSAGE_SENDING" else "create_event",
            normalized_status="timeout",
            error_code="PLATFORM_TIMEOUT",
            user_message="请求超时，请检查实际结果",
            result_uncertain=True,
            elapsed_ms=30000,
            request_json=json.dumps({"phone_number": f"1370013{i:04d}"}),
            raw_result_json=None,
            created_at=f"{created_at_base}T{12 + i % 6:02d}:{i % 60:02d}:00",
        )
        record_ids.append(record_id)
    
    # ========== result_uncertain: 10 条 ==========
    print("   插入 result_uncertain 记录 (10 条)...")
    
    for i in range(10):
        capability = ["MESSAGE_SENDING", "TASK_SCHEDULING", "NOTIFICATION"][i % 3]
        
        record_id = insert_record(
            capability=capability,
            platform_op="send_message" if capability == "MESSAGE_SENDING" else "create_event",
            normalized_status="result_uncertain",
            error_code="PLATFORM_RESULT_UNCERTAIN",
            user_message="结果不确定，请检查实际结果",
            result_uncertain=True,
            elapsed_ms=15000 + i * 500,
            request_json=json.dumps({"phone_number": f"1360013{i:04d}"}),
            raw_result_json=json.dumps({"code": "unknown", "desc": "响应格式异常"}),
            created_at=f"{created_at_base}T{13 + i % 5:02d}:{i % 60:02d}:00",
        )
        record_ids.append(record_id)
    
    # ========== auth_required: 5 条 ==========
    print("   插入 auth_required 记录 (5 条)...")
    
    for i in range(5):
        record_id = insert_record(
            capability="NOTIFICATION",
            platform_op="push_notification",
            normalized_status="auth_required",
            error_code="PLATFORM_AUTH_REQUIRED",
            user_message="需要授权才能使用此功能",
            result_uncertain=False,
            elapsed_ms=500,
            request_json=json.dumps({"title": f"需要授权的通知 {i}"}),
            raw_result_json=json.dumps({"code": "0000900034", "desc": "authCode invalid"}),
            created_at=f"{created_at_base}T{14:02d}:{i * 10:02d}:00",
        )
        record_ids.append(record_id)
    
    # ========== queued_for_delivery: 5 条 ==========
    print("   插入 queued_for_delivery 记录 (5 条)...")
    
    for i in range(5):
        record_id = insert_record(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="queued_for_delivery",
            error_code=None,
            user_message="已提交等待处理",
            result_uncertain=False,
            fallback_used=True,
            elapsed_ms=1000,
            request_json=json.dumps({"phone_number": f"1350013{i:04d}"}),
            raw_result_json=json.dumps({"code": "queued", "desc": "已加入发送队列"}),
            created_at=f"{created_at_base}T{15:02d}:{i * 10:02d}:00",
        )
        record_ids.append(record_id)
    
    # ========== 确认部分 uncertain 记录 ==========
    print("   确认 uncertain 记录...")
    
    # 获取所有 uncertain 记录
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM platform_invocations 
        WHERE result_uncertain = 1 
        ORDER BY id
    """)
    uncertain_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # confirmed_success: 6 条
    for i, record_id in enumerate(uncertain_ids[:6]):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE platform_invocations 
            SET confirmed_status = ?, confirmed_at = ?, confirm_note = ?
            WHERE id = ?
        """, [
            "confirmed_success",
            f"{created_at_base}T16:{i * 5:02d}:00",
            "用户确认操作已成功",
            record_id
        ])
        conn.commit()
        conn.close()
        print(f"   ✓ 记录 #{record_id}: confirmed_success")
    
    # confirmed_failed: 2 条
    for i, record_id in enumerate(uncertain_ids[6:8]):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE platform_invocations 
            SET confirmed_status = ?, confirmed_at = ?, confirm_note = ?
            WHERE id = ?
        """, [
            "confirmed_failed",
            f"{created_at_base}T16:{30 + i * 5:02d}:00",
            "用户确认操作失败",
            record_id
        ])
        conn.commit()
        conn.close()
        print(f"   ✓ 记录 #{record_id}: confirmed_failed")
    
    # confirmed_duplicate: 1 条
    if len(uncertain_ids) > 8:
        record_id = uncertain_ids[8]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE platform_invocations 
            SET confirmed_status = ?, confirmed_at = ?, confirm_note = ?
            WHERE id = ?
        """, [
            "confirmed_duplicate",
            f"{created_at_base}T16:45:00",
            "确认为重复操作",
            record_id
        ])
        conn.commit()
        conn.close()
        print(f"   ✓ 记录 #{record_id}: confirmed_duplicate")
    
    # 统计
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM platform_invocations")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM platform_invocations WHERE result_uncertain = 1")
    uncertain_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM platform_invocations WHERE confirmed_status IS NOT NULL")
    confirmed_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n✅ 预热完成!")
    print(f"   总记录数: {total}")
    print(f"   Uncertain 记录: {uncertain_count}")
    print(f"   已确认记录: {confirmed_count}")
    
    return {
        "total": total,
        "uncertain_count": uncertain_count,
        "confirmed_count": confirmed_count,
    }


def output_summary_json(output_path: str):
    """输出汇总 JSON"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 总体统计
    cursor.execute("SELECT COUNT(*) FROM platform_invocations")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM platform_invocations WHERE result_uncertain = 1")
    uncertain_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM platform_invocations WHERE confirmed_status IS NOT NULL")
    confirmed_count = cursor.fetchone()[0]
    
    # 按状态统计
    cursor.execute("""
        SELECT normalized_status, COUNT(*) as cnt 
        FROM platform_invocations 
        GROUP BY normalized_status
    """)
    by_status = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 按能力统计
    cursor.execute("""
        SELECT capability, COUNT(*) as cnt 
        FROM platform_invocations 
        GROUP BY capability
    """)
    by_capability = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total": total,
        "uncertain_count": uncertain_count,
        "confirmed_count": confirmed_count,
        "by_status": by_status,
        "by_capability": by_capability,
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"   汇总 JSON 已输出: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="预热平台调用审计台账")
    parser.add_argument("--preset", choices=["demo_standard"], default="demo_standard", help="预设数据集")
    parser.add_argument("--reset-before-seed", action="store_true", help="重置数据库后再预热")
    parser.add_argument("--output-summary-json", help="输出汇总 JSON 路径")
    
    args = parser.parse_args()
    
    # 重置数据库
    if args.reset_before_seed:
        reset_database()
    
    # 预热
    if args.preset == "demo_standard":
        seed_demo_standard()
    
    # 输出汇总
    if args.output_summary_json:
        output_summary_json(args.output_summary_json)


if __name__ == "__main__":
    main()
