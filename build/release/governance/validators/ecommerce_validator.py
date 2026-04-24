"""电商闭环专项验证器 - V4.3.0

检查电商闭环完整性
"""

from typing import Dict, List
from pathlib import Path
from infrastructure.path_resolver import get_project_root

class EcommerceValidator:
    """电商闭环专项验证器"""
    
    # 电商闭环必需组件
    REQUIRED_COMPONENTS = [
        "execution/ecommerce/models/lead.py",
        "execution/ecommerce/models/scorer.py",
        "execution/ecommerce/models/templates.py",
        "execution/ecommerce/models/result.py",
        "execution/ecommerce/models/reviewer.py"
    ]
    
    # 电商技能
    ECOMMERCE_SKILLS = [
        "dealer-leader-cooperation",
        "douyin-shop-operation",
        "kuaishou-shop-operation",
        "platform-comparison",
        "product-management",
        "marketing-campaign",
        "ecommerce-analytics",
        "supply-chain-management",
        "customer-service"
    ]
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.violations: List[Dict] = []
    
    def validate(self) -> Dict:
        """执行验证"""
        self.violations = []
        
        # 检查组件
        self._check_components()
        
        # 检查技能注册
        self._check_skill_registry()
        
        return {
            "valid": len(self.violations) == 0,
            "violations": self.violations,
            "components_checked": len(self.REQUIRED_COMPONENTS),
            "skills_checked": len(self.ECOMMERCE_SKILLS)
        }
    
    def _check_components(self):
        """检查必需组件"""
        for component in self.REQUIRED_COMPONENTS:
            component_path = self.workspace / component
            if not component_path.exists():
                self.violations.append({
                    "type": "missing_component",
                    "component": component
                })
    
    def _check_skill_registry(self):
        """检查技能注册"""
        import json
        
        registry_path = self.workspace / "infrastructure/inventory/skill_registry.json"
        if not registry_path.exists():
            self.violations.append({
                "type": "missing_registry"
            })
            return
        
        with open(registry_path) as f:
            registry = json.load(f)
        
        skills = registry.get("skills", {})
        
        for skill_id in self.ECOMMERCE_SKILLS:
            if skill_id not in skills:
                self.violations.append({
                    "type": "missing_skill",
                    "skill_id": skill_id
                })
            else:
                # 检查是否有完整 schema
                skill = skills[skill_id]
                if "input_schema" not in skill:
                    self.violations.append({
                        "type": "missing_input_schema",
                        "skill_id": skill_id
                    })
                if "output_schema" not in skill:
                    self.violations.append({
                        "type": "missing_output_schema",
                        "skill_id": skill_id
                    })
