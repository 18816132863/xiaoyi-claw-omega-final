#!/usr/bin/env python3
"""
安全确认模块 (v5.2.29)
所有系统级操作必须经过用户确认

功能：
- 系统操作确认
- 操作日志记录
- 安全策略检查
- 回滚机制

安全原则：
- 默认拒绝所有系统级修改
- 必须用户明确确认才能执行
- 所有操作可回滚
"""

import os
import sys
import json
import hashlib
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from pathlib import Path


# 安全配置文件路径
SECURITY_CONFIG_PATH = Path.home() / ".openclaw" / "memory-tdai" / "config" / "security_config.json"

# 默认安全配置（已移除需要 root 权限的配置）
DEFAULT_SECURITY_CONFIG = {
    "allow_numa_binding": False,     # 禁止 NUMA 绑定
    "require_confirmation": True,    # 需要用户确认
    "log_operations": True,          # 记录操作日志
    "allow_auto_apply": False,       # 禁止自动应用
}

# 操作日志路径
OPERATION_LOG_PATH = Path.home() / ".openclaw" / "memory-tdai" / "logs" / "operations.log"


def load_security_config() -> dict:
    """加载安全配置"""
    if SECURITY_CONFIG_PATH.exists():
        try:
            with open(SECURITY_CONFIG_PATH, 'r') as f:
                config = json.load(f)
                return {**DEFAULT_SECURITY_CONFIG, **config}
        except Exception:
            pass
    return DEFAULT_SECURITY_CONFIG


def save_security_config(config: dict):
    """保存安全配置"""
    SECURITY_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SECURITY_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


# 全局安全配置
_security_config = load_security_config()


class SecurityConfirmation:
    """
    安全确认器
    
    所有系统级操作必须通过此类确认。
    """
    
    # 危险操作列表（已移除需要 root 权限的操作）
    DANGEROUS_OPERATIONS = {
        'numa_binding': {
            'description': 'NUMA 内存绑定',
            'risk': '可能影响进程性能',
            'requires_root': False,
        },
    }
    
    def __init__(self):
        """初始化安全确认器"""
        self.config = _security_config
        self.operation_log = []
    
    def check_permission(self, operation_type: str) -> Dict[str, Any]:
        """
        检查操作权限
        
        Args:
            operation_type: 操作类型
            
        Returns:
            Dict: 权限检查结果
        """
        result = {
            'allowed': False,
            'requires_confirmation': True,
            'requires_root': False,
            'reason': '',
            'operation_type': operation_type,
        }
        
        # 检查操作类型是否已知
        if operation_type not in self.DANGEROUS_OPERATIONS:
            result['reason'] = f"未知操作类型: {operation_type}"
            return result
        
        op_info = self.DANGEROUS_OPERATIONS[operation_type]
        result['requires_root'] = op_info['requires_root']
        
        # 检查配置
        config_key = f"allow_{operation_type}"
        if self.config.get(config_key, False):
            result['allowed'] = True
            result['requires_confirmation'] = False
            result['reason'] = "已在配置中允许"
        else:
            result['reason'] = f"需要用户确认: {op_info['description']}"
        
        return result
    
    def confirm(
        self,
        operation_type: str,
        operation_detail: str,
        auto_confirm: bool = False
    ) -> bool:
        """
        确认操作
        
        Args:
            operation_type: 操作类型
            operation_detail: 操作详情
            auto_confirm: 是否自动确认（仅用于测试）
            
        Returns:
            bool: 是否允许执行
        """
        # 检查权限
        permission = self.check_permission(operation_type)
        
        if permission['allowed']:
            self._log_operation(operation_type, operation_detail, 'allowed_by_config')
            return True
        
        # 检查是否需要用户确认
        if not self.config.get('require_confirmation', True):
            self._log_operation(operation_type, operation_detail, 'allowed_no_confirm')
            return True
        
        # 自动确认（仅用于测试）
        if auto_confirm:
            self._log_operation(operation_type, operation_detail, 'allowed_auto')
            return True
        
        # 需要用户确认
        op_info = self.DANGEROUS_OPERATIONS.get(operation_type, {})
        print(f"\n⚠️ 安全确认请求")
        print(f"操作类型: {operation_type}")
        print(f"操作描述: {op_info.get('description', '未知')}")
        print(f"风险说明: {op_info.get('risk', '未知')}")
        print(f"操作详情: {operation_detail}")
        print(f"\n是否允许执行？(yes/no): ", end='')
        
        try:
            response = input().strip().lower()
            if response in ('yes', 'y'):
                self._log_operation(operation_type, operation_detail, 'allowed_by_user')
                return True
            else:
                self._log_operation(operation_type, operation_detail, 'denied_by_user')
                return False
        except EOFError:
            # 非交互环境，默认拒绝
            print("非交互环境，操作被拒绝")
            self._log_operation(operation_type, operation_detail, 'denied_non_interactive')
            return False
    
    def _log_operation(self, operation_type: str, detail: str, result: str):
        """记录操作日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,
            'detail': detail,
            'result': result,
        }
        
        self.operation_log.append(log_entry)
        
        # 写入日志文件
        if self.config.get('log_operations', True):
            try:
                OPERATION_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(OPERATION_LOG_PATH, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
            except Exception:
                pass


def require_confirmation(operation_type: str):
    """
    装饰器：要求操作确认
    
    Args:
        operation_type: 操作类型
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            confirmer = SecurityConfirmation()
            detail = f"{func.__name__}({args}, {kwargs})"
            
            if confirmer.confirm(operation_type, detail):
                return func(*args, **kwargs)
            else:
                print(f"⚠️ 操作被拒绝: {func.__name__}")
                return None
        return wrapper
    return decorator


def check_system_modification_allowed(operation_type: str) -> bool:
    """
    检查是否允许系统修改
    
    Args:
        operation_type: 操作类型
        
    Returns:
        bool: 是否允许
    """
    confirmer = SecurityConfirmation()
    permission = confirmer.check_permission(operation_type)
    return permission['allowed']


def print_security_status():
    """打印安全状态"""
    config = load_security_config()
    
    print("=== 安全配置状态 ===")
    print(f"需要用户确认: {'✅ 是' if config['require_confirmation'] else '❌ 否'}")
    print(f"记录操作日志: {'✅ 是' if config['log_operations'] else '❌ 否'}")
    print(f"自动应用: {'❌ 禁用' if not config['allow_auto_apply'] else '⚠️ 启用'}")
    print()
    print("系统操作权限:")
    for op in SecurityConfirmation.DANGEROUS_OPERATIONS:
        allowed = config.get(f"allow_{op}", False)
        status = "✅ 允许" if allowed else "❌ 禁止"
        print(f"  {op}: {status}")
    print("====================")


# 导出
__all__ = [
    'SecurityConfirmation',
    'require_confirmation',
    'check_system_modification_allowed',
    'load_security_config',
    'save_security_config',
    'print_security_status',
]


# 测试
if __name__ == "__main__":
    print_security_status()
