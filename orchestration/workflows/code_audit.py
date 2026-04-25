#!/usr/bin/env python3
"""
架构升级/代码审计工作流 - V2.8.0
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class CodeAuditWorkflow(WorkflowBase):
    name = "code_audit"
    description = "代码审计 - 架构检查、代码审查、优化建议"
    version = "1.0.0"
    applicable_scenarios = ["代码审计", "架构检查", "代码优化"]
    required_skills = []
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "project_path": "项目路径",
            "audit_type": "审计类型（架构/安全/性能）",
            "output_format": "输出格式"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        return True, "验证通过"
    
    def get_execution_order(self) -> List[str]:
        return [
            "scan_structure",
            "check_architecture",
            "analyze_code",
            "check_security",
            "generate_report"
        ]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {
            "structure": "项目结构",
            "issues": "问题列表",
            "recommendations": "优化建议",
            "report_file": "审计报告"
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {}
    
    def get_completion_criteria(self) -> List[str]:
        return ["已完成架构检查", "已生成审计报告"]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "跳过非关键检查"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        return True

WORKFLOW_REGISTRY = {"code_audit": CodeAuditWorkflow}
