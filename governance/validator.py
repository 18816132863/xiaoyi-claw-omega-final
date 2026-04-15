#!/usr/bin/env python3
"""
结果验证器 - V1.0.0

验证工具和技能的执行结果。
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """验证级别"""
    ERROR = "error"      # 必须通过
    WARNING = "warning"  # 警告但不阻断
    INFO = "info"        # 仅记录


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    level: ValidationLevel
    message: str
    details: Optional[Dict] = None


class Validator:
    """验证器基类"""
    
    def validate(self, result: Any) -> ValidationResult:
        """验证结果"""
        raise NotImplementedError


class TypeValidator(Validator):
    """类型验证器"""
    
    def __init__(self, expected_type: type):
        self.expected_type = expected_type
    
    def validate(self, result: Any) -> ValidationResult:
        if isinstance(result, self.expected_type):
            return ValidationResult(
                valid=True,
                level=ValidationLevel.INFO,
                message=f"类型验证通过: {type(result).__name__}"
            )
        return ValidationResult(
            valid=False,
            level=ValidationLevel.ERROR,
            message=f"类型不匹配: 期望 {self.expected_type.__name__}, 实际 {type(result).__name__}"
        )


class DictSchemaValidator(Validator):
    """字典 Schema 验证器"""
    
    def __init__(self, required_keys: List[str], optional_keys: List[str] = None):
        self.required_keys = required_keys
        self.optional_keys = optional_keys or []
    
    def validate(self, result: Any) -> ValidationResult:
        if not isinstance(result, dict):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message="结果不是字典类型"
            )
        
        missing = [k for k in self.required_keys if k not in result]
        if missing:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message=f"缺少必要字段: {missing}",
                details={"missing": missing}
            )
        
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            message="Schema 验证通过"
        )


class SkillResultValidator(Validator):
    """技能结果验证器"""
    
    def __init__(self):
        self.schema_validator = DictSchemaValidator(
            required_keys=["success"],
            optional_keys=["data", "error"]
        )
    
    def validate(self, result: Any) -> ValidationResult:
        # 验证基本结构
        schema_result = self.schema_validator.validate(result)
        if not schema_result.valid:
            return schema_result
        
        # 验证 success 字段
        if not isinstance(result.get("success"), bool):
            return ValidationResult(
                valid=False,
                level=ValidationLevel.ERROR,
                message="success 字段必须是布尔值"
            )
        
        # 验证失败时的 error 字段
        if not result.get("success") and "error" not in result:
            return ValidationResult(
                valid=False,
                level=ValidationLevel.WARNING,
                message="失败结果建议包含 error 字段"
            )
        
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            message="技能结果验证通过"
        )


class CompositeValidator(Validator):
    """组合验证器"""
    
    def __init__(self, validators: List[Validator]):
        self.validators = validators
    
    def validate(self, result: Any) -> ValidationResult:
        for validator in self.validators:
            val_result = validator.validate(result)
            if not val_result.valid and val_result.level == ValidationLevel.ERROR:
                return val_result
        return ValidationResult(
            valid=True,
            level=ValidationLevel.INFO,
            message="所有验证通过"
        )


# 预定义验证器
SKILL_RESULT_VALIDATOR = SkillResultValidator()
FILE_RESULT_VALIDATOR = DictSchemaValidator(
    required_keys=["path"],
    optional_keys=["content", "size", "modified"]
)
