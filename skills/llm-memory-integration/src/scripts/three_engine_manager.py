#!/usr/bin/env python3
"""
三引擎向量架构管理器
管理 sqlite-vec (主) + Qdrant (副) + TF-IDF (备份)
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# 添加 core 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

try:
    from sqlite_ext import connect, is_vec_available, get_vec_version
    USE_EXT = True
except ImportError:
    USE_EXT = False
    print("⚠️ sqlite_ext 模块不可用，使用标准 sqlite3")

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_TDai = Path.home() / ".openclaw" / "memory-tdai"
VECTORS_DB = MEMORY_TDai / "vectors.db"
QDRANT_STORAGE = Path.home() / ".openclaw" / "qdrant-storage"
TFIDF_STORAGE = Path.home() / ".openclaw" / "tfidf-storage"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

class ThreeEngineManager:
    """三引擎管理器"""
    
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
        return {}
    
    def check_sqlite_vec(self) -> dict:
        """检查 sqlite-vec 主引擎"""
        result = {"name": "sqlite-vec", "status": "unknown", "stats": {}}
        try:
            if VECTORS_DB.exists():
                if USE_EXT:
                    conn = connect(str(VECTORS_DB))
                else:
                    conn = sqlite3.connect(str(VECTORS_DB))
                
                cursor = conn.cursor()
                
                # 获取版本信息
                if is_vec_available():
                    result["version"] = get_vec_version()
                
                # 获取向量数量
                cursor.execute("SELECT COUNT(*) FROM l0_vec_rowids")
                l0_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM l1_vec_rowids")
                l1_count = cursor.fetchone()[0]
                
                result["status"] = "healthy"
                result["stats"] = {
                    "l0_vectors": l0_count,
                    "l1_vectors": l1_count,
                    "total_vectors": l0_count + l1_count,
                    "db_size_mb": round(VECTORS_DB.stat().st_size / (1024 * 1024), 2)
                }
                conn.close()
            else:
                result["status"] = "not_found"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        return result
    
    def check_qdrant(self) -> dict:
        """检查 Qdrant 副引擎"""
        result = {"name": "qdrant", "status": "unknown", "stats": {}}
        try:
            if QDRANT_STORAGE.exists():
                files = list(QDRANT_STORAGE.glob("**/*"))
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                result["status"] = "available"
                result["stats"] = {
                    "storage_path": str(QDRANT_STORAGE),
                    "file_count": len([f for f in files if f.is_file()]),
                    "total_size_mb": round(total_size / (1024 * 1024), 2)
                }
            else:
                QDRANT_STORAGE.mkdir(parents=True, exist_ok=True)
                result["status"] = "initialized"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        return result
    
    def check_tfidf(self) -> dict:
        """检查 TF-IDF 备份引擎"""
        result = {"name": "tfidf", "status": "unknown", "stats": {}}
        try:
            tfidf_db = TFIDF_STORAGE / "tfidf.db"
            if tfidf_db.exists():
                conn = sqlite3.connect(str(tfidf_db))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM vocabulary")
                vocab_count = cursor.fetchone()[0]
                
                conn.close()
                
                result["status"] = "healthy"
                result["stats"] = {
                    "documents": doc_count,
                    "vocabulary_size": vocab_count,
                    "db_size_kb": round(tfidf_db.stat().st_size / 1024, 2)
                }
                conn.close()
            else:
                result["status"] = "not_found"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        return result
    
    def get_status(self) -> dict:
        """获取三引擎状态"""
        return {
            "timestamp": datetime.now().isoformat(),
            "primary": self.check_sqlite_vec(),
            "secondary": self.check_qdrant(),
            "backup": self.check_tfidf()
        }
    
    def print_status(self):
        """打印状态报告"""
        status = self.get_status()
        
        print("=" * 60)
        print("   三引擎向量架构状态报告")
        print("=" * 60)
        print(f"检查时间: {status['timestamp']}")
        print()
        
        engines = [
            ("主引擎", status["primary"]),
            ("副引擎", status["secondary"]),
            ("备份引擎", status["backup"])
        ]
        
        for label, engine in engines:
            status_icon = "✅" if engine["status"] in ["healthy", "available", "initialized"] else "❌"
            print(f"{status_icon} {label}: {engine['name']} ({engine['status']})")
            if engine.get("stats"):
                for key, value in engine["stats"].items():
                    print(f"   - {key}: {value}")
            if engine.get("error"):
                print(f"   - 错误: {engine['error']}")
            print()
        
        # 计算整体健康度
        healthy_count = sum(1 for e in [status["primary"], status["secondary"], status["backup"]] 
                          if e["status"] in ["healthy", "available", "initialized"])
        
        print("-" * 60)
        print(f"整体健康度: {healthy_count}/3 引擎可用")
        
        if healthy_count == 3:
            print("状态: 🟢 全部正常")
        elif healthy_count >= 2:
            print("状态: 🟡 部分可用")
        else:
            print("状态: 🔴 需要修复")

def main():
    manager = ThreeEngineManager()
    manager.print_status()

if __name__ == "__main__":
    main()
