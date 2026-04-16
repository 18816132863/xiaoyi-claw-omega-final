"""
State Machine - Workflow 状态机
统一管理 workflow 和 step 的状态流转
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class WorkflowState(Enum):
    """Workflow 状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class StepState(Enum):
    """Step 状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


# 状态转换规则
WORKFLOW_TRANSITIONS = {
    WorkflowState.PENDING: [WorkflowState.RUNNING, WorkflowState.CANCELLED],
    WorkflowState.RUNNING: [WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.PAUSED, WorkflowState.CANCELLED],
    WorkflowState.PAUSED: [WorkflowState.RUNNING, WorkflowState.CANCELLED],
    WorkflowState.COMPLETED: [],
    WorkflowState.FAILED: [],
    WorkflowState.CANCELLED: []
}

STEP_TRANSITIONS = {
    StepState.PENDING: [StepState.RUNNING, StepState.SKIPPED],
    StepState.RUNNING: [StepState.COMPLETED, StepState.FAILED, StepState.RETRYING],
    StepState.RETRYING: [StepState.COMPLETED, StepState.FAILED],
    StepState.COMPLETED: [],
    StepState.FAILED: [StepState.SKIPPED],  # 允许跳过失败的步骤
    StepState.SKIPPED: []
}


@dataclass
class WorkflowStateRecord:
    """Workflow 状态记录"""
    instance_id: str
    state: WorkflowState
    previous_state: Optional[WorkflowState] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "state": self.state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "timestamp": self.timestamp,
            "reason": self.reason
        }


@dataclass
class StepStateRecord:
    """Step 状态记录"""
    instance_id: str
    step_id: str
    state: StepState
    previous_state: Optional[StepState] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "step_id": self.step_id,
            "state": self.state.value,
            "previous_state": self.previous_state.value if self.previous_state else None,
            "timestamp": self.timestamp,
            "reason": self.reason
        }


class WorkflowStateMachine:
    """
    Workflow 状态机
    
    统一管理 workflow 和 step 的状态流转：
    - pending -> running
    - running -> completed / failed / paused / cancelled
    - 状态转换验证
    - 状态历史记录
    """
    
    def __init__(self):
        # 当前状态
        self._workflow_states: Dict[str, WorkflowState] = {}
        self._step_states: Dict[str, Dict[str, StepState]] = {}  # instance_id -> {step_id -> state}
        
        # 状态历史
        self._workflow_history: Dict[str, List[WorkflowStateRecord]] = {}
        self._step_history: Dict[str, List[StepStateRecord]] = {}
    
    def init_workflow(self, instance_id: str) -> WorkflowState:
        """
        初始化 workflow 状态
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            初始状态
        """
        self._workflow_states[instance_id] = WorkflowState.PENDING
        self._step_states[instance_id] = {}
        self._workflow_history[instance_id] = []
        self._step_history[instance_id] = []
        
        record = WorkflowStateRecord(
            instance_id=instance_id,
            state=WorkflowState.PENDING,
            reason="Workflow initialized"
        )
        self._workflow_history[instance_id].append(record)
        
        return WorkflowState.PENDING
    
    def transition_workflow(
        self,
        instance_id: str,
        new_state: WorkflowState,
        reason: str = ""
    ) -> bool:
        """
        转换 workflow 状态
        
        Args:
            instance_id: 实例 ID
            new_state: 新状态
            reason: 原因
            
        Returns:
            是否转换成功
        """
        current_state = self._workflow_states.get(instance_id)
        if not current_state:
            # 自动初始化
            self.init_workflow(instance_id)
            current_state = WorkflowState.PENDING
        
        # 验证转换
        if new_state not in WORKFLOW_TRANSITIONS.get(current_state, []):
            return False
        
        # 执行转换
        previous_state = current_state
        self._workflow_states[instance_id] = new_state
        
        # 记录历史
        record = WorkflowStateRecord(
            instance_id=instance_id,
            state=new_state,
            previous_state=previous_state,
            reason=reason
        )
        self._workflow_history[instance_id].append(record)
        
        return True
    
    def get_workflow_state(self, instance_id: str) -> Optional[WorkflowState]:
        """
        获取 workflow 当前状态
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            当前状态
        """
        return self._workflow_states.get(instance_id)
    
    def init_step(self, instance_id: str, step_id: str) -> StepState:
        """
        初始化 step 状态
        
        Args:
            instance_id: 实例 ID
            step_id: 步骤 ID
            
        Returns:
            初始状态
        """
        if instance_id not in self._step_states:
            self._step_states[instance_id] = {}
        
        self._step_states[instance_id][step_id] = StepState.PENDING
        
        record = StepStateRecord(
            instance_id=instance_id,
            step_id=step_id,
            state=StepState.PENDING,
            reason="Step initialized"
        )
        
        if instance_id not in self._step_history:
            self._step_history[instance_id] = []
        self._step_history[instance_id].append(record)
        
        return StepState.PENDING
    
    def transition_step(
        self,
        instance_id: str,
        step_id: str,
        new_state: StepState,
        reason: str = ""
    ) -> bool:
        """
        转换 step 状态
        
        Args:
            instance_id: 实例 ID
            step_id: 步骤 ID
            new_state: 新状态
            reason: 原因
            
        Returns:
            是否转换成功
        """
        if instance_id not in self._step_states:
            self._step_states[instance_id] = {}
        
        current_state = self._step_states[instance_id].get(step_id)
        if not current_state:
            # 自动初始化
            self.init_step(instance_id, step_id)
            current_state = StepState.PENDING
        
        # 验证转换
        if new_state not in STEP_TRANSITIONS.get(current_state, []):
            return False
        
        # 执行转换
        previous_state = current_state
        self._step_states[instance_id][step_id] = new_state
        
        # 记录历史
        record = StepStateRecord(
            instance_id=instance_id,
            step_id=step_id,
            state=new_state,
            previous_state=previous_state,
            reason=reason
        )
        self._step_history[instance_id].append(record)
        
        return True
    
    def get_step_state(self, instance_id: str, step_id: str) -> Optional[StepState]:
        """
        获取 step 当前状态
        
        Args:
            instance_id: 实例 ID
            step_id: 步骤 ID
            
        Returns:
            当前状态
        """
        if instance_id not in self._step_states:
            return None
        return self._step_states[instance_id].get(step_id)
    
    def get_all_step_states(self, instance_id: str) -> Dict[str, StepState]:
        """
        获取所有 step 状态
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            step_id -> state 映射
        """
        return dict(self._step_states.get(instance_id, {}))
    
    def get_workflow_history(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        获取 workflow 状态历史
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            状态历史列表
        """
        records = self._workflow_history.get(instance_id, [])
        return [r.to_dict() for r in records]
    
    def get_step_history(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        获取 step 状态历史
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            状态历史列表
        """
        records = self._step_history.get(instance_id, [])
        return [r.to_dict() for r in records]
    
    def can_transition(self, current: WorkflowState, target: WorkflowState) -> bool:
        """
        检查是否可以转换
        
        Args:
            current: 当前状态
            target: 目标状态
            
        Returns:
            是否可以转换
        """
        return target in WORKFLOW_TRANSITIONS.get(current, [])
    
    def can_transition_step(self, current: StepState, target: StepState) -> bool:
        """
        检查 step 是否可以转换
        
        Args:
            current: 当前状态
            target: 目标状态
            
        Returns:
            是否可以转换
        """
        return target in STEP_TRANSITIONS.get(current, [])
    
    def reset(self, instance_id: str):
        """
        重置状态
        
        Args:
            instance_id: 实例 ID
        """
        if instance_id in self._workflow_states:
            del self._workflow_states[instance_id]
        if instance_id in self._step_states:
            del self._step_states[instance_id]
        if instance_id in self._workflow_history:
            del self._workflow_history[instance_id]
        if instance_id in self._step_history:
            del self._step_history[instance_id]


# 全局单例
_workflow_state_machine = None

def get_workflow_state_machine() -> WorkflowStateMachine:
    """获取状态机单例"""
    global _workflow_state_machine
    if _workflow_state_machine is None:
        _workflow_state_machine = WorkflowStateMachine()
    return _workflow_state_machine
