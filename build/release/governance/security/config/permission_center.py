#!/usr/bin/env python3
"""
配置与权限中心 - V2.8.0

统一管理：
- 默认开启/关闭的功能
- 哪些工作流允许自动执行
- 哪些动作必须人工确认
- 不同角色可调用哪些能力
- 不同项目可接入哪些外部工具
- 不同环境使用哪套配置
"""

import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum

from infrastructure.path_resolver import get_project_root

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FeatureConfig:
    """功能配置"""
    name: str
    enabled: bool
    auto_execute: bool
    requires_confirmation: bool
    risk_level: str
    allowed_roles: List[str]
    allowed_projects: List[str]

@dataclass
class RolePermission:
    """角色权限"""
    role: str
    allowed_workflows: List[str]
    allowed_entries: List[str]
    allowed_tools: List[str]
    max_risk_level: str

@dataclass
class ProjectConfig:
    """项目配置"""
    project_id: str
    project_name: str
    allowed_tools: List[str]
    allowed_workflows: List[str]
    custom_settings: Dict[str, Any]

@dataclass
class EnvironmentConfig:
    """环境配置"""
    environment: str
    features: Dict[str, bool]
    limits: Dict[str, int]
    endpoints: Dict[str, str]

class ConfigPermissionCenter:
    """配置与权限中心"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.config_path = self.project_root / 'governance' / 'config' / 'permission_config.json'
        
        # 功能配置
        self.features: Dict[str, FeatureConfig] = {}
        
        # 角色权限
        self.role_permissions: Dict[str, RolePermission] = {}
        
        # 项目配置
        self.project_configs: Dict[str, ProjectConfig] = {}
        
        # 环境配置
        self.environment_configs: Dict[str, EnvironmentConfig] = {}
        
        # 当前环境
        self.current_environment: str = Environment.DEVELOPMENT.value
        
        self._init_defaults()
        self._load()
    
    def _init_defaults(self):
        """初始化默认配置"""
        # 默认功能配置
        default_features = [
            ("task_execution", True, True, False, RiskLevel.LOW.value, ["boss", "operator", "selector"], []),
            ("workflow_auto_select", True, True, False, RiskLevel.LOW.value, ["operator"], []),
            ("product_archive", True, True, False, RiskLevel.LOW.value, ["operator", "architect"], []),
            ("blocker_mark", True, False, True, RiskLevel.MEDIUM.value, ["operator"], []),
            ("audit_execution", True, False, True, RiskLevel.MEDIUM.value, ["architect"], []),
            ("system_config_change", True, False, True, RiskLevel.HIGH.value, ["architect"], []),
            ("external_tool_access", True, False, True, RiskLevel.HIGH.value, ["operator"], []),
            ("data_export", True, False, True, RiskLevel.MEDIUM.value, ["boss", "operator"], []),
        ]
        
        for name, enabled, auto, confirm, risk, roles, projects in default_features:
            self.features[name] = FeatureConfig(
                name=name,
                enabled=enabled,
                auto_execute=auto,
                requires_confirmation=confirm,
                risk_level=risk,
                allowed_roles=roles,
                allowed_projects=projects
            )
        
        # 默认角色权限
        default_roles = [
            ("boss", ["all"], ["task", "project", "product"], ["web_search"], RiskLevel.MEDIUM.value),
            ("operator", ["all"], ["task", "project", "product"], ["all"], RiskLevel.HIGH.value),
            ("selector", ["ecommerce_product_analysis"], ["task", "product"], ["web_search"], RiskLevel.LOW.value),
            ("architect", ["code_audit"], ["audit", "product"], ["all"], RiskLevel.CRITICAL.value),
        ]
        
        for role, workflows, entries, tools, max_risk in default_roles:
            self.role_permissions[role] = RolePermission(
                role=role,
                allowed_workflows=workflows,
                allowed_entries=entries,
                allowed_tools=tools,
                max_risk_level=max_risk
            )
        
        # 默认环境配置
        for env in [Environment.DEVELOPMENT.value, Environment.STAGING.value, Environment.PRODUCTION.value]:
            self.environment_configs[env] = EnvironmentConfig(
                environment=env,
                features={"auto_execute": env != Environment.PRODUCTION.value},
                limits={"max_concurrent_tasks": 10 if env == Environment.PRODUCTION.value else 100},
                endpoints={"api": f"https://api.{env}.example.com"}
            )
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for name, fc in data.get("features", {}).items():
                self.features[name] = FeatureConfig(**fc)
            
            for role, rp in data.get("role_permissions", {}).items():
                self.role_permissions[role] = RolePermission(**rp)
    
    def _save(self):
        """保存配置"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "features": {name: asdict(fc) for name, fc in self.features.items()},
            "role_permissions": {role: asdict(rp) for role, rp in self.role_permissions.items()},
            "project_configs": {pid: asdict(pc) for pid, pc in self.project_configs.items()},
            "current_environment": self.current_environment,
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """检查功能是否启用"""
        if feature_name not in self.features:
            return False
        return self.features[feature_name].enabled
    
    def can_auto_execute(self, feature_name: str) -> bool:
        """检查是否可自动执行"""
        if feature_name not in self.features:
            return False
        feature = self.features[feature_name]
        return feature.enabled and feature.auto_execute
    
    def requires_confirmation(self, feature_name: str) -> bool:
        """检查是否需要确认"""
        if feature_name not in self.features:
            return True  # 未知功能默认需要确认
        return self.features[feature_name].requires_confirmation
    
    def check_role_permission(self, role: str, action: str, action_type: str = "workflow") -> tuple:
        """检查角色权限"""
        if role not in self.role_permissions:
            return False, f"未知角色: {role}"
        
        permission = self.role_permissions[role]
        
        if action_type == "workflow":
            if "all" not in permission.allowed_workflows and action not in permission.allowed_workflows:
                return False, f"角色 {role} 无权访问工作流 {action}"
        
        elif action_type == "entry":
            if action not in permission.allowed_entries:
                return False, f"角色 {role} 无权访问入口 {action}"
        
        elif action_type == "tool":
            if "all" not in permission.allowed_tools and action not in permission.allowed_tools:
                return False, f"角色 {role} 无权使用工具 {action}"
        
        return True, "权限检查通过"
    
    def check_risk_level(self, role: str, risk_level: str) -> bool:
        """检查风险等级"""
        if role not in self.role_permissions:
            return False
        
        permission = self.role_permissions[role]
        risk_order = [RiskLevel.LOW.value, RiskLevel.MEDIUM.value, RiskLevel.HIGH.value, RiskLevel.CRITICAL.value]
        
        max_idx = risk_order.index(permission.max_risk_level)
        action_idx = risk_order.index(risk_level)
        
        return action_idx <= max_idx
    
    def set_environment(self, environment: str):
        """设置环境"""
        if environment in self.environment_configs:
            self.current_environment = environment
            self._save()
    
    def get_environment_config(self) -> EnvironmentConfig:
        """获取当前环境配置"""
        return self.environment_configs.get(self.current_environment)
    
    def update_feature(self, feature_name: str, **kwargs):
        """更新功能配置"""
        if feature_name in self.features:
            feature = self.features[feature_name]
            for key, value in kwargs.items():
                if hasattr(feature, key):
                    setattr(feature, key, value)
            self._save()
    
    def get_all_features(self) -> List[Dict]:
        """获取所有功能"""
        return [asdict(f) for f in self.features.values()]
    
    def get_all_roles(self) -> List[Dict]:
        """获取所有角色权限"""
        return [asdict(r) for r in self.role_permissions.values()]
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 配置与权限报告",
            "",
            f"## 当前环境: {self.current_environment}",
            "",
            "## 功能配置",
            ""
        ]
        
        for feature in self.features.values():
            status = "✅" if feature.enabled else "❌"
            auto = "自动" if feature.auto_execute else "手动"
            confirm = "需确认" if feature.requires_confirmation else "无需确认"
            lines.append(f"- {status} **{feature.name}**: {auto}, {confirm}, 风险: {feature.risk_level}")
        
        lines.extend([
            "",
            "## 角色权限",
            ""
        ])
        
        for perm in self.role_permissions.values():
            lines.append(f"- **{perm.role}**: 工作流={perm.allowed_workflows}, 最大风险={perm.max_risk_level}")
        
        return "\n".join(lines)

# 全局实例
_permission_center = None

def get_permission_center() -> ConfigPermissionCenter:
    global _permission_center
    if _permission_center is None:
        _permission_center = ConfigPermissionCenter()
    return _permission_center
