#!/usr/bin/env python3
"""
店铺启动步骤工作流 - V2.8.0
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class StoreLaunchWorkflow(WorkflowBase):
    name = "store_launch"
    description = "店铺启动 - 新店铺启动全流程指导"
    version = "1.0.0"
    applicable_scenarios = ["新店启动", "店铺开设", "开店指导"]
    required_skills = ["docx"]
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "platform": "平台（淘宝/京东/拼多多）",
            "category": "主营类目",
            "budget": "启动预算"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        if not input_data.get("platform"):
            return False, "缺少必填参数: platform"
        return True, "验证通过"
    
    def get_execution_order(self) -> List[str]:
        return [
            "check_requirements",
            "prepare_documents",
            "setup_store",
            "upload_products",
            "configure_logistics",
            "launch_promotion"
        ]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {
            "checklist": "启动清单",
            "timeline": "时间线",
            "documents": "所需材料",
            "report_file": "启动指南"
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {"all_steps_completed": True}
    
    def get_completion_criteria(self) -> List[str]:
        return ["已完成所有启动步骤", "已生成启动指南"]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "跳过非必要步骤"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        steps_output = {
            "check_requirements": {"status": "已检查资质要求"},
            "prepare_documents": {"documents": ["营业执照", "身份证", "银行卡"]},
            "setup_store": {"status": "店铺已创建"},
            "upload_products": {"products": 10},
            "configure_logistics": {"logistics": "已配置"},
            "launch_promotion": {"promotion": "已启动"}
        }
        if step_name in steps_output:
            self.output[step_name] = steps_output[step_name]
            return True
        return False

WORKFLOW_REGISTRY = {"store_launch": StoreLaunchWorkflow}
