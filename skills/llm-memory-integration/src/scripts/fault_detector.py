#!/usr/bin/env python3
"""
故障检测脚本
自动检测系统故障并告警
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
WORKSPACE = Path.home() / ".openclaw" / "workspace"
LOG_FILE = WORKSPACE / "memory" / "fault_log.json"

class FaultDetector:
    """故障检测器"""
    
    def __init__(self):
        self.faults = []
    
    def check_database_connection(self):
        """检查数据库连接"""
        try:
            with sqlite3.connect(str(VECTORS_DB)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            self.faults.append({
                "type": "database_connection",
                "severity": "critical",
                "message": f"数据库连接失败: {e}",
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def check_database_integrity(self):
        """检查数据库完整性"""
        try:
            with sqlite3.connect(str(VECTORS_DB)) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
            
            if result != "ok":
                self.faults.append({
                    "type": "database_integrity",
                    "severity": "critical",
                    "message": f"数据库完整性问题: {result}",
                    "timestamp": datetime.now().isoformat()
                })
                return False
            return True
        except Exception as e:
            self.faults.append({
                "type": "database_integrity",
                "severity": "critical",
                "message": f"完整性检查失败: {e}",
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def check_vector_coverage(self):
        """检查向量覆盖率"""
        try:
            with sqlite3.connect(str(VECTORS_DB)) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM l0_conversations")
                l0_total = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM l0_vec_rowids")
                l0_vec = cursor.fetchone()[0]
            
            if l0_total > 0:
                coverage = l0_vec / l0_total
                if coverage < 0.8:
                    self.faults.append({
                        "type": "vector_coverage",
                        "severity": "warning",
                        "message": f"L0 向量覆盖率过低: {coverage*100:.1f}%",
                        "timestamp": datetime.now().isoformat()
                    })
                    return False
            return True
        except Exception as e:
            self.faults.append({
                "type": "vector_coverage",
                "severity": "warning",
                "message": f"覆盖率检查失败: {e}",
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def check_disk_space(self):
        """检查磁盘空间"""
        try:
            stat = os.statvfs(str(Path.home()))
            free_gb = stat.f_bavail * stat.f_frsize / (1024 * 1024 * 1024)
            
            if free_gb < 1:
                self.faults.append({
                    "type": "disk_space",
                    "severity": "critical",
                    "message": f"磁盘空间不足: {free_gb:.1f}GB",
                    "timestamp": datetime.now().isoformat()
                })
                return False
            elif free_gb < 5:
                self.faults.append({
                    "type": "disk_space",
                    "severity": "warning",
                    "message": f"磁盘空间较低: {free_gb:.1f}GB",
                    "timestamp": datetime.now().isoformat()
                })
            return True
        except Exception as e:
            self.faults.append({
                "type": "disk_space",
                "severity": "warning",
                "message": f"磁盘检查失败: {e}",
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    def run_checks(self):
        """运行所有检查"""
        self.check_database_connection()
        self.check_database_integrity()
        self.check_vector_coverage()
        self.check_disk_space()
        return self.faults
    
    def save_log(self):
        """保存故障日志"""
        if self.faults:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取现有日志
            if LOG_FILE.exists():
                logs = json.loads(LOG_FILE.read_text())
            else:
                logs = []
            
            # 添加新故障
            logs.extend(self.faults)
            
            # 保留最近100条
            if len(logs) > 100:
                logs = logs[-100:]
            
            LOG_FILE.write_text(json.dumps(logs, indent=2))
    
    def print_report(self):
        """打印故障报告"""
        print("=" * 60)
        print("   故障检测报告")
        print("=" * 60)
        print(f"检测时间: {datetime.now().isoformat()}")
        print()
        
        if not self.faults:
            print("✅ 未检测到故障")
        else:
            critical = [f for f in self.faults if f["severity"] == "critical"]
            warning = [f for f in self.faults if f["severity"] == "warning"]
            
            if critical:
                print(f"🔴 严重故障 ({len(critical)}):")
                for f in critical:
                    print(f"   [{f['type']}] {f['message']}")
                print()
            
            if warning:
                print(f"🟡 警告 ({len(warning)}):")
                for f in warning:
                    print(f"   [{f['type']}] {f['message']}")
            
            print()
            print(f"总计: {len(self.faults)} 个问题")

def main():
    detector = FaultDetector()
    detector.run_checks()
    detector.save_log()
    detector.print_report()

if __name__ == "__main__":
    main()
