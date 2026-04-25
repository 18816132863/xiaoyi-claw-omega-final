#!/usr/bin/env python3
"""
多租户/多工作区管理器 - V2.8.0

隔离层级：
- 客户级隔离
- 项目级隔离
- 工作区级隔离
- 角色级权限隔离
- 配置隔离
- 产物隔离
- 记忆与上下文隔离
"""

import json
import os
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class IsolationLevel(Enum):
    CUSTOMER = "customer"       # 客户级
    PROJECT = "project"         # 项目级
    WORKSPACE = "workspace"     # 工作区级

class WorkspaceStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

@dataclass
class Tenant:
    """租户"""
    tenant_id: str
    name: str
    contact: str
    created_at: str
    status: str
    settings: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class Workspace:
    """工作区"""
    workspace_id: str
    tenant_id: str
    project_id: str
    name: str
    isolation_level: str
    status: str
    data_path: str
    config_path: str
    memory_path: str
    product_path: str
    created_at: str
    updated_at: str
    roles: List[str]
    quotas: Dict[str, int]

@dataclass
class IsolationRule:
    """隔离规则"""
    rule_id: str
    source_workspace: str
    target_workspace: str
    resource_type: str
    access_allowed: bool
    audit_enabled: bool

class TenantWorkspaceManager:
    """多租户/多工作区管理器"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.tenant_path = self.project_root / 'tenant'
        self.registry_path = self.tenant_path / 'workspace_registry.json'
        
        self.tenants: Dict[str, Tenant] = {}
        self.workspaces: Dict[str, Workspace] = {}
        self.isolation_rules: List[IsolationRule] = []
        
        self._load()
    
    def _load(self):
        """加载注册表"""
        if self.registry_path.exists():
            data = json.loads(self.registry_path.read_text(encoding='utf-8'))
            
            for tid, tdata in data.get("tenants", {}).items():
                self.tenants[tid] = Tenant(**tdata)
            
            for wid, wdata in data.get("workspaces", {}).items():
                self.workspaces[wid] = Workspace(**wdata)
    
    def _save(self):
        """保存注册表"""
        self.tenant_path.mkdir(parents=True, exist_ok=True)
        data = {
            "tenants": {tid: asdict(t) for tid, t in self.tenants.items()},
            "workspaces": {wid: asdict(w) for wid, w in self.workspaces.items()},
            "isolation_rules": [asdict(r) for r in self.isolation_rules],
            "updated": datetime.now().isoformat()
        }
        self.registry_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def create_tenant(self, name: str, contact: str = "",
                      settings: Dict = None) -> Tenant:
        """创建租户"""
        tenant_id = f"tenant_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            contact=contact,
            created_at=datetime.now().isoformat(),
            status=WorkspaceStatus.ACTIVE.value,
            settings=settings or {},
            metadata={}
        )
        
        self.tenants[tenant_id] = tenant
        self._save()
        
        return tenant
    
    def create_workspace(self, tenant_id: str, project_id: str,
                         name: str, isolation_level: str = "workspace",
                         roles: List[str] = None,
                         quotas: Dict = None) -> Workspace:
        """创建工作区"""
        workspace_id = f"ws_{tenant_id}_{project_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建隔离目录
        base_path = self.tenant_path / tenant_id / project_id
        data_path = base_path / "data"
        config_path = base_path / "config"
        memory_path = base_path / "memory"
        product_path = base_path / "products"
        
        for path in [data_path, config_path, memory_path, product_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        workspace = Workspace(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            project_id=project_id,
            name=name,
            isolation_level=isolation_level,
            status=WorkspaceStatus.ACTIVE.value,
            data_path=str(data_path),
            config_path=str(config_path),
            memory_path=str(memory_path),
            product_path=str(product_path),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            roles=roles or ["operator"],
            quotas=quotas or {"max_tasks": 1000, "max_storage_mb": 1000}
        )
        
        self.workspaces[workspace_id] = workspace
        self._save()
        
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """获取工作区"""
        return self.workspaces.get(workspace_id)
    
    def get_tenant_workspaces(self, tenant_id: str) -> List[Workspace]:
        """获取租户的所有工作区"""
        return [w for w in self.workspaces.values() if w.tenant_id == tenant_id]
    
    def check_isolation(self, source_workspace: str, target_workspace: str,
                        resource_type: str) -> tuple:
        """检查隔离规则"""
        # 不同租户之间完全隔离
        source = self.workspaces.get(source_workspace)
        target = self.workspaces.get(target_workspace)
        
        if not source or not target:
            return False, "工作区不存在"
        
        if source.tenant_id != target.tenant_id:
            return False, "不同租户之间禁止访问"
        
        # 同租户内，检查隔离规则
        for rule in self.isolation_rules:
            if (rule.source_workspace == source_workspace and
                rule.target_workspace == target_workspace and
                rule.resource_type == resource_type):
                return rule.access_allowed, "规则匹配"
        
        # 默认：同租户内允许访问
        return True, "同租户默认允许"
    
    def add_isolation_rule(self, source_workspace: str, target_workspace: str,
                           resource_type: str, access_allowed: bool,
                           audit_enabled: bool = True) -> IsolationRule:
        """添加隔离规则"""
        rule = IsolationRule(
            rule_id=f"rule_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            source_workspace=source_workspace,
            target_workspace=target_workspace,
            resource_type=resource_type,
            access_allowed=access_allowed,
            audit_enabled=audit_enabled
        )
        
        self.isolation_rules.append(rule)
        self._save()
        
        return rule
    
    def suspend_workspace(self, workspace_id: str):
        """暂停工作区"""
        if workspace_id in self.workspaces:
            self.workspaces[workspace_id].status = WorkspaceStatus.SUSPENDED.value
            self._save()
    
    def archive_workspace(self, workspace_id: str):
        """归档工作区"""
        if workspace_id in self.workspaces:
            workspace = self.workspaces[workspace_id]
            workspace.status = WorkspaceStatus.ARCHIVED.value
            workspace.updated_at = datetime.now().isoformat()
            self._save()
    
    def delete_workspace(self, workspace_id: str) -> Dict:
        """删除工作区"""
        if workspace_id not in self.workspaces:
            return {"error": "工作区不存在"}
        
        workspace = self.workspaces[workspace_id]
        
        # 删除数据目录
        base_path = Path(workspace.data_path).parent
        if base_path.exists():
            shutil.rmtree(base_path)
        
        # 从注册表移除
        del self.workspaces[workspace_id]
        self._save()
        
        return {"status": "success", "message": "工作区已删除"}
    
    def get_workspace_resources(self, workspace_id: str) -> Dict:
        """获取工作区资源"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return {"error": "工作区不存在"}
        
        # 统计资源使用
        data_path = Path(workspace.data_path)
        product_path = Path(workspace.product_path)
        
        data_size = sum(f.stat().st_size for f in data_path.rglob('*') if f.is_file()) if data_path.exists() else 0
        product_count = len(list(product_path.glob('*'))) if product_path.exists() else 0
        
        return {
            "workspace_id": workspace_id,
            "data_size_mb": data_size / (1024 * 1024),
            "product_count": product_count,
            "quotas": workspace.quotas,
            "status": workspace.status
        }
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 多租户/工作区报告",
            "",
            "## 租户列表",
            ""
        ]
        
        for tenant in self.tenants.values():
            status = "✅" if tenant.status == WorkspaceStatus.ACTIVE.value else "❌"
            workspaces = self.get_tenant_workspaces(tenant.tenant_id)
            lines.append(f"- {status} **{tenant.name}** ({tenant.tenant_id}): {len(workspaces)} 个工作区")
        
        lines.extend([
            "",
            "## 工作区列表",
            ""
        ])
        
        for workspace in self.workspaces.values():
            status = "✅" if workspace.status == WorkspaceStatus.ACTIVE.value else "⏸️"
            lines.append(f"- {status} **{workspace.name}** ({workspace.isolation_level})")
            lines.append(f"  - 租户: {workspace.tenant_id}")
            lines.append(f"  - 项目: {workspace.project_id}")
            lines.append(f"  - 角色: {', '.join(workspace.roles)}")
        
        return "\n".join(lines)

# 全局实例
_workspace_manager = None

def get_workspace_manager() -> TenantWorkspaceManager:
    global _workspace_manager
    if _workspace_manager is None:
        _workspace_manager = TenantWorkspaceManager()
    return _workspace_manager
