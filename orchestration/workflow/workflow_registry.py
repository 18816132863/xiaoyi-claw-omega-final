"""
Workflow Registry - Workflow 模板注册中心
所有正式 workflow 都必须先注册
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import copy


class WorkflowStatus(Enum):
    """Workflow 模板状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class RecoveryPolicyType(Enum):
    """恢复策略类型"""
    RETRY = "retry"
    FALLBACK = "fallback"
    ROLLBACK = "rollback"
    SKIP = "skip"
    ABORT = "abort"


@dataclass
class RecoveryPolicy:
    """恢复策略"""
    policy_type: RecoveryPolicyType
    max_retries: int = 3
    retry_delay_ms: int = 1000
    fallback_skill: Optional[str] = None
    rollback_to_step: Optional[str] = None
    skip_on_failure: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_type": self.policy_type.value,
            "max_retries": self.max_retries,
            "retry_delay_ms": self.retry_delay_ms,
            "fallback_skill": self.fallback_skill,
            "rollback_to_step": self.rollback_to_step,
            "skip_on_failure": self.skip_on_failure
        }


@dataclass
class WorkflowStep:
    """Workflow 步骤"""
    step_id: str
    name: str
    action: str
    description: str = ""
    depends_on: List[str] = field(default_factory=list)
    required_capabilities: List[str] = field(default_factory=list)
    timeout_ms: int = 30000
    recovery_policy: Optional[RecoveryPolicy] = None
    is_high_risk: bool = False
    safe_mode_supported: bool = True
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "name": self.name,
            "action": self.action,
            "description": self.description,
            "depends_on": self.depends_on,
            "required_capabilities": self.required_capabilities,
            "timeout_ms": self.timeout_ms,
            "recovery_policy": self.recovery_policy.to_dict() if self.recovery_policy else None,
            "is_high_risk": self.is_high_risk,
            "safe_mode_supported": self.safe_mode_supported,
            "params": self.params
        }


@dataclass
class WorkflowTemplate:
    """Workflow 模板"""
    workflow_id: str
    version: str
    name: str
    description: str = ""
    profile_compatibility: List[str] = field(default_factory=lambda: ["default"])
    required_capabilities: List[str] = field(default_factory=list)
    steps: List[WorkflowStep] = field(default_factory=list)
    recovery_policy: Optional[RecoveryPolicy] = None
    safe_mode_supported: bool = True
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "profile_compatibility": self.profile_compatibility,
            "required_capabilities": self.required_capabilities,
            "steps": [step.to_dict() for step in self.steps],
            "recovery_policy": self.recovery_policy.to_dict() if self.recovery_policy else None,
            "safe_mode_supported": self.safe_mode_supported,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }


class WorkflowRegistry:
    """
    Workflow 注册中心
    
    所有正式 workflow 都必须先注册：
    - register(template) - 注册模板
    - get(workflow_id, version) - 获取模板
    - list() - 列出所有模板
    - resolve(workflow_id, version) - 解析模板
    """
    
    def __init__(self):
        self._templates: Dict[str, WorkflowTemplate] = {}  # key: "workflow_id:version"
        self._latest_versions: Dict[str, str] = {}  # key: workflow_id, value: latest version
        self._custom_templates: Dict[str, WorkflowTemplate] = {}
    
    def register(self, template: WorkflowTemplate) -> bool:
        """
        注册 workflow 模板
        
        Args:
            template: Workflow 模板
            
        Returns:
            是否注册成功
        """
        key = f"{template.workflow_id}:{template.version}"
        
        if key in self._templates:
            return False
        
        self._templates[key] = template
        
        # 更新最新版本
        if template.workflow_id not in self._latest_versions:
            self._latest_versions[template.workflow_id] = template.version
        else:
            # 比较版本号
            if self._compare_versions(template.version, self._latest_versions[template.workflow_id]) > 0:
                self._latest_versions[template.workflow_id] = template.version
        
        return True
    
    def unregister(self, workflow_id: str, version: str) -> bool:
        """
        注销 workflow 模板
        
        Args:
            workflow_id: Workflow ID
            version: 版本
            
        Returns:
            是否注销成功
        """
        key = f"{workflow_id}:{version}"
        
        if key not in self._templates:
            return False
        
        del self._templates[key]
        
        # 更新最新版本
        if workflow_id in self._latest_versions:
            if self._latest_versions[workflow_id] == version:
                # 找下一个最新版本
                versions = [v for k, v in [k.split(":") for k in self._templates.keys() if k.startswith(f"{workflow_id}:")]]
                if versions:
                    self._latest_versions[workflow_id] = max(versions, key=lambda v: self._parse_version(v))
                else:
                    del self._latest_versions[workflow_id]
        
        return True
    
    def get(self, workflow_id: str, version: Optional[str] = None) -> Optional[WorkflowTemplate]:
        """
        获取 workflow 模板
        
        Args:
            workflow_id: Workflow ID
            version: 版本（可选，默认最新版本）
            
        Returns:
            Workflow 模板，不存在返回 None
        """
        if version is None:
            version = self._latest_versions.get(workflow_id)
            if version is None:
                return None
        
        key = f"{workflow_id}:{version}"
        return self._templates.get(key)
    
    def list(self, status: Optional[WorkflowStatus] = None) -> List[WorkflowTemplate]:
        """
        列出所有 workflow 模板
        
        Args:
            status: 状态过滤（可选）
            
        Returns:
            模板列表
        """
        templates = list(self._templates.values())
        
        if status:
            templates = [t for t in templates if t.status == status]
        
        return templates
    
    def resolve(self, workflow_id: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        解析 workflow 模板（返回字典格式）
        
        Args:
            workflow_id: Workflow ID
            version: 版本（可选）
            
        Returns:
            模板字典
        """
        template = self.get(workflow_id, version)
        if template:
            return template.to_dict()
        return {}
    
    def get_latest_version(self, workflow_id: str) -> Optional[str]:
        """
        获取最新版本
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            最新版本号
        """
        return self._latest_versions.get(workflow_id)
    
    def update_status(self, workflow_id: str, version: str, status: WorkflowStatus) -> bool:
        """
        更新模板状态
        
        Args:
            workflow_id: Workflow ID
            version: 版本
            status: 新状态
            
        Returns:
            是否更新成功
        """
        template = self.get(workflow_id, version)
        if not template:
            return False
        
        template.status = status
        template.updated_at = datetime.now().isoformat()
        return True
    
    def get_by_profile(self, profile: str) -> List[WorkflowTemplate]:
        """
        按配置获取兼容的 workflow
        
        Args:
            profile: 配置名
            
        Returns:
            兼容的模板列表
        """
        return [
            t for t in self._templates.values()
            if profile in t.profile_compatibility and t.status == WorkflowStatus.ACTIVE
        ]
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        比较版本号
        
        Args:
            v1: 版本1
            v2: 版本2
            
        Returns:
            1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        p1 = self._parse_version(v1)
        p2 = self._parse_version(v2)
        
        if p1 > p2:
            return 1
        elif p1 < p2:
            return -1
        return 0
    
    def _parse_version(self, version: str) -> tuple:
        """
        解析版本号
        
        Args:
            version: 版本字符串
            
        Returns:
            版本元组
        """
        try:
            return tuple(int(x) for x in version.split("."))
        except:
            return (0,)


# 全局单例
_workflow_registry = None

def get_workflow_registry() -> WorkflowRegistry:
    """获取 Workflow 注册中心单例"""
    global _workflow_registry
    if _workflow_registry is None:
        _workflow_registry = WorkflowRegistry()
    return _workflow_registry
