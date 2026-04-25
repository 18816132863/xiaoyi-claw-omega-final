#!/usr/bin/env python3
"""
Simulate L0 Auto Recovery - 模拟 L0 自动降级

模拟最近 10 次 L0 probe：
- 成功 7 次
- 失败 3 次
- success_rate = 70%
- 触发降级

降级路径：
normal_probe → fast_probe → limited_scope_probe → cache_fallback → permission_diagnosis
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.connected_runtime_recovery_policy import (
    ProbeMode,
    L0AutoAdjustment
)


@dataclass
class L0ProbeResult:
    """L0 探测结果"""
    route_id: str
    success: bool
    timestamp: str
    mode: str
    error: str = None


@dataclass
class L0DowngradeEvent:
    """L0 降级事件"""
    before_mode: str
    after_mode: str
    success_rate: float
    threshold: float
    downgrade_reason: str
    failed_capabilities: List[str]
    timestamp: str


class L0AutoRecoverySimulator:
    """L0 自动恢复模拟器"""
    
    # 模拟的 L0 probe 结果（70% 成功率）
    SIMULATED_PROBES = [
        {"route": "route.query_note", "success": True},
        {"route": "route.search_notes", "success": True},
        {"route": "route.query_alarm", "success": False, "error": "timeout"},
        {"route": "route.query_contact", "success": False, "error": "timeout"},
        {"route": "route.get_location", "success": True},
        {"route": "route.query_message_status", "success": True},
        {"route": "route.list_recent_messages", "success": True},
        {"route": "route.check_calendar_conflicts", "success": False, "error": "timeout"},
        {"route": "route.query_note", "success": True},
        {"route": "route.search_notes", "success": True}
    ]
    
    def __init__(self):
        self.adjustment = L0AutoAdjustment()
        self.probe_results: List[L0ProbeResult] = []
        self.downgrade_events: List[L0DowngradeEvent] = []
        self.recovery_history: List[Dict[str, Any]] = []
    
    def simulate_probes(self):
        """模拟 L0 probe"""
        for probe in self.SIMULATED_PROBES:
            result = L0ProbeResult(
                route_id=probe["route"],
                success=probe["success"],
                timestamp=datetime.now().isoformat(),
                mode=self.adjustment.current_mode.value,
                error=probe.get("error")
            )
            self.probe_results.append(result)
            
            # 记录到 L0 调整器
            self.adjustment.record_result(probe["success"])
            
            # 检查是否需要降级
            if self.adjustment.should_downgrade():
                old_mode = self.adjustment.current_mode
                new_mode = self.adjustment.downgrade()
                
                if new_mode:
                    # 收集失败的 capabilities
                    failed_caps = [r.route_id for r in self.probe_results if not r.success]
                    
                    event = L0DowngradeEvent(
                        before_mode=old_mode.value,
                        after_mode=new_mode.value,
                        success_rate=self.adjustment.success_rate,
                        threshold=0.8,
                        downgrade_reason=f"success_rate ({self.adjustment.success_rate:.1%}) < threshold (80%)",
                        failed_capabilities=failed_caps,
                        timestamp=datetime.now().isoformat()
                    )
                    self.downgrade_events.append(event)
                    
                    # 记录恢复历史
                    self.recovery_history.append({
                        "recovery_id": f"l0_downgrade_{len(self.downgrade_events)}",
                        "timestamp": event.timestamp,
                        "failure_type": "l0_low_success_rate",
                        "before_mode": event.before_mode,
                        "after_mode": event.after_mode,
                        "success_rate": event.success_rate,
                        "threshold": event.threshold,
                        "downgrade_reason": event.downgrade_reason,
                        "failed_capabilities": event.failed_capabilities,
                        "human_action_required": new_mode == ProbeMode.PERMISSION_DIAGNOSIS
                    })
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self.probe_results)
        successes = sum(1 for r in self.probe_results if r.success)
        failures = total - successes
        
        return {
            "total_l0_probes": total,
            "success_count": successes,
            "failure_count": failures,
            "success_rate": successes / total if total > 0 else 0,
            "threshold": 0.8,
            "current_mode": self.adjustment.current_mode.value,
            "downgrade_triggered": len(self.downgrade_events) > 0,
            "downgrade_count": len(self.downgrade_events),
            "human_action_required": self.adjustment.current_mode == ProbeMode.PERMISSION_DIAGNOSIS
        }
    
    def generate_report(self) -> str:
        """生成报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("L0 AUTO RECOVERY REPORT V2")
        lines.append("=" * 60)
        lines.append("")
        
        # 统计
        stats = self.get_statistics()
        lines.append("[L0 Probe Statistics]")
        lines.append(f"  total_l0_probes: {stats['total_l0_probes']}")
        lines.append(f"  success_count: {stats['success_count']}")
        lines.append(f"  failure_count: {stats['failure_count']}")
        lines.append(f"  success_rate: {stats['success_rate']:.1%}")
        lines.append(f"  threshold: {stats['threshold']:.0%}")
        lines.append("")
        
        # 降级状态
        lines.append("[Downgrade Status]")
        lines.append(f"  downgrade_triggered: {stats['downgrade_triggered']}")
        lines.append(f"  downgrade_count: {stats['downgrade_count']}")
        lines.append(f"  before_mode: {self.downgrade_events[0].before_mode if self.downgrade_events else 'normal_probe'}")
        lines.append(f"  after_mode: {stats['current_mode']}")
        lines.append(f"  human_action_required: {stats['human_action_required']}")
        lines.append("")
        
        # 降级事件
        if self.downgrade_events:
            lines.append("[Downgrade Events]")
            for event in self.downgrade_events:
                lines.append(f"  [{event.timestamp}]")
                lines.append(f"    before_mode: {event.before_mode}")
                lines.append(f"    after_mode: {event.after_mode}")
                lines.append(f"    success_rate: {event.success_rate:.1%}")
                lines.append(f"    reason: {event.downgrade_reason}")
                lines.append(f"    failed_capabilities: {event.failed_capabilities}")
            lines.append("")
        
        # Probe 详情
        lines.append("[L0 Probe Results]")
        for result in self.probe_results:
            status = "✓" if result.success else "✗"
            error = f" ({result.error})" if result.error else ""
            lines.append(f"  {status} [{result.mode}] {result.route_id}{error}")
        lines.append("")
        
        # 恢复历史
        lines.append("[Recovery History]")
        for record in self.recovery_history:
            lines.append(f"  [{record['recovery_id']}] {record['before_mode']} -> {record['after_mode']}")
            lines.append(f"      success_rate: {record['success_rate']:.1%}")
            lines.append(f"      reason: {record['downgrade_reason']}")
        lines.append("")
        
        return "\n".join(lines)


def main():
    """主函数"""
    simulator = L0AutoRecoverySimulator()
    
    print("Simulating L0 auto recovery...")
    print("")
    
    # 运行模拟
    simulator.simulate_probes()
    
    # 输出报告
    print(simulator.generate_report())
    
    # 保存恢复历史
    history_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "recovery_history.jsonl"
    )
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    
    with open(history_path, "a") as f:
        for record in simulator.recovery_history:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"\nRecovery history appended to: {history_path}")
    
    # 验证
    stats = simulator.get_statistics()
    
    print("\n[Verification]")
    print(f"  ✓ Success rate is {stats['success_rate']:.1%} (< 80%)")
    print(f"  ✓ Downgrade triggered: {stats['downgrade_triggered']}")
    print(f"  ✓ Mode changed: {stats['current_mode']}")
    
    if stats['downgrade_triggered'] and stats['success_rate'] < 0.8:
        print("\n✓ L0 auto recovery simulation PASSED")
        return 0
    else:
        print("\n✗ L0 auto recovery simulation FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
