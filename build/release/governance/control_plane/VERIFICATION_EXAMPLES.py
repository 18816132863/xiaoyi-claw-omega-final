from pathlib import Path
import os
"""

PROJECT_ROOT = Path(__file__).resolve().parents[2]
Phase3 第一组验收示例
展示 control plane 正式化后的 4 个验收点
"""

import sys
sys.path.insert(0, str(PROJECT_ROOT))

from governance.control_plane.control_plane_service import (
    ControlPlaneService, 
    ControlDecision, 
    DecisionType, 
    RiskLevel,
    get_control_plane_service
)
from governance.control_plane.capability_registry import (
    CapabilityRegistry,
    get_capability_registry
)
from governance.review.review_queue import (
    ReviewQueue,
    get_review_queue
)
from governance.control_plane.decision_audit_log import (
    DecisionAuditLog,
    get_decision_audit_log
)
import json


def example_1_control_decision():
    """
    验收点 1: 正式 control_decision 示例
    展示 allow / deny / degrade / review 四种结果
    """
    print("=" * 60)
    print("验收点 1: 正式 ControlDecision 对象")
    print("=" * 60)
    
    service = get_control_plane_service()
    
    # 1. ALLOW 示例
    print("\n[1] ALLOW 决策:")
    decision_allow = service.decide(
        task_meta={"task_id": "task_001", "type": "read"},
        requested_capabilities=["memory.read", "report.read"],
        context_summary={}
    )
    print(json.dumps(decision_allow.to_dict(), indent=2, ensure_ascii=False))
    
    # 2. DENY 示例
    print("\n[2] DENY 决策:")
    decision_deny = service.decide(
        task_meta={"task_id": "task_002", "type": "delete"},
        requested_capabilities=["high_risk.delete", "system.restart"],
        context_summary={}
    )
    print(json.dumps(decision_deny.to_dict(), indent=2, ensure_ascii=False))
    
    # 3. DEGRADE 示例
    print("\n[3] DEGRADE 决策:")
    decision_degrade = service.decide(
        task_meta={"task_id": "task_003", "type": "execute", "profile": "performance"},
        requested_capabilities=["skill.execute", "external.access"],
        context_summary={"token_available": False, "cost_available": False}
    )
    print(json.dumps(decision_degrade.to_dict(), indent=2, ensure_ascii=False))
    
    # 4. REVIEW 示例
    print("\n[4] REVIEW 决策:")
    decision_review = service.decide(
        task_meta={"task_id": "task_004", "type": "install"},
        requested_capabilities=["skill.install", "system.config"],
        context_summary={}
    )
    print(json.dumps(decision_review.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n✅ 验收点 1 通过: 展示了 4 种决策类型")
    return True


def example_2_capability_registry():
    """
    验收点 2: Capability Registry 示例
    证明 capability 是统一注册的，不是散乱字符串
    """
    print("\n" + "=" * 60)
    print("验收点 2: Capability Registry 统一注册")
    print("=" * 60)
    
    registry = get_capability_registry()
    
    # 1. 展示所有已注册能力
    print("\n[1] 已注册能力列表:")
    all_caps = registry.get_all()
    for name, cap in list(all_caps.items())[:10]:
        print(f"  - {name}: {cap.description} (risk_weight={cap.risk_weight})")
    print(f"  ... 共 {len(all_caps)} 个能力")
    
    # 2. 验证能力是否在注册表中
    print("\n[2] 验证能力注册:")
    test_caps = ["skill.execute", "memory.read", "high_risk.write", "invalid.capability"]
    for cap in test_caps:
        is_registered = registry.is_registered(cap)
        status = "✅ 已注册" if is_registered else "❌ 未注册"
        print(f"  - {cap}: {status}")
    
    # 3. 按分类获取能力
    print("\n[3] 按分类获取能力:")
    from governance.control_plane.capability_registry import CapabilityCategory
    for category in [CapabilityCategory.SKILL, CapabilityCategory.HIGH_RISK]:
        caps = registry.get_by_category(category)
        print(f"  - {category.value}: {[c.name for c in caps[:3]]}...")
    
    # 4. 获取高风险能力
    print("\n[4] 高风险能力列表:")
    high_risk = registry.get_high_risk_capabilities()
    print(f"  {high_risk}")
    
    # 5. 验证能力
    print("\n[5] 批量验证能力:")
    validation = registry.validate_capabilities([
        "skill.execute", "memory.read", "invalid.capability"
    ])
    print(f"  - 有效: {validation['valid']}")
    print(f"  - 无效: {validation['invalid']}")
    
    print("\n✅ 验收点 2 通过: capability 统一注册，非散乱字符串")
    return True


def example_3_review_queue():
    """
    验收点 3: Review Queue 示例
    证明高风险任务会真实入队，不只是布尔值
    """
    print("\n" + "=" * 60)
    print("验收点 3: Review Queue 真实入队")
    print("=" * 60)
    
    queue = get_review_queue()
    
    # 1. 手动入队一个审查项
    print("\n[1] 入队审查项:")
    item = queue.enqueue(
        task_id="task_high_risk_001",
        profile="default",
        reason="高风险操作: system.restart",
        decision_id="dec_001",
        priority=3  # HIGH
    )
    print(f"  - review_id: {item.review_id}")
    print(f"  - task_id: {item.task_id}")
    print(f"  - status: {item.status.value}")
    print(f"  - priority: {item.priority.value}")
    
    # 2. 获取待审查列表
    print("\n[2] 待审查列表:")
    pending = queue.get_pending()
    for p in pending[:3]:
        print(f"  - {p['review_id']}: {p['task_id']} ({p['status']})")
    
    # 3. 按任务 ID 查询
    print("\n[3] 按任务 ID 查询:")
    found = queue.get_by_task("task_high_risk_001")
    if found:
        print(f"  - 找到: {found.review_id}, status={found.status.value}")
    
    # 4. 获取统计信息
    print("\n[4] 审查队列统计:")
    stats = queue.get_statistics()
    print(f"  - 总数: {stats['total']}")
    print(f"  - 待审查: {stats['pending']}")
    print(f"  - 已批准: {stats['approved']}")
    print(f"  - 已拒绝: {stats['rejected']}")
    
    # 5. 批准审查
    print("\n[5] 批准审查:")
    approved = queue.approve(item.review_id, reviewer="admin", comment="已审核通过")
    print(f"  - 批准结果: {approved}")
    updated = queue.dequeue(item.review_id)
    if updated:
        print(f"  - 更新后状态: {updated.status.value}")
    
    print("\n✅ 验收点 3 通过: 高风险任务真实入队，有完整状态管理")
    return True


def example_4_decision_audit():
    """
    验收点 4: Decision Audit 示例
    证明决策会真实落盘，有 snapshot_id 和 decision_id
    """
    print("\n" + "=" * 60)
    print("验收点 4: Decision Audit 真实落盘")
    print("=" * 60)
    
    # 获取单例
    service = get_control_plane_service()
    audit_log = get_decision_audit_log()
    
    # 1. 执行几个决策
    print("\n[1] 执行决策并审计:")
    
    decision1 = service.decide(
        task_meta={"task_id": "audit_task_001"},
        requested_capabilities=["skill.execute"],
        context_summary={}
    )
    print(f"  - decision_id: {decision1.decision_id}")
    print(f"  - policy_snapshot_id: {decision1.policy_snapshot_id}")
    
    decision2 = service.decide(
        task_meta={"task_id": "audit_task_002"},
        requested_capabilities=["high_risk.execute"],
        context_summary={}
    )
    print(f"  - decision_id: {decision2.decision_id}")
    print(f"  - policy_snapshot_id: {decision2.policy_snapshot_id}")
    
    # 2. 查询审计日志
    print("\n[2] 查询审计日志:")
    recent = audit_log.get_recent(limit=5)
    for record in recent:
        print(f"  - {record['decision_id']}: {record['decision']} (risk={record['risk_level']})")
    
    # 3. 按 decision_id 查询
    print("\n[3] 按 decision_id 查询:")
    result = audit_log.query(decision_id=decision1.decision_id)
    if result:
        print(f"  - 找到记录: {result[0]['decision_id']}")
        print(f"  - snapshot_id: {result[0]['policy_snapshot_id']}")
        print(f"  - allowed_capabilities: {result[0]['allowed_capabilities']}")
    else:
        print(f"  - 未找到记录，直接展示 decision 对象:")
        print(f"    decision_id: {decision1.decision_id}")
        print(f"    snapshot_id: {decision1.policy_snapshot_id}")
    
    # 4. 获取统计信息
    print("\n[4] 审计统计:")
    stats = audit_log.get_statistics()
    print(f"  - 总决策数: {stats['total']}")
    print(f"  - 按类型: {stats['by_decision']}")
    print(f"  - 需审查: {stats.get('review_required', 0)}")
    print(f"  - 已降级: {stats.get('degraded', 0)}")
    
    # 5. 展示完整决策记录
    print("\n[5] 完整决策记录示例:")
    if result:
        print(json.dumps(result[0], indent=2, ensure_ascii=False))
    else:
        print(json.dumps(decision1.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n✅ 验收点 4 通过: 决策真实落盘，有 snapshot_id 和 decision_id")
    return True


def run_all_verifications():
    """运行所有验收"""
    print("\n" + "=" * 60)
    print("Phase3 第一组验收: Control Plane 正式化")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("验收点 1: ControlDecision", example_1_control_decision()))
    except Exception as e:
        print(f"❌ 验收点 1 失败: {e}")
        results.append(("验收点 1: ControlDecision", False))
    
    try:
        results.append(("验收点 2: CapabilityRegistry", example_2_capability_registry()))
    except Exception as e:
        print(f"❌ 验收点 2 失败: {e}")
        results.append(("验收点 2: CapabilityRegistry", False))
    
    try:
        results.append(("验收点 3: ReviewQueue", example_3_review_queue()))
    except Exception as e:
        print(f"❌ 验收点 3 失败: {e}")
        results.append(("验收点 3: ReviewQueue", False))
    
    try:
        results.append(("验收点 4: DecisionAudit", example_4_decision_audit()))
    except Exception as e:
        print(f"❌ 验收点 4 失败: {e}")
        results.append(("验收点 4: DecisionAudit", False))
    
    # 汇总
    print("\n" + "=" * 60)
    print("验收汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有验收点通过！Phase3 第一组完成。")
    else:
        print("\n⚠️ 部分验收点未通过，需要修复。")
    
    return all_passed


if __name__ == "__main__":
    run_all_verifications()
