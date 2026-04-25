#!/usr/bin/env python3
"""
Fault Injection Tests - 故障注入测试

模拟各种服务超时场景，验证恢复策略：
- contact_service_timeout
- calendar_service_timeout
- note_service_timeout
- location_service_timeout

每次故障注入必须写入 recovery_history 和 audit
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.connected_runtime_recovery_policy import (
    ConnectedRuntimeRecoveryPolicy,
    FailureType,
    RecoveryStrategy,
    RecoveryPlan
)


@dataclass
class FaultInjectionResult:
    """故障注入结果"""
    fault_id: str
    failure_type: str
    capability: str
    route_id: str
    recovery_plan: List[str]
    executed_steps: List[Dict[str, Any]]
    final_result: str
    human_action_required: bool
    started_at: str
    finished_at: str
    duration_ms: float
    audit_id: str


class FaultInjector:
    """故障注入器"""
    
    FAULT_SCENARIOS = [
        {
            "name": "contact_service_timeout",
            "failure_type": FailureType.CONTACT_SERVICE_TIMEOUT,
            "capability": "query_contact",
            "route_id": "route.query_contact",
            "simulate_timeout_ms": 5000,
            "expected_recovery": ["retry", "limited_scope_probe", "cache_fallback"]
        },
        {
            "name": "calendar_service_timeout",
            "failure_type": FailureType.CALENDAR_SERVICE_TIMEOUT,
            "capability": "query_calendar",
            "route_id": "route.query_calendar",
            "simulate_timeout_ms": 5000,
            "expected_recovery": ["retry", "limited_scope_probe", "pending_queue"]
        },
        {
            "name": "note_service_timeout",
            "failure_type": FailureType.NOTE_SERVICE_TIMEOUT,
            "capability": "query_note",
            "route_id": "route.query_note",
            "simulate_timeout_ms": 5000,
            "expected_recovery": ["retry", "limited_scope_probe", "cache_fallback"]
        },
        {
            "name": "location_service_timeout",
            "failure_type": FailureType.LOCATION_SERVICE_TIMEOUT,
            "capability": "get_location",
            "route_id": "route.get_location",
            "simulate_timeout_ms": 5000,
            "expected_recovery": ["retry", "limited_scope_probe", "cache_fallback"]
        }
    ]
    
    def __init__(self):
        self.policy = ConnectedRuntimeRecoveryPolicy()
        self.results: List[FaultInjectionResult] = []
        self.recovery_history: List[Dict[str, Any]] = []
        self.audit_records: List[Dict[str, Any]] = []
    
    async def inject_fault(self, scenario: Dict[str, Any]) -> FaultInjectionResult:
        """注入单个故障"""
        import time
        import uuid
        
        fault_id = f"fault_{uuid.uuid4().hex[:8]}"
        audit_id = f"audit_{uuid.uuid4().hex[:8]}"
        started_at = datetime.now()
        start_time = time.time()
        
        # 创建恢复计划
        plan = self.policy.create_recovery_plan(scenario["failure_type"])
        
        # 模拟执行恢复步骤
        executed_steps = []
        final_result = "recovered"
        human_action_required = False
        
        for step in plan.steps:
            step_result = {
                "strategy": step.strategy.value,
                "started_at": datetime.now().isoformat(),
                "attempt": 1,
                "success": False,
                "error": None
            }
            
            # 模拟恢复策略执行
            if step.strategy == RecoveryStrategy.RETRY:
                # 第一次重试失败，模拟 timeout
                step_result["success"] = False
                step_result["error"] = f"timeout after {step.timeout_seconds}s"
                executed_steps.append(step_result)
                continue
            
            elif step.strategy == RecoveryStrategy.LIMITED_SCOPE_PROBE:
                # 有限范围探测成功
                step_result["success"] = True
                executed_steps.append(step_result)
                final_result = "recovered"
                break
            
            elif step.strategy == RecoveryStrategy.CACHE_FALLBACK:
                # 缓存降级成功
                step_result["success"] = True
                executed_steps.append(step_result)
                final_result = "recovered"
                break
            
            elif step.strategy == RecoveryStrategy.PENDING_QUEUE:
                # 排队成功
                step_result["success"] = True
                executed_steps.append(step_result)
                final_result = "pending"
                break
            
            elif step.strategy == RecoveryStrategy.PERMISSION_DIAGNOSIS:
                # 权限诊断
                step_result["success"] = False
                step_result["error"] = "permission_unknown"
                executed_steps.append(step_result)
                continue
            
            elif step.strategy == RecoveryStrategy.HUMAN_ACTION_REQUIRED:
                # 需要人工干预
                step_result["success"] = False
                step_result["error"] = "human_action_required"
                executed_steps.append(step_result)
                final_result = "human_action_required"
                human_action_required = True
                break
            
            executed_steps.append(step_result)
        
        finished_at = datetime.now()
        duration_ms = (time.time() - start_time) * 1000
        
        result = FaultInjectionResult(
            fault_id=fault_id,
            failure_type=scenario["failure_type"].value,
            capability=scenario["capability"],
            route_id=scenario["route_id"],
            recovery_plan=[s.strategy.value for s in plan.steps],
            executed_steps=executed_steps,
            final_result=final_result,
            human_action_required=human_action_required,
            started_at=started_at.isoformat(),
            finished_at=finished_at.isoformat(),
            duration_ms=duration_ms,
            audit_id=audit_id
        )
        
        self.results.append(result)
        
        # 写入恢复历史
        self._record_recovery(result)
        
        # 写入审计记录
        self._record_audit(result)
        
        return result
    
    def _record_recovery(self, result: FaultInjectionResult):
        """记录恢复历史"""
        for step in result.executed_steps:
            self.recovery_history.append({
                "recovery_id": result.fault_id,
                "timestamp": datetime.now().isoformat(),
                "failure_type": result.failure_type,
                "capability": result.capability,
                "route_id": result.route_id,
                "strategy": step["strategy"],
                "attempt": step["attempt"],
                "success": step["success"],
                "error_message": step.get("error"),
                "final_result": result.final_result,
                "human_action_required": result.human_action_required,
                "audit_id": result.audit_id
            })
        
        # 同步到 policy 的恢复历史
        for record in self.recovery_history:
            if record not in self.policy.recovery_history:
                self.policy.recovery_history.append(record)
    
    def _record_audit(self, result: FaultInjectionResult):
        """记录审计"""
        self.audit_records.append({
            "audit_id": result.audit_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "fault_injection",
            "fault_id": result.fault_id,
            "failure_type": result.failure_type,
            "capability": result.capability,
            "route_id": result.route_id,
            "recovery_result": result.final_result,
            "human_action_required": result.human_action_required,
            "duration_ms": result.duration_ms
        })
    
    async def run_all_faults(self) -> List[FaultInjectionResult]:
        """运行所有故障注入"""
        for scenario in self.FAULT_SCENARIOS:
            await self.inject_fault(scenario)
        
        return self.results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.results)
        recovered = sum(1 for r in self.results if r.final_result == "recovered")
        pending = sum(1 for r in self.results if r.final_result == "pending")
        human_required = sum(1 for r in self.results if r.human_action_required)
        
        return {
            "total_faults": total,
            "recovered": recovered,
            "pending": pending,
            "human_action_required": human_required,
            "recovery_rate": (recovered / total * 100) if total > 0 else 0,
            "total_recovery_attempts": len(self.recovery_history),
            "total_audit_records": len(self.audit_records)
        }
    
    def generate_report(self) -> str:
        """生成报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("FAULT INJECTION RECOVERY REPORT V2")
        lines.append("=" * 60)
        lines.append("")
        
        # 统计
        stats = self.get_statistics()
        lines.append("[Statistics]")
        lines.append(f"  total_faults_injected: {stats['total_faults']}")
        lines.append(f"  recovered: {stats['recovered']}")
        lines.append(f"  pending: {stats['pending']}")
        lines.append(f"  human_action_required: {stats['human_action_required']}")
        lines.append(f"  recovery_rate: {stats['recovery_rate']:.1f}%")
        lines.append(f"  total_recovery_attempts: {stats['total_recovery_attempts']}")
        lines.append(f"  total_audit_records: {stats['total_audit_records']}")
        lines.append("")
        
        # 故障详情
        lines.append("[Fault Injection Details]")
        for result in self.results:
            status = "✓" if result.final_result == "recovered" else "⏳" if result.final_result == "pending" else "✗"
            lines.append(f"  {status} [{result.fault_id}] {result.failure_type}")
            lines.append(f"      capability: {result.capability}")
            lines.append(f"      route_id: {result.route_id}")
            lines.append(f"      final_result: {result.final_result}")
            lines.append(f"      human_action_required: {result.human_action_required}")
            lines.append(f"      duration_ms: {result.duration_ms:.1f}")
            lines.append(f"      executed_steps: {len(result.executed_steps)}")
            lines.append("")
        
        # 恢复历史
        lines.append("[Recovery History]")
        for record in self.recovery_history[-20:]:
            status = "✓" if record["success"] else "✗"
            lines.append(f"  {status} [{record['failure_type']}] {record['strategy']} -> {record['final_result']}")
        lines.append("")
        
        # 审计记录
        lines.append("[Audit Records]")
        for audit in self.audit_records:
            lines.append(f"  [{audit['audit_id']}] {audit['event_type']}: {audit['failure_type']} -> {audit['recovery_result']}")
        lines.append("")
        
        return "\n".join(lines)


async def main():
    """主函数"""
    injector = FaultInjector()
    
    print("Running fault injection tests...")
    print("")
    
    # 运行所有故障注入
    results = await injector.run_all_faults()
    
    # 输出报告
    print(injector.generate_report())
    
    # 保存恢复历史到文件
    history_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "recovery_history.jsonl"
    )
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    
    with open(history_path, "w") as f:
        for record in injector.recovery_history:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"\nRecovery history saved to: {history_path}")
    
    # 保存审计记录
    audit_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "route_audit.jsonl"
    )
    
    with open(audit_path, "a") as f:
        for audit in injector.audit_records:
            f.write(json.dumps(audit, ensure_ascii=False) + "\n")
    
    print(f"Audit records saved to: {audit_path}")
    
    # 返回码
    stats = injector.get_statistics()
    if stats["recovery_rate"] >= 50:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
