"""
Workflow Template Loader - Workflow 模板加载器
从文件或字典加载 workflow 模板
"""

from typing import Dict, List, Optional, Any
import json
import os

from .workflow_registry import (
    WorkflowTemplate,
    WorkflowStep,
    RecoveryPolicy,
    RecoveryPolicyType,
    WorkflowStatus,
    get_workflow_registry
)


class WorkflowTemplateLoader:
    """
    Workflow 模板加载器
    
    从文件或字典加载 workflow 模板并注册
    """
    
    def __init__(self, template_dir: str = "orchestration/templates"):
        self._template_dir = template_dir
        self._registry = get_workflow_registry()
    
    def load_from_file(self, file_path: str) -> Optional[WorkflowTemplate]:
        """
        从文件加载模板
        
        Args:
            file_path: 文件路径
            
        Returns:
            Workflow 模板
        """
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self.load_from_dict(data)
        except Exception as e:
            print(f"Error loading template from {file_path}: {e}")
            return None
    
    def load_from_dict(self, data: Dict[str, Any]) -> WorkflowTemplate:
        """
        从字典加载模板
        
        Args:
            data: 模板数据
            
        Returns:
            Workflow 模板
        """
        # 解析恢复策略
        recovery_policy = None
        if data.get("recovery_policy"):
            recovery_policy = self._parse_recovery_policy(data["recovery_policy"])
        
        # 解析步骤
        steps = []
        for step_data in data.get("steps", []):
            step = self._parse_step(step_data)
            steps.append(step)
        
        # 解析状态
        status = WorkflowStatus.ACTIVE
        if data.get("status"):
            try:
                status = WorkflowStatus(data["status"])
            except:
                pass
        
        # 创建模板
        template = WorkflowTemplate(
            workflow_id=data["workflow_id"],
            version=data.get("version", "1.0.0"),
            name=data["name"],
            description=data.get("description", ""),
            profile_compatibility=data.get("profile_compatibility", ["default"]),
            required_capabilities=data.get("required_capabilities", []),
            steps=steps,
            recovery_policy=recovery_policy,
            safe_mode_supported=data.get("safe_mode_supported", True),
            status=status,
            metadata=data.get("metadata", {})
        )
        
        return template
    
    def load_and_register(self, data: Dict[str, Any]) -> bool:
        """
        加载并注册模板
        
        Args:
            data: 模板数据
            
        Returns:
            是否注册成功
        """
        template = self.load_from_dict(data)
        return self._registry.register(template)
    
    def load_all_from_dir(self, dir_path: Optional[str] = None) -> int:
        """
        从目录加载所有模板
        
        Args:
            dir_path: 目录路径（可选，默认使用 template_dir）
            
        Returns:
            加载的模板数量
        """
        target_dir = dir_path or self._template_dir
        
        if not os.path.exists(target_dir):
            return 0
        
        count = 0
        for filename in os.listdir(target_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(target_dir, filename)
                template = self.load_from_file(file_path)
                if template and self._registry.register(template):
                    count += 1
        
        return count
    
    def _parse_recovery_policy(self, data: Dict[str, Any]) -> RecoveryPolicy:
        """
        解析恢复策略
        
        Args:
            data: 策略数据
            
        Returns:
            恢复策略
        """
        policy_type = RecoveryPolicyType.RETRY
        if data.get("policy_type"):
            try:
                policy_type = RecoveryPolicyType(data["policy_type"])
            except:
                pass
        
        return RecoveryPolicy(
            policy_type=policy_type,
            max_retries=data.get("max_retries", 3),
            retry_delay_ms=data.get("retry_delay_ms", 1000),
            fallback_skill=data.get("fallback_skill"),
            rollback_to_step=data.get("rollback_to_step"),
            skip_on_failure=data.get("skip_on_failure", False)
        )
    
    def _parse_step(self, data: Dict[str, Any]) -> WorkflowStep:
        """
        解析步骤
        
        Args:
            data: 步骤数据
            
        Returns:
            Workflow 步骤
        """
        # 解析恢复策略
        recovery_policy = None
        if data.get("recovery_policy"):
            recovery_policy = self._parse_recovery_policy(data["recovery_policy"])
        
        return WorkflowStep(
            step_id=data["step_id"],
            name=data["name"],
            action=data["action"],
            description=data.get("description", ""),
            depends_on=data.get("depends_on", []),
            required_capabilities=data.get("required_capabilities", []),
            timeout_ms=data.get("timeout_ms", 30000),
            recovery_policy=recovery_policy,
            is_high_risk=data.get("is_high_risk", False),
            safe_mode_supported=data.get("safe_mode_supported", True),
            params=data.get("params", {})
        )


# 预定义模板
BUILTIN_TEMPLATES = [
    {
        "workflow_id": "minimum_loop",
        "version": "1.0.0",
        "name": "Minimum Loop",
        "description": "最小循环工作流",
        "profile_compatibility": ["default", "development", "production"],
        "required_capabilities": ["skill.execute"],
        "steps": [
            {
                "step_id": "step_1",
                "name": "Initialize",
                "action": "initialize",
                "description": "初始化",
                "depends_on": [],
                "required_capabilities": [],
                "timeout_ms": 5000
            },
            {
                "step_id": "step_2",
                "name": "Execute",
                "action": "execute",
                "description": "执行",
                "depends_on": ["step_1"],
                "required_capabilities": ["skill.execute"],
                "timeout_ms": 30000
            },
            {
                "step_id": "step_3",
                "name": "Finalize",
                "action": "finalize",
                "description": "完成",
                "depends_on": ["step_2"],
                "required_capabilities": [],
                "timeout_ms": 5000
            }
        ],
        "recovery_policy": {
            "policy_type": "retry",
            "max_retries": 3,
            "retry_delay_ms": 1000
        },
        "safe_mode_supported": True
    },
    {
        "workflow_id": "dag_example",
        "version": "1.0.0",
        "name": "DAG Example",
        "description": "DAG 示例工作流",
        "profile_compatibility": ["default", "development"],
        "required_capabilities": ["skill.execute", "memory.read", "memory.write"],
        "steps": [
            {
                "step_id": "prepare",
                "name": "Prepare Data",
                "action": "memory.read",
                "description": "准备数据",
                "depends_on": [],
                "required_capabilities": ["memory.read"],
                "timeout_ms": 10000
            },
            {
                "step_id": "process",
                "name": "Process Data",
                "action": "skill.execute",
                "description": "处理数据",
                "depends_on": ["prepare"],
                "required_capabilities": ["skill.execute"],
                "timeout_ms": 30000,
                "is_high_risk": False
            },
            {
                "step_id": "save",
                "name": "Save Results",
                "action": "memory.write",
                "description": "保存结果",
                "depends_on": ["process"],
                "required_capabilities": ["memory.write"],
                "timeout_ms": 10000
            }
        ],
        "recovery_policy": {
            "policy_type": "fallback",
            "max_retries": 2,
            "fallback_skill": "default_fallback"
        },
        "safe_mode_supported": True
    }
]


def load_builtin_templates():
    """加载内置模板"""
    loader = WorkflowTemplateLoader()
    for template_data in BUILTIN_TEMPLATES:
        loader.load_and_register(template_data)


# 全局单例
_workflow_template_loader = None

def get_workflow_template_loader() -> WorkflowTemplateLoader:
    """获取模板加载器单例"""
    global _workflow_template_loader
    if _workflow_template_loader is None:
        _workflow_template_loader = WorkflowTemplateLoader()
    return _workflow_template_loader
