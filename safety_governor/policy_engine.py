"""策略引擎"""

from typing import Dict, Any, Optional, List
from .risk_levels import RiskLevel, RiskPolicy, RiskAssessment, RISK_POLICY_MAP, BLOCKED_SCENARIOS


class PolicyEngine:
    """策略引擎"""
    
    def __init__(self):
        self._custom_rules: List[Dict[str, Any]] = []
    
    def assess(self, action: str, context: Optional[Dict[str, Any]] = None) -> RiskAssessment:
        """评估动作风险"""
        context = context or {}
        
        # 检查是否在 BLOCKED 场景中
        if self._is_blocked_scenario(action, context):
            return RiskAssessment(
                risk_level=RiskLevel.BLOCKED,
                policy=RiskPolicy.BLOCKED,
                blocked=True,
                reason=self._get_blocked_reason(action, context),
            )
        
        # 确定风险等级
        risk_level = self._determine_risk_level(action, context)
        policy = RISK_POLICY_MAP[risk_level]
        
        # 构建评估结果
        assessment = RiskAssessment(
            risk_level=risk_level,
            policy=policy,
            requires_confirmation=policy in [RiskPolicy.CONFIRM_ONCE, RiskPolicy.STRONG_CONFIRM],
            requires_preview=policy == RiskPolicy.STRONG_CONFIRM,
            requires_stepwise=policy == RiskPolicy.STRONG_CONFIRM,
            blocked=False,
        )
        
        # 设置确认提示
        if assessment.requires_confirmation:
            assessment.confirmation_prompt = self._generate_confirmation_prompt(action, risk_level)
        
        return assessment
    
    def _is_blocked_scenario(self, action: str, context: Dict[str, Any]) -> bool:
        """检查是否为 BLOCKED 场景"""
        # 检查场景标签
        scenario = context.get("scenario", "")
        if scenario in BLOCKED_SCENARIOS:
            return True
        
        # 检查关键词
        blocked_keywords = [
            "绕过反作弊", "盗号", "未授权支付", "批量骚扰",
            "规避风控", "竞技作弊", "挂机刷资源", "未授权交易",
        ]
        for keyword in blocked_keywords:
            if keyword in action or keyword in str(context):
                return True
        
        return False
    
    def _get_blocked_reason(self, action: str, context: Dict[str, Any]) -> str:
        """获取 BLOCKED 原因"""
        scenario = context.get("scenario", "")
        if scenario:
            return f"该操作涉及{scenario}，不能执行"
        return "该操作涉及违法/绕过平台限制/破坏公平/未授权风险，不能执行"
    
    def _determine_risk_level(self, action: str, context: Dict[str, Any]) -> RiskLevel:
        """确定风险等级"""
        action_lower = action.lower()
        
        # L4 高风险 - 游戏/支付/账号/隐私
        l4_keywords = ["支付", "转账", "账号", "密码", "隐私", "金融", "游戏", "抽卡", "道具", "资源消耗", "自动点击"]
        for kw in l4_keywords:
            if kw in action_lower:
                return RiskLevel.L4
        
        # L3 中高风险
        l3_keywords = ["删除", "拨电话", "重要修改", "批量删除"]
        for kw in l3_keywords:
            if kw in action_lower:
                return RiskLevel.L3
        
        # L2 中风险
        l2_keywords = ["发短信", "通知", "批量", "点击", "滑动", "输入"]
        for kw in l2_keywords:
            if kw in action_lower:
                return RiskLevel.L2
        
        # L1 低风险
        l1_keywords = ["创建", "写入", "更新", "备忘录", "日程", "闹钟"]
        for kw in l1_keywords:
            if kw in action_lower:
                return RiskLevel.L1
        
        # L0 无风险
        return RiskLevel.L0
    
    def _generate_confirmation_prompt(self, action: str, risk_level: RiskLevel) -> str:
        """生成确认提示"""
        if risk_level == RiskLevel.L4:
            return f"⚠️ 高风险操作：{action}\n\n该操作需要强确认：\n1. 先预览将要执行的动作\n2. 确认目标和后果\n3. 分步执行并验证每一步\n\n是否继续？"
        elif risk_level == RiskLevel.L3:
            return f"该操作需要确认：{action}\n\n是否继续？"
        else:
            return f"确认执行：{action}？"
    
    def add_custom_rule(self, rule: Dict[str, Any]):
        """添加自定义规则"""
        self._custom_rules.append(rule)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取策略指标"""
        return {
            "total_assessments": 0,
            "blocked_count": 0,
            "l4_count": 0,
            "l3_count": 0,
            "l2_count": 0,
            "l1_count": 0,
            "l0_count": 0,
        }
