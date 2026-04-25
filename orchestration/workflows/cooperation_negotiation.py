#!/usr/bin/env python3
"""
合作洽谈工作流 - V4.0.0
经销商-团长合作洽谈
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class CooperationNegotiationWorkflow(WorkflowBase):
    """合作洽谈工作流"""
    
    name = "cooperation_negotiation"
    description = "合作洽谈 - 生成合作方案、洽谈话术、协议模板"
    version = "1.0.0"
    applicable_scenarios = [
        "合作洽谈",
        "团长合作",
        "分销合作",
        "渠道合作"
    ]
    required_skills = ["dealer-leader-cooperation", "docx"]
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "leader_name": "团长名称（必填）",
            "category": "合作品类（必填）",
            "commission_rate": "佣金比例（必填）",
            "settlement_cycle": "结算周期（默认月结）",
            "support_items": "支持项目（可选）",
            "output_format": "输出格式（markdown/docx）"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        if not input_data.get("leader_name"):
            return False, "缺少必填参数: leader_name"
        if not input_data.get("category"):
            return False, "缺少必填参数: category"
        return True, "输入验证通过"
    
    def get_execution_order(self) -> List[str]:
        return [
            "generate_proposal",
            "generate_script",
            "generate_agreement",
            "generate_support_plan"
        ]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {
            "proposal": "合作方案",
            "script": "洽谈话术",
            "agreement": "协议模板",
            "support_plan": "支持计划"
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {"must_have_proposal": True}
    
    def get_completion_criteria(self) -> List[str]:
        return [
            "已生成合作方案",
            "已生成洽谈话术",
            "已生成协议模板"
        ]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "使用默认模板"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        leader_name = input_data.get("leader_name", "团长")
        category = input_data.get("category", "产品")
        commission = input_data.get("commission_rate", "10%")
        settlement = input_data.get("settlement_cycle", "月结")
        
        if step_name == "generate_proposal":
            self.output["proposal"] = f"""
# 合作方案

## 合作双方
- **甲方（经销商）**: [公司名称]
- **乙方（团长）**: {leader_name}

## 合作内容
- **合作品类**: {category}
- **合作模式**: 分销合作
- **佣金比例**: {commission}
- **结算周期**: {settlement}

## 甲方责任
1. 提供正品货源，保证产品质量
2. 提供产品素材（图片、视频、文案）
3. 提供售后支持
4. 按时结算佣金

## 乙方责任
1. 在社群/平台推广产品
2. 维护客户关系
3. 收集用户反馈
4. 遵守价格政策

## 合作期限
- 试用期：1个月
- 正式期：签订后1年
"""
            return True
        
        elif step_name == "generate_script":
            self.output["script"] = {
                "opening": f"您好{leader_name}，我是[公司]的[姓名]，看到您在{category}领域很有影响力...",
                "value_prop": f"我们提供{commission}的佣金，{settlement}结算，还有完整的素材和售后支持...",
                "closing": "您看什么时候方便，我们可以详细聊聊合作细节？",
                "objection_handling": {
                    "佣金太低": "我们可以根据销量阶梯调整，最高可达XX%",
                    "结算太慢": "我们可以提供周结或双周结选项",
                    "没做过": "我们有完整的培训体系，手把手教您"
                }
            }
            return True
        
        elif step_name == "generate_agreement":
            self.output["agreement"] = {
                "template": "dealer_leader_agreement.docx",
                "key_terms": [
                    "合作期限：1年",
                    f"佣金比例：{commission}",
                    f"结算周期：{settlement}",
                    "违约责任：按合同约定",
                    "争议解决：协商或诉讼"
                ]
            }
            return True
        
        elif step_name == "generate_support_plan":
            self.output["support_plan"] = {
                "training": "产品知识培训、销售技巧培训",
                "materials": "产品图片、视频、文案素材包",
                "promotion": "节日活动、新品推广支持",
                "after_sales": "7天无理由退换、质量问题包退"
            }
            return True
        
        return False

WORKFLOW_REGISTRY = {"cooperation_negotiation": CooperationNegotiationWorkflow}
