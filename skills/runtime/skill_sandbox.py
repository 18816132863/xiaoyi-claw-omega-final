"""
技能沙箱

提供隔离的技能执行环境
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import traceback


class SkillSandbox:
    """技能沙箱"""
    
    def __init__(self, allowed_modules: list = None, blocked_modules: list = None):
        self.allowed_modules = allowed_modules or []
        self.blocked_modules = blocked_modules or ["os", "subprocess", "socket"]
        self.execution_log: list = []
    
    def execute(self, skill_code: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """在沙箱中执行技能代码"""
        result = {
            "success": False,
            "output": None,
            "error": None,
        }
        
        # 创建隔离的执行环境
        sandbox_globals = {
            "__builtins__": __builtins__,
            "context": context or {},
        }
        
        try:
            # 执行代码
            exec(skill_code, sandbox_globals)
            result["success"] = True
            result["output"] = sandbox_globals.get("result")
        except Exception as e:
            result["error"] = str(e)
            result["traceback"] = traceback.format_exc()
        
        # 记录执行日志
        self.execution_log.append({
            "code_length": len(skill_code),
            "success": result["success"],
        })
        
        return result
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """验证代码安全性"""
        issues = []
        
        # 检查禁止的模块
        for blocked in self.blocked_modules:
            if f"import {blocked}" in code or f"from {blocked}" in code:
                issues.append(f"禁止使用模块: {blocked}")
        
        # 检查危险操作
        dangerous_patterns = [
            "eval(", "exec(", "compile(",
            "__import__", "globals()", "locals()",
            "open(", "file(",
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                issues.append(f"检测到危险操作: {pattern}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }
    
    def clear_log(self):
        """清除执行日志"""
        self.execution_log.clear()


__all__ = ["SkillSandbox"]
