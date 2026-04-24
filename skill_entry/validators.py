"""
Validators - 参数校验器
提供统一的输入参数校验功能
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class ValidationResult:
    """校验结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """合并两个校验结果"""
        return ValidationResult(
            valid=self.valid and other.valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings
        )


class Validators:
    """参数校验器集合"""
    
    @staticmethod
    def validate_required(data: Dict[str, Any], fields: List[str]) -> ValidationResult:
        """校验必填字段"""
        errors = []
        for field in fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )
    
    @staticmethod
    def validate_string(
        value: Any, 
        field_name: str,
        min_length: int = 0,
        max_length: int = 10000,
        pattern: Optional[str] = None
    ) -> ValidationResult:
        """校验字符串"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append(f"{field_name} must be a string")
            return ValidationResult(False, errors, warnings)
        
        if len(value) < min_length:
            errors.append(f"{field_name} must be at least {min_length} characters")
        
        if len(value) > max_length:
            errors.append(f"{field_name} must be at most {max_length} characters")
        
        if pattern and not re.match(pattern, value):
            errors.append(f"{field_name} does not match required pattern")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @staticmethod
    def validate_integer(
        value: Any,
        field_name: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> ValidationResult:
        """校验整数"""
        errors = []
        
        if not isinstance(value, int):
            errors.append(f"{field_name} must be an integer")
            return ValidationResult(False, errors, [])
        
        if min_value is not None and value < min_value:
            errors.append(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            errors.append(f"{field_name} must be at most {max_value}")
        
        return ValidationResult(len(errors) == 0, errors, [])
    
    @staticmethod
    def validate_datetime(
        value: Any,
        field_name: str,
        format: str = "%Y-%m-%d %H:%M:%S"
    ) -> ValidationResult:
        """校验日期时间格式"""
        errors = []
        
        if not isinstance(value, str):
            errors.append(f"{field_name} must be a string")
            return ValidationResult(False, errors, [])
        
        try:
            datetime.strptime(value, format)
        except ValueError:
            errors.append(f"{field_name} must be in format {format}")
        
        return ValidationResult(len(errors) == 0, errors, [])
    
    @staticmethod
    def validate_enum(
        value: Any,
        field_name: str,
        allowed_values: List[Any]
    ) -> ValidationResult:
        """校验枚举值"""
        errors = []
        
        if value not in allowed_values:
            errors.append(
                f"{field_name} must be one of: {allowed_values}, got: {value}"
            )
        
        return ValidationResult(len(errors) == 0, errors, [])
    
    @staticmethod
    def validate_list(
        value: Any,
        field_name: str,
        min_items: int = 0,
        max_items: Optional[int] = None,
        item_validator: Optional[callable] = None
    ) -> ValidationResult:
        """校验列表"""
        errors = []
        warnings = []
        
        if not isinstance(value, list):
            errors.append(f"{field_name} must be a list")
            return ValidationResult(False, errors, warnings)
        
        if len(value) < min_items:
            errors.append(f"{field_name} must have at least {min_items} items")
        
        if max_items is not None and len(value) > max_items:
            errors.append(f"{field_name} must have at most {max_items} items")
        
        if item_validator:
            for i, item in enumerate(value):
                item_result = item_validator(item, f"{field_name}[{i}]")
                errors.extend(item_result.errors)
                warnings.extend(item_result.warnings)
        
        return ValidationResult(len(errors) == 0, errors, warnings)


def validate_input(
    data: Dict[str, Any],
    schema: Dict[str, Any]
) -> ValidationResult:
    """
    根据schema校验输入数据
    
    Args:
        data: 待校验的数据
        schema: 校验规则
        
    Returns:
        校验结果
    """
    results = []
    
    # 校验必填字段
    if "required" in schema:
        result = Validators.validate_required(data, schema["required"])
        results.append(result)
    
    # 校验字段类型和约束
    for field, rules in schema.get("fields", {}).items():
        if field not in data:
            continue
        
        value = data[field]
        field_type = rules.get("type")
        
        if field_type == "string":
            result = Validators.validate_string(
                value, field,
                min_length=rules.get("min_length", 0),
                max_length=rules.get("max_length", 10000),
                pattern=rules.get("pattern")
            )
            results.append(result)
        
        elif field_type == "integer":
            result = Validators.validate_integer(
                value, field,
                min_value=rules.get("min"),
                max_value=rules.get("max")
            )
            results.append(result)
        
        elif field_type == "datetime":
            result = Validators.validate_datetime(
                value, field,
                format=rules.get("format", "%Y-%m-%d %H:%M:%S")
            )
            results.append(result)
        
        elif field_type == "enum":
            result = Validators.validate_enum(
                value, field,
                rules.get("values", [])
            )
            results.append(result)
        
        elif field_type == "list":
            result = Validators.validate_list(
                value, field,
                min_items=rules.get("min_items", 0),
                max_items=rules.get("max_items"),
                item_validator=rules.get("item_validator")
            )
            results.append(result)
    
    # 合并所有结果
    final_result = ValidationResult(True, [], [])
    for r in results:
        final_result = final_result.merge(r)
    
    return final_result
