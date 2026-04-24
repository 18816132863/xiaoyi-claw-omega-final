from collections import defaultdict
#!/usr/bin/env python3
"""
服务模板与复制引擎 - V2.8.0

模板类型：
- 行业模板
- 项目模板
- 客户交付模板
- 工作流模板
- 产物模板
- 启动模板
"""

import json
import shutil
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class TemplateType(Enum):
    INDUSTRY = "industry"           # 行业模板
    PROJECT = "project"             # 项目模板
    CUSTOMER = "customer"           # 客户交付模板
    WORKFLOW = "workflow"           # 工作流模板
    PRODUCT = "product"             # 产物模板
    BOOTSTRAP = "bootstrap"         # 启动模板

class TemplateStatus(Enum):
    DRAFT = "draft"                 # 草稿
    PUBLISHED = "published"         # 已发布
    DEPRECATED = "deprecated"       # 已废弃

@dataclass
class Template:
    """模板"""
    template_id: str
    name: str
    template_type: str
    description: str
    version: str
    status: str
    content: Dict[str, Any]
    variables: List[Dict]           # 可配置变量
    dependencies: List[str]
    tags: List[str]
    created_at: str
    updated_at: str
    usage_count: int

@dataclass
class TemplateInstance:
    """模板实例"""
    instance_id: str
    template_id: str
    tenant_id: str
    workspace_id: str
    variables_applied: Dict[str, Any]
    created_at: str
    status: str

class TemplateReplicationEngine:
    """服务模板与复制引擎"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.template_path = self.project_root / 'templates'
        self.registry_path = self.template_path / 'template_registry.json'
        
        self.templates: Dict[str, Template] = {}
        self.instances: List[TemplateInstance] = []
        
        self._init_default_templates()
        self._load()
    
    def _init_default_templates(self):
        """初始化默认模板"""
        default_templates = [
            # 电商行业模板
            Template(
                template_id="tpl_industry_ecommerce",
                name="电商行业模板",
                template_type=TemplateType.INDUSTRY.value,
                description="电商行业标准配置模板",
                version="1.0.0",
                status=TemplateStatus.PUBLISHED.value,
                content={
                    "workflows": ["ecommerce_product_analysis", "partner_selection"],
                    "products": ["comparison_list", "contact_list", "report"],
                    "permissions": ["task_execution", "product_archive"],
                    "settings": {"default_output_format": "markdown"}
                },
                variables=[
                    {"name": "platform", "type": "string", "default": "淘宝", "description": "电商平台"},
                    {"name": "category", "type": "string", "default": "", "description": "主营类目"}
                ],
                dependencies=[],
                tags=["电商", "选品", "分析"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                usage_count=0
            ),
            # 工厂行业模板
            Template(
                template_id="tpl_industry_factory",
                name="工厂行业模板",
                template_type=TemplateType.INDUSTRY.value,
                description="工厂筛选与比价标准模板",
                version="1.0.0",
                status=TemplateStatus.PUBLISHED.value,
                content={
                    "workflows": ["factory_comparison"],
                    "products": ["comparison_list", "contact_list"],
                    "permissions": ["task_execution", "product_archive"],
                    "settings": {"default_output_format": "xlsx"}
                },
                variables=[
                    {"name": "product_type", "type": "string", "default": "", "description": "产品类型"},
                    {"name": "region", "type": "string", "default": "广东", "description": "地区偏好"}
                ],
                dependencies=[],
                tags=["工厂", "采购", "比价"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                usage_count=0
            ),
            # 项目模板
            Template(
                template_id="tpl_project_standard",
                name="标准项目模板",
                template_type=TemplateType.PROJECT.value,
                description="标准项目配置模板",
                version="1.0.0",
                status=TemplateStatus.PUBLISHED.value,
                content={
                    "stages": ["初始化", "规划", "执行", "验收", "归档"],
                    "workflows": ["store_launch", "file_organization"],
                    "products": ["execution_plan", "todo_list", "summary"],
                    "roles": ["operator", "reviewer"]
                },
                variables=[
                    {"name": "project_name", "type": "string", "default": "", "description": "项目名称"},
                    {"name": "deadline", "type": "date", "default": "", "description": "截止日期"}
                ],
                dependencies=[],
                tags=["项目", "管理"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                usage_count=0
            ),
            # 客户交付模板
            Template(
                template_id="tpl_customer_delivery",
                name="客户交付模板",
                template_type=TemplateType.CUSTOMER.value,
                description="新客户交付标准模板",
                version="1.0.0",
                status=TemplateStatus.PUBLISHED.value,
                content={
                    "onboarding_steps": [
                        "创建工作区",
                        "配置权限",
                        "导入模板",
                        "初始化项目",
                        "交付培训"
                    ],
                    "default_package": "pkg_basic_analysis",
                    "default_settings": {}
                },
                variables=[
                    {"name": "customer_name", "type": "string", "default": "", "description": "客户名称"},
                    {"name": "contact", "type": "string", "default": "", "description": "联系人"}
                ],
                dependencies=[],
                tags=["客户", "交付", "入驻"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                usage_count=0
            ),
            # 工作流模板
            Template(
                template_id="tpl_workflow_analysis",
                name="分析工作流模板",
                template_type=TemplateType.WORKFLOW.value,
                description="通用分析工作流模板",
                version="1.0.0",
                status=TemplateStatus.PUBLISHED.value,
                content={
                    "steps": [
                        {"name": "数据收集", "skill": "web_search"},
                        {"name": "数据分析", "skill": "data_analysis"},
                        {"name": "报告生成", "skill": "docx"}
                    ],
                    "fallback": "简化分析",
                    "timeout": 300
                },
                variables=[
                    {"name": "analysis_type", "type": "string", "default": "general", "description": "分析类型"}
                ],
                dependencies=[],
                tags=["工作流", "分析"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                usage_count=0
            ),
            # 产物模板
            Template(
                template_id="tpl_product_report",
                name="报告产物模板",
                template_type=TemplateType.PRODUCT.value,
                description="标准报告产物模板",
                version="1.0.0",
                status=TemplateStatus.PUBLISHED.value,
                content={
                    "format": "markdown",
                    "sections": ["概述", "分析", "结论", "建议"],
                    "style": {"heading_level": 2, "bullet_points": True}
                },
                variables=[
                    {"name": "title", "type": "string", "default": "分析报告", "description": "报告标题"}
                ],
                dependencies=[],
                tags=["产物", "报告"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                usage_count=0
            ),
            # 启动模板
            Template(
                template_id="tpl_bootstrap_quick",
                name="快速启动模板",
                template_type=TemplateType.BOOTSTRAP.value,
                description="快速启动配置模板",
                version="1.0.0",
                status=TemplateStatus.PUBLISHED.value,
                content={
                    "initial_setup": [
                        "创建工作区",
                        "配置基础权限",
                        "导入行业模板",
                        "创建首个项目"
                    ],
                    "default_settings": {
                        "mode": "execution",
                        "role": "operator"
                    }
                },
                variables=[],
                dependencies=[],
                tags=["启动", "初始化"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                usage_count=0
            )
        ]
        
        for template in default_templates:
            self.templates[template.template_id] = template
    
    def _load(self):
        """加载模板"""
        if self.registry_path.exists():
            data = json.loads(self.registry_path.read_text(encoding='utf-8'))
            
            for tid, tdata in data.get("templates", {}).items():
                self.templates[tid] = Template(**tdata)
            
            self.instances = [TemplateInstance(**i) for i in data.get("instances", [])]
    
    def _save(self):
        """保存模板"""
        self.template_path.mkdir(parents=True, exist_ok=True)
        data = {
            "templates": {tid: asdict(t) for tid, t in self.templates.items()},
            "instances": [asdict(i) for i in self.instances],
            "updated": datetime.now().isoformat()
        }
        self.registry_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """获取模板"""
        return self.templates.get(template_id)
    
    def list_templates(self, template_type: str = None, 
                       status: str = None, tags: List[str] = None) -> List[Template]:
        """列出模板"""
        templates = list(self.templates.values())
        
        if template_type:
            templates = [t for t in templates if t.template_type == template_type]
        
        if status:
            templates = [t for t in templates if t.status == status]
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
        
        return templates
    
    def create_template(self, name: str, template_type: str,
                        description: str, content: Dict,
                        variables: List[Dict] = None,
                        dependencies: List[str] = None,
                        tags: List[str] = None) -> Template:
        """创建模板"""
        template_id = f"tpl_{template_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        template = Template(
            template_id=template_id,
            name=name,
            template_type=template_type,
            description=description,
            version="1.0.0",
            status=TemplateStatus.DRAFT.value,
            content=content,
            variables=variables or [],
            dependencies=dependencies or [],
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            usage_count=0
        )
        
        self.templates[template_id] = template
        self._save()
        
        return template
    
    def publish_template(self, template_id: str) -> Dict:
        """发布模板"""
        if template_id not in self.templates:
            return {"error": "模板不存在"}
        
        template = self.templates[template_id]
        template.status = TemplateStatus.PUBLISHED.value
        template.updated_at = datetime.now().isoformat()
        self._save()
        
        return {"status": "success", "template_id": template_id}
    
    def deprecate_template(self, template_id: str) -> Dict:
        """废弃模板"""
        if template_id not in self.templates:
            return {"error": "模板不存在"}
        
        template = self.templates[template_id]
        template.status = TemplateStatus.DEPRECATED.value
        template.updated_at = datetime.now().isoformat()
        self._save()
        
        return {"status": "success", "template_id": template_id}
    
    def instantiate(self, template_id: str, tenant_id: str,
                    workspace_id: str, variables: Dict = None) -> TemplateInstance:
        """实例化模板"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")
        
        # 应用变量
        applied_vars = {}
        for var in template.variables:
            var_name = var["name"]
            if variables and var_name in variables:
                applied_vars[var_name] = variables[var_name]
            else:
                applied_vars[var_name] = var.get("default", "")
        
        instance = TemplateInstance(
            instance_id=f"inst_{template_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            template_id=template_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            variables_applied=applied_vars,
            created_at=datetime.now().isoformat(),
            status="active"
        )
        
        self.instances.append(instance)
        template.usage_count += 1
        self._save()
        
        return instance
    
    def upgrade_template(self, template_id: str, new_content: Dict,
                         new_version: str = None) -> Template:
        """升级模板"""
        if template_id not in self.templates:
            raise ValueError(f"模板不存在: {template_id}")
        
        template = self.templates[template_id]
        template.content = new_content
        if new_version:
            template.version = new_version
        template.updated_at = datetime.now().isoformat()
        self._save()
        
        return template
    
    def get_template_content(self, template_id: str, 
                             variables: Dict = None) -> Dict:
        """获取模板内容（应用变量）"""
        template = self.get_template(template_id)
        if not template:
            return {}
        
        content = template.content.copy()
        
        # 应用变量
        if variables:
            for var in template.variables:
                var_name = var["name"]
                if var_name in variables:
                    # 替换内容中的变量占位符
                    placeholder = f"{{{var_name}}}"
                    value = str(variables[var_name])
                    
                    def replace_recursive(obj):
                        if isinstance(obj, str):
                            return obj.replace(placeholder, value)
                        elif isinstance(obj, dict):
                            return {k: replace_recursive(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [replace_recursive(item) for item in obj]
                        return obj
                    
                    content = replace_recursive(content)
        
        return content
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 模板复制报告",
            "",
            "## 模板列表",
            ""
        ]
        
        for template in self.templates.values():
            status = "✅" if template.status == TemplateStatus.PUBLISHED.value else "📝"
            lines.append(f"### {status} {template.name} (v{template.version})")
            lines.append(f"- 类型: {template.template_type}")
            lines.append(f"- 使用次数: {template.usage_count}")
            lines.append(f"- 标签: {', '.join(template.tags)}")
            lines.append("")
        
        lines.extend([
            "## 实例统计",
            ""
        ])
        
        instance_count = defaultdict(int)
        for instance in self.instances:
            instance_count[instance.template_id] += 1
        
        for tid, count in instance_count.items():
            template = self.get_template(tid)
            if template:
                lines.append(f"- {template.name}: {count} 个实例")
        
        return "\n".join(lines)

# 全局实例
_replication_engine = None

def get_replication_engine() -> TemplateReplicationEngine:
    global _replication_engine
    if _replication_engine is None:
        _replication_engine = TemplateReplicationEngine()
    return _replication_engine
