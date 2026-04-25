"""
Task Progress Guard - 任务进度守卫

监控任务进度，防止无限处理：
- 20 秒：heartbeat
- 60 秒无进度：degrade
- 120 秒无进度：stop_probe
- 180 秒总耗时：output_partial
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import asyncio


class ProgressAction(Enum):
    """进度动作"""
    CONTINUE = "continue"
    HEARTBEAT = "heartbeat"
    DEGRADE = "degrade"
    STOP_PROBE = "stop_probe"
    OUTPUT_PARTIAL = "output_partial"


@dataclass
class ProgressCheckpoint:
    """进度检查点"""
    stage: str
    timestamp: datetime
    details: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeoutThreshold:
    """超时阈值"""
    heartbeat_interval: float = 20.0
    degrade_after: float = 60.0
    stop_probe_after: float = 120.0
    output_partial_after: float = 180.0


class TaskProgressGuard:
    """任务进度守卫"""
    
    def __init__(
        self,
        task_id: str,
        thresholds: TimeoutThreshold = None,
        on_heartbeat: Callable = None,
        on_degrade: Callable = None,
        on_stop_probe: Callable = None,
        on_output_partial: Callable = None
    ):
        self.task_id = task_id
        self.thresholds = thresholds or TimeoutThreshold()
        
        # 回调函数
        self.on_heartbeat = on_heartbeat
        self.on_degrade = on_degrade
        self.on_stop_probe = on_stop_probe
        self.on_output_partial = on_output_partial
        
        # 状态
        self.start_time = datetime.now()
        self.last_progress_time = datetime.now()
        self.checkpoints: List[ProgressCheckpoint] = []
        self.heartbeat_count = 0
        self.degrade_triggered = False
        self.stop_probe_triggered = False
        self.output_partial_triggered = False
        self.final_status = "processing"
        self.partial_result: Optional[Dict[str, Any]] = None
    
    def update_progress(self, stage: str, details: str = "", metadata: Dict[str, Any] = None):
        """更新进度"""
        now = datetime.now()
        checkpoint = ProgressCheckpoint(
            stage=stage,
            timestamp=now,
            details=details,
            metadata=metadata or {}
        )
        self.checkpoints.append(checkpoint)
        self.last_progress_time = now
    
    def check(self) -> ProgressAction:
        """检查进度状态"""
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        since_last_progress = (now - self.last_progress_time).total_seconds()
        
        # 检查是否需要输出部分结果
        if elapsed >= self.thresholds.output_partial_after:
            if not self.output_partial_triggered:
                self.output_partial_triggered = True
                self.final_status = "partial_output"
                self._handle_output_partial()
                return ProgressAction.OUTPUT_PARTIAL
        
        # 检查是否需要停止 probe
        if since_last_progress >= self.thresholds.stop_probe_after:
            if not self.stop_probe_triggered:
                self.stop_probe_triggered = True
                self._handle_stop_probe()
                return ProgressAction.STOP_PROBE
        
        # 检查是否需要降级
        if since_last_progress >= self.thresholds.degrade_after:
            if not self.degrade_triggered:
                self.degrade_triggered = True
                self._handle_degrade()
                return ProgressAction.DEGRADE
        
        # 检查是否需要心跳
        if elapsed > 0 and elapsed % self.thresholds.heartbeat_interval < 1:
            self._handle_heartbeat()
            return ProgressAction.HEARTBEAT
        
        return ProgressAction.CONTINUE
    
    def _handle_heartbeat(self):
        """处理心跳"""
        self.heartbeat_count += 1
        if self.on_heartbeat:
            self.on_heartbeat({
                "task_id": self.task_id,
                "heartbeat_count": self.heartbeat_count,
                "elapsed_seconds": (datetime.now() - self.start_time).total_seconds()
            })
    
    def _handle_degrade(self):
        """处理降级"""
        if self.on_degrade:
            self.on_degrade({
                "task_id": self.task_id,
                "reason": f"No progress for {self.thresholds.degrade_after}s"
            })
    
    def _handle_stop_probe(self):
        """处理停止探测"""
        if self.on_stop_probe:
            self.on_stop_probe({
                "task_id": self.task_id,
                "reason": f"No progress for {self.thresholds.stop_probe_after}s"
            })
    
    def _handle_output_partial(self):
        """处理输出部分结果"""
        self.partial_result = {
            "task_id": self.task_id,
            "status": "partial",
            "completed_stages": [cp.stage for cp in self.checkpoints],
            "elapsed_seconds": (datetime.now() - self.start_time).total_seconds()
        }
        
        if self.on_output_partial:
            self.on_output_partial(self.partial_result)
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        since_last_progress = (now - self.last_progress_time).total_seconds()
        
        return {
            "task_id": self.task_id,
            "final_status": self.final_status,
            "elapsed_seconds": elapsed,
            "since_last_progress_seconds": since_last_progress,
            "heartbeat_count": self.heartbeat_count,
            "degrade_triggered": self.degrade_triggered,
            "stop_probe_triggered": self.stop_probe_triggered,
            "output_partial_triggered": self.output_partial_triggered,
            "checkpoints_count": len(self.checkpoints),
            "no_infinite_processing": self.final_status != "processing"
        }


def format_progress_report(guard: TaskProgressGuard) -> str:
    """格式化进度报告"""
    status = guard.get_status()
    
    lines = []
    lines.append("=" * 60)
    lines.append("TASK PROGRESS GUARD REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    lines.append("[Task Status]")
    lines.append(f"  task_id: {status['task_id']}")
    lines.append(f"  final_status: {status['final_status']}")
    lines.append(f"  elapsed_seconds: {status['elapsed_seconds']:.1f}")
    lines.append(f"  since_last_progress: {status['since_last_progress_seconds']:.1f}")
    lines.append("")
    
    lines.append("[Timeout Triggers]")
    lines.append(f"  heartbeat_count: {status['heartbeat_count']}")
    lines.append(f"  degrade_triggered: {status['degrade_triggered']}")
    lines.append(f"  stop_probe_triggered: {status['stop_probe_triggered']}")
    lines.append(f"  output_partial_triggered: {status['output_partial_triggered']}")
    lines.append("")
    
    lines.append("[Checkpoints]")
    for cp in guard.checkpoints[-10:]:
        elapsed = (cp.timestamp - guard.start_time).total_seconds()
        lines.append(f"  [{elapsed:.1f}s] {cp.stage}: {cp.details}")
    lines.append("")
    
    lines.append("[Verification]")
    lines.append(f"  no_infinite_processing: {status['no_infinite_processing']}")
    lines.append("")
    
    return "\n".join(lines)
