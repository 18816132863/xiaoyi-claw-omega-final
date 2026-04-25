#!/usr/bin/env python3
"""
架构统一集成入口 - V2.8.0
使用统一路径解析，禁止硬编码
"""

import sys
from typing import Optional

# 使用统一路径解析
from infrastructure.path_resolver import get_project_root, get_cached_project_root

PROJECT_ROOT = get_cached_project_root()
sys.path.insert(0, str(PROJECT_ROOT))

# 导入各层集成模块
from core.prompt_integration import get_prompt_orchestrator
from execution.plugin_integration import get_plugin_orchestrator
from governance.security.auth_integration import get_auth_middleware

class ArchitectureIntegration:
    """架构集成管理器"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.prompt_orchestrator = get_prompt_orchestrator()
        self.plugin_orchestrator = get_plugin_orchestrator()
        self.auth_middleware = get_auth_middleware()
        self._initialized = False
    
    def initialize(self):
        """初始化架构"""
        if self._initialized:
            return
        
        self.prompt_orchestrator.load_layer(1)
        self.plugin_orchestrator.list_plugins()
        self.auth_middleware.get_status()
        self._initialized = True
    
    def get_startup_prompt(self) -> str:
        """获取启动提示词"""
        return self.prompt_orchestrator.load_minimal()
    
    def get_layer_prompt(self, layer: int) -> str:
        """获取层级提示词"""
        return self.prompt_orchestrator.load_layer(layer)
    
    def call_plugin(self, name: str, arg: dict):
        """调用插件"""
        return self.plugin_orchestrator.call_plugin(name, arg)
    
    def check_permission(self, operation: str, target: str) -> tuple:
        """检查权限"""
        if operation == "exec":
            return self.auth_middleware.check_exec_permission(target)
        elif operation == "write":
            return self.auth_middleware.check_write_permission(target)
        elif operation == "read":
            return self.auth_middleware.check_read_permission(target)
        return True, "允许"
    
    def grant_auth(self, **kwargs) -> str:
        """授权"""
        return self.auth_middleware.grant_temp_auth(**kwargs)
    
    def revoke_auth(self):
        """撤销授权"""
        self.auth_middleware.revoke_auth()
    
    def get_status(self) -> dict:
        """获取状态"""
        return {
            "initialized": self._initialized,
            "project_root": str(self.project_root),
            "auth": self.auth_middleware.get_status(),
            "plugins": len(self.plugin_orchestrator.list_plugins()),
            "tokens": self.prompt_orchestrator.get_token_estimate(),
        }

# 全局实例
_integration: Optional[ArchitectureIntegration] = None

def get_integration():
    """获取全局集成管理器"""
    global _integration
    if _integration is None:
        _integration = ArchitectureIntegration()
        _integration.initialize()
    return _integration

def startup():
    """启动"""
    return get_integration().initialize()

def status():
    """状态"""
    return get_integration().get_status()
