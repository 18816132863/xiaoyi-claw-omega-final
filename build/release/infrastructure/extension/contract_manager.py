#!/usr/bin/env python3
"""
外部扩展协议管理器 - V2.8.0

规范：
- 新技能如何接入
- 新工作流如何上架
- 新外部工具如何接入
- 权限如何声明
- 风险如何分级
- 健康检查如何做
- 替换与下线如何处理
"""

import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class ExtensionType(Enum):
    SKILL = "skill"           # 技能
    WORKFLOW = "workflow"     # 工作流
    TOOL = "tool"             # 外部工具
    PLUGIN = "plugin"         # 插件

class ExtensionStatus(Enum):
    PENDING = "pending"       # 待审核
    APPROVED = "approved"     # 已批准
    ACTIVE = "active"         # 活跃
    DEPRECATED = "deprecated" # 已废弃
    REMOVED = "removed"       # 已下线

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ExtensionContract:
    """扩展契约"""
    extension_id: str
    name: str
    type: str
    version: str
    description: str
    author: str
    risk_level: str
    required_permissions: List[str]
    dependencies: List[str]
    health_check_endpoint: str
    fallback_extension: Optional[str]
    status: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]

@dataclass
class ExtensionValidation:
    """扩展验证结果"""
    extension_id: str
    valid: bool
    errors: List[str]
    warnings: List[str]
    validated_at: str

class ExtensionContractManager:
    """外部扩展协议管理器"""
    
    # 接入契约要求
    CONTRACT_REQUIREMENTS = {
        ExtensionType.SKILL.value: [
            "必须有 SKILL.md 文件",
            "必须声明风险等级",
            "必须声明所需权限",
            "必须提供健康检查方法",
            "必须提供回退方案（可选）"
        ],
        ExtensionType.WORKFLOW.value: [
            "必须继承 WorkflowBase",
            "必须定义输入输出模板",
            "必须声明所需技能",
            "必须定义失败回退逻辑",
            "必须提供完成判定标准"
        ],
        ExtensionType.TOOL.value: [
            "必须声明 API 端点",
            "必须声明认证方式",
            "必须声明风险等级",
            "必须提供错误处理",
            "必须提供健康检查"
        ],
        ExtensionType.PLUGIN.value: [
            "必须实现标准接口",
            "必须声明依赖",
            "必须声明风险等级",
            "必须提供配置说明"
        ]
    }
    
    def __init__(self):
        self.project_root = get_project_root()
        self.contract_path = self.project_root / 'extension' / 'contracts.json'
        
        self.contracts: Dict[str, ExtensionContract] = {}
        self.validations: Dict[str, ExtensionValidation] = {}
        
        self._load()
    
    def _load(self):
        """加载契约"""
        if self.contract_path.exists():
            data = json.loads(self.contract_path.read_text(encoding='utf-8'))
            for ext_id, contract in data.get("contracts", {}).items():
                self.contracts[ext_id] = ExtensionContract(**contract)
    
    def _save(self):
        """保存契约"""
        self.contract_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "contracts": {ext_id: asdict(c) for ext_id, c in self.contracts.items()},
            "updated": datetime.now().isoformat()
        }
        self.contract_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def register_extension(self, name: str, ext_type: str, version: str,
                           description: str, author: str, risk_level: str,
                           required_permissions: List[str], dependencies: List[str],
                           health_check_endpoint: str = "",
                           fallback_extension: str = None,
                           metadata: Dict = None) -> ExtensionContract:
        """注册扩展"""
        extension_id = f"{ext_type}_{name}_{version}".replace(" ", "_").lower()
        
        contract = ExtensionContract(
            extension_id=extension_id,
            name=name,
            type=ext_type,
            version=version,
            description=description,
            author=author,
            risk_level=risk_level,
            required_permissions=required_permissions,
            dependencies=dependencies,
            health_check_endpoint=health_check_endpoint,
            fallback_extension=fallback_extension,
            status=ExtensionStatus.PENDING.value,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.contracts[extension_id] = contract
        self._save()
        
        return contract
    
    def validate_extension(self, extension_id: str) -> ExtensionValidation:
        """验证扩展"""
        if extension_id not in self.contracts:
            return ExtensionValidation(
                extension_id=extension_id,
                valid=False,
                errors=["扩展不存在"],
                warnings=[],
                validated_at=datetime.now().isoformat()
            )
        
        contract = self.contracts[extension_id]
        errors = []
        warnings = []
        
        # 检查契约要求
        requirements = self.CONTRACT_REQUIREMENTS.get(contract.type, [])
        
        # 基础验证
        if not contract.name:
            errors.append("缺少名称")
        
        if not contract.version:
            errors.append("缺少版本号")
        
        if not contract.description:
            warnings.append("缺少描述")
        
        if contract.risk_level not in [r.value for r in RiskLevel]:
            errors.append(f"无效的风险等级: {contract.risk_level}")
        
        # 检查依赖
        for dep in contract.dependencies:
            if dep not in self.contracts:
                warnings.append(f"依赖不存在: {dep}")
        
        # 检查回退
        if contract.fallback_extension:
            if contract.fallback_extension not in self.contracts:
                warnings.append(f"回退扩展不存在: {contract.fallback_extension}")
        
        valid = len(errors) == 0
        
        validation = ExtensionValidation(
            extension_id=extension_id,
            valid=valid,
            errors=errors,
            warnings=warnings,
            validated_at=datetime.now().isoformat()
        )
        
        self.validations[extension_id] = validation
        
        # 更新状态
        if valid:
            contract.status = ExtensionStatus.APPROVED.value
            self._save()
        
        return validation
    
    def activate_extension(self, extension_id: str) -> Dict:
        """激活扩展"""
        if extension_id not in self.contracts:
            return {"error": "扩展不存在"}
        
        contract = self.contracts[extension_id]
        
        # 检查是否已验证
        if extension_id not in self.validations or not self.validations[extension_id].valid:
            return {"error": "扩展未通过验证"}
        
        contract.status = ExtensionStatus.ACTIVE.value
        contract.updated_at = datetime.now().isoformat()
        self._save()
        
        return {"status": "success", "extension_id": extension_id}
    
    def deprecate_extension(self, extension_id: str, reason: str = "") -> Dict:
        """废弃扩展"""
        if extension_id not in self.contracts:
            return {"error": "扩展不存在"}
        
        contract = self.contracts[extension_id]
        contract.status = ExtensionStatus.DEPRECATED.value
        contract.updated_at = datetime.now().isoformat()
        contract.metadata["deprecation_reason"] = reason
        self._save()
        
        return {"status": "success", "message": f"扩展已废弃: {reason}"}
    
    def remove_extension(self, extension_id: str) -> Dict:
        """下线扩展"""
        if extension_id not in self.contracts:
            return {"error": "扩展不存在"}
        
        contract = self.contracts[extension_id]
        contract.status = ExtensionStatus.REMOVED.value
        contract.updated_at = datetime.now().isoformat()
        self._save()
        
        return {"status": "success", "message": "扩展已下线"}
    
    def get_active_extensions(self, ext_type: str = None) -> List[ExtensionContract]:
        """获取活跃扩展"""
        extensions = [
            c for c in self.contracts.values()
            if c.status == ExtensionStatus.ACTIVE.value
        ]
        
        if ext_type:
            extensions = [e for e in extensions if e.type == ext_type]
        
        return extensions
    
    def get_extensions_by_risk(self, risk_level: str) -> List[ExtensionContract]:
        """按风险等级获取扩展"""
        return [
            c for c in self.contracts.values()
            if c.risk_level == risk_level
        ]
    
    def health_check(self, extension_id: str) -> Dict:
        """健康检查"""
        if extension_id not in self.contracts:
            return {"error": "扩展不存在"}
        
        contract = self.contracts[extension_id]
        
        # 简化实现：检查状态
        if contract.status != ExtensionStatus.ACTIVE.value:
            return {
                "extension_id": extension_id,
                "healthy": False,
                "reason": f"扩展状态: {contract.status}"
            }
        
        return {
            "extension_id": extension_id,
            "healthy": True,
            "status": contract.status,
            "last_check": datetime.now().isoformat()
        }
    
    def get_contract_requirements(self, ext_type: str) -> List[str]:
        """获取接入契约要求"""
        return self.CONTRACT_REQUIREMENTS.get(ext_type, [])
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 扩展协议报告",
            "",
            "## 扩展统计",
            ""
        ]
        
        status_count = {}
        for contract in self.contracts.values():
            status_count[contract.status] = status_count.get(contract.status, 0) + 1
        
        for status, count in status_count.items():
            lines.append(f"- {status}: {count}")
        
        lines.extend([
            "",
            "## 活跃扩展",
            ""
        ])
        
        for ext in self.get_active_extensions():
            lines.append(f"- **{ext.name}** ({ext.type}): {ext.risk_level} 风险")
        
        lines.extend([
            "",
            "## 高风险扩展",
            ""
        ])
        
        high_risk = self.get_extensions_by_risk(RiskLevel.HIGH.value) + \
                    self.get_extensions_by_risk(RiskLevel.CRITICAL.value)
        
        for ext in high_risk:
            lines.append(f"- ⚠️ **{ext.name}**: {ext.risk_level}")
        
        lines.extend([
            "",
            "## 接入契约要求",
            ""
        ])
        
        for ext_type, requirements in self.CONTRACT_REQUIREMENTS.items():
            lines.append(f"### {ext_type}")
            for req in requirements:
                lines.append(f"- {req}")
            lines.append("")
        
        return "\n".join(lines)

# 全局实例
_contract_manager = None

def get_contract_manager() -> ExtensionContractManager:
    global _contract_manager
    if _contract_manager is None:
        _contract_manager = ExtensionContractManager()
    return _contract_manager
