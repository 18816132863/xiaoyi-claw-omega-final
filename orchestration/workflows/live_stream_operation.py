#!/usr/bin/env python3
"""
直播带货工作流 - V4.0.0
抖音/快手直播带货全流程
"""

from typing import Dict, List, Any
from orchestration.workflows.workflow_base import WorkflowBase

class LiveStreamOperationWorkflow(WorkflowBase):
    """直播带货工作流"""
    
    name = "live_stream_operation"
    description = "直播带货 - 选品、脚本、预热、直播、复盘全流程"
    version = "1.0.0"
    applicable_scenarios = [
        "直播带货",
        "直播脚本",
        "直播选品",
        "直播复盘"
    ]
    required_skills = ["douyin-shop-operation", "kuaishou-shop-operation"]
    
    def get_input_template(self) -> Dict[str, Any]:
        return {
            "platform": "平台（douyin/kuaishou）",
            "category": "产品品类（必填）",
            "duration": "直播时长（默认2小时）",
            "products": "产品列表（可选）",
            "target_sales": "目标销售额（可选）",
            "anchor_style": "主播风格（可选）"
        }
    
    def validate_input(self, input_data: Dict) -> tuple:
        if not input_data.get("category"):
            return False, "缺少必填参数: category"
        if input_data.get("platform") not in ["douyin", "kuaishou"]:
            return False, "platform 必须是 douyin 或 kuaishou"
        return True, "输入验证通过"
    
    def get_execution_order(self) -> List[str]:
        return [
            "select_products",
            "design_script",
            "create_preheat_content",
            "setup_live_room",
            "monitor_live",
            "analyze_results"
        ]
    
    def get_output_template(self) -> Dict[str, Any]:
        return {
            "products": "选品方案",
            "script": "直播脚本",
            "preheat": "预热内容",
            "live_config": "直播间配置",
            "monitor_data": "直播数据",
            "analysis": "复盘分析"
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        return {"must_have_products": True}
    
    def get_completion_criteria(self) -> List[str]:
        return [
            "已完成选品",
            "已生成脚本",
            "已准备预热内容",
            "已配置直播间"
        ]
    
    def get_fallback_logic(self, step_name: str, error: str) -> str:
        return "使用默认模板"
    
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        platform = input_data.get("platform", "douyin")
        category = input_data.get("category", "产品")
        duration = int(input_data.get("duration", 120))  # 分钟
        
        if step_name == "select_products":
            # 选品策略
            self.output["products"] = {
                "main_product": {
                    "name": f"{category}主推款",
                    "role": "主推",
                    "price_range": "中等价位",
                    "margin": "20-30%",
                    "time_slot": "黄金时段（开播30-60分钟）"
                },
                "traffic_product": {
                    "name": f"{category}引流款",
                    "role": "引流",
                    "price_range": "低价",
                    "margin": "5-10%",
                    "time_slot": "开场（0-30分钟）"
                },
                "profit_product": {
                    "name": f"{category}利润款",
                    "role": "利润",
                    "price_range": "中高价位",
                    "margin": "30-50%",
                    "time_slot": "稳定期（60-90分钟）"
                },
                "strategy": "引流款拉人气 → 主推款冲销量 → 利润款赚利润"
            }
            return True
        
        elif step_name == "design_script":
            # 直播脚本
            style = "老铁风格" if platform == "kuaishou" else "专业风格"
            greeting = "老铁们好！" if platform == "kuaishou" else "大家好！"
            
            self.output["script"] = {
                "style": style,
                "duration": f"{duration}分钟",
                "segments": [
                    {
                        "time": "0-5分钟",
                        "content": f"{greeting}欢迎来到直播间",
                        "action": "暖场、互动、预告福利"
                    },
                    {
                        "time": "5-30分钟",
                        "content": "介绍引流款产品",
                        "action": "限时秒杀、制造紧迫感"
                    },
                    {
                        "time": "30-60分钟",
                        "content": "主推款产品介绍",
                        "action": "详细讲解、用户见证、互动答疑"
                    },
                    {
                        "time": "60-90分钟",
                        "content": "利润款产品介绍",
                        "action": "品质强调、价值塑造"
                    },
                    {
                        "time": "90-120分钟",
                        "content": "返场、收尾",
                        "action": "爆款返场、感谢粉丝、预告下场"
                    }
                ],
                "key_phrases": [
                    "限时限量，手慢无",
                    "今天直播间专享价",
                    "拍下立减XX元",
                    "赠品仅剩XX份"
                ] if platform == "douyin" else [
                    "老铁们，这个价格真的值",
                    "给主播点点关注",
                    "双击666",
                    "下单支持一下"
                ]
            }
            return True
        
        elif step_name == "create_preheat_content":
            # 预热内容
            self.output["preheat"] = {
                "short_videos": [
                    {"type": "产品预告", "content": f"明天{category}直播，价格惊喜"},
                    {"type": "福利预告", "content": "直播间专属福利，先到先得"},
                    {"type": "倒计时", "content": "直播倒计时，最后X小时"}
                ],
                "poster": {
                    "title": f"{category}专场直播",
                    "highlights": ["限时特价", "买一送一", "直播间专享"],
                    "time": "今晚8点"
                },
                "notification": "开播前1小时发送粉丝通知"
            }
            return True
        
        elif step_name == "setup_live_room":
            # 直播间配置
            self.output["live_config"] = {
                "title": f"{category}专场 | 限时特价",
                "cover": "产品主图+价格标签",
                "category": category,
                "tags": [category, "直播带货", "限时特价"],
                "coupons": [
                    {"name": "新人券", "amount": 10, "condition": 50},
                    {"name": "满减券", "amount": 20, "condition": 100}
                ],
                "lottery": {
                    "time": "每30分钟",
                    "prize": "小礼品/优惠券"
                }
            }
            return True
        
        elif step_name == "monitor_live":
            # 直播监控指标
            self.output["monitor_data"] = {
                "real_time_metrics": [
                    "在线人数",
                    "新增关注",
                    "商品点击",
                    "下单转化",
                    "GMV"
                ],
                "alert_thresholds": {
                    "online_drop": "在线人数下降超过30%",
                    "low_conversion": "转化率低于2%",
                    "high_refund": "退款率超过5%"
                },
                "optimization_actions": {
                    "online_drop": "发福袋、互动、秒杀",
                    "low_conversion": "强调价格优势、限时限量",
                    "high_refund": "检查产品描述、调整话术"
                }
            }
            return True
        
        elif step_name == "analyze_results":
            # 复盘分析
            self.output["analysis"] = {
                "metrics": {
                    "total_viewers": "总观看人数",
                    "peak_online": "最高在线",
                    "total_sales": "总销售额",
                    "conversion_rate": "转化率",
                    "avg_order_value": "客单价"
                },
                "product_analysis": "各产品销量、转化率对比",
                "time_analysis": "各时段流量、转化对比",
                "improvement": [
                    "优化开场话术，提高留存",
                    "调整产品顺序，优化节奏",
                    "增加互动环节，提高参与"
                ]
            }
            return True
        
        return False

WORKFLOW_REGISTRY = {"live_stream_operation": LiveStreamOperationWorkflow}
