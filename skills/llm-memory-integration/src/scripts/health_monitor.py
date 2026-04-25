#!/usr/bin/env python3
"""
健康监控脚本
检查系统各组件健康状态
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# 路径配置
MEMORY_TDai = Path.home() / ".openclaw" / "memory-tdai"
VECTORS_DB = MEMORY_TDai / "vectors.db"
TFIDF_DB = Path.home() / ".openclaw" / "tfidf-storage" / "tfidf.db"
QDRANT_STORAGE = Path.home() / ".openclaw" / "qdrant-storage"
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

class HealthMonitor:
    """健康监控器"""
    
    def __init__(self):
        self.results = {}
    
    def check_database(self):
        """检查数据库健康"""
        result = {"status": "unknown", "details": {}}
        try:
            if VECTORS_DB.exists():
                conn = sqlite3.connect(str(VECTORS_DB))
                cursor = conn.cursor()
                
                # 检查表完整性
                cursor.execute("PRAGMA integrity_check")
                integrity = cursor.fetchone()[0]
                
                # 获取统计
                cursor.execute("SELECT COUNT(*) FROM l0_conversations")
                l0_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM l0_vec_rowids")
                l0_vec = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM l1_records")
                l1_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM l1_vec_rowids")
                l1_vec = cursor.fetchone()[0]
                
                conn.close()
                
                result["status"] = "healthy" if integrity == "ok" else "warning"
                result["details"] = {
                    "integrity": integrity,
                    "l0_conversations": l0_count,
                    "l0_vectors": l0_vec,
                    "l0_coverage": f"{l0_vec * 100 // max(l0_count, 1)}%",
                    "l1_records": l1_count,
                    "l1_vectors": l1_vec,
                    "l1_coverage": f"{l1_vec * 100 // max(l1_count, 1)}%",
                    "size_mb": round(VECTORS_DB.stat().st_size / 1024 / 1024, 2)
                }
            else:
                result["status"] = "error"
                result["details"]["error"] = "Database not found"
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
        
        return result
    
    def check_tfidf(self):
        """检查 TF-IDF 引擎"""
        result = {"status": "unknown", "details": {}}
        try:
            if TFIDF_DB.exists():
                conn = sqlite3.connect(str(TFIDF_DB))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM documents")
                doc_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM vocabulary")
                vocab_count = cursor.fetchone()[0]
                
                conn.close()
                
                result["status"] = "healthy"
                result["details"] = {
                    "documents": doc_count,
                    "vocabulary": vocab_count,
                    "size_kb": round(TFIDF_DB.stat().st_size / 1024, 2)
                }
            else:
                result["status"] = "warning"
                result["details"]["error"] = "TF-IDF database not found"
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
        
        return result
    
    def check_qdrant(self):
        """检查 Qdrant 引擎"""
        result = {"status": "unknown", "details": {}}
        try:
            if QDRANT_STORAGE.exists():
                sync_file = QDRANT_STORAGE / "sync_status.json"
                if sync_file.exists():
                    sync = json.loads(sync_file.read_text())
                    result["status"] = "available"
                    result["details"] = {
                        "sync_status": sync.get("status", "unknown"),
                        "l0_vectors": sync.get("l0_vectors", 0),
                        "l1_vectors": sync.get("l1_vectors", 0),
                        "last_sync": sync.get("synced_at", "never")
                    }
                else:
                    result["status"] = "warning"
                    result["details"]["error"] = "Sync status not found"
            else:
                result["status"] = "error"
                result["details"]["error"] = "Qdrant storage not found"
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
        
        return result
    
    def check_config(self):
        """检查配置文件"""
        result = {"status": "unknown", "details": {}}
        try:
            if CONFIG_PATH.exists():
                config = json.loads(CONFIG_PATH.read_text())
                plugins = config.get("plugins", {}).get("entries", {})
                
                result["status"] = "healthy"
                result["details"] = {
                    "memory_tencentdb": plugins.get("memory-tencentdb", {}).get("enabled", False),
                    "xiaoyi_channel": plugins.get("xiaoyi-channel", {}).get("enabled", False),
                    "heartbeat": config.get("heartbeat", {}).get("every", "disabled")
                }
            else:
                result["status"] = "error"
                result["details"]["error"] = "Config not found"
        except Exception as e:
            result["status"] = "error"
            result["details"]["error"] = str(e)
        
        return result
    
    def run_checks(self):
        """运行所有检查"""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "database": self.check_database(),
            "tfidf": self.check_tfidf(),
            "qdrant": self.check_qdrant(),
            "config": self.check_config()
        }
        return self.results
    
    def print_report(self):
        """打印健康报告"""
        print("=" * 60)
        print("   AI 长时记忆系统健康报告")
        print("=" * 60)
        print(f"检查时间: {self.results['timestamp']}")
        print()
        
        components = [
            ("向量数据库", self.results["database"]),
            ("TF-IDF 引擎", self.results["tfidf"]),
            ("Qdrant 引擎", self.results["qdrant"]),
            ("配置文件", self.results["config"])
        ]
        
        healthy_count = 0
        for name, result in components:
            status = result["status"]
            icon = "✅" if status == "healthy" else "⚠️" if status in ["warning", "available"] else "❌"
            print(f"{icon} {name}: {status}")
            if result.get("details"):
                for key, value in result["details"].items():
                    print(f"   - {key}: {value}")
            print()
            
            if status in ["healthy", "available"]:
                healthy_count += 1
        
        print("-" * 60)
        print(f"健康度: {healthy_count}/{len(components)}")
        
        if healthy_count == len(components):
            print("状态: 🟢 全部健康")
        elif healthy_count >= len(components) * 0.7:
            print("状态: 🟡 部分警告")
        else:
            print("状态: 🔴 需要修复")

def main():
    monitor = HealthMonitor()
    monitor.run_checks()
    monitor.print_report()

if __name__ == "__main__":
    main()
