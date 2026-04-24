#!/usr/bin/env python3
"""
受控自治治理器 - V2.8.1

能力：
- 自动执行动作清单
- 必须确认动作清单
- 必须暂停等待条件
- 回滚触发条件
- 升级上报条件
- 人工接管条件
- 自治行为审计记录
- 自治边界可配置机制
"""

import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class AutonomyLevel(Enum):
    FULL_AUTO = "full_auto"           # 完全自动
    SUPERVISED = "supervised"         # 监督执行
    CONFIRM_REQUIRED = "confirm"      # 需确认
    MANUAL_ONLY = "manual_only"       # 仅手动

class ActionType(Enum):
    EXECUTE = "execute"               # 执行
    CONFIRM = "confirm"               # 确认
    PAUSE = "pause"                   # 暂停
    ROLLBACK = "rollback"             # 回滚
    ESCALATE = "escalate"             # 升级
    HANDOVER = "handover"             # 接管

class ActionRisk(Enum):
    LOW = "low"                       # 低风险
    MEDIUM = "medium"                 # 中风险
    HIGH = "high"                     # 高风险
    CRITICAL = "critical"             # 关键风险

@dataclass
class AutonomyBoundary:
    """自治边界"""
    boundary_id: str
    name: str
    description: str
    allowed_actions: List[str]        # 允许的动作
    confirm_required_actions: List[str]  # 需确认的动作
    pause_conditions: List[str]       # 暂停条件
    rollback_conditions: List[str]    # 回滚条件
    escalate_conditions: List[str]    # 升级条件
    handover_conditions: List[str]    # 接管条件
    max_auto_executions: int          # 最大自动执行次数
    time_window_hours: int            # 时间窗口

@dataclass
class AutonomousAction:
    """自治动作"""
    action_id: str
    action_type: str
    action_name: str
    risk_level: str
    description: str
    parameters: Dict[str, Any]
    pre_conditions: List[str]         # 前置条件
    post_conditions: List[str]        # 后置条件
    rollback_action: Optional[str]    # 回滚动作
    timeout_seconds: int
    status: str                       # pending / executing / completed / failed / rolled_back
    result: Optional[Dict]
    executed_at: Optional[str]
    completed_at: Optional[str]
    audit_trail: List[Dict]

@dataclass
class AutonomyAuditRecord:
    """自治审计记录"""
    record_id: str
    action_id: str
    action_type: str
    decision: str                     # auto_execute / confirm_required / paused / escalated
    reason: str
    human_approved: bool
    approver: Optional[str]
    timestamp: str
    context: Dict

class BoundedAutonomyGovernor:
    """受控自治治理器"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.autonomy_path = self.project_root / 'autonomy'
        self.config_path = self.autonomy_path / 'autonomy_config.json'
        
        # 自治边界
        self.boundaries: Dict[str, AutonomyBoundary] = {}
        
        # 动作队列
        self.action_queue: List[AutonomousAction] = []
        
        # 审计记录
        self.audit_records: List[AutonomyAuditRecord] = []
        
        # 执行统计
        self.stats = {
            "total_actions": 0,
            "auto_executed": 0,
            "confirmed": 0,
            "paused": 0,
            "escalated": 0,
            "rolled_back": 0
        }
        
        self._init_default_boundaries()
        self._load()
    
    def _init_default_boundaries(self):
        """初始化默认边界"""
        # 低风险边界 - 允许自动执行
        low_risk_boundary = AutonomyBoundary(
            boundary_id="boundary_low_risk",
            name="低风险操作边界",
            description="低风险操作可自动执行",
            allowed_actions=["read_file", "list_directory", "search", "generate_report"],
            confirm_required_actions=[],
            pause_conditions=["error_rate > 10%"],
            rollback_conditions=["execution_failed"],
            escalate_conditions=["consecutive_failures >= 3"],
            handover_conditions=["manual_request"],
            max_auto_executions=100,
            time_window_hours=24
        )
        
        # 中风险边界 - 需要监督
        medium_risk_boundary = AutonomyBoundary(
            boundary_id="boundary_medium_risk",
            name="中风险操作边界",
            description="中风险操作需要确认",
            allowed_actions=["create_file", "modify_file", "send_message"],
            confirm_required_actions=["delete_file", "external_api_call"],
            pause_conditions=["resource_usage > 80%"],
            rollback_conditions=["validation_failed"],
            escalate_conditions=["timeout_exceeded"],
            handover_conditions=["user_intervention"],
            max_auto_executions=50,
            time_window_hours=24
        )
        
        # 高风险边界 - 必须确认
        high_risk_boundary = AutonomyBoundary(
            boundary_id="boundary_high_risk",
            name="高风险操作边界",
            description="高风险操作必须人工确认",
            allowed_actions=[],
            confirm_required_actions=["system_config_change", "permission_change", "data_deletion"],
            pause_conditions=["any_error"],
            rollback_conditions=["any_failure"],
            escalate_conditions=["any_warning"],
            handover_conditions=["always"],
            max_auto_executions=0,
            time_window_hours=24
        )
        
        self.boundaries[low_risk_boundary.boundary_id] = low_risk_boundary
        self.boundaries[medium_risk_boundary.boundary_id] = medium_risk_boundary
        self.boundaries[high_risk_boundary.boundary_id] = high_risk_boundary
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for bid, boundary in data.get("boundaries", {}).items():
                self.boundaries[bid] = AutonomyBoundary(**boundary)
            
            self.audit_records = [AutonomyAuditRecord(**r) for r in data.get("audit_records", [])]
            self.stats = data.get("stats", self.stats)
    
    def _save(self):
        """保存配置"""
        self.autonomy_path.mkdir(parents=True, exist_ok=True)
        data = {
            "boundaries": {bid: asdict(b) for bid, b in self.boundaries.items()},
            "audit_records": [asdict(r) for r in self.audit_records[-1000:]],
            "stats": self.stats,
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _generate_action_id(self) -> str:
        """生成动作ID"""
        return f"action_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    def _generate_record_id(self) -> str:
        """生成记录ID"""
        return f"audit_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    # === 动作评估 ===
    def evaluate_action(self, action_name: str, parameters: Dict = None,
                        risk_level: str = "low") -> Dict:
        """评估动作是否可以自动执行"""
        # 根据风险级别选择边界
        boundary_id = f"boundary_{risk_level}_risk"
        boundary = self.boundaries.get(boundary_id)
        
        if not boundary:
            return {
                "decision": "escalate",
                "reason": "未找到对应的自治边界",
                "can_execute": False
            }
        
        # 检查是否在允许列表
        if action_name in boundary.allowed_actions:
            # 检查执行次数限制
            if self.stats["auto_executed"] >= boundary.max_auto_executions:
                return {
                    "decision": "confirm_required",
                    "reason": "已达自动执行上限",
                    "can_execute": False,
                    "boundary": boundary_id
                }
            
            return {
                "decision": "auto_execute",
                "reason": "在允许列表内，可自动执行",
                "can_execute": True,
                "boundary": boundary_id
            }
        
        # 检查是否需要确认
        if action_name in boundary.confirm_required_actions:
            return {
                "decision": "confirm_required",
                "reason": "此操作需要人工确认",
                "can_execute": False,
                "boundary": boundary_id
            }
        
        # 不在允许列表
        return {
            "decision": "escalate",
            "reason": "操作不在允许列表内",
            "can_execute": False,
            "boundary": boundary_id
        }
    
    # === 动作执行 ===
    def submit_action(self, action_name: str, parameters: Dict,
                      risk_level: str = "low", description: str = "",
                      rollback_action: str = None) -> AutonomousAction:
        """提交动作"""
        action_id = self._generate_action_id()
        
        action = AutonomousAction(
            action_id=action_id,
            action_type="execute",
            action_name=action_name,
            risk_level=risk_level,
            description=description,
            parameters=parameters,
            pre_conditions=[],
            post_conditions=[],
            rollback_action=rollback_action,
            timeout_seconds=300,
            status="pending",
            result=None,
            executed_at=None,
            completed_at=None,
            audit_trail=[]
        )
        
        # 评估动作
        evaluation = self.evaluate_action(action_name, parameters, risk_level)
        
        # 记录审计
        audit = AutonomyAuditRecord(
            record_id=self._generate_record_id(),
            action_id=action_id,
            action_type=action_name,
            decision=evaluation["decision"],
            reason=evaluation["reason"],
            human_approved=False,
            approver=None,
            timestamp=datetime.now().isoformat(),
            context={"parameters": parameters, "risk_level": risk_level}
        )
        self.audit_records.append(audit)
        
        # 更新统计
        self.stats["total_actions"] += 1
        if evaluation["decision"] == "auto_execute":
            self.stats["auto_executed"] += 1
        elif evaluation["decision"] == "confirm_required":
            self.stats["confirmed"] += 1
        elif evaluation["decision"] == "paused":
            self.stats["paused"] += 1
        elif evaluation["decision"] == "escalate":
            self.stats["escalated"] += 1
        
        self._save()
        
        return action
    
    def approve_action(self, action_id: str, approver: str) -> Dict:
        """批准动作"""
        for action in self.action_queue:
            if action.action_id == action_id:
                action.status = "approved"
                action.audit_trail.append({
                    "event": "approved",
                    "approver": approver,
                    "timestamp": datetime.now().isoformat()
                })
                self._save()
                return {"status": "approved", "action_id": action_id}
        
        return {"error": "动作不存在"}
    
    def execute_action(self, action_id: str, executor: Callable = None) -> Dict:
        """执行动作"""
        for action in self.action_queue:
            if action.action_id == action_id:
                action.status = "executing"
                action.executed_at = datetime.now().isoformat()
                
                try:
                    # 执行动作（简化实现）
                    if executor:
                        result = executor(action.parameters)
                    else:
                        result = {"status": "simulated"}
                    
                    action.result = result
                    action.status = "completed"
                    action.completed_at = datetime.now().isoformat()
                    
                except Exception as e:
                    action.status = "failed"
                    action.result = {"error": str(e)}
                    
                    # 检查是否需要回滚
                    if action.rollback_action:
                        self.rollback_action(action_id)
                
                self._save()
                return {"status": action.status, "result": action.result}
        
        return {"error": "动作不存在"}
    
    def rollback_action(self, action_id: str) -> Dict:
        """回滚动作"""
        for action in self.action_queue:
            if action.action_id == action_id:
                action.status = "rolled_back"
                action.audit_trail.append({
                    "event": "rollback",
                    "timestamp": datetime.now().isoformat()
                })
                self.stats["rolled_back"] += 1
                self._save()
                return {"status": "rolled_back", "action_id": action_id}
        
        return {"error": "动作不存在"}
    
    # === 条件检查 ===
    def check_pause_conditions(self, boundary_id: str) -> List[str]:
        """检查暂停条件"""
        boundary = self.boundaries.get(boundary_id)
        if not boundary:
            return []
        
        triggered = []
        for condition in boundary.pause_conditions:
            # 简化实现：检查条件
            if "error_rate" in condition:
                # 模拟检查
                pass
            triggered.append(condition)
        
        return triggered
    
    def check_rollback_conditions(self, boundary_id: str) -> List[str]:
        """检查回滚条件"""
        boundary = self.boundaries.get(boundary_id)
        if not boundary:
            return []
        
        triggered = []
        for condition in boundary.rollback_conditions:
            triggered.append(condition)
        
        return triggered
    
    def check_escalate_conditions(self, boundary_id: str) -> List[str]:
        """检查升级条件"""
        boundary = self.boundaries.get(boundary_id)
        if not boundary:
            return []
        
        triggered = []
        for condition in boundary.escalate_conditions:
            triggered.append(condition)
        
        return triggered
    
    # === 边界管理 ===
    def create_boundary(self, name: str, description: str,
                        allowed_actions: List[str],
                        confirm_required_actions: List[str],
                        max_auto_executions: int = 100) -> AutonomyBoundary:
        """创建边界"""
        boundary_id = f"boundary_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        boundary = AutonomyBoundary(
            boundary_id=boundary_id,
            name=name,
            description=description,
            allowed_actions=allowed_actions,
            confirm_required_actions=confirm_required_actions,
            pause_conditions=[],
            rollback_conditions=[],
            escalate_conditions=[],
            handover_conditions=[],
            max_auto_executions=max_auto_executions,
            time_window_hours=24
        )
        
        self.boundaries[boundary_id] = boundary
        self._save()
        
        return boundary
    
    def get_boundary(self, boundary_id: str) -> Optional[AutonomyBoundary]:
        """获取边界"""
        return self.boundaries.get(boundary_id)
    
    def list_boundaries(self) -> List[AutonomyBoundary]:
        """列出边界"""
        return list(self.boundaries.values())
    
    # === 报告 ===
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 自治治理报告",
            f"\n生成时间: {datetime.now().isoformat()}",
            "",
            "## 执行统计",
            ""
        ]
        
        for key, value in self.stats.items():
            lines.append(f"- {key}: {value}")
        
        lines.extend([
            "",
            "## 自治边界",
            ""
        ])
        
        for boundary in self.boundaries.values():
            lines.append(f"### {boundary.name}")
            lines.append(f"- 允许自动执行: {len(boundary.allowed_actions)} 个动作")
            lines.append(f"- 需要确认: {len(boundary.confirm_required_actions)} 个动作")
            lines.append(f"- 最大自动执行次数: {boundary.max_auto_executions}")
            lines.append("")
        
        lines.extend([
            "## 最近审计记录",
            ""
        ])
        
        for record in self.audit_records[-10:]:
            lines.append(f"- [{record.decision}] {record.action_type} ({record.timestamp[:10]})")
        
        return "\n".join(lines)

# 全局实例
_autonomy_governor = None

def get_autonomy_governor() -> BoundedAutonomyGovernor:
    global _autonomy_governor
    if _autonomy_governor is None:
        _autonomy_governor = BoundedAutonomyGovernor()
    return _autonomy_governor
