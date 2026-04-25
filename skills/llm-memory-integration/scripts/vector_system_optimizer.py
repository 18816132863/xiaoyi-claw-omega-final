#!/usr/bin/env python3
"""向量系统优化 - 自动优化向量索引、清理孤立向量、重建索引（安全修复版）"""
import sqlite3
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
from paths import VEC_EXT
CONFIG_FILE = Path.home() / ".openclaw" / "skills" / "llm-memory-integration" / "config" / "vector_optimize.json"
LOG_FILE = Path.home() / ".openclaw" / "memory-tdai" / ".metadata" / "vector_optimize.log"

# 默认配置
DEFAULT_CONFIG = {
    "optimize_interval": 604800,     # 优化间隔（秒）- 7天
    "max_db_size_mb": 100,           # 最大数据库大小（MB）
    "orphan_threshold": 10,          # 孤立向量阈值
    "auto_vacuum": True,             # 自动 VACUUM
    "auto_reindex": True,            # 自动重建索引
    "auto_cleanup_orphans": True,    # 自动清理孤立向量
    "backup_before_optimize": True   # 优化前备份
}

class VectorSystemOptimizer:
    def __init__(self):
        self.db_path = VECTORS_DB
        self.vec_ext = VEC_EXT
        self.log_file = LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except:
                pass
        return DEFAULT_CONFIG
    
    def _save_config(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.config, ensure_ascii=False, indent=2))
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(message)
    
    def get_db_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        return conn
    
    def get_db_stats(self) -> Dict:
        """获取数据库统计"""
        # 数据库大小
        db_size_mb = self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
        
        stats = {"db_size_mb": round(db_size_mb, 2)}
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 查询各表记录数
            tables = ['l1_records', 'l1_vec', 'l0_conversations', 'l0_vec', 'l1_fts']
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                except:
                    stats[table] = 0
            
            conn.close()
        except Exception as e:
            self.log(f"❌ 获取统计失败: {e}")
        
        return stats
    
    def check_orphans(self) -> Dict:
        """检查孤立向量"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # L1 孤立向量
            cursor.execute("""
                SELECT COUNT(*) FROM l1_vec v
                LEFT JOIN l1_records r ON v.record_id = r.record_id
                WHERE r.record_id IS NULL
            """)
            l1_orphans = cursor.fetchone()[0]
            
            # L0 孤立向量
            cursor.execute("""
                SELECT COUNT(*) FROM l0_vec v
                LEFT JOIN l0_conversations c ON v.message_id = c.message_id
                WHERE c.message_id IS NULL
            """)
            l0_orphans = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "l1_orphans": l1_orphans,
                "l0_orphans": l0_orphans,
                "total_orphans": l1_orphans + l0_orphans
            }
        except Exception as e:
            self.log(f"❌ 检查孤立向量失败: {e}")
            return {"l1_orphans": 0, "l0_orphans": 0, "total_orphans": 0}
    
    def cleanup_orphans(self) -> int:
        """清理孤立向量"""
        self.log("🗑️ 开始清理孤立向量...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 清理 L1 孤立向量
            cursor.execute("""
                DELETE FROM l1_vec WHERE record_id IN (
                    SELECT v.record_id FROM l1_vec v
                    LEFT JOIN l1_records r ON v.record_id = r.record_id
                    WHERE r.record_id IS NULL
                )
            """)
            l1_deleted = cursor.rowcount
            
            # 清理 L0 孤立向量
            cursor.execute("""
                DELETE FROM l0_vec WHERE message_id IN (
                    SELECT v.message_id FROM l0_vec v
                    LEFT JOIN l0_conversations c ON v.message_id = c.message_id
                    WHERE c.message_id IS NULL
                )
            """)
            l0_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            total = l1_deleted + l0_deleted
            self.log(f"✅ 清理完成: L1 {l1_deleted} 条, L0 {l0_deleted} 条, 共 {total} 条")
            return total
        except Exception as e:
            self.log(f"❌ 清理孤立向量失败: {e}")
            return 0
    
    def vacuum(self):
        """VACUUM 数据库"""
        self.log("🔄 开始 VACUUM...")
        
        try:
            # 备份
            if self.config["backup_before_optimize"]:
                backup_path = self.db_path.with_suffix(f".db.backup_{datetime.now().strftime('%Y%m%d')}")
                shutil.copy2(self.db_path, backup_path)
                self.log(f"✅ 备份到: {backup_path}")
            
            # VACUUM
            conn = self.get_db_connection()
            conn.execute("VACUUM")
            conn.close()
            
            new_size = self.db_path.stat().st_size / (1024 * 1024)
            self.log(f"✅ VACUUM 完成，新大小: {new_size:.2f} MB")
        except Exception as e:
            self.log(f"❌ VACUUM 失败: {e}")
    
    def reindex_fts(self):
        """重建 FTS 索引"""
        self.log("🔄 开始重建 FTS 索引...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # 删除旧索引
            cursor.execute("DROP TABLE IF EXISTS l1_fts;")
            
            # 创建新索引
            cursor.execute("""
                CREATE VIRTUAL TABLE l1_fts USING fts5(
                    record_id,
                    content,
                    type,
                    scene_name,
                    content='l1_records',
                    content_rowid='rowid'
                );
            """)
            
            # 重建
            cursor.execute("INSERT INTO l1_fts(l1_fts) VALUES('rebuild');")
            
            conn.commit()
            conn.close()
            
            self.log("✅ FTS 索引重建完成")
        except Exception as e:
            self.log(f"❌ FTS 索引重建失败: {e}")
    
    def optimize(self):
        """完整优化"""
        self.log("=" * 60)
        self.log("🚀 开始向量系统优化")
        self.log("=" * 60)
        
        # 1. 获取统计
        stats = self.get_db_stats()
        self.log(f"📊 数据库大小: {stats.get('db_size_mb', 0):.2f} MB")
        self.log(f"📊 L1 记录: {stats.get('l1_records', 0)} 条")
        self.log(f"📊 L0 记录: {stats.get('l0_conversations', 0)} 条")
        
        # 2. 检查孤立向量
        orphans = self.check_orphans()
        self.log(f"🔍 孤立向量: L1 {orphans['l1_orphans']} 条, L0 {orphans['l0_orphans']} 条")
        
        # 3. 清理孤立向量
        if orphans['total_orphans'] > self.config['orphan_threshold']:
            self.cleanup_orphans()
        
        # 4. VACUUM
        if self.config['auto_vacuum'] and stats.get('db_size_mb', 0) > self.config['max_db_size_mb']:
            self.vacuum()
        
        # 5. 重建 FTS
        if self.config['auto_reindex']:
            self.reindex_fts()
        
        self.log("=" * 60)
        self.log("✅ 向量系统优化完成")
        self.log("=" * 60)

def main():
    optimizer = VectorSystemOptimizer()
    optimizer.optimize()

if __name__ == "__main__":
    main()
