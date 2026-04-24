#!/usr/bin/env python3
"""
商业封装层管理器 - V2.8.0

服务包定义：
- 基础分析包：数据分析、报告生成
- 项目推进包：项目跟踪、状态管理
- 审计诊断包：架构检查、代码审计
- 产物交付包：文档生成、产物管理
- 行业专项包：电商、工厂、直播等
- 定制增强包：高级功能、定制服务
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class PackageType(Enum):
    BASIC_ANALYSIS = "basic_analysis"       # 基础分析包
    PROJECT_ADVANCE = "project_advance"     # 项目推进包
    AUDIT_DIAGNOSIS = "audit_diagnosis"    # 审计诊断包
    PRODUCT_DELIVERY = "product_delivery"   # 产物交付包
    INDUSTRY_SPECIAL = "industry_special"   # 行业专项包
    CUSTOM_ENHANCED = "custom_enhanced"     # 定制增强包

class PackageStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"

@dataclass
class ServicePackage:
    """服务包"""
    package_id: str
    name: str
    package_type: str
    description: str
    included_workflows: List[str]
    included_products: List[str]
    permissions: List[str]
    limitations: Dict[str, Any]
    dependencies: List[str]
    upgrade_path: List[str]
    status: str
    price_tier: str
    created_at: str
    updated_at: str

class BusinessPackagingManager:
    """商业封装层管理器"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.package_path = self.project_root / 'business' / 'service_packages.json'
        
        self.packages: Dict[str, ServicePackage] = {}
        
        self._init_default_packages()
        self._load()
    
    def _init_default_packages(self):
        """初始化默认服务包"""
        default_packages = [
            # 基础分析包
            ServicePackage(
                package_id="pkg_basic_analysis",
                name="基础分析包",
                package_type=PackageType.BASIC_ANALYSIS.value,
                description="数据分析与报告生成基础能力",
                included_workflows=["ecommerce_product_analysis"],
                included_products=["markdown_report", "csv_table"],
                permissions=["task_execution", "product_archive"],
                limitations={"max_tasks_per_day": 100, "max_products_per_month": 500},
                dependencies=[],
                upgrade_path=["pkg_project_advance", "pkg_industry_special"],
                status=PackageStatus.ACTIVE.value,
                price_tier="basic",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            # 项目推进包
            ServicePackage(
                package_id="pkg_project_advance",
                name="项目推进包",
                package_type=PackageType.PROJECT_ADVANCE.value,
                description="项目跟踪与状态管理能力",
                included_workflows=["store_launch", "file_organization"],
                included_products=["execution_plan", "todo_list", "summary"],
                permissions=["task_execution", "project_management", "product_archive"],
                limitations={"max_projects": 10, "max_tasks_per_project": 1000},
                dependencies=["pkg_basic_analysis"],
                upgrade_path=["pkg_custom_enhanced"],
                status=PackageStatus.ACTIVE.value,
                price_tier="standard",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            # 审计诊断包
            ServicePackage(
                package_id="pkg_audit_diagnosis",
                name="审计诊断包",
                package_type=PackageType.AUDIT_DIAGNOSIS.value,
                description="架构检查与代码审计能力",
                included_workflows=["code_audit"],
                included_products=["audit_report"],
                permissions=["audit_execution", "product_archive"],
                limitations={"max_audits_per_month": 50},
                dependencies=[],
                upgrade_path=["pkg_custom_enhanced"],
                status=PackageStatus.ACTIVE.value,
                price_tier="standard",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            # 产物交付包
            ServicePackage(
                package_id="pkg_product_delivery",
                name="产物交付包",
                package_type=PackageType.PRODUCT_DELIVERY.value,
                description="文档生成与产物管理能力",
                included_workflows=["file_organization"],
                included_products=["markdown_report", "txt_instruction", "csv_table", "xlsx_table"],
                permissions=["task_execution", "product_archive", "data_export"],
                limitations={"max_storage_mb": 1000},
                dependencies=["pkg_basic_analysis"],
                upgrade_path=["pkg_custom_enhanced"],
                status=PackageStatus.ACTIVE.value,
                price_tier="basic",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            # 行业专项包
            ServicePackage(
                package_id="pkg_industry_ecommerce",
                name="电商行业专项包",
                package_type=PackageType.INDUSTRY_SPECIAL.value,
                description="电商行业专项能力",
                included_workflows=["ecommerce_product_analysis", "partner_selection"],
                included_products=["comparison_list", "contact_list"],
                permissions=["task_execution", "product_archive", "external_tool_access"],
                limitations={"max_tasks_per_day": 500},
                dependencies=["pkg_basic_analysis"],
                upgrade_path=["pkg_custom_enhanced"],
                status=PackageStatus.ACTIVE.value,
                price_tier="premium",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            # 行业专项包 - 工厂
            ServicePackage(
                package_id="pkg_industry_factory",
                name="工厂行业专项包",
                package_type=PackageType.INDUSTRY_SPECIAL.value,
                description="工厂筛选与比价专项能力",
                included_workflows=["factory_comparison"],
                included_products=["comparison_list", "contact_list"],
                permissions=["task_execution", "product_archive", "external_tool_access"],
                limitations={"max_tasks_per_day": 200},
                dependencies=["pkg_basic_analysis"],
                upgrade_path=["pkg_custom_enhanced"],
                status=PackageStatus.ACTIVE.value,
                price_tier="premium",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            # 定制增强包
            ServicePackage(
                package_id="pkg_custom_enhanced",
                name="定制增强包",
                package_type=PackageType.CUSTOM_ENHANCED.value,
                description="高级功能与定制服务",
                included_workflows=["all"],
                included_products=["all"],
                permissions=["all"],
                limitations={},
                dependencies=["pkg_basic_analysis"],
                upgrade_path=[],
                status=PackageStatus.ACTIVE.value,
                price_tier="enterprise",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        ]
        
        for pkg in default_packages:
            self.packages[pkg.package_id] = pkg
    
    def _load(self):
        """加载服务包"""
        if self.package_path.exists():
            data = json.loads(self.package_path.read_text(encoding='utf-8'))
            for pkg_id, pkg_data in data.get("packages", {}).items():
                self.packages[pkg_id] = ServicePackage(**pkg_data)
    
    def _save(self):
        """保存服务包"""
        self.package_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "packages": {pkg_id: asdict(pkg) for pkg_id, pkg in self.packages.items()},
            "updated": datetime.now().isoformat()
        }
        self.package_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def get_package(self, package_id: str) -> Optional[ServicePackage]:
        """获取服务包"""
        return self.packages.get(package_id)
    
    def list_packages(self, package_type: str = None, status: str = None) -> List[ServicePackage]:
        """列出服务包"""
        packages = list(self.packages.values())
        
        if package_type:
            packages = [p for p in packages if p.package_type == package_type]
        
        if status:
            packages = [p for p in packages if p.status == status]
        
        return packages
    
    def create_custom_package(self, name: str, package_type: str,
                             description: str, included_workflows: List[str],
                             included_products: List[str], permissions: List[str],
                             limitations: Dict, dependencies: List[str],
                             price_tier: str = "custom") -> ServicePackage:
        """创建自定义服务包"""
        package_id = f"pkg_custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        package = ServicePackage(
            package_id=package_id,
            name=name,
            package_type=package_type,
            description=description,
            included_workflows=included_workflows,
            included_products=included_products,
            permissions=permissions,
            limitations=limitations,
            dependencies=dependencies,
            upgrade_path=[],
            status=PackageStatus.ACTIVE.value,
            price_tier=price_tier,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.packages[package_id] = package
        self._save()
        
        return package
    
    def check_workflow_access(self, package_id: str, workflow: str) -> tuple:
        """检查工作流访问权限"""
        package = self.get_package(package_id)
        if not package:
            return False, "服务包不存在"
        
        if "all" in package.included_workflows:
            return True, "允许访问"
        
        if workflow in package.included_workflows:
            return True, "允许访问"
        
        return False, f"服务包不包含工作流: {workflow}"
    
    def check_product_access(self, package_id: str, product_type: str) -> tuple:
        """检查产物访问权限"""
        package = self.get_package(package_id)
        if not package:
            return False, "服务包不存在"
        
        if "all" in package.included_products:
            return True, "允许访问"
        
        if product_type in package.included_products:
            return True, "允许访问"
        
        return False, f"服务包不包含产物类型: {product_type}"
    
    def check_limitation(self, package_id: str, limit_type: str, current_value: int) -> tuple:
        """检查限制"""
        package = self.get_package(package_id)
        if not package:
            return False, "服务包不存在"
        
        limit = package.limitations.get(limit_type)
        if limit is None:
            return True, "无限制"
        
        if current_value >= limit:
            return False, f"已达上限: {limit}"
        
        return True, f"剩余: {limit - current_value}"
    
    def get_upgrade_options(self, package_id: str) -> List[Dict]:
        """获取升级选项"""
        package = self.get_package(package_id)
        if not package:
            return []
        
        options = []
        for upgrade_id in package.upgrade_path:
            upgrade_pkg = self.get_package(upgrade_id)
            if upgrade_pkg:
                options.append({
                    "package_id": upgrade_id,
                    "name": upgrade_pkg.name,
                    "price_tier": upgrade_pkg.price_tier
                })
        
        return options
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 服务包体系报告",
            "",
            "## 服务包列表",
            ""
        ]
        
        for pkg in self.packages.values():
            status = "✅" if pkg.status == PackageStatus.ACTIVE.value else "❌"
            lines.append(f"### {status} {pkg.name}")
            lines.append(f"- 类型: {pkg.package_type}")
            lines.append(f"- 价格层级: {pkg.price_tier}")
            lines.append(f"- 包含工作流: {', '.join(pkg.included_workflows[:5])}")
            lines.append(f"- 包含产物: {', '.join(pkg.included_products[:5])}")
            if pkg.limitations:
                lines.append(f"- 限制: {pkg.limitations}")
            lines.append("")
        
        return "\n".join(lines)

# 全局实例
_packaging_manager = None

def get_packaging_manager() -> BusinessPackagingManager:
    global _packaging_manager
    if _packaging_manager is None:
        _packaging_manager = BusinessPackagingManager()
    return _packaging_manager
