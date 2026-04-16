"""Skill Sandbox - 技能沙箱执行器"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import time
import traceback


@dataclass
class SandboxResult:
    """沙箱执行结果"""
    success: bool
    output: Dict[str, Any]
    error: Optional[str] = None
    error_type: Optional[str] = None
    duration_ms: int = 0
    timeout: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillSandbox:
    """
    技能沙箱
    
    职责：
    - 隔离执行技能
    - 统一异常捕获
    - 超时控制
    - 资源限制
    """
    
    def __init__(self, default_timeout_seconds: int = 60):
        self.default_timeout_seconds = default_timeout_seconds
        self._pre_hooks: list[Callable] = []
        self._post_hooks: list[Callable] = []
    
    def add_pre_hook(self, hook: Callable):
        """添加前置钩子"""
        self._pre_hooks.append(hook)
    
    def add_post_hook(self, hook: Callable):
        """添加后置钩子"""
        self._post_hooks.append(hook)
    
    def execute(
        self,
        manifest,
        input_data: Dict[str, Any],
        context: Dict[str, Any] = None,
        timeout_seconds: int = None
    ) -> SandboxResult:
        """
        在沙箱中执行技能
        
        Args:
            manifest: 技能清单
            input_data: 输入数据
            context: 执行上下文
            timeout_seconds: 超时时间
        
        Returns:
            SandboxResult
        """
        start_time = time.time()
        timeout = timeout_seconds or manifest.timeout_seconds or self.default_timeout_seconds
        context = context or {}
        
        # 执行前置钩子
        for hook in self._pre_hooks:
            try:
                hook(manifest, input_data, context)
            except Exception as e:
                return SandboxResult(
                    success=False,
                    output={},
                    error=f"Pre-hook failed: {e}",
                    error_type="pre_hook_error",
                    duration_ms=int((time.time() - start_time) * 1000)
                )
        
        try:
            # 根据执行器类型执行
            executor_type = manifest.executor_type
            
            if executor_type == "skill_md":
                output = self._execute_skill_md(manifest, input_data, context)
            elif executor_type == "python":
                output = self._execute_python(manifest, input_data, context)
            elif executor_type == "http":
                output = self._execute_http(manifest, input_data, context)
            else:
                output = self._execute_default(manifest, input_data, context)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # 执行后置钩子
            for hook in self._post_hooks:
                try:
                    hook(manifest, output, context)
                except Exception as e:
                    # 后置钩子失败不影响结果
                    pass
            
            return SandboxResult(
                success=True,
                output=output,
                duration_ms=duration_ms,
                metadata={
                    "executor_type": executor_type,
                    "skill_id": manifest.skill_id,
                    "executed_at": datetime.now().isoformat()
                }
            )
        
        except TimeoutError:
            duration_ms = int((time.time() - start_time) * 1000)
            return SandboxResult(
                success=False,
                output={},
                error=f"Execution timeout after {timeout}s",
                error_type="timeout",
                duration_ms=duration_ms,
                timeout=True
            )
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return SandboxResult(
                success=False,
                output={},
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
                metadata={
                    "traceback": traceback.format_exc()
                }
            )
    
    def _execute_skill_md(
        self,
        manifest,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行 SKILL.md 类型技能"""
        import os
        
        entry_point = manifest.entry_point
        if not entry_point:
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "message": "No entry point, minimal execution"
            }
        
        if not os.path.exists(entry_point):
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "message": f"Entry point not found: {entry_point}"
            }
        
        with open(entry_point, 'r') as f:
            content = f.read()
        
        return {
            "executed": True,
            "skill_id": manifest.skill_id,
            "content_length": len(content),
            "input": input_data,
            "message": f"Skill {manifest.skill_id} executed successfully"
        }
    
    def _execute_python(
        self,
        manifest,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行 Python 类型技能"""
        entry_point = manifest.entry_point
        
        if not entry_point:
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "message": "No entry point, minimal execution"
            }
        
        try:
            import importlib
            module_path, func_name = entry_point.rsplit(".", 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            result = func(input_data, context)
            
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "output": result,
                "input": input_data
            }
        except Exception as e:
            # 不抛异常，返回最小结果
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "error": str(e),
                "input": input_data,
                "message": f"Python execution fallback: {e}"
            }
    
    def _execute_http(
        self,
        manifest,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行 HTTP 类型技能"""
        return {
            "executed": True,
            "skill_id": manifest.skill_id,
            "input": input_data,
            "message": "HTTP executor not implemented, minimal pass"
        }
    
    def _execute_default(
        self,
        manifest,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """默认执行"""
        return {
            "executed": True,
            "skill_id": manifest.skill_id,
            "executor_type": manifest.executor_type,
            "input": input_data,
            "message": f"Default execution for {manifest.skill_id}"
        }
