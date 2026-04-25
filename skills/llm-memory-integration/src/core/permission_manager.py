"""
权限管理器 - 权限分离和审计日志
"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class PermissionManager:
    """权限管理器"""
    
    # 权限级别定义（已移除 Level 4 - 系统命令执行）
    LEVELS = {
        0: "普通用户权限",
        1: "文件系统访问",
        2: "网络访问",
        3: "原生扩展加载",
    }
    
    # 高风险操作定义（已移除 Level 4 操作）
    HIGH_RISK_OPERATIONS = {
        3: ["load_extension"],
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化权限管理器"""
        self.config_path = config_path or self._get_default_config_path()
        self.audit_log_path = self._get_audit_log_path()
        self.permissions = self._load_permissions()
        
    def _get_default_config_path(self) -> str:
        """获取默认配置路径"""
        base_dir = Path.home() / ".openclaw" / "workspace" / "skills" / "llm-memory-integration"
        return str(base_dir / "config" / "permissions.json")
    
    def _get_audit_log_path(self) -> str:
        """获取审计日志路径"""
        base_dir = Path.home() / ".openclaw" / "workspace" / "skills" / "llm-memory-integration"
        log_dir = base_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return str(log_dir / "audit.log")
    
    def _load_permissions(self) -> Dict:
        """加载权限配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载权限配置失败: {e}")
        
        # 返回默认配置（已移除 Level 4）
        return {
            "version": "1.0.0",
            "permissions": {
                "level_0": {"enabled": True},
                "level_1": {"enabled": True},
                "level_2": {"enabled": True},
                "level_3": {"enabled": False, "require_confirmation": True}
            }
        }
    
    def check_permission(self, level: int, operation: str, 
                        details: Optional[Dict] = None) -> bool:
        """
        检查权限
        
        Args:
            level: 权限级别 (0-4)
            operation: 操作名称
            details: 操作详情
        
        Returns:
            bool: 是否有权限
        """
        # 1. 检查权限级别是否有效
        if level not in self.LEVELS:
            self._log_audit(level, operation, False, "无效的权限级别")
            return False
        
        # 2. 检查权限是否启用
        level_key = f"level_{level}"
        if not self.permissions.get("permissions", {}).get(level_key, {}).get("enabled", False):
            self._log_audit(level, operation, False, "权限未启用")
            return False
        
        # 3. 检查是否需要用户确认
        if self._requires_confirmation(level):
            if not self._user_confirmed(operation, level):
                self._log_audit(level, operation, False, "用户未确认")
                return False
        
        # 4. 记录审计日志
        self._log_audit(level, operation, True, "权限检查通过", details)
        return True
    
    def _requires_confirmation(self, level: int) -> bool:
        """检查是否需要用户确认"""
        level_key = f"level_{level}"
        return self.permissions.get("permissions", {}).get(level_key, {}).get("require_confirmation", False)
    
    def _user_confirmed(self, operation: str, level: int) -> bool:
        """用户确认"""
        # 在实际实现中，这里应该弹出确认对话框
        # 目前返回 False，表示需要用户手动确认
        print(f"⚠️ 需要用户确认: {operation} (Level {level})")
        return False
    
    def _log_audit(self, level: int, operation: str, granted: bool, 
                   reason: str, details: Optional[Dict] = None):
        """记录审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "level_name": self.LEVELS.get(level, "未知"),
            "operation": operation,
            "granted": granted,
            "reason": reason,
            "user": os.getenv("USER", "unknown"),
            "process": os.getpid(),
            "details": details or {}
        }
        
        try:
            with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"写入审计日志失败: {e}")
    
    def get_audit_logs(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        logs = []
        try:
            if os.path.exists(self.audit_log_path):
                with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-limit:]:
                        if line.strip():
                            logs.append(json.loads(line))
        except Exception as e:
            print(f"读取审计日志失败: {e}")
        return logs
    
    def enable_permission(self, level: int, confirm: bool = False) -> bool:
        """启用权限"""
        if level not in self.LEVELS:
            return False
        
        if level >= 3 and not confirm:
            print(f"⚠️ 启用 Level {level} 权限需要用户确认")
            return False
        
        level_key = f"level_{level}"
        self.permissions.setdefault("permissions", {}).setdefault(level_key, {})["enabled"] = True
        
        # 保存配置
        self._save_permissions()
        
        # 记录审计日志
        self._log_audit(level, "enable_permission", True, "用户启用权限")
        return True
    
    def disable_permission(self, level: int) -> bool:
        """禁用权限"""
        if level not in self.LEVELS:
            return False
        
        level_key = f"level_{level}"
        self.permissions.setdefault("permissions", {}).setdefault(level_key, {})["enabled"] = False
        
        # 保存配置
        self._save_permissions()
        
        # 记录审计日志
        self._log_audit(level, "disable_permission", True, "用户禁用权限")
        return True
    
    def _save_permissions(self):
        """保存权限配置"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.permissions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存权限配置失败: {e}")
    
    def get_permission_status(self) -> Dict:
        """获取权限状态"""
        status = {}
        for level in self.LEVELS:
            level_key = f"level_{level}"
            status[f"level_{level}"] = {
                "name": self.LEVELS[level],
                "enabled": self.permissions.get("permissions", {}).get(level_key, {}).get("enabled", False)
            }
        return status


# 全局权限管理器实例
_permission_manager = None


def get_permission_manager() -> PermissionManager:
    """获取全局权限管理器实例"""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager


# 便捷函数
def check_permission(level: int, operation: str, details: Optional[Dict] = None) -> bool:
    """检查权限"""
    return get_permission_manager().check_permission(level, operation, details)


def enable_permission(level: int, confirm: bool = False) -> bool:
    """启用权限"""
    return get_permission_manager().enable_permission(level, confirm)


def disable_permission(level: int) -> bool:
    """禁用权限"""
    return get_permission_manager().disable_permission(level)


def get_audit_logs(limit: int = 100) -> List[Dict]:
    """获取审计日志"""
    return get_permission_manager().get_audit_logs(limit)
