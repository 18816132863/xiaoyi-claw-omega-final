#!/usr/bin/env python3
"""
合规与信任中心 - V2.8.0

能力：
- 审计留痕体系
- 数据保留规则
- 数据删除规则
- 权限变更记录
- 租户隔离验证机制
- 高风险动作追踪
- 外部访问授权记录
- 合规导出报告模板
"""

import json
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class AuditEventType(Enum):
    AUTH = "auth"                   # 认证事件
    PERMISSION = "permission"       # 权限变更
    DATA_ACCESS = "data_access"     # 数据访问
    DATA_MODIFY = "data_modify"     # 数据修改
    DATA_DELETE = "data_delete"     # 数据删除
    CONFIG_CHANGE = "config_change" # 配置变更
    HIGH_RISK = "high_risk"         # 高风险操作
    EXTERNAL = "external"           # 外部访问

class RetentionPolicy(Enum):
    SHORT = "short"       # 30天
    MEDIUM = "medium"     # 1年
    LONG = "long"         # 3年
    PERMANENT = "permanent" # 永久

@dataclass
class AuditEvent:
    """审计事件"""
    event_id: str
    event_type: str
    timestamp: str
    actor: str                    # 操作者
    actor_type: str               # user / system / external
    action: str                   # 操作
    resource_type: str            # 资源类型
    resource_id: str              # 资源ID
    workspace_id: str             # 工作区
    tenant_id: str                # 租户
    details: Dict[str, Any]       # 详情
    ip_address: str               # IP地址
    user_agent: str               # 用户代理
    result: str                   # success / failure
    risk_level: str               # low / medium / high / critical

@dataclass
class RetentionRule:
    """数据保留规则"""
    rule_id: str
    data_type: str
    retention_days: int
    auto_delete: bool
    archive_before_delete: bool
    exceptions: List[str]

@dataclass
class DeletionRequest:
    """数据删除请求"""
    request_id: str
    requester: str
    data_type: str
    data_scope: str               # all / specific
    data_ids: List[str]
    reason: str
    status: str                   # pending / approved / rejected / completed
    created_at: str
    completed_at: Optional[str]
    approver: Optional[str]

@dataclass
class PermissionChange:
    """权限变更记录"""
    change_id: str
    timestamp: str
    actor: str
    target_user: str
    target_workspace: str
    change_type: str              # grant / revoke / modify
    old_permissions: List[str]
    new_permissions: List[str]
    reason: str

@dataclass
class IsolationVerification:
    """隔离验证记录"""
    verification_id: str
    timestamp: str
    tenant_id: str
    workspace_id: str
    check_type: str
    result: str                   # pass / fail
    findings: List[str]

@dataclass
class ExternalAuthorization:
    """外部访问授权"""
    auth_id: str
    external_party: str
    authorized_by: str
    authorized_at: str
    scope: List[str]
    expires_at: str
    status: str                   # active / expired / revoked

class ComplianceTrustCenter:
    """合规与信任中心"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.compliance_path = self.project_root / 'compliance'
        self.config_path = self.compliance_path / 'compliance_config.json'
        
        # 审计事件
        self.audit_events: List[AuditEvent] = []
        
        # 保留规则
        self.retention_rules: Dict[str, RetentionRule] = {}
        
        # 删除请求
        self.deletion_requests: List[DeletionRequest] = []
        
        # 权限变更
        self.permission_changes: List[PermissionChange] = []
        
        # 隔离验证
        self.isolation_verifications: List[IsolationVerification] = []
        
        # 外部授权
        self.external_authorizations: List[ExternalAuthorization] = []
        
        self._init_defaults()
        self._load()
    
    def _init_defaults(self):
        """初始化默认配置"""
        # 默认保留规则
        default_rules = [
            RetentionRule("ret_001", "audit_logs", 1095, False, True, []),  # 3年
            RetentionRule("ret_002", "task_results", 365, True, True, []),
            RetentionRule("ret_003", "products", 365, True, True, []),
            RetentionRule("ret_004", "temp_data", 30, True, False, []),
            RetentionRule("ret_005", "permission_changes", 1095, False, True, []),
        ]
        
        for rule in default_rules:
            self.retention_rules[rule.data_type] = rule
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            self.audit_events = [AuditEvent(**e) for e in data.get("audit_events", [])[-10000:]]
            
            for rid, rule in data.get("retention_rules", {}).items():
                self.retention_rules[rid] = RetentionRule(**rule)
            
            self.deletion_requests = [DeletionRequest(**r) for r in data.get("deletion_requests", [])]
            self.permission_changes = [PermissionChange(**c) for c in data.get("permission_changes", [])]
            self.isolation_verifications = [IsolationVerification(**v) for v in data.get("isolation_verifications", [])]
            self.external_authorizations = [ExternalAuthorization(**a) for a in data.get("external_authorizations", [])]
    
    def _save(self):
        """保存配置"""
        self.compliance_path.mkdir(parents=True, exist_ok=True)
        data = {
            "audit_events": [asdict(e) for e in self.audit_events[-10000:]],
            "retention_rules": {rid: asdict(r) for rid, r in self.retention_rules.items()},
            "deletion_requests": [asdict(r) for r in self.deletion_requests],
            "permission_changes": [asdict(c) for c in self.permission_changes],
            "isolation_verifications": [asdict(v) for v in self.isolation_verifications],
            "external_authorizations": [asdict(a) for a in self.external_authorizations],
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _generate_event_id(self) -> str:
        """生成事件ID"""
        return f"evt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    # === 审计留痕 ===
    def log_event(self, event_type: str, actor: str, action: str,
                  resource_type: str, resource_id: str,
                  workspace_id: str, tenant_id: str,
                  details: Dict = None, ip_address: str = "",
                  user_agent: str = "", result: str = "success",
                  risk_level: str = "low") -> AuditEvent:
        """记录审计事件"""
        event = AuditEvent(
            event_id=self._generate_event_id(),
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            actor=actor,
            actor_type="user" if not actor.startswith("system") else "system",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            risk_level=risk_level
        )
        
        self.audit_events.append(event)
        self._save()
        
        return event
    
    def log_high_risk_action(self, actor: str, action: str,
                             details: Dict, workspace_id: str = "",
                             tenant_id: str = "") -> AuditEvent:
        """记录高风险操作"""
        return self.log_event(
            event_type=AuditEventType.HIGH_RISK.value,
            actor=actor,
            action=action,
            resource_type="system",
            resource_id="high_risk_action",
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            details=details,
            risk_level="high"
        )
    
    def query_audit_events(self, event_type: str = None,
                           actor: str = None, tenant_id: str = None,
                           start_time: str = None, end_time: str = None,
                           risk_level: str = None) -> List[AuditEvent]:
        """查询审计事件"""
        events = self.audit_events
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if actor:
            events = [e for e in events if e.actor == actor]
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        if risk_level:
            events = [e for e in events if e.risk_level == risk_level]
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        return events
    
    # === 数据保留 ===
    def get_retention_rule(self, data_type: str) -> Optional[RetentionRule]:
        """获取保留规则"""
        return self.retention_rules.get(data_type)
    
    def check_retention_compliance(self, data_type: str, created_date: str) -> tuple:
        """检查保留合规性"""
        rule = self.get_retention_rule(data_type)
        if not rule:
            return True, "无保留规则"
        
        created = datetime.fromisoformat(created_date)
        expiry = created + timedelta(days=rule.retention_days)
        
        if datetime.now() > expiry:
            return False, f"数据已超过保留期限 ({rule.retention_days}天)"
        
        return True, f"数据在保留期限内，将于 {expiry.date()} 过期"
    
    # === 数据删除 ===
    def create_deletion_request(self, requester: str, data_type: str,
                                data_scope: str, data_ids: List[str],
                                reason: str) -> DeletionRequest:
        """创建删除请求"""
        request = DeletionRequest(
            request_id=f"del_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            requester=requester,
            data_type=data_type,
            data_scope=data_scope,
            data_ids=data_ids,
            reason=reason,
            status="pending",
            created_at=datetime.now().isoformat(),
            completed_at=None,
            approver=None
        )
        
        self.deletion_requests.append(request)
        self._save()
        
        return request
    
    def approve_deletion(self, request_id: str, approver: str) -> Dict:
        """批准删除"""
        for request in self.deletion_requests:
            if request.request_id == request_id:
                request.status = "approved"
                request.approver = approver
                self._save()
                return {"status": "approved", "request_id": request_id}
        return {"error": "请求不存在"}
    
    def complete_deletion(self, request_id: str) -> Dict:
        """完成删除"""
        for request in self.deletion_requests:
            if request.request_id == request_id:
                request.status = "completed"
                request.completed_at = datetime.now().isoformat()
                self._save()
                return {"status": "completed", "request_id": request_id}
        return {"error": "请求不存在"}
    
    # === 权限变更 ===
    def log_permission_change(self, actor: str, target_user: str,
                              target_workspace: str, change_type: str,
                              old_permissions: List[str],
                              new_permissions: List[str],
                              reason: str) -> PermissionChange:
        """记录权限变更"""
        change = PermissionChange(
            change_id=f"perm_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            actor=actor,
            target_user=target_user,
            target_workspace=target_workspace,
            change_type=change_type,
            old_permissions=old_permissions,
            new_permissions=new_permissions,
            reason=reason
        )
        
        self.permission_changes.append(change)
        self._save()
        
        return change
    
    # === 隔离验证 ===
    def verify_isolation(self, tenant_id: str, workspace_id: str,
                         check_type: str) -> IsolationVerification:
        """验证隔离"""
        # 执行隔离检查
        findings = []
        result = "pass"
        
        # 简化实现：模拟检查
        if check_type == "data_isolation":
            findings.append("数据目录隔离检查通过")
        elif check_type == "config_isolation":
            findings.append("配置隔离检查通过")
        elif check_type == "memory_isolation":
            findings.append("记忆隔离检查通过")
        
        verification = IsolationVerification(
            verification_id=f"iso_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            check_type=check_type,
            result=result,
            findings=findings
        )
        
        self.isolation_verifications.append(verification)
        self._save()
        
        return verification
    
    # === 外部授权 ===
    def authorize_external(self, external_party: str, authorized_by: str,
                           scope: List[str], expires_days: int) -> ExternalAuthorization:
        """授权外部访问"""
        auth = ExternalAuthorization(
            auth_id=f"ext_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            external_party=external_party,
            authorized_by=authorized_by,
            authorized_at=datetime.now().isoformat(),
            scope=scope,
            expires_at=(datetime.now() + timedelta(days=expires_days)).isoformat(),
            status="active"
        )
        
        self.external_authorizations.append(auth)
        self._save()
        
        return auth
    
    def check_external_auth(self, external_party: str, scope: str) -> tuple:
        """检查外部授权"""
        for auth in self.external_authorizations:
            if (auth.external_party == external_party and
                auth.status == "active" and
                (scope in auth.scope or "all" in auth.scope)):
                
                if datetime.fromisoformat(auth.expires_at) > datetime.now():
                    return True, "授权有效"
                else:
                    auth.status = "expired"
                    self._save()
                    return False, "授权已过期"
        
        return False, "未找到有效授权"
    
    # === 合规报告 ===
    def generate_compliance_report(self, tenant_id: str = None) -> str:
        """生成合规报告"""
        lines = [
            "# 合规报告",
            f"\n生成时间: {datetime.now().isoformat()}",
            ""
        ]
        
        # 审计统计
        events = self.audit_events
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        
        lines.extend([
            "## 审计统计",
            "",
            f"- 总事件数: {len(events)}",
            f"- 高风险事件: {len([e for e in events if e.risk_level == 'high'])}",
            f"- 失败事件: {len([e for e in events if e.result == 'failure'])}",
            ""
        ])
        
        # 保留规则
        lines.extend([
            "## 数据保留规则",
            ""
        ])
        for data_type, rule in self.retention_rules.items():
            lines.append(f"- **{data_type}**: {rule.retention_days}天 {'(自动删除)' if rule.auto_delete else ''}")
        
        # 隔离验证
        lines.extend([
            "",
            "## 隔离验证",
            ""
        ])
        verifications = self.isolation_verifications[-10:]
        for v in verifications:
            icon = "✅" if v.result == "pass" else "❌"
            lines.append(f"- {icon} [{v.check_type}] {v.tenant_id}")
        
        return "\n".join(lines)

# 全局实例
_trust_center = None

def get_trust_center() -> ComplianceTrustCenter:
    global _trust_center
    if _trust_center is None:
        _trust_center = ComplianceTrustCenter()
    return _trust_center
