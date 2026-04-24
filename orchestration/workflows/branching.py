"""工作流条件分支"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class BranchCondition(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    UNCERTAIN = "uncertain"
    CUSTOM = "custom"


@dataclass
class Branch:
    """分支定义"""
    condition: BranchCondition
    steps: List[Dict[str, Any]]
    else_branch: Optional["Branch"] = None


def evaluate_condition(condition: BranchCondition, result: Dict[str, Any], custom_evaluator: Optional[Callable] = None) -> bool:
    """评估条件"""
    if condition == BranchCondition.SUCCESS:
        return result.get("success", False) and result.get("normalized_status") == "completed"
    elif condition == BranchCondition.FAILURE:
        return not result.get("success", False) or result.get("normalized_status") == "failed"
    elif condition == BranchCondition.TIMEOUT:
        return result.get("normalized_status") == "timeout"
    elif condition == BranchCondition.UNCERTAIN:
        return result.get("normalized_status") == "result_uncertain"
    elif condition == BranchCondition.CUSTOM:
        if custom_evaluator:
            return custom_evaluator(result)
        return False
    return False


def execute_branching_workflow(
    steps: List[Dict[str, Any]],
    branches: List[Branch],
    context: Optional[Dict[str, Any]] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    执行带条件分支的工作流
    
    Args:
        steps: 初始步骤列表
        branches: 分支定义列表
        context: 执行上下文
        dry_run: 是否预演模式
        
    Returns:
        执行结果
    """
    context = context or {}
    results = []
    
    # 执行初始步骤
    for step in steps:
        if dry_run:
            results.append({
                "step": step.get("name", "unnamed"),
                "dry_run": True,
                "skipped": True
            })
            continue
        
        # 执行步骤
        step_result = _execute_step(step, context)
        results.append(step_result)
        
        # 检查分支条件
        for branch in branches:
            if evaluate_condition(branch.condition, step_result):
                # 执行分支步骤
                branch_results = []
                for branch_step in branch.steps:
                    branch_results.append(_execute_step(branch_step, context))
                
                results.append({
                    "branch": branch.condition.value,
                    "steps": branch_results
                })
                break
        else:
            # 执行 else 分支
            for branch in branches:
                if branch.else_branch:
                    else_results = []
                    for else_step in branch.else_branch.steps:
                        else_results.append(_execute_step(else_step, context))
                    
                    results.append({
                        "branch": "else",
                        "steps": else_results
                    })
                    break
    
    return {
        "success": True,
        "dry_run": dry_run,
        "results": results
    }


def _execute_step(step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """执行单个步骤"""
    import importlib
    
    capability = step.get("capability")
    params = step.get("params", {})
    
    try:
        module = importlib.import_module(f"capabilities.{capability}")
        if hasattr(module, "run"):
            result = module.run(**params)
            return {
                "step": step.get("name", capability),
                "success": result.get("success", False),
                "result": result
            }
        else:
            return {
                "step": step.get("name", capability),
                "success": False,
                "error": f"Capability {capability} has no run function"
            }
    except Exception as e:
        return {
            "step": step.get("name", capability),
            "success": False,
            "error": str(e)
        }
