#!/usr/bin/env python3
"""
主播/团长合作筛选工作流 - V2.8.0
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class PartnerSelectionWorkflow(WorkflowBase):
    name = "partner_selection"
    description = "主播/团长合作筛选 - 筛选合作对象、评估合作价值"
    version = "1.0.0"
    applicable_scenarios = ["主播筛选", "团长合作", "达人合作"]
    required_skills = ["xiaoyi-web-search"]
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "partner_type": "合作类型（主播/团长）",
            "category": "品类",
            "budget": "预算",
            "followers_min": "最低粉丝数"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        if not input_data.get("partner_type"):
            return False, "缺少必填参数: partner_type"
        return True, "验证通过"
    
    def get_execution_order(self) -> List[str]:
        return ["search_partners", "analyze_data", "evaluate_fit", "generate_list"]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {"partners": "合作对象列表", "recommendations": "推荐名单"}
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {"min_partners": 5}
    
    def get_completion_criteria(self) -> List[str]:
        return ["已筛选合作对象", "已生成推荐名单"]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "简化筛选"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        if step_name == "search_partners":
            self.output["partners"] = [{"name": f"主播{i}", "followers": 10000 * i} for i in range(1, 6)]
        elif step_name == "analyze_data":
            self.output["analysis"] = {"avg_followers": 30000}
        elif step_name == "evaluate_fit":
            self.output["fit_scores"] = {"主播1": 0.9, "主播2": 0.8}
        elif step_name == "generate_list":
            self.output["recommendations"] = ["推荐主播1", "备选主播2"]
        return True

WORKFLOW_REGISTRY = {"partner_selection": PartnerSelectionWorkflow}
