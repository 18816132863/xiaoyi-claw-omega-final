"""
Workflow Contract Validator - Workflow 契约校验器
在 workflow 运行前校验契约
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import os

from orchestration.workflow.workflow_registry import (
    WorkflowTemplate,
    WorkflowStep,
    get_workflow_registry
)


@dataclass
class ValidationResult:
    """校验结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class WorkflowContractValidator:
    """
    Workflow 契约校验器
    
    在 workflow 运行前校验：
    1. 模板是否存在
    2. Profile 是否兼容
    3. 能力是否允许
    4. 依赖是否可解析
    5. 恢复策略是否有效
    """
    
    def __init__(self):
        self._registry = get_workflow_registry()
    
    def validate(
        self,
        workflow_id: str,
        version: Optional[str],
        profile: str,
        allowed_capabilities: List[str],
        input_data: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        校验 workflow 契约
        
        Args:
            workflow_id: Workflow ID
            version: 版本
            profile: 配置
            allowed_capabilities: 允许的能力
            input_data: 输入数据
            
        Returns:
            校验结果
        """
        errors = []
        warnings = []
        
        # 1. 校验模板是否存在
        template = self._registry.get(workflow_id, version)
        if not template:
            errors.append(f"Workflow template not found: {workflow_id}:{version or 'latest'}")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        # 2. 校验 Profile 兼容性
        if profile not in template.profile_compatibility:
            errors.append(f"Profile '{profile}' not compatible with workflow. Allowed: {template.profile_compatibility}")
        
        # 3. 校验 workflow 级别能力
        for cap in template.required_capabilities:
            if cap not in allowed_capabilities:
                errors.append(f"Required capability '{cap}' not allowed for profile '{profile}'")
        
        # 4. 校验步骤级别能力
        for step in template.steps:
            for cap in step.required_capabilities:
                if cap not in allowed_capabilities:
                    errors.append(f"Step '{step.step_id}' requires capability '{cap}' which is not allowed")
        
        # 5. 校验依赖可解析性
        dep_errors = self._validate_dependencies(template.steps)
        errors.extend(dep_errors)
        
        # 6. 校验恢复策略
        recovery_warnings = self._validate_recovery_policy(template)
        warnings.extend(recovery_warnings)
        
        # 7. 校验 safe mode 支持
        if profile == "safe" and not template.safe_mode_supported:
            errors.append("Workflow does not support safe mode")
        
        # 8. 校验高风险步骤
        for step in template.steps:
            if step.is_high_risk and profile in ["safe", "restricted"]:
                warnings.append(f"Step '{step.step_id}' is high risk and may be blocked in profile '{profile}'")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_step(
        self,
        step: WorkflowStep,
        profile: str,
        allowed_capabilities: List[str]
    ) -> ValidationResult:
        """
        校验单个步骤
        
        Args:
            step: 步骤
            profile: 配置
            allowed_capabilities: 允许的能力
            
        Returns:
            校验结果
        """
        errors = []
        warnings = []
        
        # 1. 校验能力
        for cap in step.required_capabilities:
            if cap not in allowed_capabilities:
                errors.append(f"Capability '{cap}' not allowed")
        
        # 2. 校验 safe mode
        if profile == "safe" and not step.safe_mode_supported:
            errors.append("Step does not support safe mode")
        
        # 3. 校验高风险
        if step.is_high_risk and profile in ["safe", "restricted"]:
            warnings.append("High risk step may be blocked")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_input(
        self,
        workflow_id: str,
        version: Optional[str],
        input_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        校验输入数据
        
        Args:
            workflow_id: Workflow ID
            version: 版本
            input_data: 输入数据
            
        Returns:
            校验结果
        """
        errors = []
        warnings = []
        
        template = self._registry.get(workflow_id, version)
        if not template:
            errors.append("Template not found")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        # 检查输入参数（如果有定义）
        # 这里可以扩展为更复杂的 schema 校验
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_dependencies(self, steps: List[WorkflowStep]) -> List[str]:
        """
        校验依赖可解析性
        
        Args:
            steps: 步骤列表
            
        Returns:
            错误列表
        """
        errors = []
        step_ids = {step.step_id for step in steps}
        
        for step in steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step '{step.step_id}' depends on non-existent step '{dep}'")
        
        # 检查循环依赖
        cycle = self._detect_cycle(steps)
        if cycle:
            errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
        
        return errors
    
    def _detect_cycle(self, steps: List[WorkflowStep]) -> Optional[List[str]]:
        """
        检测循环依赖
        
        Args:
            steps: 步骤列表
            
        Returns:
            循环路径（如果存在）
        """
        # 构建依赖图
        graph = {step.step_id: step.depends_on for step in steps}
        
        # DFS 检测循环
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for dep in graph.get(node, []):
                if dep not in visited:
                    result = dfs(dep)
                    if result:
                        return result
                elif dep in rec_stack:
                    # 找到循环
                    cycle_start = path.index(dep)
                    return path[cycle_start:] + [dep]
            
            path.pop()
            rec_stack.remove(node)
            return None
        
        for step_id in graph:
            if step_id not in visited:
                cycle = dfs(step_id)
                if cycle:
                    return cycle
        
        return None
    
    def _validate_recovery_policy(self, template: WorkflowTemplate) -> List[str]:
        """
        校验恢复策略
        
        Args:
            template: 模板
            
        Returns:
            警告列表
        """
        warnings = []
        
        # 检查 workflow 级别恢复策略
        if template.recovery_policy:
            if template.recovery_policy.fallback_skill:
                # 检查 fallback skill 是否存在
                pass  # 可以扩展为检查 skill registry
            
            if template.recovery_policy.rollback_to_step:
                step_ids = {s.step_id for s in template.steps}
                if template.recovery_policy.rollback_to_step not in step_ids:
                    warnings.append(f"Rollback target step '{template.recovery_policy.rollback_to_step}' not found")
        
        # 检查步骤级别恢复策略
        for step in template.steps:
            if step.recovery_policy and step.recovery_policy.rollback_to_step:
                step_ids = {s.step_id for s in template.steps}
                if step.recovery_policy.rollback_to_step not in step_ids:
                    warnings.append(f"Step '{step.step_id}' rollback target '{step.recovery_policy.rollback_to_step}' not found")
        
        return warnings


# 全局单例
_workflow_contract_validator = None

def get_workflow_contract_validator() -> WorkflowContractValidator:
    """获取契约校验器单例"""
    global _workflow_contract_validator
    if _workflow_contract_validator is None:
        _workflow_contract_validator = WorkflowContractValidator()
    return _workflow_contract_validator
