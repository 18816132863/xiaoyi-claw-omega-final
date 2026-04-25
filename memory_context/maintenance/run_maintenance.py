#!/usr/bin/env python3
"""运行所有维护任务"""
import subprocess
import json
from pathlib import Path
from datetime import datetime

VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
from paths import VEC_EXT
LOG_FILE = Path.home() / ".openclaw" / "memory-tdai" / ".metadata" / "maintenance.log"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def run_vacuum():
    """执行 VACUUM"""
    log("执行 VACUUM...")
    result = subprocess.run(
        ["sqlite3", str(VECTORS_DB), "VACUUM;"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        log("VACUUM 完成")
        return True
    else:
        log(f"VACUUM 失败: {result.stderr}")
        return False

def run_analyze():
    """执行 ANALYZE"""
    log("执行 ANALYZE...")
    result = subprocess.run(
        ["sqlite3", str(VECTORS_DB), "ANALYZE;"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        log("ANALYZE 完成")
        return True
    else:
        log(f"ANALYZE 失败: {result.stderr}")
        return False

def check_coverage():
    """检查覆盖率"""
    log("检查向量覆盖率...")
    result = subprocess.run(
        ["sqlite3", "-cmd", f".load {VEC_EXT}", str(VECTORS_DB),
         "SELECT COUNT(*) FROM l1_records; SELECT COUNT(*) FROM l1_vec; "
         "SELECT COUNT(*) FROM l0_conversations; SELECT COUNT(*) FROM l0_vec;"],
        capture_output=True, text=True, timeout=60
    )
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 4:
            l1_records = int(lines[0])
            l1_vec = int(lines[1])
            l0_conversations = int(lines[2])
            l0_vec = int(lines[3])
            
            l1_coverage = 100.0 * l1_vec / max(l1_records, 1)
            l0_coverage = 100.0 * l0_vec / max(l0_conversations, 1)
            
            log(f"L1 覆盖率: {l1_coverage:.1f}% ({l1_vec}/{l1_records})")
            log(f"L0 覆盖率: {l0_coverage:.1f}% ({l0_vec}/{l0_conversations})")
            
            return {
                "l1_coverage": l1_coverage,
                "l0_coverage": l0_coverage
            }
    
    log("覆盖率检查失败")
    return None

def check_db_size():
    """检查数据库大小"""
    size_mb = VECTORS_DB.stat().st_size / (1024 * 1024)
    log(f"数据库大小: {size_mb:.2f} MB")
    return size_mb

def main():
    """主函数"""
    log("=" * 50)
    log("开始维护任务")
    log("=" * 50)
    
    # 1. VACUUM
    run_vacuum()
    
    # 2. ANALYZE
    run_analyze()
    
    # 3. 覆盖率检查
    coverage = check_coverage()
    
    # 4. 数据库大小
    size = check_db_size()
    
    # 5. 总结
    log("=" * 50)
    log("维护任务完成")
    
    if coverage:
        status = "✅ 正常"
        if coverage["l1_coverage"] < 95:
            status = "⚠️ L1 覆盖率偏低"
        elif coverage["l0_coverage"] < 60:
            status = "⚠️ L0 覆盖率偏低"
        log(f"状态: {status}")
    
    log("=" * 50)

if __name__ == "__main__":
    main()
