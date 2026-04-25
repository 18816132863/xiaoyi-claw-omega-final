#!/usr/bin/env python3
"""
组织协同编排层 - V2.8.1

能力：
- 角色分工定义
- 任务委派机制
- 审批流转机制
- 交接节点管理
- 人机协作边界
- 外部伙伴协作挂接
- 协同过程审计记录
- 协同阻塞识别
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class RoleType(Enum):
    HUMAN = "human"                   # 人类角色
    AI = "ai"                         # AI角色
    EXTERNAL = "external"             # 外部伙伴
    SYSTEM = "system"                 # 系统角色

class OrgTaskStatus(Enum):
    """组织协同任务状态（与 domain.tasks.specs.TaskStatus 不同）"""
    PENDING = "pending"               # 待处理
    ASSIGNED = "assigned"             # 已分配
    IN_PROGRESS = "in_progress"       # 进行中
    PENDING_REVIEW = "pending_review" # 待审核
    APPROVED = "approved"             # 已批准
    REJECTED = "rejected"             # 已拒绝
    COMPLETED = "completed"           # 已完成
    BLOCKED = "blocked"               # 已阻塞

class ApprovalAction(Enum):
    APPROVE = "approve"               # 批准
    REJECT = "reject"                 # 拒绝
    ESCALATE = "escalate"             # 升级
    DELEGATE = "delegate"             # 委派

@dataclass
class Role:
    """角色"""
    role_id: str
    name: str
    role_type: str
    description: str
    permissions: List[str]
    responsibilities: List[str]
    can_delegate_to: List[str]        # 可委派给的角色
    max_concurrent_tasks: int
    contact: str

@dataclass
class CollaborativeTask:
    """协同任务"""
    task_id: str
    name: str
    description: str
    status: str
    priority: str
    assignee: str                     # 当前负责人
    assignee_role: str                # 负责人角色
    creator: str
    created_at: str
    due_date: Optional[str]
    dependencies: List[str]           # 依赖任务
    handover_nodes: List[Dict]        # 交接节点
    approval_chain: List[Dict]        # 审批链
    current_approval_step: int
    audit_trail: List[Dict]
    blocked_reason: Optional[str]

@dataclass
class HandoverNode:
    """交接节点"""
    node_id: str
    task_id: str
    from_role: str
    to_role: str
    conditions: List[str]             # 交接条件
    required_artifacts: List[str]     # 必需产物
    status: str                       # pending / completed
    completed_at: Optional[str]
    notes: str

@dataclass
class ApprovalRequest:
    """审批请求"""
    request_id: str
    task_id: str
    step: int
    approver_role: str
    approver: Optional[str]
    action: Optional[str]
    comment: str
    status: str                       # pending / approved / rejected
    created_at: str
    processed_at: Optional[str]

class OrgCollaborationOrchestrator:
    """组织协同编排层"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.collab_path = self.project_root / 'collaboration'
        self.config_path = self.collab_path / 'collaboration_config.json'
        
        # 角色
        self.roles: Dict[str, Role] = {}
        
        # 任务
        self.tasks: Dict[str, CollaborativeTask] = {}
        
        # 交接节点
        self.handover_nodes: List[HandoverNode] = []
        
        # 审批请求
        self.approval_requests: List[ApprovalRequest] = []
        
        self._init_default_roles()
        self._load()
    
    def _init_default_roles(self):
        """初始化默认角色"""
        default_roles = [
            Role(
                role_id="role_owner",
                name="项目所有者",
                role_type=RoleType.HUMAN.value,
                description="项目最终负责人",
                permissions=["all"],
                responsibilities=["决策", "审批", "资源分配"],
                can_delegate_to=["role_manager", "role_operator"],
                max_concurrent_tasks=10,
                contact=""
            ),
            Role(
                role_id="role_manager",
                name="项目经理",
                role_type=RoleType.HUMAN.value,
                description="项目执行管理者",
                permissions=["task_assign", "task_review", "report_view"],
                responsibilities=["任务分配", "进度跟踪", "问题升级"],
                can_delegate_to=["role_operator"],
                max_concurrent_tasks=20,
                contact=""
            ),
            Role(
                role_id="role_operator",
                name="执行者",
                role_type=RoleType.HUMAN.value,
                description="任务执行者",
                permissions=["task_execute", "report_submit"],
                responsibilities=["任务执行", "结果提交"],
                can_delegate_to=[],
                max_concurrent_tasks=5,
                contact=""
            ),
            Role(
                role_id="role_ai_assistant",
                name="AI助手",
                role_type=RoleType.AI.value,
                description="AI辅助执行",
                permissions=["task_execute", "data_analyze", "report_generate"],
                responsibilities=["辅助执行", "数据分析", "报告生成"],
                can_delegate_to=[],
                max_concurrent_tasks=100,
                contact="system"
            ),
            Role(
                role_id="role_external_partner",
                name="外部伙伴",
                role_type=RoleType.EXTERNAL.value,
                description="外部协作伙伴",
                permissions=["limited_task_execute"],
                responsibilities=["外部任务执行"],
                can_delegate_to=[],
                max_concurrent_tasks=10,
                contact=""
            ),
        ]
        
        for role in default_roles:
            self.roles[role.role_id] = role
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for rid, role in data.get("roles", {}).items():
                self.roles[rid] = Role(**role)
            
            for tid, task in data.get("tasks", {}).items():
                self.tasks[tid] = CollaborativeTask(**task)
            
            self.handover_nodes = [HandoverNode(**n) for n in data.get("handover_nodes", [])]
            self.approval_requests = [ApprovalRequest(**r) for r in data.get("approval_requests", [])]
    
    def _save(self):
        """保存配置"""
        self.collab_path.mkdir(parents=True, exist_ok=True)
        data = {
            "roles": {rid: asdict(r) for rid, r in self.roles.items()},
            "tasks": {tid: asdict(t) for tid, t in self.tasks.items()},
            "handover_nodes": [asdict(n) for n in self.handover_nodes],
            "approval_requests": [asdict(r) for r in self.approval_requests],
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _generate_task_id(self) -> str:
        """生成任务ID"""
        return f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # === 角色管理 ===
    def get_role(self, role_id: str) -> Optional[Role]:
        """获取角色"""
        return self.roles.get(role_id)
    
    def list_roles(self, role_type: str = None) -> List[Role]:
        """列出角色"""
        roles = list(self.roles.values())
        if role_type:
            roles = [r for r in roles if r.role_type == role_type]
        return roles
    
    def check_permission(self, role_id: str, permission: str) -> tuple:
        """检查权限"""
        role = self.get_role(role_id)
        if not role:
            return False, "角色不存在"
        
        if "all" in role.permissions or permission in role.permissions:
            return True, "权限检查通过"
        
        return False, f"无权限: {permission}"
    
    # === 任务管理 ===
    def create_task(self, name: str, description: str, assignee_role: str,
                    creator: str, priority: str = "medium",
                    due_date: str = None, dependencies: List[str] = None) -> CollaborativeTask:
        """创建任务"""
        task_id = self._generate_task_id()
        
        task = CollaborativeTask(
            task_id=task_id,
            name=name,
            description=description,
            status=OrgTaskStatus.PENDING.value,
            priority=priority,
            assignee="",
            assignee_role=assignee_role,
            creator=creator,
            created_at=datetime.now().isoformat(),
            due_date=due_date,
            dependencies=dependencies or [],
            handover_nodes=[],
            approval_chain=[],
            current_approval_step=0,
            audit_trail=[],
            blocked_reason=None
        )
        
        self.tasks[task_id] = task
        self._save()
        
        return task
    
    def assign_task(self, task_id: str, assignee: str) -> Dict:
        """分配任务"""
        if task_id not in self.tasks:
            return {"error": "任务不存在"}
        
        task = self.tasks[task_id]
        task.assignee = assignee
        task.status = OrgTaskStatus.ASSIGNED.value
        task.audit_trail.append({
            "event": "assigned",
            "assignee": assignee,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
        
        return {"status": "assigned", "task_id": task_id}
    
    def start_task(self, task_id: str) -> Dict:
        """开始任务"""
        if task_id not in self.tasks:
            return {"error": "任务不存在"}
        
        task = self.tasks[task_id]
        
        # 检查依赖
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                if self.tasks[dep_id].status != OrgTaskStatus.COMPLETED.value:
                    task.status = OrgTaskStatus.BLOCKED.value
                    task.blocked_reason = f"依赖任务未完成: {dep_id}"
                    self._save()
                    return {"status": "blocked", "reason": task.blocked_reason}
        
        task.status = OrgTaskStatus.IN_PROGRESS.value
        task.audit_trail.append({
            "event": "started",
            "timestamp": datetime.now().isoformat()
        })
        self._save()
        
        return {"status": "in_progress", "task_id": task_id}
    
    def complete_task(self, task_id: str, result: Dict = None) -> Dict:
        """完成任务"""
        if task_id not in self.tasks:
            return {"error": "任务不存在"}
        
        task = self.tasks[task_id]
        task.status = OrgTaskStatus.COMPLETED.value
        task.audit_trail.append({
            "event": "completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
        
        return {"status": "completed", "task_id": task_id}
    
    # === 委派机制 ===
    def delegate_task(self, task_id: str, from_role: str, to_role: str,
                      reason: str) -> Dict:
        """委派任务"""
        if task_id not in self.tasks:
            return {"error": "任务不存在"}
        
        task = self.tasks[task_id]
        
        # 检查是否可以委派
        role = self.get_role(from_role)
        if role and to_role not in role.can_delegate_to:
            return {"error": f"不能委派给角色: {to_role}"}
        
        task.assignee_role = to_role
        task.audit_trail.append({
            "event": "delegated",
            "from_role": from_role,
            "to_role": to_role,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
        
        return {"status": "delegated", "task_id": task_id}
    
    # === 审批流转 ===
    def create_approval_chain(self, task_id: str, approvers: List[Dict]) -> Dict:
        """创建审批链"""
        if task_id not in self.tasks:
            return {"error": "任务不存在"}
        
        task = self.tasks[task_id]
        task.approval_chain = approvers
        task.current_approval_step = 0
        task.status = OrgTaskStatus.PENDING_REVIEW.value
        self._save()
        
        return {"status": "approval_chain_created", "task_id": task_id}
    
    def submit_for_approval(self, task_id: str) -> Dict:
        """提交审批"""
        if task_id not in self.tasks:
            return {"error": "任务不存在"}
        
        task = self.tasks[task_id]
        
        if not task.approval_chain:
            return {"error": "未设置审批链"}
        
        current_step = task.current_approval_step
        if current_step >= len(task.approval_chain):
            return {"error": "审批已完成"}
        
        approver = task.approval_chain[current_step]
        
        request = ApprovalRequest(
            request_id=f"approval_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task_id=task_id,
            step=current_step,
            approver_role=approver.get("role", ""),
            approver=None,
            action=None,
            comment="",
            status="pending",
            created_at=datetime.now().isoformat(),
            processed_at=None
        )
        
        self.approval_requests.append(request)
        self._save()
        
        return {"status": "submitted", "request_id": request.request_id}
    
    def process_approval(self, request_id: str, action: str, comment: str = "",
                         approver: str = "") -> Dict:
        """处理审批"""
        for request in self.approval_requests:
            if request.request_id == request_id:
                request.action = action
                request.comment = comment
                request.approver = approver
                request.processed_at = datetime.now().isoformat()
                
                task = self.tasks.get(request.task_id)
                if task:
                    if action == ApprovalAction.APPROVE.value:
                        task.current_approval_step += 1
                        if task.current_approval_step >= len(task.approval_chain):
                            task.status = OrgTaskStatus.APPROVED.value
                        task.audit_trail.append({
                            "event": "approved",
                            "step": request.step,
                            "approver": approver,
                            "comment": comment,
                            "timestamp": datetime.now().isoformat()
                        })
                    elif action == ApprovalAction.REJECT.value:
                        task.status = OrgTaskStatus.REJECTED.value
                        task.audit_trail.append({
                            "event": "rejected",
                            "step": request.step,
                            "approver": approver,
                            "comment": comment,
                            "timestamp": datetime.now().isoformat()
                        })
                
                request.status = action
                self._save()
                return {"status": action, "request_id": request_id}
        
        return {"error": "审批请求不存在"}
    
    # === 交接管理 ===
    def create_handover(self, task_id: str, from_role: str, to_role: str,
                        conditions: List[str], required_artifacts: List[str]) -> HandoverNode:
        """创建交接节点"""
        node = HandoverNode(
            node_id=f"handover_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task_id=task_id,
            from_role=from_role,
            to_role=to_role,
            conditions=conditions,
            required_artifacts=required_artifacts,
            status="pending",
            completed_at=None,
            notes=""
        )
        
        self.handover_nodes.append(node)
        
        if task_id in self.tasks:
            self.tasks[task_id].handover_nodes.append({
                "node_id": node.node_id,
                "from_role": from_role,
                "to_role": to_role
            })
        
        self._save()
        
        return node
    
    def complete_handover(self, node_id: str, notes: str = "") -> Dict:
        """完成交接"""
        for node in self.handover_nodes:
            if node.node_id == node_id:
                node.status = "completed"
                node.completed_at = datetime.now().isoformat()
                node.notes = notes
                self._save()
                return {"status": "completed", "node_id": node_id}
        
        return {"error": "交接节点不存在"}
    
    # === 阻塞识别 ===
    def identify_blockers(self) -> List[Dict]:
        """识别阻塞"""
        blockers = []
        
        for task in self.tasks.values():
            if task.status == OrgTaskStatus.BLOCKED.value:
                blockers.append({
                    "task_id": task.task_id,
                    "name": task.name,
                    "reason": task.blocked_reason
                })
            
            # 检查超时
            if task.due_date:
                due = datetime.fromisoformat(task.due_date)
                if datetime.now() > due and task.status not in [OrgTaskStatus.COMPLETED.value, OrgTaskStatus.APPROVED.value]:
                    blockers.append({
                        "task_id": task.task_id,
                        "name": task.name,
                        "reason": "任务已超时"
                    })
        
        return blockers
    
    # === 报告 ===
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 组织协同报告",
            f"\n生成时间: {datetime.now().isoformat()}",
            "",
            "## 任务统计",
            ""
        ]
        
        status_counts = {}
        for task in self.tasks.values():
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
        
        for status, count in status_counts.items():
            lines.append(f"- {status}: {count}")
        
        lines.extend([
            "",
            "## 阻塞任务",
            ""
        ])
        
        blockers = self.identify_blockers()
        for blocker in blockers:
            lines.append(f"- ⚠️ {blocker['name']}: {blocker['reason']}")
        
        if not blockers:
            lines.append("- 无阻塞")
        
        lines.extend([
            "",
            "## 待审批",
            ""
        ])
        
        pending_approvals = [r for r in self.approval_requests if r.status == "pending"]
        for request in pending_approvals:
            lines.append(f"- [{request.approver_role}] {request.task_id}")
        
        return "\n".join(lines)

# 全局实例
_org_orchestrator = None

def get_org_orchestrator() -> OrgCollaborationOrchestrator:
    global _org_orchestrator
    if _org_orchestrator is None:
        _org_orchestrator = OrgCollaborationOrchestrator()
    return _org_orchestrator
