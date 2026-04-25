#!/usr/bin/env python3
"""向量覆盖率监控 - 自动检查 + 告警 + 自动修复"""
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
from paths import VEC_EXT
LOG_FILE = Path.home() / ".openclaw" / "memory-tdai" / ".metadata" / "coverage_monitor.log"
CONFIG_FILE = Path.home() / ".openclaw" / "skills" / "llm-memory-integration" / "config" / "coverage_thresholds.json"

# 默认阈值
DEFAULT_THRESHOLDS = {
    "l1_min_coverage": 95.0,  # L1 最低覆盖率
    "l0_min_coverage": 60.0,  # L0 最低覆盖率
    "check_interval": 3600,   # 检查间隔（秒）
    "auto_fix": False,        # 🔒 安全修复：默认禁用自动修复
    "alert_on_low": True,     # 低覆盖率告警
    "_comment": "⚠️ auto_fix 默认禁用，需用户手动触发"
}

class CoverageMonitor:
    def __init__(self):
        self.db_path = VECTORS_DB
        self.vec_ext = VEC_EXT
        self.log_file = LOG_FILE
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text())
            except Exception as e:
                pass
            logger.error(f"操作失败: {e}")
        return DEFAULT_THRESHOLDS
    
    def _save_config(self):
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self.config, ensure_ascii=False, indent=2))
    
    def check_coverage(self):
        """检查向量覆盖率"""
        result = subprocess.run(
            f'sqlite3 -cmd ".load {self.vec_ext}" "{self.db_path}" '
            f'"SELECT COUNT(*) FROM l1_records; SELECT COUNT(*) FROM l1_vec; '
            f'SELECT COUNT(*) FROM l0_conversations; SELECT COUNT(*) FROM l0_vec;"',
            shell=False, capture_output=True, text=True, timeout=10
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
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "l1_records": l1_records,
                    "l1_vec": l1_vec,
                    "l1_coverage": round(l1_coverage, 2),
                    "l0_conversations": l0_conversations,
                    "l0_vec": l0_vec,
                    "l0_coverage": round(l0_coverage, 2),
                    "status": "ok" if l1_coverage >= self.config["l1_min_coverage"] and l0_coverage >= self.config["l0_min_coverage"] else "low"
                }
        
        return {"status": "error", "message": result.stderr}
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def alert(self, coverage_data):
        """低覆盖率告警"""
        if coverage_data["status"] == "low":
            l1_gap = self.config["l1_min_coverage"] - coverage_data["l1_coverage"]
            l0_gap = self.config["l0_min_coverage"] - coverage_data["l0_coverage"]
            
            message = f"⚠️ 覆盖率告警: L1={coverage_data['l1_coverage']}% (缺口{l1_gap:.1f}%), L0={coverage_data['l0_coverage']}% (缺口{l0_gap:.1f}%)"
            self.log(message)
            print(message)
            
            if self.config["auto_fix"]:
                self.auto_fix(coverage_data)
    
    def auto_fix(self, coverage_data):
        """自动修复低覆盖率"""
        # 🔒 安全修复：检查是否启用自动修复
        if not self.config.get("auto_fix", False):
            self.log("⚠️ 自动修复已禁用，请手动运行: vector_coverage_monitor.py fix")
            print("⚠️ 自动修复已禁用，请手动运行: python3 vector_coverage_monitor.py fix")
            return
        
        self.log("🔧 启动自动修复...")
        
        # 检查缺失向量
        if coverage_data["l1_coverage"] < self.config["l1_min_coverage"]:
            missing = coverage_data["l1_records"] - coverage_data["l1_vec"]
            self.log(f"L1 缺失 {missing} 条向量，尝试补填...")
            
            # 调用补填脚本
            try:
                result = subprocess.run(
                    f"python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/backfill_l0_vectors.py --l1", shell=False, capture_output=True, text=True, timeout=300
                )  # SECURITY FIX: shell=False removed
                if result.returncode == 0:
                    self.log("✅ L1 向量补填完成")
                else:
                    self.log(f"❌ L1 向量补填失败: {result.stderr}")
            except Exception as e:
                self.log(f"❌ L1 向量补填异常: {e}")
        
        if coverage_data["l0_coverage"] < self.config["l0_min_coverage"]:
            missing = coverage_data["l0_conversations"] - coverage_data["l0_vec"]
            self.log(f"L0 缺失 {missing} 条向量，尝试补填...")
            
            try:
                result = subprocess.run(
                    f"python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/backfill_l0_vectors.py", shell=False, capture_output=True, text=True, timeout=600
                )  # SECURITY FIX: shell=False removed
                if result.returncode == 0:
                    self.log("✅ L0 向量补填完成")
                else:
                    self.log(f"❌ L0 向量补填失败: {result.stderr}")
            except Exception as e:
                self.log(f"❌ L0 向量补填异常: {e}")
    
    def run_daemon(self):
        """守护进程模式"""
        # 🔒 安全修复：警告守护进程风险
        print("⚠️ 警告：守护进程模式会持续运行，请确保：")
        print("  1. Embedding API 已正确配置")
        print("  2. auto_fix 已禁用（推荐）")
        print("  3. 了解守护进程的资源消耗")
        print()
        
        confirm = input("是否继续启动守护进程？(yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ 守护进程启动已取消")
            return
        
        self.log("📊 向量覆盖率监控启动")
        print(f"📊 向量覆盖率监控启动 (间隔: {self.config['check_interval']}秒)")
        
        while True:
            try:
                coverage = self.check_coverage()
                
                if coverage["status"] == "ok":
                    self.log(f"✅ 覆盖率正常: L1={coverage['l1_coverage']}%, L0={coverage['l0_coverage']}%")
                elif coverage["status"] == "low":
                    self.alert(coverage)
                else:
                    self.log(f"❌ 检查失败: {coverage.get('message', 'unknown')}")
                
                time.sleep(self.config["check_interval"])
            except KeyboardInterrupt:
                self.log("🛑 监控停止")
                break
            except Exception as e:
                self.log(f"❌ 异常: {e}")
                time.sleep(60)
    
    def show_status(self):
        """显示当前状态"""
        coverage = self.check_coverage()
        
        print("=" * 60)
        print("向量覆盖率状态")
        print("=" * 60)
        print(f"检查时间: {coverage.get('timestamp', 'N/A')}")
        print(f"\nL1 记忆:")
        print(f"  总数: {coverage.get('l1_records', 0)}")
        print(f"  向量: {coverage.get('l1_vec', 0)}")
        print(f"  覆盖率: {coverage.get('l1_coverage', 0)}%")
        print(f"  阈值: {self.config['l1_min_coverage']}%")
        print(f"  状态: {'✅ 正常' if coverage.get('l1_coverage', 0) >= self.config['l1_min_coverage'] else '⚠️ 偏低'}")
        
        print(f"\nL0 对话:")
        print(f"  总数: {coverage.get('l0_conversations', 0)}")
        print(f"  向量: {coverage.get('l0_vec', 0)}")
        print(f"  覆盖率: {coverage.get('l0_coverage', 0)}%")
        print(f"  阈值: {self.config['l0_min_coverage']}%")
        print(f"  状态: {'✅ 正常' if coverage.get('l0_coverage', 0) >= self.config['l0_min_coverage'] else '⚠️ 偏低'}")
        
        print("\n" + "=" * 60)
        print("配置")
        print("=" * 60)
        for k, v in self.config.items():
            print(f"{k}: {v}")

def main():
    import sys
    
    monitor = CoverageMonitor()
    
    if len(sys.argv) < 2:
        monitor.show_status()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "check":
        monitor.show_status()
    elif cmd == "daemon":
        monitor.run_daemon()
    elif cmd == "fix":
        coverage = monitor.check_coverage()
        monitor.auto_fix(coverage)
    elif cmd == "config":
        if len(sys.argv) >= 4:
            key = sys.argv[2]
            value = sys.argv[3]
            if key in monitor.config:
                if key in ["l1_min_coverage", "l0_min_coverage"]:
                    monitor.config[key] = float(value)
                elif key in ["check_interval"]:
                    monitor.config[key] = int(value)
                elif key in ["auto_fix", "alert_on_low"]:
                    monitor.config[key] = value.lower() == "true"
                monitor._save_config()
                print(f"✅ 已更新 {key} = {value}")
            else:
                print(f"❌ 未知配置项: {key}")
        else:
            print("用法: vector_coverage_monitor.py config <key> <value>")
    else:
        print(f"未知命令: {cmd}")
        print("用法: vector_coverage_monitor.py [check|daemon|fix|config]")

if __name__ == "__main__":
    main()
