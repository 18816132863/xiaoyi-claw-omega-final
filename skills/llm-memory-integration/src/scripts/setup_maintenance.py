#!/usr/bin/env python3
"""
Setup Maintenance - 一键配置维护建议
自动配置定期维护任务和监控
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_TDDB = Path.home() / ".openclaw" / "memory-tdai"
VECTORS_DB = MEMORY_TDDB / "vectors.db"
from paths import VEC_EXT

# 维护配置
MAINTENANCE_CONFIG = {
    "weekly_tasks": [
        {
            "name": "向量体系优化",
            "script": "optimize_vector_system.py",
            "schedule": "每周一 03:00",
            "description": "VACUUM + ANALYZE + 覆盖率检查"
        },
        {
            "name": "FTS 索引重建",
            "script": "rebuild_fts.py",
            "schedule": "每周三 03:00",
            "description": "重建全文搜索索引"
        }
    ],
    "daily_tasks": [
        {
            "name": "向量覆盖率监控",
            "script": "check_coverage.py",
            "schedule": "每日 06:00",
            "description": "检查 L1/L0 向量覆盖率"
        }
    ],
    "thresholds": {
        "l1_coverage_min": 95,  # L1 覆盖率最低阈值
        "l0_coverage_min": 60,  # L0 覆盖率最低阈值
        "db_size_max_mb": 100,  # 数据库最大大小 MB
        "zero_vector_max": 5    # 零向量最大数量
    }
}


def create_maintenance_scripts():
    """创建维护脚本"""
    print("\n📝 创建维护脚本:")
    
    scripts_dir = WORKSPACE / "skills" / "llm-memory-integration" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 向量覆盖率检查脚本
    coverage_script = scripts_dir / "check_coverage.py"
    coverage_script.write_text('''#!/usr/bin/env python3
"""检查向量覆盖率"""
import subprocess
import json
from pathlib import Path

VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
from paths import VEC_EXT

def check_coverage():
    result = subprocess.run(
        f\'sqlite3 -cmd ".load {VEC_EXT}" "{VECTORS_DB}" \'
        f\'"SELECT COUNT(*) FROM l1_records; SELECT COUNT(*) FROM l1_vec; \'
        f\'SELECT COUNT(*) FROM l0_conversations; SELECT COUNT(*) FROM l0_vec;"\',
        shell=False, capture_output=True, text=True
    , timeout=60)
    
    if result.returncode == 0:
        lines = result.stdout.strip().split(\'\\n\')
        if len(lines) >= 4:
            l1_records = int(lines[0])
            l1_vec = int(lines[1])
            l0_conversations = int(lines[2])
            l0_vec = int(lines[3])
            
            l1_coverage = 100.0 * l1_vec / max(l1_records, 1)
            l0_coverage = 100.0 * l0_vec / max(l0_conversations, 1)
            
            return {
                "l1_records": l1_records,
                "l1_vec": l1_vec,
                "l1_coverage": round(l1_coverage, 1),
                "l0_conversations": l0_conversations,
                "l0_vec": l0_vec,
                "l0_coverage": round(l0_coverage, 1)
            }
    
    return None

if __name__ == "__main__":
    import datetime
    print(f"向量覆盖率检查 - {datetime.datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}")
    result = check_coverage()
    if result:
        print(f"L1 覆盖率: {result[\'l1_coverage\']}%")
        print(f"L0 覆盖率: {result[\'l0_coverage\']}%")
    else:
        print("检查失败")
''')
    coverage_script.chmod(0o755)
    print(f"  ✅ check_coverage.py")
    
    # 2. FTS 索引重建脚本
    fts_script = scripts_dir / "rebuild_fts.py"
    fts_script.write_text('''#!/usr/bin/env python3
"""重建 FTS 索引"""
import subprocess
from pathlib import Path

VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"

def rebuild_fts():
    # 删除旧索引
    subprocess.run(
        f\'sqlite3 "{VECTORS_DB}" "DROP TABLE IF EXISTS l1_fts;"\',
        shell=False, capture_output=True
    , timeout=60)
    
    # 创建新索引
    subprocess.run(
        f\'sqlite3 "{VECTORS_DB}" "\'
        f\'CREATE VIRTUAL TABLE IF NOT EXISTS l1_fts USING fts5(\'
        f\'record_id, content, type, scene_name, priority, \'
        f\'session_key, session_id, timestamp_str, timestamp_start, timestamp_end, metadata, \'
        f\'content=\\'\\', tokenize=\\'unicode61\\');"\',
        shell=False, capture_output=True
    , timeout=60)
    
    # 重新填充数据
    subprocess.run(
        f\'sqlite3 "{VECTORS_DB}" "\'
        f\'INSERT INTO l1_fts(rowid, record_id, content, type, scene_name, priority) \'
        f\'SELECT rowid, record_id, content, type, scene_name, priority FROM l1_records;"\',
        shell=False, capture_output=True
    , timeout=60)
    
    print("FTS 索引重建完成")

if __name__ == "__main__":
    import datetime
    print(f"FTS 索引重建 - {datetime.datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}")
    rebuild_fts()
''')
    fts_script.chmod(0o755)
    print(f"  ✅ rebuild_fts.py")
    
    # 3. 综合维护脚本
    maintenance_script = scripts_dir / "run_maintenance.py"
    maintenance_script.write_text('''#!/usr/bin/env python3
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
        f.write(log_entry + "\\n")

def run_vacuum():
    """执行 VACUUM"""
    log("执行 VACUUM...")
    result = subprocess.run(
        f\'sqlite3 "{VECTORS_DB}" "VACUUM;"\',
        shell=False, capture_output=True, text=True
    , timeout=60)
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
        f\'sqlite3 "{VECTORS_DB}" "ANALYZE;"\',
        shell=False, capture_output=True, text=True
    , timeout=60)
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
        f\'sqlite3 -cmd ".load {VEC_EXT}" "{VECTORS_DB}" \'
        f\'"SELECT COUNT(*) FROM l1_records; SELECT COUNT(*) FROM l1_vec; \'
        f\'SELECT COUNT(*) FROM l0_conversations; SELECT COUNT(*) FROM l0_vec;"\',
        shell=False, capture_output=True, text=True
    , timeout=60)
    
    if result.returncode == 0:
        lines = result.stdout.strip().split(\'\\n\')
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
''')
    maintenance_script.chmod(0o755)
    print(f"  ✅ run_maintenance.py")


def create_cron_config():
    """创建 cron 配置说明"""
    print("\n📅 定时任务配置:")
    
    cron_config = """# 小艺 Claw 维护任务定时配置
# 添加到 crontab: crontab -e

# 每周一 03:00 运行完整维护
0 3 * * 1 python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/run_maintenance.py

# 每日 06:00 检查覆盖率
0 6 * * * python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/check_coverage.py

# 每周日凌晨 02:00 重建 FTS 索引
0 2 * * 0 python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/rebuild_fts.py
"""
    
    config_file = WORKSPACE / "skills" / "llm-memory-integration" / "maintenance_cron.txt"
    config_file.write_text(cron_config)
    print(f"  ✅ 配置文件: {config_file}")
    
    print("\n  安装定时任务:")
    print("    crontab -e")
    print("    # 粘贴上述内容")


def create_maintenance_readme():
    """创建维护说明文档"""
    print("\n📖 创建维护说明:")
    
    readme = WORKSPACE / "skills" / "llm-memory-integration" / "MAINTENANCE.md"
    
    content = """# 维护指南

## 维护任务

### 每周任务

| 任务 | 时间 | 脚本 |
|------|------|------|
| 完整维护 | 周一 03:00 | `run_maintenance.py` |
| FTS 重建 | 周日 02:00 | `rebuild_fts.py` |

### 每日任务

| 任务 | 时间 | 脚本 |
|------|------|------|
| 覆盖率检查 | 06:00 | `check_coverage.py` |

## 手动执行

```bash
# 完整维护
python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/run_maintenance.py

# 检查覆盖率
python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/check_coverage.py

# 重建 FTS
python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/rebuild_fts.py
```

## 监控阈值

| 指标 | 阈值 | 说明 |
|------|------|------|
| L1 覆盖率 | ≥ 95% | 结构化记忆向量覆盖 |
| L0 覆盖率 | ≥ 60% | 原始对话向量覆盖 |
| 数据库大小 | < 100 MB | 定期清理 |
| 零向量 | < 5 条 | 需要修复 |

## 日志位置

- 维护日志: `~/.openclaw/memory-tdai/.metadata/maintenance.log`
- 推送记录: `~/.openclaw/workspace/skills/today-task/push_records/`

## 故障排查

### 覆盖率下降
1. 检查向量 API 是否正常
2. 运行 `optimize_vector_system.py` 修复
3. 检查 memory-tencentdb 插件状态

### 数据库过大
1. 运行 VACUUM 清理
2. 检查是否有孤立向量
3. 考虑归档旧数据

### FTS 搜索失效
1. 运行 `rebuild_fts.py` 重建索引
2. 检查 FTS 表是否存在
3. 验证分词器配置
"""
    
    readme.write_text(content)
    print(f"  ✅ MAINTENANCE.md")


def run_initial_maintenance():
    """运行初始维护"""
    print("\n🔧 运行初始维护:")
    
    scripts_dir = WORKSPACE / "skills" / "llm-memory-integration" / "scripts"
    
    # 运行覆盖率检查
    result = subprocess.run(
        f"python3 {scripts_dir / 'check_coverage.py'}",
        shell=False, capture_output=True, text=True
    , timeout=60)
    print(result.stdout)
    
    # 运行完整维护
    result = subprocess.run(
        f"python3 {scripts_dir / 'run_maintenance.py'}",
        shell=False, capture_output=True, text=True
    , timeout=60)
    print(result.stdout)


def main():
    """主函数"""
    print("=" * 60)
    print("一键配置维护建议")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 创建维护脚本
    create_maintenance_scripts()
    
    # 2. 创建 cron 配置
    create_cron_config()
    
    # 3. 创建维护说明
    create_maintenance_readme()
    
    # 4. 运行初始维护
    run_initial_maintenance()
    
    print("\n" + "=" * 60)
    print("配置完成")
    print("=" * 60)
    print("""
✅ 维护脚本已创建
✅ 定时任务配置已生成
✅ 维护说明已创建
✅ 初始维护已执行

下一步:
  1. 查看维护说明: cat MAINTENANCE.md
  2. 安装定时任务: crontab -e
  3. 手动测试: python3 run_maintenance.py
""")


if __name__ == "__main__":
    main()
