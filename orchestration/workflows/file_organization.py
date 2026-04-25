#!/usr/bin/env python3
"""
文件整理与输出工作流 - V2.8.0
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class FileOrganizationWorkflow(WorkflowBase):
    name = "file_organization"
    description = "文件整理 - 整理、分类、归档文件"
    version = "1.0.0"
    applicable_scenarios = ["文件整理", "文档归档", "资料整理"]
    required_skills = []
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "source_dir": "源目录",
            "target_dir": "目标目录",
            "organize_by": "分类方式（类型/日期/项目）"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        return True, "验证通过"
    
    def get_execution_order(self) -> List[str]:
        return ["scan_files", "categorize", "organize", "generate_report"]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {"files": "文件列表", "categories": "分类结果", "report": "整理报告"}
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {}
    
    def get_completion_criteria(self) -> List[str]:
        return ["已扫描文件", "已分类整理"]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "跳过问题文件"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        return True

WORKFLOW_REGISTRY = {"file_organization": FileOrganizationWorkflow}
