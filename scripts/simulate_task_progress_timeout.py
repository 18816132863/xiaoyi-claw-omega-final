#!/usr/bin/env python3
"""
Simulate Task Progress Timeout - 模拟任务进度超时

规则：
- 20 秒：heartbeat
- 60 秒无进度：degrade
- 120 秒无进度：stop_probe
- 180 秒总耗时：output_partial

使用模拟时间，不真实 sleep
"""

import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TimeoutAction(Enum):
    """超时动作"""
    CONTINUE = "continue"
    HEARTBEAT = "heartbeat"
    DEGRADE = "degrade"
    STOP_PROBE = "stop_probe"
    OUTPUT_PARTIAL = "output_partial"


@dataclass
class SimulatedClock:
    """模拟时钟"""
    start_time: datetime
    current_time: datetime
    speed_multiplier: float = 1.0  # 时间加速倍数
    
    def advance(self, seconds: float):
        """前进时间"""
        self.current_time += timedelta(seconds=seconds)
    
    def elapsed_seconds(self) -> float:
        """已经过秒数"""
        return (self.current_time - self.start_time).total_seconds()


@dataclass
class ProgressStage:
    """进度阶段"""
    name: str
    started_at: float
    completed_at: Optional[float] = None
    details: str = ""


@dataclass
class TimeoutEvent:
    """超时事件"""
    action: str
    triggered_at: float
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


class TaskProgressSimulator:
    """任务进度模拟器"""
    
    # 超时阈值（秒）
    HEARTBEAT_INTERVAL = 20
    DEGRADE_THRESHOLD = 60
    STOP_PROBE_THRESHOLD = 120
    OUTPUT_PARTIAL_THRESHOLD = 180
    
    def __init__(self, task_id: str = "simulated_task"):
        self.task_id = task_id
        self.clock = SimulatedClock(
            start_time=datetime.now(),
            current_time=datetime.now()
        )
        self.progress_stages: List[ProgressStage] = []
        self.timeout_events: List[TimeoutEvent] = []
        self.heartbeat_count = 0
        self.last_progress_time = 0.0
        self.partial_result: Optional[Dict[str, Any]] = None
        self.final_status = "processing"
    
    def add_progress(self, stage_name: str, details: str = ""):
        """添加进度"""
        elapsed = self.clock.elapsed_seconds()
        stage = ProgressStage(
            name=stage_name,
            started_at=elapsed,
            details=details
        )
        self.progress_stages.append(stage)
        self.last_progress_time = elapsed
    
    def check_timeouts(self) -> TimeoutAction:
        """检查超时"""
        elapsed = self.clock.elapsed_seconds()
        since_last_progress = elapsed - self.last_progress_time
        
        # 检查是否需要输出部分结果
        if elapsed >= self.OUTPUT_PARTIAL_THRESHOLD:
            event = TimeoutEvent(
                action="output_partial",
                triggered_at=elapsed,
                reason=f"Total elapsed {elapsed:.0f}s >= {self.OUTPUT_PARTIAL_THRESHOLD}s",
                details={
                    "elapsed_seconds": elapsed,
                    "threshold": self.OUTPUT_PARTIAL_THRESHOLD
                }
            )
            self.timeout_events.append(event)
            self.final_status = "partial_output"
            self._generate_partial_result()
            return TimeoutAction.OUTPUT_PARTIAL
        
        # 检查是否需要停止 probe
        if since_last_progress >= self.STOP_PROBE_THRESHOLD:
            event = TimeoutEvent(
                action="stop_probe",
                triggered_at=elapsed,
                reason=f"No progress for {since_last_progress:.0f}s >= {self.STOP_PROBE_THRESHOLD}s",
                details={
                    "since_last_progress": since_last_progress,
                    "threshold": self.STOP_PROBE_THRESHOLD
                }
            )
            self.timeout_events.append(event)
            return TimeoutAction.STOP_PROBE
        
        # 检查是否需要降级
        if since_last_progress >= self.DEGRADE_THRESHOLD:
            event = TimeoutEvent(
                action="degrade",
                triggered_at=elapsed,
                reason=f"No progress for {since_last_progress:.0f}s >= {self.DEGRADE_THRESHOLD}s",
                details={
                    "since_last_progress": since_last_progress,
                    "threshold": self.DEGRADE_THRESHOLD
                }
            )
            self.timeout_events.append(event)
            return TimeoutAction.DEGRADE
        
        return TimeoutAction.CONTINUE
    
    def emit_heartbeat(self):
        """发送心跳"""
        elapsed = self.clock.elapsed_seconds()
        event = TimeoutEvent(
            action="heartbeat",
            triggered_at=elapsed,
            reason=f"Heartbeat interval {self.HEARTBEAT_INTERVAL}s",
            details={
                "heartbeat_number": self.heartbeat_count + 1,
                "elapsed_seconds": elapsed
            }
        )
        self.timeout_events.append(event)
        self.heartbeat_count += 1
    
    def _generate_partial_result(self):
        """生成部分结果"""
        self.partial_result = {
            "task_id": self.task_id,
            "status": "partial",
            "completed_stages": [s.name for s in self.progress_stages],
            "elapsed_seconds": self.clock.elapsed_seconds(),
            "message": "Task timed out, partial results returned"
        }
    
    def simulate(self, scenario: str = "timeout") -> Dict[str, Any]:
        """运行模拟"""
        # 初始进度
        self.add_progress("initialization", "Task started")
        
        # 模拟时间流逝
        if scenario == "timeout":
            # 模拟 180 秒无进度
            for i in range(9):  # 9 * 20 = 180 秒
                self.clock.advance(self.HEARTBEAT_INTERVAL)
                self.emit_heartbeat()
                
                action = self.check_timeouts()
                if action == TimeoutAction.OUTPUT_PARTIAL:
                    break
        
        elif scenario == "partial_progress":
            # 模拟部分进度后超时
            self.clock.advance(30)
            self.add_progress("data_fetch", "Fetching data...")
            
            self.clock.advance(30)
            self.emit_heartbeat()
            
            self.clock.advance(60)
            self.emit_heartbeat()
            self.emit_heartbeat()
            
            self.clock.advance(60)
            action = self.check_timeouts()
        
        return self.get_result()
    
    def get_result(self) -> Dict[str, Any]:
        """获取结果"""
        return {
            "task_id": self.task_id,
            "final_status": self.final_status,
            "elapsed_seconds": self.clock.elapsed_seconds(),
            "heartbeat_count": self.heartbeat_count,
            "progress_stages_count": len(self.progress_stages),
            "timeout_events_count": len(self.timeout_events),
            "degrade_triggered": any(e.action == "degrade" for e in self.timeout_events),
            "stop_probe_triggered": any(e.action == "stop_probe" for e in self.timeout_events),
            "output_partial_triggered": any(e.action == "output_partial" for e in self.timeout_events),
            "partial_result": self.partial_result,
            "no_infinite_processing": self.final_status != "processing"
        }
    
    def generate_report(self) -> str:
        """生成报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("TASK PROGRESS TIMEOUT REPORT V2")
        lines.append("=" * 60)
        lines.append("")
        
        # 基本信息
        result = self.get_result()
        lines.append("[Task Info]")
        lines.append(f"  task_id: {result['task_id']}")
        lines.append(f"  final_status: {result['final_status']}")
        lines.append(f"  elapsed_seconds: {result['elapsed_seconds']:.0f}")
        lines.append("")
        
        # 心跳统计
        lines.append("[Heartbeat]")
        lines.append(f"  heartbeat_count: {result['heartbeat_count']}")
        lines.append(f"  interval_seconds: {self.HEARTBEAT_INTERVAL}")
        lines.append("")
        
        # 超时触发
        lines.append("[Timeout Triggers]")
        lines.append(f"  degrade_triggered: {result['degrade_triggered']}")
        lines.append(f"  stop_probe_triggered: {result['stop_probe_triggered']}")
        lines.append(f"  output_partial_triggered: {result['output_partial_triggered']}")
        lines.append("")
        
        # 超时事件详情
        lines.append("[Timeout Events]")
        for event in self.timeout_events:
            lines.append(f"  [{event.triggered_at:.0f}s] {event.action}: {event.reason}")
        lines.append("")
        
        # 进度阶段
        lines.append("[Progress Stages]")
        for stage in self.progress_stages:
            lines.append(f"  [{stage.started_at:.0f}s] {stage.name}: {stage.details}")
        lines.append("")
        
        # 部分结果
        if self.partial_result:
            lines.append("[Partial Result]")
            lines.append(f"  status: {self.partial_result['status']}")
            lines.append(f"  completed_stages: {self.partial_result['completed_stages']}")
            lines.append(f"  message: {self.partial_result['message']}")
            lines.append("")
        
        # 验证
        lines.append("[Verification]")
        lines.append(f"  no_infinite_processing: {result['no_infinite_processing']}")
        lines.append(f"  partial_result_generated: {self.partial_result is not None}")
        lines.append("")
        
        return "\n".join(lines)


def main():
    """主函数"""
    print("Simulating task progress timeout...")
    print("")
    
    # 运行模拟
    simulator = TaskProgressSimulator(task_id="test_task_001")
    result = simulator.simulate(scenario="timeout")
    
    # 输出报告
    print(simulator.generate_report())
    
    # 验证
    print("[Final Verification]")
    
    passed = True
    
    if result["heartbeat_count"] > 0:
        print(f"  ✓ Heartbeat emitted: {result['heartbeat_count']} times")
    else:
        print("  ✗ No heartbeat emitted")
        passed = False
    
    if result["degrade_triggered"]:
        print("  ✓ Degrade triggered")
    else:
        print("  ✗ Degrade not triggered")
        passed = False
    
    if result["stop_probe_triggered"]:
        print("  ✓ Stop probe triggered")
    else:
        print("  ✗ Stop probe not triggered")
        passed = False
    
    if result["output_partial_triggered"]:
        print("  ✓ Output partial triggered")
    else:
        print("  ✗ Output partial not triggered")
        passed = False
    
    if result["no_infinite_processing"]:
        print("  ✓ No infinite processing")
    else:
        print("  ✗ Still in processing state")
        passed = False
    
    if passed:
        print("\n✓ Task progress timeout simulation PASSED")
        return 0
    else:
        print("\n✗ Task progress timeout simulation FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
