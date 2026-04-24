"""注册表完整性验证器 - V4.3.0

检查技能条目字段是否缺失，entry 路径是否有效
"""

from typing import Dict, List
from pathlib import Path
from infrastructure.path_resolver import get_project_root
import json

class RegistryValidator:
    """注册表完整性验证器"""
    
    # 必需字段
    REQUIRED_FIELDS = [
        "id", "name", "category", "description",
        "entry", "version", "status"
    ]
    
    # 推荐字段
    RECOMMENDED_FIELDS = [
        "input_schema", "output_schema", "dependencies",
        "owner", "tags"
    ]
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.registry_path = self.workspace / "infrastructure/inventory/skill_registry.json"
        self.violations: List[Dict] = []
    
    def validate(self) -> Dict:
        """执行验证"""
        self.violations = []
        
        if not self.registry_path.exists():
            return {
                "valid": False,
                "violations": [{"error": "注册表文件不存在"}],
                "total_skills": 0
            }
        
        with open(self.registry_path) as f:
            registry = json.load(f)
        
        skills = registry.get("skills", {})
        
        for skill_id, skill_info in skills.items():
            self._validate_skill(skill_id, skill_info)
        
        return {
            "valid": len(self.violations) == 0,
            "violations": self.violations,
            "total_skills": len(skills),
            "valid_skills": len(skills) - len([v for v in self.violations if v["type"] == "missing_field"])
        }
    
    def _validate_skill(self, skill_id: str, skill_info: Dict):
        """验证单个技能"""
        # 检查必需字段
        for field in self.REQUIRED_FIELDS:
            if field not in skill_info or not skill_info[field]:
                self.violations.append({
                    "skill_id": skill_id,
                    "type": "missing_field",
                    "field": field
                })
        
        # 检查 entry 路径
        if "entry" in skill_info:
            entry_path = self.workspace / skill_info["entry"]
            if not entry_path.exists():
                self.violations.append({
                    "skill_id": skill_id,
                    "type": "invalid_entry",
                    "entry": skill_info["entry"]
                })
        
        # 检查 version/status 格式
        if "version" in skill_info:
            if not re.match(r"^\d+\.\d+\.\d+$", str(skill_info["version"])):
                self.violations.append({
                    "skill_id": skill_id,
                    "type": "invalid_version",
                    "version": skill_info["version"]
                })
        
        if "status" in skill_info:
            valid_statuses = ["active", "deprecated", "experimental", "planned"]
            if skill_info["status"] not in valid_statuses:
                self.violations.append({
                    "skill_id": skill_id,
                    "type": "invalid_status",
                    "status": skill_info["status"]
                })

import re
