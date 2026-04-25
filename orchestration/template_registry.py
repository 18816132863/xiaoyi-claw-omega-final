"""
Template Registry - 模板注册表
管理任务模板和工作流模板
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaskTemplate:
    """任务模板"""
    name: str
    description: str
    task_type: str
    default_params: Dict[str, Any] = field(default_factory=dict)
    required_params: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def render(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """渲染模板参数"""
        # 检查必需参数
        missing = [p for p in self.required_params if p not in params]
        if missing:
            raise ValueError(f"缺少必需参数: {missing}")
        
        # 合并默认参数
        result = dict(self.default_params)
        result.update(params)
        
        return result


@dataclass
class WorkflowTemplate:
    """工作流模板"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    default_params: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TemplateRegistry:
    """
    模板注册表
    管理任务模板和工作流模板
    """
    
    def __init__(self):
        self._task_templates: Dict[str, TaskTemplate] = {}
        self._workflow_templates: Dict[str, WorkflowTemplate] = {}
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """初始化默认模板"""
        # 默认消息任务模板
        self.register_task_template(TaskTemplate(
            name="scheduled_message",
            description="定时消息任务模板",
            task_type="scheduled_message",
            default_params={
                "message": "",
                "channel": "default"
            },
            required_params=["message"]
        ))
        
        # 默认循环任务模板
        self.register_task_template(TaskTemplate(
            name="recurring_message",
            description="循环消息任务模板",
            task_type="recurring_message",
            default_params={
                "message": "",
                "cron_expr": "0 9 * * *"
            },
            required_params=["message"]
        ))
    
    def register_task_template(self, template: TaskTemplate) -> None:
        """注册任务模板"""
        self._task_templates[template.name] = template
        logger.info(f"Registered task template: {template.name}")
    
    def register_workflow_template(self, template: WorkflowTemplate) -> None:
        """注册工作流模板"""
        self._workflow_templates[template.name] = template
        logger.info(f"Registered workflow template: {template.name}")
    
    def get_task_template(self, name: str) -> Optional[TaskTemplate]:
        """获取任务模板"""
        return self._task_templates.get(name)
    
    def get_workflow_template(self, name: str) -> Optional[WorkflowTemplate]:
        """获取工作流模板"""
        return self._workflow_templates.get(name)
    
    def list_task_templates(self) -> List[str]:
        """列出所有任务模板"""
        return list(self._task_templates.keys())
    
    def list_workflow_templates(self) -> List[str]:
        """列出所有工作流模板"""
        return list(self._workflow_templates.keys())
    
    def render_task(self, template_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """渲染任务模板"""
        template = self.get_task_template(template_name)
        if not template:
            raise ValueError(f"模板不存在: {template_name}")
        
        return template.render(params)
