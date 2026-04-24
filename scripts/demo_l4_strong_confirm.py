"""场景演示：L4 高风险强确认"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from safety_governor import PolicyEngine, ApprovalGate, RiskLevel, RiskPolicy
from device_capability_bus import CapabilityExecutor, DeviceCapabilityRequest


def demo_l4_strong_confirm():
    """演示：L4 高风险操作的强确认流程"""
    
    print("=" * 60)
    print("场景演示：L4 高风险强确认")
    print("=" * 60)
    
    # 1. 模拟高风险操作
    action = "自动点击游戏内的抽卡按钮"
    print(f"\n用户请求: {action}")
    
    # 2. 评估风险
    engine = PolicyEngine()
    assessment = engine.assess(action, {"context": "game"})
    
    print(f"\n风险评估:")
    print(f"  等级: {assessment.risk_level.value}")
    print(f"  策略: {assessment.policy.value}")
    print(f"  需要预览: {assessment.requires_preview}")
    print(f"  需要分步执行: {assessment.requires_stepwise}")
    
    # 3. L4 强确认流程
    preview = {}
    if assessment.policy == RiskPolicy.STRONG_CONFIRM:
        print(f"\n⚠️ 进入 L4 强确认流程:")
        
        # 3.1 生成预览
        preview = {
            "action": action,
            "target": "抽卡按钮",
            "location": "(540, 1200)",
            "consequence": "将消耗游戏货币进行抽卡",
            "estimated_cost": "100 钻石",
        }
        
        print(f"\n步骤 1: 操作预览")
        print(f"  动作: {preview['action']}")
        print(f"  目标: {preview['target']}")
        print(f"  位置: {preview['location']}")
        print(f"  后果: {preview['consequence']}")
        print(f"  预估消耗: {preview['estimated_cost']}")
        
        # 3.2 第一次确认
        print(f"\n步骤 2: 第一次确认（确认目标）")
        print(f"  提示: {assessment.confirmation_prompt}")
        print(f"  用户响应: 确认")
        
        # 3.3 第二次确认
        print(f"\n步骤 3: 第二次确认（确认后果）")
        print(f"  提示: 确认要消耗 100 钻石进行抽卡吗？")
        print(f"  用户响应: 确认")
        
        # 3.4 创建审批请求
        gate = ApprovalGate()
        request = gate.create_approval_request(
            action=action,
            risk_level=assessment.risk_level,
            preview_data=preview,
            confirmation_prompt="已确认目标和后果，是否执行？",
        )
        
        print(f"\n步骤 4: 最终确认")
        print(f"  审批ID: {request.approval_id}")
        print(f"  用户响应: 确认执行")
        
        # 3.5 执行
        result = gate.approve(request.approval_id, approver="user", note="双重确认通过")
        
        print(f"\n步骤 5: 执行")
        print(f"  执行: 点击 (540, 1200)")
        print(f"  结果: 抽卡成功")
        
        # 3.6 验证结果
        print(f"\n步骤 6: 验证结果")
        print(f"  页面状态: 抽卡结果页面")
        print(f"  钻石余额: 减少 100")
        
        # 3.7 记录审计
        print(f"\n步骤 7: 记录审计")
        print(f"  审计ID: {request.approval_id}")
        print(f"  全程已记录")
    
    print(f"\n✅ L4 强确认流程完成")
    
    return {
        "action": action,
        "assessment": {
            "risk_level": assessment.risk_level.value,
            "policy": assessment.policy.value,
        },
        "preview": preview,
        "approved": True,
    }


if __name__ == "__main__":
    result = demo_l4_strong_confirm()
    print(f"\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)
