#!/usr/bin/env python3
"""
工厂筛选与比价工作流 - V2.8.0

适用场景：
- 筛选供应商/工厂
- 对比报价和资质
- 生成供应商评估报告
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class FactoryComparisonWorkflow(WorkflowBase):
    """工厂筛选与比价工作流"""
    
    name = "factory_comparison"
    description = "工厂筛选与比价 - 筛选供应商、对比报价、评估资质"
    version = "1.0.0"
    applicable_scenarios = [
        "供应商筛选",
        "工厂比价",
        "采购决策",
        "供应商评估"
    ]
    required_skills = ["xiaoyi-web-search", "docx"]
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "product_type": "产品类型（必填）",
            "quantity": "采购数量",
            "budget": "预算范围",
            "requirements": "特殊要求",
            "region": "地区偏好"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        if not input_data.get("product_type"):
            return False, "缺少必填参数: product_type"
        return True, "输入验证通过"
    
    def get_execution_order(self) -> List[str]:
        return [
            "search_factories",
            "collect_quotes",
            "verify_qualifications",
            "compare_prices",
            "generate_report"
        ]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {
            "factories": "工厂列表",
            "quotes": "报价对比",
            "qualifications": "资质评估",
            "recommendations": "推荐供应商",
            "report_file": "报告文件"
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {
            "must_have_factories": True,
            "min_factory_count": 3
        }
    
    def get_completion_criteria(self) -> List[str]:
        return [
            "已搜索工厂",
            "已收集报价",
            "已验证资质",
            "已生成对比报告"
        ]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "使用简化流程"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        if step_name == "search_factories":
            self.output["factories"] = [
                {"name": f"工厂{i}", "region": "广东", "rating": 4.5}
                for i in range(1, 6)
            ]
            return True
        elif step_name == "collect_quotes":
            self.output["quotes"] = [
                {"factory": f"工厂{i}", "price": 10 + i, "moq": 100}
                for i in range(1, 6)
            ]
            return True
        elif step_name == "verify_qualifications":
            self.output["qualifications"] = {"verified": 5, "pending": 0}
            return True
        elif step_name == "compare_prices":
            self.output["price_comparison"] = {"best": "工厂1", "avg": 12}
            return True
        elif step_name == "generate_report":
            self.output["recommendations"] = ["推荐工厂1", "备选工厂2"]
            self.output["report_file"] = "reports/工厂比价报告.md"
            return True
        return False

WORKFLOW_REGISTRY = {
    "factory_comparison": FactoryComparisonWorkflow
}
