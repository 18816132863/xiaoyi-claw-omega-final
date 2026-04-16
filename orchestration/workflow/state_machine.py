"""State Machine - 工作流状态机"""

from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class State(Enum):
    """工作流状态"""
    IDLE = "idle"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Event(Enum):
    """工作流事件"""
    START = "start"
    PLAN_COMPLETE = "plan_complete"
    STEP_COMPLETE = "step_complete"
    STEP_FAIL = "step_fail"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    ALL_COMPLETE = "all_complete"
    FATAL_ERROR = "fatal_error"


@dataclass
class Transition:
    """状态转换"""
    from_state: State
    to_state: State
    event: Event
    action: Optional[Callable] = None
    guard: Optional[Callable] = None


@dataclass
class StateHistory:
    """状态历史"""
    from_state: State
    to_state: State
    event: Event
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


class WorkflowStateMachine:
    """
    工作流状态机
    
    管理：
    - 状态转换
    - 转换条件
    - 转换动作
    - 状态历史
    """
    
    def __init__(self):
        self.current_state = State.IDLE
        self.history: List[StateHistory] = []
        self._transitions: Dict[tuple, Transition] = {}
        self._enter_actions: Dict[State, Callable] = {}
        self._exit_actions: Dict[State, Callable] = {}
        self._setup_default_transitions()
    
    def _setup_default_transitions(self):
        """设置默认转换"""
        self.add_transition(Transition(State.IDLE, State.PLANNING, Event.START))
        self.add_transition(Transition(State.PLANNING, State.READY, Event.PLAN_COMPLETE))
        self.add_transition(Transition(State.READY, State.RUNNING, Event.START))
        self.add_transition(Transition(State.RUNNING, State.PAUSED, Event.PAUSE))
        self.add_transition(Transition(State.PAUSED, State.RUNNING, Event.RESUME))
        self.add_transition(Transition(State.RUNNING, State.COMPLETED, Event.ALL_COMPLETE))
        self.add_transition(Transition(State.RUNNING, State.FAILED, Event.FATAL_ERROR))
        self.add_transition(Transition(State.RUNNING, State.CANCELLED, Event.CANCEL))
        self.add_transition(Transition(State.PAUSED, State.CANCELLED, Event.CANCEL))
        self.add_transition(Transition(State.FAILED, State.RUNNING, Event.RESUME))
    
    def add_transition(self, transition: Transition):
        """添加转换规则"""
        key = (transition.from_state, transition.event)
        self._transitions[key] = transition
    
    def set_enter_action(self, state: State, action: Callable):
        """设置进入状态动作"""
        self._enter_actions[state] = action
    
    def set_exit_action(self, state: State, action: Callable):
        """设置退出状态动作"""
        self._exit_actions[state] = action
    
    def can_transition(self, event: Event) -> bool:
        """检查是否可转换"""
        key = (self.current_state, event)
        if key not in self._transitions:
            return False
        
        transition = self._transitions[key]
        if transition.guard:
            return transition.guard()
        
        return True
    
    def transition(self, event: Event, metadata: Dict = None) -> bool:
        """执行状态转换"""
        key = (self.current_state, event)
        if key not in self._transitions:
            return False
        
        transition = self._transitions[key]
        
        # 检查守卫条件
        if transition.guard and not transition.guard():
            return False
        
        from_state = self.current_state
        
        # 执行退出动作
        if from_state in self._exit_actions:
            try:
                self._exit_actions[from_state]()
            except Exception as e:
                print(f"Warning: Exit action failed: {e}")
        
        # 更新状态
        self.current_state = transition.to_state
        
        # 记录历史
        self.history.append(StateHistory(
            from_state=from_state,
            to_state=self.current_state,
            event=event,
            metadata=metadata or {}
        ))
        
        # 执行转换动作
        if transition.action:
            try:
                transition.action()
            except Exception as e:
                # 回滚状态
                self.current_state = from_state
                raise e
        
        # 执行进入动作
        if self.current_state in self._enter_actions:
            try:
                self._enter_actions[self.current_state]()
            except Exception as e:
                print(f"Warning: Enter action failed: {e}")
        
        return True
    
    def get_valid_events(self) -> List[Event]:
        """获取有效事件"""
        valid = []
        for (state, event) in self._transitions.keys():
            if state == self.current_state:
                valid.append(event)
        return valid
    
    def get_history(self, limit: int = None) -> List[StateHistory]:
        """获取历史"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def reset(self):
        """重置"""
        self.current_state = State.IDLE
        self.history.clear()
    
    def is_terminal(self) -> bool:
        """是否终止状态"""
        return self.current_state in [State.COMPLETED, State.FAILED, State.CANCELLED]
    
    def is_running(self) -> bool:
        """是否运行中"""
        return self.current_state == State.RUNNING
    
    def is_paused(self) -> bool:
        """是否暂停"""
        return self.current_state == State.PAUSED
    
    def get_state(self) -> State:
        """获取当前状态"""
        return self.current_state
