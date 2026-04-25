#!/usr/bin/env python3
"""
达人合作工作流 - V4.0.0
抖音/快手达人筛选与合作
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class InfluencerCooperationWorkflow(WorkflowBase):
    """达人合作工作流"""
    
    name = "influencer_cooperation"
    description = "达人合作 - 筛选达人、设计方案、谈判签约、效果追踪"
    version = "1.0.0"
    applicable_scenarios = [
        "找达人",
        "达人合作",
        "达人筛选",
        "达人带货"
    ]
    required_skills = ["douyin-shop-operation", "kuaishou-shop-operation", "dealer-leader-cooperation"]
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "platform": "平台（douyin/kuaishou）",
            "category": "产品品类（必填）",
            "followers_min": "最低粉丝数（默认1万）",
            "budget": "合作预算（可选）",
            "cooperation_type": "合作类型（纯佣/混合/年框）",
            "top_n": "筛选数量（默认10）"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        if not input_data.get("category"):
            return False, "缺少必填参数: category"
        return True, "输入验证通过"
    
    def get_execution_order(self) -> List[str]:
        return [
            "search_influencers",
            "filter_influencers",
            "evaluate_influencers",
            "design_proposal",
            "generate_contract"
        ]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {
            "influencers": "达人列表",
            "rankings": "排名结果",
            "proposal": "合作方案",
            "contract": "合同模板"
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {"min_influencers": 3}
    
    def get_completion_criteria(self) -> List[str]:
        return [
            "已筛选达人",
            "已评估达人价值",
            "已生成合作方案"
        ]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "使用默认筛选条件"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        platform = input_data.get("platform", "douyin")
        category = input_data.get("category", "产品")
        followers_min = int(input_data.get("followers_min", 10000))
        coop_type = input_data.get("cooperation_type", "纯佣")
        
        if step_name == "search_influencers":
            # 搜索达人
            self.output["influencers"] = [
                {
                    "id": f"I{i:03d}",
                    "name": f"{category}达人{i}",
                    "platform": platform,
                    "followers": followers_min * (10 - i),
                    "avg_views": followers_min * (10 - i) * 0.1,
                    "engagement_rate": 3 + 0.5 * (5 - i),
                    "category": category,
                    "price_per_video": 1000 * (10 - i) if coop_type != "纯佣" else 0,
                    "commission_rate": 15 + i
                }
                for i in range(1, 11)
            ]
            return True
        
        elif step_name == "filter_influencers":
            # 筛选达人
            influencers = self.output.get("influencers", [])
            budget = input_data.get("budget")
            
            filtered = influencers
            if budget:
                filtered = [i for i in filtered if i["price_per_video"] <= budget]
            
            self.output["filtered_influencers"] = filtered
            return True
        
        elif step_name == "evaluate_influencers":
            # 评估达人
            influencers = self.output.get("filtered_influencers", [])
            for inf in influencers:
                # 综合评分 = 粉丝分(25%) + 互动分(35%) + 转化分(25%) + 性价比(15%)
                inf["score"] = (
                    min(inf["followers"] / 100000, 1) * 0.25 +
                    min(inf["engagement_rate"] / 10, 1) * 0.35 +
                    min(inf["avg_views"] / 10000, 1) * 0.25 +
                    (1 - min(inf["commission_rate"] / 30, 1)) * 0.15
                )
            
            sorted_inf = sorted(influencers, key=lambda x: x["score"], reverse=True)
            top_n = int(input_data.get("top_n", 10))
            self.output["rankings"] = sorted_inf[:top_n]
            return True
        
        elif step_name == "design_proposal":
            # 设计合作方案
            rankings = self.output.get("rankings", [])
            top_pick = rankings[0] if rankings else None
            
            if top_pick:
                self.output["proposal"] = {
                    "influencer": top_pick["name"],
                    "cooperation_type": coop_type,
                    "commission_rate": f"{top_pick['commission_rate']}%",
                    "price_per_video": f"¥{top_pick['price_per_video']}" if top_pick['price_per_video'] > 0 else "无坑位费",
                    "settlement": "月结",
                    "support": [
                        "提供产品素材",
                        "提供样品",
                        "提供售后支持"
                    ],
                    "kpi": {
                        "min_sales": "月销售额≥1万",
                        "min_videos": "月发布≥4条",
                        "min_lives": "月直播≥2场"
                    }
                }
            return True
        
        elif step_name == "generate_contract":
            # 生成合同
            proposal = self.output.get("proposal", {})
            self.output["contract"] = {
                "template": "influencer_cooperation_contract.docx",
                "key_terms": [
                    f"合作类型：{proposal.get('cooperation_type', '纯佣')}",
                    f"佣金比例：{proposal.get('commission_rate', '15%')}",
                    f"坑位费：{proposal.get('price_per_video', '无')}",
                    f"结算周期：{proposal.get('settlement', '月结')}",
                    "合作期限：3个月",
                    "违约责任：按合同约定"
                ]
            }
            return True
        
        return False

WORKFLOW_REGISTRY = {"influencer_cooperation": InfluencerCooperationWorkflow}
