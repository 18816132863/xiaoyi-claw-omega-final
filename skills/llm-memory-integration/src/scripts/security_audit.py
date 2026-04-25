#!/usr/bin/env python3
"""
安全审计脚本
记录安全相关操作和事件
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
AUDIT_LOG = WORKSPACE / "memory" / "security_audit.json"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

class SecurityAuditor:
    """安全审计器"""
    
    def __init__(self):
        self.audit_log = []
    
    def load_log(self):
        """加载现有日志"""
        if AUDIT_LOG.exists():
            self.audit_log = json.loads(AUDIT_LOG.read_text())
    
    def save_log(self):
        """保存日志"""
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        # 保留最近500条
        if len(self.audit_log) > 500:
            self.audit_log = self.audit_log[-500:]
        AUDIT_LOG.write_text(json.dumps(self.audit_log, indent=2))
    
    def add_event(self, event_type, severity, message, details=None):
        """添加审计事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "severity": severity,
            "message": message,
            "details": details or {}
        }
        self.audit_log.append(event)
        return event
    
    def audit_config_integrity(self):
        """审计配置文件完整性"""
        if CONFIG_PATH.exists():
            content = CONFIG_PATH.read_text()
            file_hash = hashlib.sha256(content.encode()).hexdigest()
            
            self.add_event(
                "config_integrity",
                "info",
                "配置文件完整性检查",
                {"hash": file_hash[:16], "size": len(content)}
            )
            return True
        else:
            self.add_event(
                "config_integrity",
                "critical",
                "配置文件不存在"
            )
            return False
    
    def audit_plugin_status(self):
        """审计插件状态"""
        try:
            config = json.loads(CONFIG_PATH.read_text())
            plugins = config.get("plugins", {}).get("entries", {})
            
            security_plugins = ["execution-validator-plugin", "memory-tencentdb"]
            for plugin in security_plugins:
                enabled = plugins.get(plugin, {}).get("enabled", False)
                self.add_event(
                    "plugin_status",
                    "info" if enabled else "warning",
                    f"插件状态: {plugin}",
                    {"enabled": enabled}
                )
            return True
        except Exception as e:
            self.add_event(
                "plugin_status",
                "error",
                f"插件状态检查失败: {e}"
            )
            return False
    
    def audit_file_permissions(self):
        """审计文件权限"""
        sensitive_paths = [
            Path.home() / ".openclaw" / "openclaw.json",
            Path.home() / ".config" / "ima" / "api_key",
        ]
        
        for path in sensitive_paths:
            if path.exists():
                stat = path.stat()
                mode = oct(stat.st_mode)[-3:]
                
                # 检查是否过于开放
                if mode in ["777", "666"]:
                    self.add_event(
                        "file_permission",
                        "warning",
                        f"文件权限过于开放: {path.name}",
                        {"mode": mode, "path": str(path)}
                    )
                else:
                    self.add_event(
                        "file_permission",
                        "info",
                        f"文件权限正常: {path.name}",
                        {"mode": mode}
                    )
        
        return True
    
    def run_audit(self):
        """运行完整审计"""
        self.load_log()
        
        self.audit_config_integrity()
        self.audit_plugin_status()
        self.audit_file_permissions()
        
        self.save_log()
        return self.audit_log[-10:]  # 返回最近10条
    
    def print_report(self):
        """打印审计报告"""
        print("=" * 60)
        print("   安全审计报告")
        print("=" * 60)
        print(f"审计时间: {datetime.now().isoformat()}")
        print()
        
        recent = self.audit_log[-10:] if self.audit_log else []
        
        if not recent:
            print("暂无审计记录")
            return
        
        for event in recent:
            severity = event["severity"]
            icon = "🔴" if severity == "critical" else "🟡" if severity == "warning" else "✅"
            print(f"{icon} [{event['type']}] {event['message']}")
            if event.get("details"):
                for k, v in event["details"].items():
                    print(f"   - {k}: {v}")
        
        print()
        print(f"总记录数: {len(self.audit_log)}")

def main():
    auditor = SecurityAuditor()
    auditor.run_audit()
    auditor.print_report()

if __name__ == "__main__":
    main()
