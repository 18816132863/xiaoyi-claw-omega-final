"""
Device Runtime State - 设备运行时状态精细化管理

状态拆分：
1. session_connected：小艺会话是否连接
2. runtime_bridge_ready：call_device_tool / 小艺工具桥是否可用
3. permission_ready：联系人/日历/备忘录/位置/截图等权限是否可用
4. capability_service_ready：单个能力服务是否响应
5. action_ready：是否允许真实动作执行

关键原则：
- 不能因为某个能力 timeout 就判定"设备不可达"
- 必须区分不同类型的失败原因
- 小艺 Claw 连接端默认 session_connected = true
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class SessionState(Enum):
    """会话连接状态"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNKNOWN = "unknown"


class BridgeState(Enum):
    """运行时桥状态"""
    READY = "ready"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class PermissionState(Enum):
    """权限状态"""
    GRANTED = "granted"
    DENIED = "denied"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"


class CapabilityState(Enum):
    """能力服务状态"""
    READY = "ready"
    TIMEOUT = "timeout"
    ERROR = "error"
    UNAVAILABLE = "unavailable"


class ActionState(Enum):
    """动作执行状态"""
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    CONFIRM_REQUIRED = "confirm_required"
    STRONG_CONFIRM_REQUIRED = "strong_confirm_required"


@dataclass
class PermissionCheckResult:
    """权限检查结果"""
    permission_name: str
    state: PermissionState
    last_check_time: datetime
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class CapabilityCheckResult:
    """能力检查结果"""
    capability_name: str
    state: CapabilityState
    last_check_time: datetime
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class DeviceRuntimeState:
    """设备运行时完整状态"""
    
    # 会话状态
    session_connected: SessionState = SessionState.UNKNOWN
    session_last_heartbeat: Optional[datetime] = None
    
    # 运行时桥状态
    runtime_bridge_ready: BridgeState = BridgeState.UNAVAILABLE
    bridge_last_check: Optional[datetime] = None
    
    # 权限状态（细粒度）
    permissions: Dict[str, PermissionCheckResult] = field(default_factory=dict)
    
    # 能力服务状态（细粒度）
    capabilities: Dict[str, CapabilityCheckResult] = field(default_factory=dict)
    
    # 动作执行状态
    action_ready: ActionState = ActionState.BLOCKED
    
    # 元数据
    last_full_check: Optional[datetime] = None
    check_duration_ms: float = 0.0
    is_xiaoyi_channel: bool = False  # 是否在小艺 Claw 连接端运行
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_connected": self.session_connected.value,
            "session_last_heartbeat": self.session_last_heartbeat.isoformat() if self.session_last_heartbeat else None,
            "runtime_bridge_ready": self.runtime_bridge_ready.value,
            "bridge_last_check": self.bridge_last_check.isoformat() if self.bridge_last_check else None,
            "permissions": {
                name: {
                    "state": p.state.value,
                    "last_check_time": p.last_check_time.isoformat(),
                    "error_message": p.error_message,
                    "retry_count": p.retry_count
                }
                for name, p in self.permissions.items()
            },
            "capabilities": {
                name: {
                    "state": c.state.value,
                    "last_check_time": c.last_check_time.isoformat(),
                    "response_time_ms": c.response_time_ms,
                    "error_message": c.error_message,
                    "retry_count": c.retry_count
                }
                for name, c in self.capabilities.items()
            },
            "action_ready": self.action_ready.value,
            "last_full_check": self.last_full_check.isoformat() if self.last_full_check else None,
            "check_duration_ms": self.check_duration_ms,
            "is_xiaoyi_channel": self.is_xiaoyi_channel
        }
    
    def get_summary(self) -> str:
        """获取状态摘要"""
        if self.is_xiaoyi_channel:
            # 小艺连接端，默认 session 已连接
            base = "session_connected=true"
        else:
            base = f"session_connected={self.session_connected.value}"
        
        # 计算可用能力比例
        ready_caps = sum(1 for c in self.capabilities.values() if c.state == CapabilityState.READY)
        total_caps = len(self.capabilities) if self.capabilities else 1
        
        # 计算权限状态
        granted_perms = sum(1 for p in self.permissions.values() if p.state == PermissionState.GRANTED)
        total_perms = len(self.permissions) if self.permissions else 1
        
        # 判断整体状态
        if ready_caps == total_caps and granted_perms == total_perms:
            overall = "fully_ready"
        elif ready_caps > 0 or granted_perms > 0:
            overall = "partial"
        else:
            overall = "limited"
        
        return f"{base}, connected_runtime={overall}, capabilities={ready_caps}/{total_caps}, permissions={granted_perms}/{total_perms}"


class DeviceRuntimeStateChecker:
    """设备运行时状态检查器"""
    
    # 必须检查的权限列表
    REQUIRED_PERMISSIONS = [
        "contact",
        "calendar", 
        "note",
        "location",
        "notification",
        "screenshot"
    ]
    
    # 必须检查的能力列表
    REQUIRED_CAPABILITIES = [
        "contact_service",
        "calendar_service",
        "note_service",
        "location_service",
        "message_service",
        "phone_service"
    ]
    
    def __init__(self, is_xiaoyi_channel: bool = True):
        self.is_xiaoyi_channel = is_xiaoyi_channel
        self.state = DeviceRuntimeState(is_xiaoyi_channel=is_xiaoyi_channel)
    
    async def check_session_connected(self) -> bool:
        """检查会话是否连接"""
        # 小艺连接端默认已连接
        if self.is_xiaoyi_channel:
            self.state.session_connected = SessionState.CONNECTED
            self.state.session_last_heartbeat = datetime.now()
            return True
        
        # 非小艺连接端需要实际检查
        # 这里可以通过心跳或其他机制检查
        # 暂时返回 unknown
        self.state.session_connected = SessionState.UNKNOWN
        return False
    
    async def check_runtime_bridge(self) -> bool:
        """检查运行时桥是否可用"""
        try:
            # 检查 call_device_tool 是否可用
            # 这里可以尝试调用一个轻量级 probe
            self.state.runtime_bridge_ready = BridgeState.READY
            self.state.bridge_last_check = datetime.now()
            return True
        except Exception as e:
            self.state.runtime_bridge_ready = BridgeState.ERROR
            self.state.bridge_last_check = datetime.now()
            return False
    
    async def check_permission(self, permission_name: str) -> PermissionCheckResult:
        """检查单个权限"""
        now = datetime.now()
        
        # 这里应该调用实际的权限检查
        # 暂时返回 unknown
        result = PermissionCheckResult(
            permission_name=permission_name,
            state=PermissionState.UNKNOWN,
            last_check_time=now
        )
        
        self.state.permissions[permission_name] = result
        return result
    
    async def check_capability(self, capability_name: str, timeout_ms: float = 5000) -> CapabilityCheckResult:
        """检查单个能力服务"""
        import time
        now = datetime.now()
        start = time.time()
        
        try:
            # 这里应该调用实际的能力检查
            # 暂时返回 ready
            elapsed_ms = (time.time() - start) * 1000
            
            result = CapabilityCheckResult(
                capability_name=capability_name,
                state=CapabilityState.READY,
                last_check_time=now,
                response_time_ms=elapsed_ms
            )
        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            
            # 区分 timeout 和其他错误
            if "timeout" in str(e).lower():
                state = CapabilityState.TIMEOUT
            else:
                state = CapabilityState.ERROR
            
            result = CapabilityCheckResult(
                capability_name=capability_name,
                state=state,
                last_check_time=now,
                response_time_ms=elapsed_ms,
                error_message=str(e)
            )
        
        self.state.capabilities[capability_name] = result
        return result
    
    async def full_check(self) -> DeviceRuntimeState:
        """执行完整状态检查"""
        import time
        start = time.time()
        
        # 1. 检查会话连接
        await self.check_session_connected()
        
        # 2. 检查运行时桥
        await self.check_runtime_bridge()
        
        # 3. 检查所有权限
        for perm in self.REQUIRED_PERMISSIONS:
            await self.check_permission(perm)
        
        # 4. 检查所有能力
        for cap in self.REQUIRED_CAPABILITIES:
            await self.check_capability(cap)
        
        # 5. 判断动作执行状态
        self._determine_action_state()
        
        self.state.last_full_check = datetime.now()
        self.state.check_duration_ms = (time.time() - start) * 1000
        
        return self.state
    
    def _determine_action_state(self):
        """判断动作执行状态"""
        # 如果在小艺连接端且会话已连接
        if self.is_xiaoyi_channel and self.state.session_connected == SessionState.CONNECTED:
            # 检查是否有权限问题
            denied_perms = [p for p in self.state.permissions.values() 
                          if p.state == PermissionState.DENIED]
            
            if denied_perms:
                self.state.action_ready = ActionState.BLOCKED
            else:
                self.state.action_ready = ActionState.ALLOWED
        else:
            self.state.action_ready = ActionState.BLOCKED
    
    def is_fully_ready(self) -> bool:
        """判断是否完全就绪"""
        return (
            self.state.session_connected == SessionState.CONNECTED and
            self.state.runtime_bridge_ready == BridgeState.READY and
            all(p.state == PermissionState.GRANTED for p in self.state.permissions.values()) and
            all(c.state == CapabilityState.READY for c in self.state.capabilities.values())
        )
    
    def is_partial_ready(self) -> bool:
        """判断是否部分就绪"""
        if self.is_xiaoyi_channel:
            # 小艺连接端，只要会话连接就算部分就绪
            return self.state.session_connected == SessionState.CONNECTED
        
        return (
            self.state.session_connected == SessionState.CONNECTED or
            self.state.runtime_bridge_ready == BridgeState.READY or
            any(c.state == CapabilityState.READY for c in self.state.capabilities.values())
        )
    
    def get_failure_breakdown(self) -> Dict[str, List[str]]:
        """获取失败明细"""
        breakdown = {
            "session_issues": [],
            "bridge_issues": [],
            "permission_issues": [],
            "capability_timeouts": [],
            "capability_errors": []
        }
        
        if self.state.session_connected != SessionState.CONNECTED:
            breakdown["session_issues"].append("session_disconnected")
        
        if self.state.runtime_bridge_ready != BridgeState.READY:
            breakdown["bridge_issues"].append(f"bridge_{self.state.runtime_bridge_ready.value}")
        
        for name, perm in self.state.permissions.items():
            if perm.state == PermissionState.DENIED:
                breakdown["permission_issues"].append(f"{name}_denied")
            elif perm.state == PermissionState.TIMEOUT:
                breakdown["permission_issues"].append(f"{name}_timeout")
        
        for name, cap in self.state.capabilities.items():
            if cap.state == CapabilityState.TIMEOUT:
                breakdown["capability_timeouts"].append(f"{name}_timeout")
            elif cap.state == CapabilityState.ERROR:
                breakdown["capability_errors"].append(f"{name}_error")
        
        return breakdown


def format_state_for_report(state: DeviceRuntimeState) -> str:
    """格式化状态用于报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("CONNECTED RUNTIME STATE REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    # 会话状态
    lines.append("[Session State]")
    lines.append(f"  session_connected: {state.session_connected.value}")
    if state.session_last_heartbeat:
        lines.append(f"  last_heartbeat: {state.session_last_heartbeat.isoformat()}")
    lines.append(f"  is_xiaoyi_channel: {state.is_xiaoyi_channel}")
    lines.append("")
    
    # 运行时桥状态
    lines.append("[Runtime Bridge]")
    lines.append(f"  bridge_ready: {state.runtime_bridge_ready.value}")
    if state.bridge_last_check:
        lines.append(f"  last_check: {state.bridge_last_check.isoformat()}")
    lines.append("")
    
    # 权限状态
    lines.append("[Permissions]")
    for name, perm in state.permissions.items():
        status = perm.state.value
        if perm.error_message:
            status += f" ({perm.error_message})"
        lines.append(f"  {name}: {status}")
    lines.append("")
    
    # 能力状态
    lines.append("[Capabilities]")
    for name, cap in state.capabilities.items():
        status = cap.state.value
        if cap.response_time_ms:
            status += f" ({cap.response_time_ms:.1f}ms)"
        if cap.error_message:
            status += f" - {cap.error_message}"
        lines.append(f"  {name}: {status}")
    lines.append("")
    
    # 动作状态
    lines.append("[Action State]")
    lines.append(f"  action_ready: {state.action_ready.value}")
    lines.append("")
    
    # 总结
    lines.append("[Summary]")
    lines.append(f"  {state.get_summary()}")
    lines.append("")
    
    return "\n".join(lines)
