"""安全检查 - V4.3.0

L5 治理层安全模块，负责权限检查、操作审计。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root
import json

@dataclass
class SecurityCheck:
    """安全检查结果"""
    allowed: bool
    reason: str
    risk_level: str  # low, medium, high, critical
    requires_confirm: bool

class SecurityGuard:
    """安全守卫"""
    
    PROTECTED_PATHS = [
        "AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md",
        "core/ARCHITECTURE.md",
        "infrastructure/inventory/skill_registry.json"
    ]
    
    DANGEROUS_OPERATIONS = ["delete", "rm", "truncate", "drop"]
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.audit_log: List[Dict] = []
    
    def check_operation(self, operation: str, target: str) -> SecurityCheck:
        """检查操作是否允许"""
        # 检查危险操作
        if any(danger in operation.lower() for danger in self.DANGEROUS_OPERATIONS):
            # 检查是否是受保护路径
            for protected in self.PROTECTED_PATHS:
                if protected in target:
                    return SecurityCheck(
                        allowed=False,
                        reason=f"受保护文件: {protected}",
                        risk_level="critical",
                        requires_confirm=True
                    )
            
            return SecurityCheck(
                allowed=True,
                reason="需要确认",
                risk_level="medium",
                requires_confirm=True
            )
        
        return SecurityCheck(
            allowed=True,
            reason="安全操作",
            risk_level="low",
            requires_confirm=False
        )
    
    def log_operation(self, operation: str, target: str, result: str):
        """记录操作日志"""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "target": target,
            "result": result
        })
    
    def get_stats(self) -> Dict:
        """获取安全统计"""
        return {
            "protected_paths": len(self.PROTECTED_PATHS),
            "audit_log_size": len(self.audit_log)
        }

# 全局实例
_guard = None

def get_guard() -> SecurityGuard:
    global _guard
    if _guard is None:
        _guard = SecurityGuard()
    return _guard
