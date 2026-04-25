#!/usr/bin/env python3
"""
佣金设计工作流 - V4.0.0
经销商-团长佣金体系设计
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class CommissionDesignWorkflow(WorkflowBase):
    """佣金设计工作流"""
    
    name = "commission_design"
    description = "佣金设计 - 设计团长佣金体系、阶梯佣金、促销佣金"
    version = "1.0.0"
    applicable_scenarios = [
        "设计佣金",
        "佣金方案",
        "分销佣金",
        "团长佣金"
    ]
    required_skills = ["dealer-leader-cooperation"]
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "category": "产品品类（必填）",
            "gross_margin": "毛利率%（必填）",
            "avg_order_value": "客单价（可选）",
            "target_sales": "目标月销额（可选）",
            "competition_level": "竞争程度（高/中/低）"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        if not input_data.get("category"):
            return False, "缺少必填参数: category"
        if not input_data.get("gross_margin"):
            return False, "缺少必填参数: gross_margin（毛利率）"
        return True, "输入验证通过"
    
    def get_execution_order(self) -> List[str]:
        return [
            "analyze_margin",
            "design_base_commission",
            "design_tiered_commission",
            "design_promotion_commission",
            "generate_scheme"
        ]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {
            "margin_analysis": "毛利分析",
            "base_commission": "基础佣金",
            "tiered_commission": "阶梯佣金",
            "promotion_commission": "促销佣金",
            "scheme": "完整方案"
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {
            "commission_within_margin": True,
            "min_commission_rate": 0.05
        }
    
    def get_completion_criteria(self) -> List[str]:
        return [
            "已分析毛利空间",
            "已设计基础佣金",
            "已设计阶梯佣金",
            "已生成完整方案"
        ]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "使用默认佣金比例"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        gross_margin = float(input_data.get("gross_margin", 30))
        
        if step_name == "analyze_margin":
            # 分析毛利空间
            self.output["margin_analysis"] = {
                "gross_margin": gross_margin,
                "available_for_commission": gross_margin * 0.6,  # 60%可用于佣金
                "cost_ratio": 100 - gross_margin,
                "profit_target": gross_margin * 0.3  # 30%作为利润目标
            }
            return True
        
        elif step_name == "design_base_commission":
            # 设计基础佣金
            available = gross_margin * 0.6
            # 基础佣金 = 可用空间的50%
            base_rate = available * 0.5
            
            self.output["base_commission"] = {
                "rate": round(base_rate, 1),
                "description": f"基础佣金率 {round(base_rate, 1)}%",
                "example": f"客单价100元，佣金 {round(base_rate, 1)} 元"
            }
            return True
        
        elif step_name == "design_tiered_commission":
            # 设计阶梯佣金
            base_rate = self.output["base_commission"]["rate"]
            
            self.output["tiered_commission"] = {
                "tiers": [
                    {"level": "青铜团长", "sales_min": 0, "sales_max": 10000, "rate": base_rate},
                    {"level": "白银团长", "sales_min": 10000, "sales_max": 50000, "rate": base_rate + 1},
                    {"level": "黄金团长", "sales_min": 50000, "sales_max": 100000, "rate": base_rate + 2},
                    {"level": "钻石团长", "sales_min": 100000, "sales_max": 999999, "rate": base_rate + 3}
                ],
                "description": "月销售额越高，佣金比例越高"
            }
            return True
        
        elif step_name == "design_promotion_commission":
            # 设计促销佣金
            base_rate = self.output["base_commission"]["rate"]
            
            self.output["promotion_commission"] = {
                "new_product": base_rate + 2,  # 新品推广加2%
                "clearance": base_rate + 3,     # 清仓加3%
                "festival": base_rate + 1.5,    # 节日促销加1.5%
                "first_order": base_rate + 5,   # 首单加5%
                "description": "促销活动额外佣金激励"
            }
            return True
        
        elif step_name == "generate_scheme":
            # 生成完整方案
            self.output["scheme"] = {
                "category": input_data.get("category"),
                "gross_margin": gross_margin,
                "base_commission": self.output["base_commission"],
                "tiered_commission": self.output["tiered_commission"],
                "promotion_commission": self.output["promotion_commission"],
                "settlement_cycle": "月结",
                "payment_method": "银行转账/微信/支付宝",
                "summary": f"""
## 佣金方案总结

- **品类**: {input_data.get('category')}
- **毛利率**: {gross_margin}%
- **基础佣金**: {self.output['base_commission']['rate']}%
- **阶梯佣金**: 青铜{self.output['tiered_commission']['tiers'][0]['rate']}% → 钻石{self.output['tiered_commission']['tiers'][3]['rate']}%
- **促销佣金**: 新品+2%, 清仓+3%, 节日+1.5%
- **结算周期**: 月结
"""
            }
            return True
        
        return False

WORKFLOW_REGISTRY = {"commission_design": CommissionDesignWorkflow}
