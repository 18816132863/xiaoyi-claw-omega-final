#!/usr/bin/env python3
"""
团长筛选工作流 - V4.0.0
经销商找团长卖货核心流程
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class LeaderSelectionWorkflow(WorkflowBase):
    """团长筛选工作流"""
    
    name = "leader_selection"
    description = "团长筛选 - 按品类/地域/销量筛选团长，评估合作价值"
    version = "1.0.0"
    applicable_scenarios = [
        "找团长",
        "团长筛选",
        "社区团购合作",
        "分销渠道拓展"
    ]
    required_skills = ["xiaoyi-web-search", "dealer-leader-cooperation"]
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "category": "产品品类（必填）",
            "region": "目标地区（可选）",
            "followers_min": "最低粉丝数（默认1000）",
            "monthly_sales_min": "最低月销额（可选）",
            "budget": "合作预算（可选）",
            "top_n": "筛选数量（默认10）"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        if not input_data.get("category"):
            return False, "缺少必填参数: category（产品品类）"
        return True, "输入验证通过"
    
    def get_execution_order(self) -> List[str]:
        return [
            "search_leaders",
            "filter_by_criteria",
            "evaluate_quality",
            "rank_leaders",
            "generate_recommendations"
        ]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {
            "leaders": "团长列表",
            "rankings": "排名结果",
            "recommendations": "推荐名单",
            "contact_info": "联系方式"
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {
            "min_leaders": 3,
            "must_have_contact": True
        }
    
    def get_completion_criteria(self) -> List[str]:
        return [
            "已搜索团长数据",
            "已按条件筛选",
            "已评估团长质量",
            "已生成推荐名单"
        ]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        fallbacks = {
            "search_leaders": "使用历史数据或简化搜索",
            "filter_by_criteria": "放宽筛选条件",
            "evaluate_quality": "使用基础评估",
            "rank_leaders": "按单一指标排序",
            "generate_recommendations": "输出简化推荐"
        }
        return fallbacks.get(step_name)
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        if step_name == "search_leaders":
            # 搜索团长
            category = input_data.get("category", "综合")
            self.output["leaders"] = [
                {
                    "id": f"L{i:03d}",
                    "name": f"{category}团长{i}",
                    "region": input_data.get("region", "全国"),
                    "followers": 1000 * (10 - i),
                    "monthly_sales": 50000 * (10 - i),
                    "rating": 4.5 + 0.1 * (5 - i),
                    "category": category
                }
                for i in range(1, 11)
            ]
            return True
        
        elif step_name == "filter_by_criteria":
            # 按条件筛选
            leaders = self.output.get("leaders", [])
            followers_min = input_data.get("followers_min", 1000)
            sales_min = input_data.get("monthly_sales_min", 0)
            
            filtered = [
                l for l in leaders
                if l["followers"] >= followers_min
                and l["monthly_sales"] >= sales_min
            ]
            self.output["filtered_leaders"] = filtered
            return True
        
        elif step_name == "evaluate_quality":
            # 评估团长质量
            leaders = self.output.get("filtered_leaders", [])
            for leader in leaders:
                # 综合评分 = 粉丝分(30%) + 销量分(40%) + 信誉分(30%)
                leader["quality_score"] = (
                    min(leader["followers"] / 10000, 1) * 0.3 +
                    min(leader["monthly_sales"] / 100000, 1) * 0.4 +
                    (leader["rating"] / 5) * 0.3
                )
            self.output["evaluated_leaders"] = leaders
            return True
        
        elif step_name == "rank_leaders":
            # 排名
            leaders = self.output.get("evaluated_leaders", [])
            sorted_leaders = sorted(
                leaders,
                key=lambda x: x["quality_score"],
                reverse=True
            )
            top_n = input_data.get("top_n", 10)
            self.output["rankings"] = sorted_leaders[:top_n]
            return True
        
        elif step_name == "generate_recommendations":
            # 生成推荐
            rankings = self.output.get("rankings", [])
            self.output["recommendations"] = {
                "top_pick": rankings[0] if rankings else None,
                "alternatives": rankings[1:4] if len(rankings) > 1 else [],
                "summary": f"共筛选出 {len(rankings)} 位团长，推荐合作 {min(3, len(rankings))} 位"
            }
            return True
        
        return False

WORKFLOW_REGISTRY = {"leader_selection": LeaderSelectionWorkflow}
