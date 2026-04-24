"""
Capability Registry - 能力统一注册表
所有 capability 名称固定，不允许各模块自己乱写字符串
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import json


class CapabilityCategory(Enum):
    """能力分类"""
    SKILL = "skill"
    WORKFLOW = "workflow"
    MEMORY = "memory"
    REPORT = "report"
    EXTERNAL = "external"
    SYSTEM = "system"
    HIGH_RISK = "high_risk"


@dataclass
class CapabilityDefinition:
    """能力定义"""
    name: str
    category: CapabilityCategory
    description: str
    risk_weight: float = 1.0
    requires_review: bool = False
    dependencies: List[str] = field(default_factory=list)


class GovernanceCapabilityRegistry:
    """
    治理能力注册表（与 capabilities.registry.CapabilityRegistry 不同）
    
    统一管理所有 capability，确保：
    1. capability 名称固定
    2. requested_capabilities 统一从这里取
    3. allowed/blocked capabilities 基于此 registry
    """
    
    # 预定义能力
    BUILTIN_CAPABILITIES = {
        # Skill 相关
        "skill.execute": CapabilityDefinition(
            name="skill.execute",
            category=CapabilityCategory.SKILL,
            description="执行技能",
            risk_weight=1.0,
            requires_review=False
        ),
        "skill.install": CapabilityDefinition(
            name="skill.install",
            category=CapabilityCategory.SKILL,
            description="安装新技能",
            risk_weight=2.0,
            requires_review=True
        ),
        "skill.remove": CapabilityDefinition(
            name="skill.remove",
            category=CapabilityCategory.SKILL,
            description="移除技能",
            risk_weight=2.5,
            requires_review=True
        ),
        "skill.upgrade": CapabilityDefinition(
            name="skill.upgrade",
            category=CapabilityCategory.SKILL,
            description="升级技能",
            risk_weight=2.0,
            requires_review=True
        ),
        
        # Workflow 相关
        "workflow.execute": CapabilityDefinition(
            name="workflow.execute",
            category=CapabilityCategory.WORKFLOW,
            description="执行工作流",
            risk_weight=1.5,
            requires_review=False
        ),
        "workflow.create": CapabilityDefinition(
            name="workflow.create",
            category=CapabilityCategory.WORKFLOW,
            description="创建工作流",
            risk_weight=2.0,
            requires_review=True
        ),
        "workflow.modify": CapabilityDefinition(
            name="workflow.modify",
            category=CapabilityCategory.WORKFLOW,
            description="修改工作流",
            risk_weight=2.0,
            requires_review=True
        ),
        
        # Memory 相关
        "memory.read": CapabilityDefinition(
            name="memory.read",
            category=CapabilityCategory.MEMORY,
            description="读取记忆",
            risk_weight=0.5,
            requires_review=False
        ),
        "memory.write": CapabilityDefinition(
            name="memory.write",
            category=CapabilityCategory.MEMORY,
            description="写入记忆",
            risk_weight=1.0,
            requires_review=False
        ),
        "memory.delete": CapabilityDefinition(
            name="memory.delete",
            category=CapabilityCategory.MEMORY,
            description="删除记忆",
            risk_weight=2.0,
            requires_review=True
        ),
        
        # Report 相关
        "report.read": CapabilityDefinition(
            name="report.read",
            category=CapabilityCategory.REPORT,
            description="读取报告",
            risk_weight=0.5,
            requires_review=False
        ),
        "report.write": CapabilityDefinition(
            name="report.write",
            category=CapabilityCategory.REPORT,
            description="写入报告",
            risk_weight=1.5,
            requires_review=False
        ),
        "report.delete": CapabilityDefinition(
            name="report.delete",
            category=CapabilityCategory.REPORT,
            description="删除报告",
            risk_weight=2.5,
            requires_review=True
        ),
        
        # External 相关
        "external.access": CapabilityDefinition(
            name="external.access",
            category=CapabilityCategory.EXTERNAL,
            description="访问外部资源",
            risk_weight=2.0,
            requires_review=False
        ),
        "external.api": CapabilityDefinition(
            name="external.api",
            category=CapabilityCategory.EXTERNAL,
            description="调用外部 API",
            risk_weight=2.5,
            requires_review=True
        ),
        "external.network": CapabilityDefinition(
            name="external.network",
            category=CapabilityCategory.EXTERNAL,
            description="网络访问",
            risk_weight=2.0,
            requires_review=False
        ),
        
        # System 相关
        "system.config": CapabilityDefinition(
            name="system.config",
            category=CapabilityCategory.SYSTEM,
            description="系统配置",
            risk_weight=3.0,
            requires_review=True
        ),
        "system.restart": CapabilityDefinition(
            name="system.restart",
            category=CapabilityCategory.SYSTEM,
            description="系统重启",
            risk_weight=4.0,
            requires_review=True
        ),
        
        # High Risk 相关
        "high_risk.write": CapabilityDefinition(
            name="high_risk.write",
            category=CapabilityCategory.HIGH_RISK,
            description="高风险写入操作",
            risk_weight=5.0,
            requires_review=True
        ),
        "high_risk.delete": CapabilityDefinition(
            name="high_risk.delete",
            category=CapabilityCategory.HIGH_RISK,
            description="高风险删除操作",
            risk_weight=5.0,
            requires_review=True
        ),
        "high_risk.execute": CapabilityDefinition(
            name="high_risk.execute",
            category=CapabilityCategory.HIGH_RISK,
            description="高风险执行操作",
            risk_weight=5.0,
            requires_review=True
        ),
    }
    
    def __init__(self):
        self._registry: Dict[str, CapabilityDefinition] = dict(self.BUILTIN_CAPABILITIES)
        self._custom_capabilities: Dict[str, CapabilityDefinition] = {}
    
    def register(self, capability: CapabilityDefinition) -> bool:
        """
        注册新能力
        
        Args:
            capability: 能力定义
            
        Returns:
            是否注册成功
        """
        if capability.name in self._registry:
            return False
        
        self._registry[capability.name] = capability
        self._custom_capabilities[capability.name] = capability
        return True
    
    def unregister(self, name: str) -> bool:
        """
        注销能力
        
        Args:
            name: 能力名称
            
        Returns:
            是否注销成功
        """
        if name not in self._registry:
            return False
        
        # 不允许注销内置能力
        if name in self.BUILTIN_CAPABILITIES:
            return False
        
        del self._registry[name]
        if name in self._custom_capabilities:
            del self._custom_capabilities[name]
        return True
    
    def is_registered(self, name: str) -> bool:
        """
        检查能力是否已注册
        
        Args:
            name: 能力名称
            
        Returns:
            是否已注册
        """
        return name in self._registry
    
    def get(self, name: str) -> Optional[CapabilityDefinition]:
        """
        获取能力定义
        
        Args:
            name: 能力名称
            
        Returns:
            能力定义，不存在返回 None
        """
        return self._registry.get(name)
    
    def get_all(self) -> Dict[str, CapabilityDefinition]:
        """
        获取所有能力
        
        Returns:
            所有能力定义
        """
        return dict(self._registry)
    
    def get_by_category(self, category: CapabilityCategory) -> List[CapabilityDefinition]:
        """
        按分类获取能力
        
        Args:
            category: 能力分类
            
        Returns:
            该分类下的所有能力
        """
        return [
            cap for cap in self._registry.values()
            if cap.category == category
        ]
    
    def get_high_risk_capabilities(self) -> List[str]:
        """
        获取高风险能力列表
        
        Returns:
            高风险能力名称列表
        """
        return [
            name for name, cap in self._registry.items()
            if cap.risk_weight >= 3.0 or cap.requires_review
        ]
    
    def get_review_required_capabilities(self) -> List[str]:
        """
        获取需要 review 的能力列表
        
        Returns:
            需要 review 的能力名称列表
        """
        return [
            name for name, cap in self._registry.items()
            if cap.requires_review
        ]
    
    def validate_capabilities(self, capabilities: List[str]) -> Dict[str, List[str]]:
        """
        验证能力列表
        
        Args:
            capabilities: 能力列表
            
        Returns:
            {"valid": [...], "invalid": [...]}
        """
        valid = []
        invalid = []
        
        for cap in capabilities:
            if self.is_registered(cap):
                valid.append(cap)
            else:
                invalid.append(cap)
        
        return {"valid": valid, "invalid": invalid}
    
    def calculate_risk_score(self, capabilities: List[str]) -> float:
        """
        计算能力组合的风险分数
        
        Args:
            capabilities: 能力列表
            
        Returns:
            风险分数
        """
        total_score = 0.0
        for cap_name in capabilities:
            cap = self.get(cap_name)
            if cap:
                total_score += cap.risk_weight
        return total_score
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载注册表
        
        Returns:
            重载结果
        """
        # 保留自定义能力，重置内置能力
        self._registry = dict(self.BUILTIN_CAPABILITIES)
        self._registry.update(self._custom_capabilities)
        
        return {
            "status": "reloaded",
            "total_capabilities": len(self._registry),
            "builtin": len(self.BUILTIN_CAPABILITIES),
            "custom": len(self._custom_capabilities)
        }
    
    def export_registry(self) -> str:
        """
        导出注册表为 JSON
        
        Returns:
            JSON 字符串
        """
        data = {
            name: {
                "name": cap.name,
                "category": cap.category.value,
                "description": cap.description,
                "risk_weight": cap.risk_weight,
                "requires_review": cap.requires_review,
                "dependencies": cap.dependencies
            }
            for name, cap in self._registry.items()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


# 全局单例
_capability_registry = None

def get_capability_registry() -> GovernanceCapabilityRegistry:
    """获取能力注册表单例"""
    global _capability_registry
    if _capability_registry is None:
        _capability_registry = GovernanceCapabilityRegistry()
    return _capability_registry
