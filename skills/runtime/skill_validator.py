"""Skill Validator - 技能验证器"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]


class SkillValidator:
    """技能验证器"""
    
    REQUIRED_FIELDS = [
        "skill_id", "name", "version", "description", 
        "category", "executor_type"
    ]
    
    VALID_CATEGORIES = [
        "ai", "search", "image", "document", "video",
        "finance", "code", "ecommerce", "data", "memory",
        "audio", "automation", "communication", "utility", "other"
    ]
    
    VALID_EXECUTOR_TYPES = ["skill_md", "python", "http", "subprocess"]
    
    def validate_manifest(self, manifest_data: Dict) -> ValidationResult:
        """验证技能清单"""
        errors = []
        warnings = []
        
        # 检查必需字段
        for field in self.REQUIRED_FIELDS:
            if field not in manifest_data or not manifest_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # 检查分类
        if "category" in manifest_data:
            if manifest_data["category"] not in self.VALID_CATEGORIES:
                errors.append(f"Invalid category: {manifest_data['category']}")
        
        # 检查执行器类型
        if "executor_type" in manifest_data:
            if manifest_data["executor_type"] not in self.VALID_EXECUTOR_TYPES:
                errors.append(f"Invalid executor_type: {manifest_data['executor_type']}")
        
        # 检查版本格式
        if "version" in manifest_data:
            version = manifest_data["version"]
            if not self._is_valid_version(version):
                warnings.append(f"Version format may be invalid: {version}")
        
        # 检查超时
        if "timeout_seconds" in manifest_data:
            timeout = manifest_data["timeout_seconds"]
            if not isinstance(timeout, int) or timeout < 1:
                errors.append(f"Invalid timeout_seconds: {timeout}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _is_valid_version(self, version: str) -> bool:
        """检查版本格式"""
        parts = version.split(".")
        if len(parts) < 2:
            return False
        try:
            [int(p) for p in parts]
            return True
        except ValueError:
            return False
    
    def validate_input(self, manifest, input_data: Dict) -> ValidationResult:
        """验证输入数据"""
        errors = []
        warnings = []
        
        # 检查输入契约
        input_contract = manifest.input_contract if hasattr(manifest, 'input_contract') else {}
        
        if input_contract:
            required_fields = input_contract.get("required", [])
            for field in required_fields:
                if field not in input_data:
                    errors.append(f"Missing required input field: {field}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_output(self, manifest, output_data: Dict) -> ValidationResult:
        """验证输出数据"""
        errors = []
        warnings = []
        
        # 检查输出契约
        output_contract = manifest.output_contract if hasattr(manifest, 'output_contract') else {}
        
        if output_contract:
            required_fields = output_contract.get("required", [])
            for field in required_fields:
                if field not in output_data:
                    errors.append(f"Missing required output field: {field}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
