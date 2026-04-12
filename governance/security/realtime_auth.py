#!/usr/bin/env python3
"""
实时权限控制
V2.7.0 - 2026-04-10

借鉴 LegnaChat 的实时授权机制
"""

import os
import json
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

@dataclass
class AuthSession:
    """授权会话"""
    session_id: str
    created_at: float
    expires_at: float
    allowed_operations: Set[str] = field(default_factory=set)
    allowed_paths: Set[str] = field(default_factory=set)
    denied_operations: Set[str] = field(default_factory=set)

@dataclass
class OperationLog:
    """操作日志"""
    timestamp: float
    operation: str
    path: Optional[str]
    allowed: bool
    reason: str

class RealtimeAuthManager:
    """实时权限管理器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "security_config.json"
        self.current_session: Optional[AuthSession] = None
        self.operation_logs: List[OperationLog] = []
        
        # 使用 path_resolver 获取安全路径
        try:
            from infrastructure.path_resolver import get_project_root
            _workspace = str(get_project_root())
            _repo = str(get_project_root() / "repo")
        except ImportError:
            _workspace = "."
            _repo = "./repo"
        
        # 默认安全配置
        self.default_config = {
            "safe_paths": [
                _workspace,
                "/tmp",
                _repo,
            ],
            "dangerous_commands": [
                "rm", "sudo", "chmod", "chown",
                "mkfs", "dd", "fdisk",
                "shutdown", "reboot", "halt",
            ],
            "dangerous_patterns": [
                "rm -rf /",
                "> /dev/",
                "chmod 777",
            ],
            "auth_timeout": 3600,  # 1小时
            "log_max_entries": 1000,
        }
        
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return self.default_config
    
    def _save_config(self):
        """保存配置"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def grant_auth(self, operations: List[str] = None, paths: List[str] = None,
                   timeout: int = None) -> str:
        """授予权限"""
        session_id = f"auth_{int(time.time() * 1000)}"
        timeout = timeout or self.config["auth_timeout"]
        
        self.current_session = AuthSession(
            session_id=session_id,
            created_at=time.time(),
            expires_at=time.time() + timeout,
            allowed_operations=set(operations or []),
            allowed_paths=set(paths or []),
        )
        
        return session_id
    
    def revoke_auth(self):
        """撤销权限"""
        self.current_session = None
    
    def check_command(self, command: str) -> tuple:
        """
        检查命令是否允许
        
        Returns:
            (allowed: bool, reason: str)
        """
        # 检查危险命令
        command_lower = command.lower()
        
        for dangerous in self.config["dangerous_commands"]:
            if command_lower.startswith(dangerous + " ") or command_lower == dangerous:
                # 检查是否有授权
                if self.current_session and dangerous in self.current_session.allowed_operations:
                    if time.time() < self.current_session.expires_at:
                        self._log_operation(f"cmd:{command}", None, True, "已授权")
                        return True, "已授权"
                
                self._log_operation(f"cmd:{command}", None, False, "危险命令，需要授权")
                return False, f"危险命令 '{dangerous}' 需要授权"
        
        # 检查危险模式
        for pattern in self.config["dangerous_patterns"]:
            if pattern in command:
                self._log_operation(f"cmd:{command}", None, False, "危险模式")
                return False, f"检测到危险模式 '{pattern}'"
        
        # 安全命令
        self._log_operation(f"cmd:{command}", None, True, "安全命令")
        return True, "安全命令"
    
    def check_path(self, path: str, operation: str = "write") -> tuple:
        """
        检查路径是否允许
        
        Returns:
            (allowed: bool, reason: str)
        """
        abs_path = os.path.abspath(path)
        
        # 检查是否在安全路径
        for safe_path in self.config["safe_paths"]:
            if abs_path.startswith(safe_path):
                self._log_operation(operation, path, True, "安全路径")
                return True, "安全路径"
        
        # 检查是否有授权
        if self.current_session:
            if time.time() < self.current_session.expires_at:
                for allowed_path in self.current_session.allowed_paths:
                    if abs_path.startswith(allowed_path):
                        self._log_operation(operation, path, True, "已授权路径")
                        return True, "已授权路径"
        
        self._log_operation(operation, path, False, "需要授权")
        return False, f"路径 '{path}' 不在安全目录，需要授权"
    
    def _log_operation(self, operation: str, path: Optional[str], allowed: bool, reason: str):
        """记录操作日志"""
        self.operation_logs.append(OperationLog(
            timestamp=time.time(),
            operation=operation,
            path=path,
            allowed=allowed,
            reason=reason
        ))
        
        # 限制日志数量
        if len(self.operation_logs) > self.config["log_max_entries"]:
            self.operation_logs = self.operation_logs[-self.config["log_max_entries"]:]
    
    def get_auth_status(self) -> dict:
        """获取授权状态"""
        if not self.current_session:
            return {
                "authenticated": False,
                "message": "未授权"
            }
        
        if time.time() > self.current_session.expires_at:
            self.current_session = None
            return {
                "authenticated": False,
                "message": "授权已过期"
            }
        
        remaining = self.current_session.expires_at - time.time()
        return {
            "authenticated": True,
            "session_id": self.current_session.session_id,
            "remaining_seconds": int(remaining),
            "allowed_operations": list(self.current_session.allowed_operations),
            "allowed_paths": list(self.current_session.allowed_paths),
        }
    
    def get_recent_logs(self, limit: int = 20) -> List[dict]:
        """获取最近日志"""
        logs = self.operation_logs[-limit:]
        return [
            {
                "time": datetime.fromtimestamp(log.timestamp).strftime("%H:%M:%S"),
                "operation": log.operation,
                "path": log.path,
                "allowed": log.allowed,
                "reason": log.reason,
            }
            for log in logs
        ]
    
    def add_safe_path(self, path: str):
        """添加安全路径"""
        abs_path = os.path.abspath(path)
        if abs_path not in self.config["safe_paths"]:
            self.config["safe_paths"].append(abs_path)
            self._save_config()
    
    def remove_safe_path(self, path: str):
        """移除安全路径"""
        abs_path = os.path.abspath(path)
        if abs_path in self.config["safe_paths"]:
            self.config["safe_paths"].remove(abs_path)
            self._save_config()

# 全局实例
_auth_manager: Optional[RealtimeAuthManager] = None

def get_auth_manager() -> RealtimeAuthManager:
    """获取全局权限管理器"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = RealtimeAuthManager()
    return _auth_manager

def check_command(command: str) -> tuple:
    """检查命令（便捷函数）"""
    return get_auth_manager().check_command(command)

def check_path(path: str, operation: str = "write") -> tuple:
    """检查路径（便捷函数）"""
    return get_auth_manager().check_path(path, operation)

def grant_auth(**kwargs) -> str:
    """授权（便捷函数）"""
    return get_auth_manager().grant_auth(**kwargs)

def revoke_auth():
    """撤销授权（便捷函数）"""
    get_auth_manager().revoke_auth()
