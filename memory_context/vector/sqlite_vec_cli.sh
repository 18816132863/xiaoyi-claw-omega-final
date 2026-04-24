#!/bin/bash
#
# SQLite-vec 命令行工具
# 终极鸽子王 V23.0 - 向量极致层
#
# 用法:
#   ./sqlite_vec_cli.sh init <db_path>              # 初始化数据库
#   ./sqlite_vec_cli.sh insert <db_path> <id> <text> # 插入向量
#   ./sqlite_vec_cli.sh search <db_path> <query>    # 搜索向量
#   ./sqlite_vec_cli.sh list <db_path>              # 列出所有向量
#   ./sqlite_vec_cli.sh count <db_path>             # 统计向量数量
#   ./sqlite_vec_cli.sh delete <db_path> <id>       # 删除向量
#   ./sqlite_vec_cli.sh clear <db_path>             # 清空数据库
#

set -e

VEC0_SO="$WORKSPACE/repo/lib/python3.12/site-packages/sqlite_vec/vec0.so"
DIMENSION=1024
TABLE_NAME="embeddings"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 检查 vec0 扩展
check_vec0() {
    if [ ! -f "$VEC0_SO" ]; then
        log_error "vec0.so not found at $VEC0_SO"
        exit 1
    fi
}

# 初始化数据库
init_db() {
    local db_path="$1"
    check_vec0
    
    python3 << EOF
from pysqlite3 import dbapi2 as sqlite3

conn = sqlite3.connect("$db_path")
conn.enable_load_extension(True)
conn.load_extension("$VEC0_SO")

conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS $TABLE_NAME 
    USING vec0(
        id TEXT PRIMARY KEY,
        embedding float[$DIMENSION],
        content TEXT,
        metadata TEXT,
        created_at TEXT
    )
""")

conn.execute("""
    CREATE TABLE IF NOT EXISTS _vec_metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    )
""")

conn.commit()
conn.close()
print("✅ Database initialized: $db_path")
EOF
}

# 插入向量
insert_vec() {
    local db_path="$1"
    local id="$2"
    local text="$3"
    
    python3 << EOF
import json
from pysqlite3 import dbapi2 as sqlite3
from datetime import datetime, timezone
import hashlib

# 简单的本地向量生成 (实际使用时替换为 Qwen Embedding)
# 简单的本地向量生成 (实际使用时替换为 Qwen Embedding)
def get_embedding(text, dim=$DIMENSION):
    # 生成足够长的哈希
    h = hashlib.sha512(text.encode()).digest()
    while len(h) < dim:
        h = h + hashlib.sha512(h).digest()
    vec = [float(b) / 255.0 for b in h[:dim]]
    norm = sum(v * v for v in vec) ** 0.5
    return [v / norm for v in vec] if norm > 0 else vec

conn = sqlite3.connect("$db_path")
conn.enable_load_extension(True)
conn.load_extension("$VEC0_SO")

embedding = get_embedding("$text")

conn.execute(
    "INSERT OR REPLACE INTO $TABLE_NAME (id, embedding, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
    ("$id", json.dumps(embedding), "$text", "{}", datetime.now(timezone.utc).isoformat())
)

conn.commit()
conn.close()
print("✅ Inserted: $id")
EOF
}

# 搜索向量
search_vec() {
    local db_path="$1"
    local query="$2"
    local top_k="${3:-10}"
    
    python3 << EOF
import json
import hashlib
from pysqlite3 import dbapi2 as sqlite3
def get_embedding(text, dim=$DIMENSION):
    h = hashlib.sha512(text.encode()).digest()
    while len(h) < dim:
        h = h + hashlib.sha512(h).digest()
    vec = [float(b) / 255.0 for b in h[:dim]]
    norm = sum(v * v for v in vec) ** 0.5
    return [v / norm for v in vec] if norm > 0 else vec
    norm = sum(v * v for v in vec) ** 0.5
    return [v / norm for v in vec] if norm > 0 else vec

conn = sqlite3.connect("$db_path")
conn.enable_load_extension(True)
conn.load_extension("$VEC0_SO")

query_embedding = get_embedding("$query")

rows = conn.execute(
    "SELECT id, content, distance FROM $TABLE_NAME WHERE embedding MATCH ? ORDER BY distance LIMIT $top_k",
    (json.dumps(query_embedding),)
).fetchall()

print(f"🔍 Search results for: $query")
print("-" * 60)
for row in rows:
    score = 1.0 - row[2]
    print(f"  [{score:.3f}] {row[0]}: {row[1][:50]}...")

conn.close()
EOF
}

# 列出所有向量
list_vec() {
    local db_path="$1"
    
    python3 << EOF
from pysqlite3 import dbapi2 as sqlite3

conn = sqlite3.connect("$db_path")
conn.enable_load_extension(True)
conn.load_extension("$VEC0_SO")

rows = conn.execute("SELECT id, content, created_at FROM $TABLE_NAME").fetchall()

print(f"📋 Vectors in database: {len(rows)}")
print("-" * 60)
for row in rows:
    print(f"  {row[0]}: {row[1][:40]}... ({row[2]})")

conn.close()
EOF
}

# 统计向量数量
count_vec() {
    local db_path="$1"
    
    python3 << EOF
from pysqlite3 import dbapi2 as sqlite3

conn = sqlite3.connect("$db_path")
conn.enable_load_extension(True)
conn.load_extension("$VEC0_SO")

count = conn.execute("SELECT COUNT(*) FROM $TABLE_NAME").fetchone()[0]
print(f"📊 Vector count: {count}")

conn.close()
EOF
}

# 删除向量
delete_vec() {
    local db_path="$1"
    local id="$2"
    
    python3 << EOF
from pysqlite3 import dbapi2 as sqlite3

conn = sqlite3.connect("$db_path")
conn.enable_load_extension(True)
conn.load_extension("$VEC0_SO")

conn.execute("DELETE FROM $TABLE_NAME WHERE id = ?", ("$id",))
conn.commit()

print("✅ Deleted: $id")

conn.close()
EOF
}

# 清空数据库
clear_db() {
    local db_path="$1"
    
    python3 << EOF
from pysqlite3 import dbapi2 as sqlite3

conn = sqlite3.connect("$db_path")
conn.enable_load_extension(True)
conn.load_extension("$VEC0_SO")

conn.execute("DELETE FROM $TABLE_NAME")
conn.commit()

print("✅ Database cleared")

conn.close()
EOF
}

# 主命令
case "$1" in
    init)
        init_db "$2"
        ;;
    insert)
        insert_vec "$2" "$3" "$4"
        ;;
    search)
        search_vec "$2" "$3" "$4"
        ;;
    list)
        list_vec "$2"
        ;;
    count)
        count_vec "$2"
        ;;
    delete)
        delete_vec "$2" "$3"
        ;;
    clear)
        clear_db "$2"
        ;;
    *)
        echo "SQLite-vec CLI - 终极鸽子王 V23.0"
        echo ""
        echo "用法:"
        echo "  $0 init <db_path>              初始化数据库"
        echo "  $0 insert <db_path> <id> <text> 插入向量"
        echo "  $0 search <db_path> <query> [k] 搜索向量"
        echo "  $0 list <db_path>              列出所有向量"
        echo "  $0 count <db_path>             统计向量数量"
        echo "  $0 delete <db_path> <id>       删除向量"
        echo "  $0 clear <db_path>             清空数据库"
        ;;
esac
