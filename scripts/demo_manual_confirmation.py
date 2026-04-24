"""场景演示：人工确认闭环"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from safety_governor import PolicyEngine, ApprovalGate, RiskLevel
from closed_loop_verifier import AuditWriter


def demo_manual_confirmation():
    """演示：处理 uncertain 记录的人工确认闭环"""
    
    print("=" * 60)
    print("场景演示：人工确认闭环")
    print("=" * 60)
    
    # 1. 模拟 uncertain 记录
    uncertain_record = {
        "invocation_id": "inv_12345",
        "capability": "MESSAGE_SENDING",
        "status": "result_uncertain",
        "error": "timeout",
        "user_message": "消息发送超时，结果不确定",
    }
    
    print(f"\n发现 uncertain 记录:")
    print(f"  ID: {uncertain_record['invocation_id']}")
    print(f"  能力: {uncertain_record['capability']}")
    print(f"  状态: {uncertain_record['status']}")
    print(f"  原因: {uncertain_record['error']}")
    
    # 2. 评估风险
    engine = PolicyEngine()
    assessment = engine.assess("确认消息发送结果", {"original_capability": uncertain_record["capability"]})
    
    print(f"\n风险评估:")
    print(f"  等级: {assessment.risk_level.value}")
    print(f"  策略: {assessment.policy.value}")
    print(f"  需要确认: {assessment.requires_confirmation}")
    
    # 3. 创建审批请求
    gate = ApprovalGate()
    request = gate.create_approval_request(
        action="确认消息发送结果",
        risk_level=assessment.risk_level,
        preview_data=uncertain_record,
        confirmation_prompt="消息发送超时，请确认是否发送成功？",
    )
    
    print(f"\n审批请求已创建:")
    print(f"  ID: {request.approval_id}")
    print(f"  提示: {request.confirmation_prompt}")
    
    # 4. 模拟用户确认
    print(f"\n用户确认: 发送成功")
    result = gate.approve(request.approval_id, approver="user", note="用户确认消息已送达")
    
    print(f"\n审批结果:")
    print(f"  批准: {result.approved}")
    print(f"  时间: {result.approved_at}")
    
    # 5. 写入审计
    audit = AuditWriter()
    audit.write({
        "event": "manual_confirmation",
        "invocation_id": uncertain_record["invocation_id"],
        "result": "confirmed_success",
        "approver": "user",
    })
    
    print(f"\n✅ 审计记录已写入")
    
    return {
        "uncertain_record": uncertain_record,
        "assessment": {
            "risk_level": assessment.risk_level.value,
            "policy": assessment.policy.value,
        },
        "approval_result": {
            "approved": result.approved,
            "approval_id": result.approval_id,
        },
    }


if __name__ == "__main__":
    result = demo_manual_confirmation()
    print(f"\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)
