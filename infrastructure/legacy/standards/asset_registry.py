#!/usr/bin/env python3
"""
平台标准资产注册中心 - V2.8.0

资产类型：
- 标准工作流规范
- 标准产物规范
- 标准行业模板
- 标准服务包定义
- 标准接口契约
- 标准测试集
- 标准审计模板
- 标准交付手册
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class AssetType(Enum):
    WORKFLOW = "workflow"           # 工作流规范
    PRODUCT = "product"             # 产物规范
    TEMPLATE = "template"           # 行业模板
    SERVICE_PACKAGE = "service_package"  # 服务包
    INTERFACE = "interface"         # 接口契约
    TEST_SUITE = "test_suite"       # 测试集
    AUDIT = "audit"                 # 审计模板
    DELIVERY = "delivery"           # 交付手册

class AssetStatus(Enum):
    DRAFT = "draft"                 # 草稿
    PUBLISHED = "published"         # 已发布
    DEPRECATED = "deprecated"       # 已废弃
    RETIRED = "retired"             # 已下线

@dataclass
class StandardAsset:
    """标准资产"""
    asset_id: str
    name: str
    asset_type: str
    version: str
    status: str
    description: str
    specification: Dict            # 规范定义
    examples: List[Dict]           # 示例
    test_cases: List[Dict]         # 测试用例
    dependencies: List[str]        # 依赖
    tags: List[str]
    owner: str
    created_at: str
    updated_at: str
    published_at: Optional[str]
    deprecation_date: Optional[str]
    usage_count: int

@dataclass
class AssetVersion:
    """资产版本"""
    asset_id: str
    version: str
    changes: List[str]
    breaking_changes: bool
    created_at: str

@dataclass
class ComplianceCheck:
    """合规检查"""
    check_id: str
    asset_id: str
    check_type: str
    result: str                     # pass / fail
    findings: List[str]
    checked_at: str

class StandardAssetRegistry:
    """平台标准资产注册中心"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.standards_path = self.project_root / 'standards'
        self.config_path = self.standards_path / 'assets.json'
        
        # 资产
        self.assets: Dict[str, StandardAsset] = {}
        
        # 版本历史
        self.versions: List[AssetVersion] = []
        
        # 合规检查
        self.compliance_checks: List[ComplianceCheck] = []
        
        self._init_default_assets()
        self._load()
    
    def _init_default_assets(self):
        """初始化默认资产"""
        # 标准工作流规范
        workflow_asset = StandardAsset(
            asset_id="std_workflow_001",
            name="标准工作流规范",
            asset_type=AssetType.WORKFLOW.value,
            version="1.0.0",
            status=AssetStatus.PUBLISHED.value,
            description="工作流定义标准规范",
            specification={
                "required_fields": ["name", "description", "steps", "inputs", "outputs"],
                "step_schema": {
                    "name": "string",
                    "skill": "string",
                    "inputs": "object",
                    "outputs": "object",
                    "fallback": "string?",
                    "timeout": "number?"
                },
                "validation_rules": [
                    "所有步骤必须有名称",
                    "所有步骤必须指定技能",
                    "必须有至少一个输入定义",
                    "必须有至少一个输出定义"
                ]
            },
            examples=[
                {
                    "name": "示例工作流",
                    "description": "这是一个示例",
                    "steps": [
                        {"name": "步骤1", "skill": "web_search", "inputs": {}, "outputs": {}}
                    ],
                    "inputs": [{"name": "query", "type": "string"}],
                    "outputs": [{"name": "result", "type": "object"}]
                }
            ],
            test_cases=[
                {"name": "测试必需字段", "input": {}, "expected": "fail"},
                {"name": "测试完整定义", "input": {"name": "test"}, "expected": "pass"}
            ],
            dependencies=[],
            tags=["workflow", "standard"],
            owner="platform",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            published_at=datetime.now().isoformat(),
            deprecation_date=None,
            usage_count=0
        )
        
        # 标准产物规范
        product_asset = StandardAsset(
            asset_id="std_product_001",
            name="标准产物规范",
            asset_type=AssetType.PRODUCT.value,
            version="1.0.0",
            status=AssetStatus.PUBLISHED.value,
            description="产物输出标准规范",
            specification={
                "supported_formats": ["markdown", "html", "docx", "xlsx", "csv", "txt"],
                "required_metadata": ["created_at", "creator", "workspace_id"],
                "naming_convention": "{type}_{timestamp}_{random}",
                "storage_rules": {
                    "max_size_mb": 100,
                    "retention_days": 365,
                    "archive_after_days": 90
                }
            },
            examples=[
                {
                    "format": "markdown",
                    "metadata": {"created_at": "2024-01-01", "creator": "system"},
                    "content": "# 报告标题\n\n内容..."
                }
            ],
            test_cases=[],
            dependencies=[],
            tags=["product", "standard"],
            owner="platform",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            published_at=datetime.now().isoformat(),
            deprecation_date=None,
            usage_count=0
        )
        
        # 标准服务包定义
        package_asset = StandardAsset(
            asset_id="std_package_001",
            name="标准服务包定义",
            asset_type=AssetType.SERVICE_PACKAGE.value,
            version="1.0.0",
            status=AssetStatus.PUBLISHED.value,
            description="服务包定义标准规范",
            specification={
                "required_fields": ["name", "type", "workflows", "products", "permissions"],
                "package_types": ["basic_analysis", "project_advance", "audit_diagnosis", "product_delivery", "industry_special", "custom_enhanced"],
                "pricing_tiers": ["basic", "standard", "premium", "enterprise"],
                "limitation_rules": {
                    "max_tasks_per_day": "number",
                    "max_projects": "number",
                    "max_storage_mb": "number"
                }
            },
            examples=[],
            test_cases=[],
            dependencies=[],
            tags=["package", "standard"],
            owner="platform",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            published_at=datetime.now().isoformat(),
            deprecation_date=None,
            usage_count=0
        )
        
        # 标准接口契约
        interface_asset = StandardAsset(
            asset_id="std_interface_001",
            name="标准接口契约",
            asset_type=AssetType.INTERFACE.value,
            version="1.0.0",
            status=AssetStatus.PUBLISHED.value,
            description="接口契约标准规范",
            specification={
                "request_format": {
                    "action": "string (required)",
                    "params": "object (optional)",
                    "auth_token": "string (required)",
                    "workspace_id": "string (required)"
                },
                "response_format": {
                    "request_id": "string",
                    "status": "string",
                    "result": "object (optional)",
                    "error": "string (optional)"
                },
                "error_codes": {
                    "1xxx": "客户端错误",
                    "2xxx": "认证授权错误",
                    "3xxx": "资源错误",
                    "4xxx": "业务错误",
                    "5xxx": "系统错误"
                }
            },
            examples=[],
            test_cases=[],
            dependencies=[],
            tags=["interface", "standard"],
            owner="platform",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            published_at=datetime.now().isoformat(),
            deprecation_date=None,
            usage_count=0
        )
        
        # 标准测试集
        test_asset = StandardAsset(
            asset_id="std_test_001",
            name="标准测试集",
            asset_type=AssetType.TEST_SUITE.value,
            version="1.0.0",
            status=AssetStatus.PUBLISHED.value,
            description="测试用例标准规范",
            specification={
                "test_types": ["unit", "integration", "e2e", "performance", "security"],
                "required_fields": ["name", "type", "steps", "expected"],
                "coverage_rules": {
                    "min_coverage": 80,
                    "critical_paths": 100
                }
            },
            examples=[],
            test_cases=[],
            dependencies=[],
            tags=["test", "standard"],
            owner="platform",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            published_at=datetime.now().isoformat(),
            deprecation_date=None,
            usage_count=0
        )
        
        # 标准审计模板
        audit_asset = StandardAsset(
            asset_id="std_audit_001",
            name="标准审计模板",
            asset_type=AssetType.AUDIT.value,
            version="1.0.0",
            status=AssetStatus.PUBLISHED.value,
            description="审计模板标准规范",
            specification={
                "audit_types": ["security", "compliance", "performance", "access"],
                "required_sections": ["summary", "findings", "recommendations", "appendix"],
                "retention_rules": {
                    "audit_logs": "3年",
                    "access_logs": "1年",
                    "performance_logs": "30天"
                }
            },
            examples=[],
            test_cases=[],
            dependencies=[],
            tags=["audit", "standard"],
            owner="platform",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            published_at=datetime.now().isoformat(),
            deprecation_date=None,
            usage_count=0
        )
        
        # 标准交付手册
        delivery_asset = StandardAsset(
            asset_id="std_delivery_001",
            name="标准交付手册",
            asset_type=AssetType.DELIVERY.value,
            version="1.0.0",
            status=AssetStatus.PUBLISHED.value,
            description="交付手册标准规范",
            specification={
                "required_sections": [
                    "项目概述",
                    "交付范围",
                    "交付清单",
                    "使用说明",
                    "维护指南",
                    "联系方式"
                ],
                "document_format": "markdown",
                "version_control": "required"
            },
            examples=[],
            test_cases=[],
            dependencies=[],
            tags=["delivery", "standard"],
            owner="platform",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            published_at=datetime.now().isoformat(),
            deprecation_date=None,
            usage_count=0
        )
        
        self.assets[workflow_asset.asset_id] = workflow_asset
        self.assets[product_asset.asset_id] = product_asset
        self.assets[package_asset.asset_id] = package_asset
        self.assets[interface_asset.asset_id] = interface_asset
        self.assets[test_asset.asset_id] = test_asset
        self.assets[audit_asset.asset_id] = audit_asset
        self.assets[delivery_asset.asset_id] = delivery_asset
    
    def _load(self):
        """加载资产"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for aid, asset in data.get("assets", {}).items():
                self.assets[aid] = StandardAsset(**asset)
            
            self.versions = [AssetVersion(**v) for v in data.get("versions", [])]
            self.compliance_checks = [ComplianceCheck(**c) for c in data.get("compliance_checks", [])]
    
    def _save(self):
        """保存资产"""
        self.standards_path.mkdir(parents=True, exist_ok=True)
        data = {
            "assets": {aid: asdict(a) for aid, a in self.assets.items()},
            "versions": [asdict(v) for v in self.versions],
            "compliance_checks": [asdict(c) for c in self.compliance_checks],
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def get_asset(self, asset_id: str) -> Optional[StandardAsset]:
        """获取资产"""
        return self.assets.get(asset_id)
    
    def list_assets(self, asset_type: str = None,
                    status: str = None, tags: List[str] = None) -> List[StandardAsset]:
        """列出资产"""
        assets = list(self.assets.values())
        
        if asset_type:
            assets = [a for a in assets if a.asset_type == asset_type]
        if status:
            assets = [a for a in assets if a.status == status]
        if tags:
            assets = [a for a in assets if any(tag in a.tags for tag in tags)]
        
        return assets
    
    def create_asset(self, name: str, asset_type: str,
                     description: str, specification: Dict,
                     owner: str, tags: List[str] = None) -> StandardAsset:
        """创建资产"""
        asset_id = f"std_{asset_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        asset = StandardAsset(
            asset_id=asset_id,
            name=name,
            asset_type=asset_type,
            version="1.0.0",
            status=AssetStatus.DRAFT.value,
            description=description,
            specification=specification,
            examples=[],
            test_cases=[],
            dependencies=[],
            tags=tags or [],
            owner=owner,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            published_at=None,
            deprecation_date=None,
            usage_count=0
        )
        
        self.assets[asset_id] = asset
        self._save()
        
        return asset
    
    def publish_asset(self, asset_id: str) -> Dict:
        """发布资产"""
        if asset_id not in self.assets:
            return {"error": "资产不存在"}
        
        asset = self.assets[asset_id]
        asset.status = AssetStatus.PUBLISHED.value
        asset.published_at = datetime.now().isoformat()
        self._save()
        
        return {"status": "published", "asset_id": asset_id}
    
    def deprecate_asset(self, asset_id: str, deprecation_date: str) -> Dict:
        """废弃资产"""
        if asset_id not in self.assets:
            return {"error": "资产不存在"}
        
        asset = self.assets[asset_id]
        asset.status = AssetStatus.DEPRECATED.value
        asset.deprecation_date = deprecation_date
        self._save()
        
        return {"status": "deprecated", "asset_id": asset_id}
    
    def upgrade_version(self, asset_id: str, new_version: str,
                        changes: List[str], breaking: bool = False) -> AssetVersion:
        """升级版本"""
        if asset_id not in self.assets:
            raise ValueError("资产不存在")
        
        asset = self.assets[asset_id]
        old_version = asset.version
        
        # 记录版本历史
        version = AssetVersion(
            asset_id=asset_id,
            version=old_version,
            changes=changes,
            breaking_changes=breaking,
            created_at=datetime.now().isoformat()
        )
        
        self.versions.append(version)
        
        # 更新资产版本
        asset.version = new_version
        asset.updated_at = datetime.now().isoformat()
        self._save()
        
        return version
    
    def validate_compliance(self, asset_id: str, target: Dict) -> ComplianceCheck:
        """验证合规性"""
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError("资产不存在")
        
        findings = []
        result = "pass"
        
        # 检查必需字段
        spec = asset.specification
        if "required_fields" in spec:
            for field in spec["required_fields"]:
                if field not in target:
                    findings.append(f"缺少必需字段: {field}")
                    result = "fail"
        
        check = ComplianceCheck(
            check_id=f"check_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            asset_id=asset_id,
            check_type="compliance",
            result=result,
            findings=findings,
            checked_at=datetime.now().isoformat()
        )
        
        self.compliance_checks.append(check)
        self._save()
        
        return check
    
    def record_usage(self, asset_id: str):
        """记录使用"""
        if asset_id in self.assets:
            self.assets[asset_id].usage_count += 1
            self._save()
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 平台标准资产报告",
            "",
            "## 资产列表",
            ""
        ]
        
        for asset in self.assets.values():
            status = "✅" if asset.status == AssetStatus.PUBLISHED.value else "📝"
            lines.append(f"### {status} {asset.name} (v{asset.version})")
            lines.append(f"- 类型: {asset.asset_type}")
            lines.append(f"- 状态: {asset.status}")
            lines.append(f"- 使用次数: {asset.usage_count}")
            lines.append(f"- 标签: {', '.join(asset.tags)}")
            lines.append("")
        
        lines.extend([
            "## 合规检查统计",
            ""
        ])
        
        passed = len([c for c in self.compliance_checks if c.result == "pass"])
        failed = len([c for c in self.compliance_checks if c.result == "fail"])
        lines.append(f"- 通过: {passed}")
        lines.append(f"- 失败: {failed}")
        
        return "\n".join(lines)

# 全局实例
_asset_registry = None

def get_asset_registry() -> StandardAssetRegistry:
    global _asset_registry
    if _asset_registry is None:
        _asset_registry = StandardAssetRegistry()
    return _asset_registry
